"""
Прочие обработчики: достижения, ежедневка, отдых, титулы
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import ACHIEVEMENTS, DAILY_REWARDS, ITEMS
from utils.storage import get_player, save_data
from utils.helpers import safe_edit_message


async def show_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать достижения"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "🏆 ДОСТИЖЕНИЯ\n\n"

    unlocked = 0
    total = len(ACHIEVEMENTS)

    for ach_id, ach in ACHIEVEMENTS.items():
        has_ach = ach_id in player.achievements
        status = "✅" if has_ach else "❌"
        if has_ach:
            unlocked += 1

        text += f"{status} {ach['emoji']} {ach['name']}\n"
        text += f"  {ach['desc']}\n\n"

    text = text[:18] + f"\n🏅 Получено: {unlocked}/{total}\n\n" + text[18:]

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="menu")]]

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать ежедневную награду"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    # Проверить, можно ли получить
    today = datetime.now().strftime("%Y-%m-%d")
    can_claim = player.last_daily != today

    # Текущий день в цикле
    current_day = (player.daily_streak % 7) + 1
    reward = DAILY_REWARDS[current_day - 1]

    text = f"🎁 ЕЖЕДНЕВНАЯ НАГРАДА\n\n"
    text += f"🔥 Серия: {player.daily_streak} дней\n"
    text += f"📅 День цикла: {current_day}/7\n\n"

    text += "Награды за 7 дней:\n"
    for i, r in enumerate(DAILY_REWARDS, 1):
        marker = "👉" if i == current_day else "  "
        items_text = ", ".join([
            f"{ITEMS.get(item_id, {}).get('emoji', '')} x{amount}"
            for item_id, amount in r.get("items", [])
        ])

        if r["gold"] > 0 and items_text:
            text += f"{marker} День {i}: 💰{r['gold']} + {items_text}\n"
        elif r["gold"] > 0:
            text += f"{marker} День {i}: 💰{r['gold']}\n"
        else:
            text += f"{marker} День {i}: {items_text}\n"

    keyboard = []

    if can_claim:
        keyboard.append([InlineKeyboardButton("🎁 Получить награду", callback_data="claim_daily")])
    else:
        text += "\n✅ Награда уже получена сегодня!"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu")])

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def claim_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить ежедневную награду"""
    query = update.callback_query

    player = get_player(query.from_user.id)

    today = datetime.now().strftime("%Y-%m-%d")

    if player.last_daily == today:
        await query.answer("Награда уже получена!", show_alert=True)
        return

    # Проверить серию
    yesterday = (datetime.now().timestamp() - 86400)
    yesterday_str = datetime.fromtimestamp(yesterday).strftime("%Y-%m-%d")

    if player.last_daily != yesterday_str:
        player.daily_streak = 0

    # Увеличить серию
    player.daily_streak += 1

    # Получить награду
    current_day = ((player.daily_streak - 1) % 7)
    reward = DAILY_REWARDS[current_day]

    reward_text = []

    if reward["gold"] > 0:
        player.gold += reward["gold"]
        player.stats["gold_earned"] = player.stats.get("gold_earned", 0) + reward["gold"]
        reward_text.append(f"💰 {reward['gold']} золота")

    for item_id, amount in reward.get("items", []):
        player.inventory[item_id] = player.inventory.get(item_id, 0) + amount
        item_name = ITEMS.get(item_id, {}).get("name", item_id)
        reward_text.append(f"📦 {item_name} x{amount}")

    player.last_daily = today
    player.stats["dailies_claimed"] = player.stats.get("dailies_claimed", 0) + 1

    save_data()

    await query.answer(f"День {current_day + 1}! {', '.join(reward_text)}")

    await show_daily(update, context)


async def rest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отдых - восстановить HP и ману"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    # Восстановить 20% HP и маны
    hp_restore = int(player.get_max_hp() * 0.2)
    mana_restore = int(player.get_max_mana() * 0.3)

    old_hp = player.hp
    old_mana = player.mana

    player.hp = min(player.hp + hp_restore, player.get_max_hp())
    player.mana = min(player.mana + mana_restore, player.get_max_mana())

    hp_gained = player.hp - old_hp
    mana_gained = player.mana - old_mana

    save_data()

    text = f"""💤 ОТДЫХ

Ты немного отдохнул...

❤️ HP: +{hp_gained} ({player.hp}/{player.get_max_hp()})
💙 Мана: +{mana_gained} ({player.mana}/{player.get_max_mana()})

Посети таверну для полного восстановления!"""

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="menu")]]

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_titles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать титулы"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "🏷️ ТИТУЛЫ\n\n"

    if player.title:
        text += f"Текущий: 『{player.title}』\n\n"

    if not player.titles:
        text += "У тебя пока нет титулов.\n"
        text += "Выполняй сюжетные квесты, чтобы получить титулы!"
    else:
        text += "Доступные титулы:\n"
        for title in player.titles:
            marker = "✅" if title == player.title else "⬜"
            text += f"{marker} {title}\n"

    keyboard = []

    for title in player.titles:
        if title != player.title:
            keyboard.append([InlineKeyboardButton(
                f"Выбрать: {title}",
                callback_data=f"select_title_{title}"
            )])

    if player.title:
        keyboard.append([InlineKeyboardButton(
            "❌ Снять титул",
            callback_data="select_title_none"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="profile")])

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def select_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбрать титул"""
    query = update.callback_query

    title = query.data.replace("select_title_", "")
    player = get_player(query.from_user.id)

    if title == "none":
        player.title = None
        await query.answer("Титул снят")
    elif title in player.titles:
        player.title = title
        await query.answer(f"Титул: {title}")
    else:
        await query.answer("Титул недоступен!", show_alert=True)
        return

    save_data()

    await show_titles(update, context)
