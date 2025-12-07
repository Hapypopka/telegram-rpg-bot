"""
Обработчики подземелий
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import DUNGEONS
from models import Fight
from utils.storage import get_player, save_data
from utils.helpers import update_fight_ui


# Активные бои
active_fights = {}


async def show_dungeons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список подземелий"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "🏰 ПОДЗЕМЕЛЬЯ\n\nВыбери подземелье для исследования:\n\n"

    keyboard = []

    for dungeon_id, dungeon in DUNGEONS.items():
        locked = player.level < dungeon["min_level"]
        status = "🔒" if locked else "✅"

        text += f"{dungeon['emoji']} {dungeon['name']}\n"
        text += f"  Уровень: {dungeon['min_level']}+ | Этажей: {dungeon['floors']}\n"
        text += f"  Босс: {dungeon['boss_emoji']} {dungeon['boss']}\n"
        text += f"  ⚙️ {dungeon['mechanic_desc']}\n\n"

        if not locked:
            keyboard.append([InlineKeyboardButton(
                f"{dungeon['emoji']} {dungeon['name']}",
                callback_data=f"dungeon_{dungeon_id}"
            )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_dungeon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбрать подземелье"""
    query = update.callback_query
    await query.answer()

    dungeon_id = query.data.replace("dungeon_", "")
    player = get_player(query.from_user.id)

    if dungeon_id not in DUNGEONS:
        await query.answer("Подземелье не найдено!", show_alert=True)
        return

    dungeon = DUNGEONS[dungeon_id]

    if player.level < dungeon["min_level"]:
        await query.answer(f"Нужен уровень {dungeon['min_level']}!", show_alert=True)
        return

    # Показать информацию о подземелье
    text = f"""{dungeon['emoji']} {dungeon['name']}

📜 {dungeon['description']}

📊 Характеристики:
Этажей: {dungeon['floors']}
Босс: {dungeon['boss_emoji']} {dungeon['boss']}

⚙️ Особая механика:
{dungeon['mechanic_desc']}

💰 Награды:
Опыт: x{dungeon['exp_mult']}
Золото: x{dungeon['gold_mult']}
Ресурс: {dungeon['drop_resource']}

Готов начать?"""

    keyboard = [
        [InlineKeyboardButton("⚔️ Войти", callback_data=f"enter_{dungeon_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="dungeons")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def enter_dungeon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Войти в подземелье"""
    query = update.callback_query
    await query.answer()

    dungeon_id = query.data.replace("enter_", "")
    player = get_player(query.from_user.id)

    if dungeon_id not in DUNGEONS:
        return

    dungeon = DUNGEONS[dungeon_id]

    # Установить текущее подземелье
    player.current_dungeon = dungeon_id
    player.current_floor = 1
    save_data()

    # Создать бой
    fight = Fight(player, dungeon_id, 1, is_boss=False)
    active_fights[query.from_user.id] = fight

    # Сразу показать интерфейс боя
    await update_fight_ui(query, fight, player, f"⚔️ Этаж 1 - {fight.enemy_name} атакует!")


async def next_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перейти на следующий этаж"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    if not player.current_dungeon:
        await query.answer("Ты не в подземелье!", show_alert=True)
        return

    dungeon = DUNGEONS[player.current_dungeon]
    player.current_floor += 1

    # Проверить, не босс ли это
    is_boss = player.current_floor >= dungeon["floors"]

    # Создать бой
    fight = Fight(player, player.current_dungeon, player.current_floor, is_boss=is_boss)
    active_fights[query.from_user.id] = fight

    save_data()

    if is_boss:
        extra = f"👑 БОСС! {fight.enemy_name} ждёт тебя!"
    else:
        extra = f"⚔️ Этаж {player.current_floor} - {fight.enemy_name} атакует!"

    await update_fight_ui(query, fight, player, extra)


async def fight_boss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сразиться с боссом"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    if not player.current_dungeon:
        return

    # Создать бой с боссом
    fight = Fight(player, player.current_dungeon, player.current_floor, is_boss=True)
    active_fights[query.from_user.id] = fight

    await update_fight_ui(query, fight, player, f"👑 БОЙ С БОССОМ! {fight.enemy_name}!")


def get_active_fight(user_id: int):
    """Получить активный бой игрока"""
    return active_fights.get(user_id)


def remove_active_fight(user_id: int):
    """Удалить активный бой"""
    if user_id in active_fights:
        del active_fights[user_id]
