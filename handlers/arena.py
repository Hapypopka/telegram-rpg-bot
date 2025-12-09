"""
Обработчики PvP арены
"""

import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from data import CLASSES
from models.pvp_fight import PvPFight
from utils.storage import get_player, save_data, players
from utils.helpers import create_hp_bar, create_mana_bar, safe_edit_message

# Очередь поиска матча: {user_id: {"player": Player, "time": datetime, "chat_id": int}}
pvp_queue = {}

# Активные PvP бои: {fight_id: PvPFight}
active_pvp_fights = {}

# Маппинг игрок -> fight_id
player_to_fight = {}

# Награды за победу
PVP_REWARDS = {
    "gold_base": 100,       # Базовое золото
    "gold_per_level": 20,   # +золото за уровень соперника
    "rating_win": 25,       # Рейтинг за победу
    "rating_loss": -15,     # Рейтинг за поражение
    "streak_bonus": 10,     # Бонус за серию побед
}


def get_rating_rank(rating: int) -> str:
    """Получить звание по рейтингу"""
    if rating >= 2000:
        return "👑 Легенда"
    elif rating >= 1700:
        return "💎 Грандмастер"
    elif rating >= 1500:
        return "🏆 Мастер"
    elif rating >= 1300:
        return "⚔️ Боец"
    elif rating >= 1100:
        return "🗡️ Новичок"
    else:
        return "📜 Ученик"


async def show_arena(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню арены"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    # Проверить, в бою ли игрок
    if query.from_user.id in player_to_fight:
        await query.answer("Ты уже в бою!", show_alert=True)
        return

    # Проверить, в поиске ли игрок
    in_queue = query.from_user.id in pvp_queue

    rank = get_rating_rank(player.pvp_rating)
    winrate = 0
    total_games = player.pvp_wins + player.pvp_losses
    if total_games > 0:
        winrate = int(player.pvp_wins / total_games * 100)

    text = f"""⚔️ PVP АРЕНА

{rank}
🏅 Рейтинг: {player.pvp_rating}

📊 Статистика:
├ Победы: {player.pvp_wins}
├ Поражения: {player.pvp_losses}
├ Винрейт: {winrate}%
└ Серия побед: {player.pvp_win_streak}

👥 В очереди: {len(pvp_queue)} игроков"""

    if in_queue:
        text += "\n\n🔍 Идёт поиск соперника..."
        keyboard = [
            [InlineKeyboardButton("❌ Отменить поиск", callback_data="pvp_cancel")],
            [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("⚔️ Найти соперника", callback_data="pvp_search")],
            [InlineKeyboardButton("🏆 Рейтинг игроков", callback_data="pvp_leaderboard")],
            [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
        ]

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def pvp_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать поиск соперника"""
    query = update.callback_query
    user_id = query.from_user.id

    player = get_player(user_id)

    # Проверки
    if not player.player_class:
        await query.answer("Сначала выбери класс!", show_alert=True)
        return

    if player.level < 3:
        await query.answer("Арена доступна с 3 уровня!", show_alert=True)
        return

    if user_id in player_to_fight:
        await query.answer("Ты уже в бою!", show_alert=True)
        return

    if user_id in pvp_queue:
        await query.answer("Ты уже в очереди!", show_alert=True)
        return

    # Поиск соперника в очереди
    opponent_id = None
    for qid, qdata in pvp_queue.items():
        if qid != user_id:
            # Проверить разницу в рейтинге (±200)
            rating_diff = abs(player.pvp_rating - qdata["player"].pvp_rating)
            if rating_diff <= 300:
                opponent_id = qid
                break

    if opponent_id:
        # Нашли соперника - начинаем бой
        opponent_data = pvp_queue.pop(opponent_id)
        opponent = opponent_data["player"]
        opponent_chat_id = opponent_data["chat_id"]

        await query.answer("Соперник найден!")

        # Создать бой
        fight = PvPFight(player, opponent)
        fight_id = f"{user_id}_{opponent_id}_{int(datetime.now().timestamp())}"
        active_pvp_fights[fight_id] = fight
        player_to_fight[user_id] = fight_id
        player_to_fight[opponent_id] = fight_id

        # Отправить сообщение обоим игрокам
        await start_pvp_fight(query, context, fight, fight_id, user_id, opponent_id, opponent_chat_id)
    else:
        # Добавить в очередь
        pvp_queue[user_id] = {
            "player": player,
            "time": datetime.now(),
            "chat_id": query.message.chat_id
        }
        await query.answer("Поиск соперника начат")
        await show_arena(update, context)


async def pvp_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить поиск"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in pvp_queue:
        del pvp_queue[user_id]
        await query.answer("Поиск отменён")
    else:
        await query.answer("Ты не в очереди")

    await show_arena(update, context)


async def start_pvp_fight(query, context, fight: PvPFight, fight_id: str, p1_id: int, p2_id: int, p2_chat_id: int):
    """Начать PvP бой"""
    # Сообщение для игрока 1 (инициатор)
    text1 = get_pvp_fight_text(fight, 1)
    kb1 = get_pvp_fight_keyboard(fight, 1)
    msg1 = await query.edit_message_text(text1, reply_markup=kb1)
    fight.message_id_p1 = msg1.message_id

    # Сообщение для игрока 2
    text2 = get_pvp_fight_text(fight, 2)
    kb2 = get_pvp_fight_keyboard(fight, 2)
    msg2 = await context.bot.send_message(
        chat_id=p2_chat_id,
        text=text2,
        reply_markup=kb2
    )
    fight.message_id_p2 = msg2.message_id


def get_pvp_fight_text(fight: PvPFight, viewer: int) -> str:
    """Получить текст боя для игрока"""
    p1 = fight.get_player_stats(1)
    p2 = fight.get_player_stats(2)

    class_emoji_1 = CLASSES.get(p1["class"], {}).get("emoji", "❓")
    class_emoji_2 = CLASSES.get(p2["class"], {}).get("emoji", "❓")

    hp_bar_1 = create_hp_bar(p1["hp"], p1["max_hp"])
    hp_bar_2 = create_hp_bar(p2["hp"], p2["max_hp"])

    turn_marker_1 = "👉 " if fight.current_turn == 1 else "   "
    turn_marker_2 = "👉 " if fight.current_turn == 2 else "   "

    your_turn = fight.current_turn == viewer

    text = f"""⚔️ PVP БОЙ

{turn_marker_1}{class_emoji_1} {p1['name']} (Lvl {p1['level']})
{hp_bar_1} {p1['hp']}/{p1['max_hp']}
💙 {p1['mana']} | ⚔️ {p1['damage']} | 🛡️ {p1['defense']}

VS

{turn_marker_2}{class_emoji_2} {p2['name']} (Lvl {p2['level']})
{hp_bar_2} {p2['hp']}/{p2['max_hp']}
💙 {p2['mana']} | ⚔️ {p2['damage']} | 🛡️ {p2['defense']}
"""

    # Последние 3 записи лога
    if fight.fight_log:
        text += "\n📜 Бой:\n"
        for log in fight.fight_log[-3:]:
            text += f"  {log}\n"

    if your_turn:
        text += "\n⏳ ТВОЙ ХОД!"
    else:
        other = p2["name"] if viewer == 1 else p1["name"]
        text += f"\n⏳ Ход {other}..."

    return text


def get_pvp_fight_keyboard(fight: PvPFight, viewer: int):
    """Получить клавиатуру боя"""
    your_turn = fight.current_turn == viewer

    if not your_turn:
        # Не твой ход - только кнопка сдаться
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏳️ Сдаться", callback_data="pvp_forfeit")]
        ])

    # Твой ход - все действия
    player_obj = fight.player1 if viewer == 1 else fight.player2
    cooldowns = fight.cooldowns_p1 if viewer == 1 else fight.cooldowns_p2

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Атака", callback_data="pvp_attack"),
            InlineKeyboardButton("🛡️ Блок", callback_data="pvp_block")
        ]
    ]

    # Скиллы
    player_class = player_obj.player_class
    skills = CLASSES.get(player_class, {}).get("skills", {})
    skill_buttons = []
    for skill_id, skill in skills.items():
        cd = cooldowns.get(skill_id, 0)
        if cd > 0:
            btn_text = f"{skill['emoji']} ({cd})"
        else:
            btn_text = f"{skill['emoji']} {skill['name']}"
        skill_buttons.append(
            InlineKeyboardButton(btn_text, callback_data=f"pvp_skill_{skill_id}")
        )

    # По 2 скилла в ряд
    for i in range(0, len(skill_buttons), 2):
        keyboard.append(skill_buttons[i:i+2])

    keyboard.append([InlineKeyboardButton("🏳️ Сдаться", callback_data="pvp_forfeit")])

    return InlineKeyboardMarkup(keyboard)


async def pvp_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Атака в PvP"""
    query = update.callback_query
    user_id = query.from_user.id

    fight_id = player_to_fight.get(user_id)
    if not fight_id:
        await query.answer("Ты не в бою!", show_alert=True)
        return

    fight = active_pvp_fights.get(fight_id)
    if not fight or not fight.is_active:
        await query.answer("Бой завершён!", show_alert=True)
        return

    # Определить номер игрока
    player_num = 1 if user_id == fight.player1_id else 2

    # Проверить ход
    if fight.current_turn != player_num:
        await query.answer("Не твой ход!", show_alert=True)
        return

    await query.answer()

    # Атака
    fight.attack(player_num)

    # Проверить победу
    if not fight.is_active:
        await end_pvp_fight(context, fight, fight_id)
        return

    # Следующий ход
    fight.next_turn()

    # Обновить сообщения
    await update_pvp_messages(context, fight, query.message.chat_id)


async def pvp_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Блок в PvP"""
    query = update.callback_query
    user_id = query.from_user.id

    fight_id = player_to_fight.get(user_id)
    if not fight_id:
        await query.answer("Ты не в бою!", show_alert=True)
        return

    fight = active_pvp_fights.get(fight_id)
    if not fight or not fight.is_active:
        await query.answer("Бой завершён!", show_alert=True)
        return

    player_num = 1 if user_id == fight.player1_id else 2

    if fight.current_turn != player_num:
        await query.answer("Не твой ход!", show_alert=True)
        return

    await query.answer()

    fight.block(player_num)
    fight.next_turn()

    await update_pvp_messages(context, fight, query.message.chat_id)


async def pvp_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использовать скилл в PvP"""
    query = update.callback_query
    user_id = query.from_user.id

    skill_id = query.data.replace("pvp_skill_", "")

    fight_id = player_to_fight.get(user_id)
    if not fight_id:
        await query.answer("Ты не в бою!", show_alert=True)
        return

    fight = active_pvp_fights.get(fight_id)
    if not fight or not fight.is_active:
        await query.answer("Бой завершён!", show_alert=True)
        return

    player_num = 1 if user_id == fight.player1_id else 2

    if fight.current_turn != player_num:
        await query.answer("Не твой ход!", show_alert=True)
        return

    # Использовать скилл
    result = fight.use_skill(player_num, skill_id)

    if "error" in result:
        await query.answer(result["error"], show_alert=True)
        return

    await query.answer()

    # Проверить победу
    if not fight.is_active:
        await end_pvp_fight(context, fight, fight_id)
        return

    fight.next_turn()
    await update_pvp_messages(context, fight, query.message.chat_id)


async def pvp_forfeit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сдаться в PvP"""
    query = update.callback_query
    user_id = query.from_user.id

    fight_id = player_to_fight.get(user_id)
    if not fight_id:
        await query.answer("Ты не в бою!", show_alert=True)
        return

    fight = active_pvp_fights.get(fight_id)
    if not fight or not fight.is_active:
        await query.answer("Бой уже завершён!", show_alert=True)
        return

    await query.answer("Ты сдался...")

    player_num = 1 if user_id == fight.player1_id else 2
    fight.forfeit(player_num)

    await end_pvp_fight(context, fight, fight_id)


async def update_pvp_messages(context, fight: PvPFight, current_chat_id: int):
    """Обновить сообщения обоих игроков"""
    # Обновить для игрока 1
    try:
        text1 = get_pvp_fight_text(fight, 1)
        kb1 = get_pvp_fight_keyboard(fight, 1)
        await context.bot.edit_message_text(
            chat_id=fight.player1_id,
            message_id=fight.message_id_p1,
            text=text1,
            reply_markup=kb1
        )
    except BadRequest:
        pass  # Сообщение не изменилось - игнорируем
    except Exception:
        pass

    # Обновить для игрока 2
    try:
        text2 = get_pvp_fight_text(fight, 2)
        kb2 = get_pvp_fight_keyboard(fight, 2)
        await context.bot.edit_message_text(
            chat_id=fight.player2_id,
            message_id=fight.message_id_p2,
            text=text2,
            reply_markup=kb2
        )
    except BadRequest:
        pass  # Сообщение не изменилось - игнорируем
    except Exception:
        pass


async def end_pvp_fight(context, fight: PvPFight, fight_id: str):
    """Завершить PvP бой"""
    winner_num = fight.winner
    winner = fight.player1 if winner_num == 1 else fight.player2
    loser = fight.player2 if winner_num == 1 else fight.player1

    # Обновить статистику
    winner_player = get_player(winner.user_id)
    loser_player = get_player(loser.user_id)

    # Рейтинг
    rating_change = PVP_REWARDS["rating_win"]
    streak_bonus = winner_player.pvp_win_streak * PVP_REWARDS["streak_bonus"]
    rating_change += min(streak_bonus, 50)  # Макс +50 за серию

    winner_player.pvp_rating += rating_change
    loser_player.pvp_rating = max(0, loser_player.pvp_rating + PVP_REWARDS["rating_loss"])

    # Статистика
    winner_player.pvp_wins += 1
    winner_player.pvp_win_streak += 1
    loser_player.pvp_losses += 1
    loser_player.pvp_win_streak = 0

    # Золото
    gold_reward = PVP_REWARDS["gold_base"] + loser_player.level * PVP_REWARDS["gold_per_level"]
    winner_player.gold += gold_reward

    save_data()

    # Текст результата
    winner_text = f"""🏆 ПОБЕДА!

Ты победил {loser.name}!

Награды:
├ 💰 +{gold_reward} золота
├ 🏅 +{rating_change} рейтинга
└ 🔥 Серия побед: {winner_player.pvp_win_streak}

Твой рейтинг: {winner_player.pvp_rating}"""

    loser_text = f"""💀 ПОРАЖЕНИЕ

{winner.name} победил тебя!

├ 🏅 {PVP_REWARDS['rating_loss']} рейтинга
└ 🔥 Серия прервана

Твой рейтинг: {loser_player.pvp_rating}"""

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ На арену", callback_data="arena")],
        [InlineKeyboardButton("🏠 В меню", callback_data="menu")]
    ])

    # Отправить результаты
    try:
        await context.bot.edit_message_text(
            chat_id=winner.user_id,
            message_id=fight.message_id_p1 if winner_num == 1 else fight.message_id_p2,
            text=winner_text,
            reply_markup=kb
        )
    except BadRequest:
        pass
    except Exception:
        pass

    try:
        await context.bot.edit_message_text(
            chat_id=loser.user_id,
            message_id=fight.message_id_p2 if winner_num == 1 else fight.message_id_p1,
            text=loser_text,
            reply_markup=kb
        )
    except BadRequest:
        pass
    except Exception:
        pass

    # Очистить данные боя
    del active_pvp_fights[fight_id]
    if fight.player1_id in player_to_fight:
        del player_to_fight[fight.player1_id]
    if fight.player2_id in player_to_fight:
        del player_to_fight[fight.player2_id]


async def show_pvp_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать рейтинг игроков"""
    query = update.callback_query
    await query.answer()

    # Собрать всех игроков с PvP статистикой
    pvp_players = []
    for user_id, player in players.items():
        if player.pvp_wins + player.pvp_losses > 0:
            pvp_players.append({
                "name": player.name,
                "rating": player.pvp_rating,
                "wins": player.pvp_wins,
                "losses": player.pvp_losses,
                "class": player.player_class
            })

    # Сортировать по рейтингу
    pvp_players.sort(key=lambda x: x["rating"], reverse=True)

    text = "🏆 РЕЙТИНГ PVP\n\n"

    if not pvp_players:
        text += "Пока никто не играл в PvP!"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(pvp_players[:10]):
            medal = medals[i] if i < 3 else f"{i+1}."
            class_emoji = CLASSES.get(p["class"], {}).get("emoji", "❓")
            winrate = int(p["wins"] / (p["wins"] + p["losses"]) * 100) if (p["wins"] + p["losses"]) > 0 else 0
            text += f"{medal} {class_emoji} {p['name']}\n"
            text += f"   🏅 {p['rating']} | {p['wins']}W/{p['losses']}L ({winrate}%)\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="arena")]]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
