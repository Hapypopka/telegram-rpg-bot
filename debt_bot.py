# debt_bot.py
import os
import random
import logging
from datetime import datetime

import aiosqlite
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# ========== CONFIG ==========
TOKEN = "8550867725:AAHAhxhwn8Fu_6_m-fj5io5I0cjAUzCXlM4"  # <- твой токен

DEFAULT_SEND_HOUR = 12
DEFAULT_SEND_MINUTE = 0
DB_PATH = "debts.db"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Scheduler
scheduler = AsyncIOScheduler()
# ============================

# ========== DB helpers ==========
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_chat_id INTEGER NOT NULL,
                debtor_chat_id INTEGER,
                debtor_username TEXT,
                deadline DATE NOT NULL,
                memes_path TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                send_hour INTEGER NOT NULL,
                send_minute INTEGER NOT NULL
            )"""
        )
        await db.commit()


async def add_debt(owner_chat_id: int, debtor_chat_id, debtor_username,
                   deadline_date: str, memes_path: str, send_hour: int, send_minute: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO debts (owner_chat_id, debtor_chat_id, debtor_username, deadline, memes_path, send_hour, send_minute) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (owner_chat_id, debtor_chat_id, debtor_username, deadline_date, memes_path, send_hour, send_minute),
        )
        await db.commit()
        return cur.lastrowid


async def get_debt(debt_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM debts WHERE id = ?", (debt_id,))
        return await cur.fetchone()


async def find_debt_by_debtor(debtor_identifier: str):
    async with aiosqlite.connect(DB_PATH) as db:
        if debtor_identifier.startswith("@"):
            cur = await db.execute("SELECT * FROM debts WHERE debtor_username = ? AND active = 1", (debtor_identifier,))
        else:
            try:
                cid = int(debtor_identifier)
                cur = await db.execute("SELECT * FROM debts WHERE debtor_chat_id = ? AND active = 1", (cid,))
            except ValueError:
                return None
        return await cur.fetchone()


async def list_active_debts():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM debts WHERE active = 1")
        return await cur.fetchall()


async def mark_returned(debt_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE debts SET active = 0 WHERE id = ?", (debt_id,))
        await db.commit()
# ================================

# ========== utilities ==========
def pick_random_media(folder_path: str):
    if not os.path.isdir(folder_path):
        return None
    files = [f for f in os.listdir(folder_path) if not f.startswith(".")]
    if not files:
        return None
    return os.path.join(folder_path, random.choice(files))


def parse_date(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_time(s: str):
    try:
        t = datetime.strptime(s, "%H:%M").time()
        return t.hour, t.minute
    except Exception:
        return None
# ================================

# ========== scheduler job ==========
async def send_meme_job(app, debt_row):
    debt_id, owner_chat_id, debtor_chat_id, debtor_username, deadline, memes_path, active, send_hour, send_minute = debt_row

    if active != 1:
        return

    media_file = pick_random_media(memes_path)
    if not media_file:
        try:
            await app.bot.send_message(owner_chat_id, f"❗ Не могу отправить мем должнику (id {debt_id}). Папка пуста или не существует: {memes_path}")
        except Exception:
            logger.exception("Can't notify owner about empty memes folder.")
        return

    caption = f"Напоминание про долг{(' — ' + debtor_username) if debtor_username else ''}.\nЕсли вернул(а) — нажми кнопку."

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Я вернул(а) 💸", callback_data=f"returned_by_debtor:{debt_id}")]])

    target_chat = debtor_chat_id or debtor_username
    if not target_chat:
        try:
            await app.bot.send_message(owner_chat_id, f"❗ Невозможно отправить напоминание: не задан идентификатор должника для долга #{debt_id}.")
        except Exception:
            logger.exception("Can't notify owner about missing debtor id.")
        return

    try:
        await app.bot.send_document(chat_id=target_chat, document=open(media_file, "rb"), caption=caption, reply_markup=keyboard)
    except Exception as e:
        logger.warning("Failed to send meme to %s: %s", target_chat, e)
        try:
            await app.bot.send_message(owner_chat_id, f"❗ Не удалось отправить мем пользователю {target_chat}. Скорее всего он не запускал бота или блокирует сообщения. Ошибка: {e}")
        except Exception:
            pass
# ================================

# ========== handlers ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет! Я бот-напоминалка про долги.\n"
        f"Твой chat_id: {update.message.chat_id}\n\n"
        f"Команды:\n"
        "/start_debt <chat_id> YYYY-MM-DD [HH:MM]\n"
        "/set_memes_path <debt_id> <path> — задать папку мемов для конкретной задачи\n"
        "/returned <debt_id or chat_id> — отметить долг возвращённым\n"
        "/list — список активных долгов"
    )


async def start_debt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    parts = msg.split()
    if len(parts) < 3:
        await update.message.reply_text("Неверный синтаксис. Пример:\n/start_debt @username 2025-12-07 12:30")
        return

    _, debtor_ident, date_str, *rest = parts
    t = parse_time(rest[0]) if rest else None
    send_hour, send_minute = t if t else (DEFAULT_SEND_HOUR, DEFAULT_SEND_MINUTE)

    dt = parse_date(date_str)
    if not dt:
        await update.message.reply_text("Неверная дата. Используй формат YYYY-MM-DD.")
        return

    debtor_chat_id = None
    debtor_username = None
    if debtor_ident.startswith("@"):
        debtor_username = debtor_ident
    else:
        try:
            debtor_chat_id = int(debtor_ident)
        except ValueError:
            await update.message.reply_text("Должник должен быть указан как @username или chat_id (число).")
            return

    owner_chat_id = update.message.chat_id
    default_memes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memes")
    debt_id = await add_debt(owner_chat_id, debtor_chat_id, debtor_username, dt.isoformat(), default_memes_path, send_hour, send_minute)

    row = await get_debt(debt_id)
    trigger = CronTrigger(hour=send_hour, minute=send_minute)
    scheduler.add_job(send_meme_job, trigger, args=(context.application, row), id=str(debt_id))

    await update.message.reply_text(
        f"Задача создана (id {debt_id}). Должник: {debtor_ident}. Дедлайн: {dt.isoformat()}.\n"
        f"Мемы будут слать в {send_hour:02d}:{send_minute:02d}.\n"
        f"Папка мемов по умолчанию: {default_memes_path}.\n"
        f"Чтобы указать свою папку: /set_memes_path {debt_id} /путь/к/папке"
    )


async def set_memes_path_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text("Использование:\n/set_memes_path <debt_id> <путь_к_папке>")
        return
    _, debt_id_s, path = parts
    try:
        debt_id = int(debt_id_s)
    except ValueError:
        await update.message.reply_text("debt_id должен быть числом.")
        return

    row = await get_debt(debt_id)
    if not row or update.message.chat_id != row[1]:
        await update.message.reply_text("Только владелец долга может менять папку мемов.")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE debts SET memes_path = ? WHERE id = ?", (path, debt_id))
        await db.commit()
    await update.message.reply_text(f"Путь для мемов для задачи {debt_id} установлен на: {path}")


async def returned_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text("Использование:\n/returned <debt_id или @username или chat_id>")
        return
    identifier = parts[1].strip()

    debt_row = await get_debt(int(identifier)) if identifier.isdigit() else await find_debt_by_debtor(identifier)
    if not debt_row:
        await update.message.reply_text("Активная задача не найдена.")
        return

    if update.message.chat_id != debt_row[1]:
        await update.message.reply_text("Только владелец долга может отметить его возвращённым.")
        return

    await mark_returned(debt_row[0])
    try:
        scheduler.remove_job(str(debt_row[0]))
    except Exception:
        pass

    await update.message.reply_text(f"Отмечено как возвращённое: задача {debt_row[0]}.")

    debtor_chat = debt_row[2] or debt_row[3]
    if debtor_chat:
        try:
            await context.bot.send_message(debtor_chat, "Спасибо — долг отмечен как возвращённый. ✅")
        except Exception:
            pass


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_chat_id = update.message.chat_id
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, debtor_username, debtor_chat_id, deadline, memes_path, send_hour, send_minute "
            "FROM debts WHERE owner_chat_id = ? AND active = 1", (owner_chat_id,)
        )
        rows = await cur.fetchall()

    if not rows:
        await update.message.reply_text("У тебя нет активных задач.")
        return

    lines = [f"id {r[0]} — должник {r[1] or r[2]}, дедлайн {r[3]}, время {r[5]:02d}:{r[6]:02d}, папка {r[4]}" for r in rows]
    await update.message.reply_text("\n".join(lines))


async def callback_returned_by_debtor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("returned_by_debtor:"):
        return

    debt_id = int(query.data.split(":")[1])
    debt_row = await get_debt(debt_id)
    if not debt_row:
        await query.edit_message_text("Задача не найдена.")
        return

    await mark_returned(debt_id)
    try:
        scheduler.remove_job(str(debt_id))
    except Exception:
        pass

    try:
        await query.edit_message_text("Спасибо! Мы отметили долг как возвращённый. ✅")
    except Exception:
        pass

    owner_chat_id = debt_row[1]
    debtor_username = debt_row[3] or debt_row[2]
    try:
        await context.bot.send_message(owner_chat_id, f"Пользователь {debtor_username} пометил долг #{debt_id} как возвращённый.")
    except Exception:
        pass
# ================================

# ========== startup ==========
async def on_startup(app):
    # Инициализация БД
    await init_db()
    # Восстановление активных долгов
    rows = await list_active_debts()
    for r in rows:
        debt_id = r[0]
        send_hour = r[7]
        send_minute = r[8]
        trigger = CronTrigger(hour=send_hour, minute=send_minute)
        scheduler.add_job(send_meme_job, trigger, args=(app, r), id=str(debt_id))
    scheduler.start()
    logger.info("Scheduler started, %d jobs restored", len(rows))


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_debt", start_debt_cmd))
    app.add_handler(CommandHandler("set_memes_path", set_memes_path_cmd))
    app.add_handler(CommandHandler("returned", returned_cmd))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CallbackQueryHandler(callback_returned_by_debtor, pattern=r"^returned_by_debtor:"))

    # Вызов инициализации через post_init
    app.post_init = on_startup

    # Запуск бота
    app.run_polling()


if __name__ == "__main__":
    main()
