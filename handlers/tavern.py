"""
Обработчики таверны: еда, наёмники, кузнец, алхимик, квесты
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import (
    TAVERN_FOOD, MERCENARIES, BLACKSMITH_UPGRADES,
    ALCHEMY_RECIPES, QUESTS, ITEMS
)
from utils.storage import get_player, save_data


async def show_tavern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать таверну"""
    query = update.callback_query
    await query.answer()

    text = """🍺 **ТАВЕРНА**

Добро пожаловать в таверну "Пьяный Гоблин"!

Здесь ты можешь:
🍖 Поесть - восстановить HP и получить бафы
🤝 Нанять наёмника - помощь в бою
⚒️ Кузнец - улучшить снаряжение
🧪 Алхимик - создать зелья"""

    keyboard = [
        [
            InlineKeyboardButton("🍖 Еда", callback_data="tavern_food"),
            InlineKeyboardButton("🤝 Наёмники", callback_data="tavern_mercs")
        ],
        [
            InlineKeyboardButton("⚒️ Кузнец", callback_data="tavern_smith"),
            InlineKeyboardButton("🧪 Алхимик", callback_data="tavern_alchemy")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def show_food_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню еды"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"🍖 **МЕНЮ ТАВЕРНЫ**\n\n💰 Золото: {player.gold}\n\n"

    keyboard = []

    for food_id, food in TAVERN_FOOD.items():
        text += f"{food['emoji']} **{food['name']}** - {food['price']} 💰\n"
        text += f"  _{food['desc']}_\n\n"

        keyboard.append([InlineKeyboardButton(
            f"{food['emoji']} {food['name']} ({food['price']}💰)",
            callback_data=f"buy_food_{food_id}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def buy_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Купить еду"""
    query = update.callback_query

    food_id = query.data.replace("buy_food_", "")
    player = get_player(query.from_user.id)

    if food_id not in TAVERN_FOOD:
        await query.answer("Еда не найдена!", show_alert=True)
        return

    food = TAVERN_FOOD[food_id]

    if player.gold < food["price"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    player.gold -= food["price"]
    player.stats["gold_spent"] = player.stats.get("gold_spent", 0) + food["price"]

    result_text = f"{food['emoji']} {food['name']}\n"

    # Лечение
    if "heal" in food:
        heal = food["heal"]
        player.hp = min(player.hp + heal, player.get_max_hp())
        result_text += f"❤️ +{heal} HP\n"

    if food.get("heal_full"):
        player.hp = player.get_max_hp()
        result_text += "❤️ HP полностью восстановлено!\n"

    if food.get("mana_full"):
        player.mana = player.get_max_mana()
        result_text += "💙 Мана полностью восстановлена!\n"

    # Бафы
    if "buff" in food:
        buff = food["buff"]
        duration = buff.get("duration", 300)
        expires = datetime.now().timestamp() + duration

        for buff_type, value in buff.items():
            if buff_type != "duration":
                player.food_buffs[buff_type] = {"value": value, "expires": expires}
                if buff_type == "hp":
                    result_text += f"💚 +{value} макс HP на {duration//60} мин\n"
                elif buff_type == "damage":
                    result_text += f"⚔️ +{value} урона на {duration//60} мин\n"
                elif buff_type == "defense":
                    result_text += f"🛡️ {'+' if value >= 0 else ''}{value} защиты на {duration//60} мин\n"
                elif buff_type == "crit":
                    result_text += f"🎯 +{value}% крита на {duration//60} мин\n"
                elif buff_type == "mana_regen":
                    result_text += f"💙 +{value} реген маны на {duration//60} мин\n"

    save_data()
    await query.answer(f"Куплено: {food['name']}")

    # Обновить меню
    await show_food_menu(update, context)


async def show_mercenaries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать наёмников"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"🤝 **НАЁМНИКИ**\n\n💰 Золото: {player.gold}\n\n"

    # Текущий наёмник
    if player.mercenary:
        merc = MERCENARIES.get(player.mercenary["id"], {})
        text += f"👤 Текущий: {merc.get('emoji', '')} {merc.get('name', 'Неизвестно')}\n"
        text += f"   Осталось боёв: {player.mercenary.get('fights', 0)}\n\n"

    keyboard = []

    for merc_id, merc in MERCENARIES.items():
        text += f"{merc['emoji']} **{merc['name']}** - {merc['price']} 💰\n"
        text += f"  {merc['desc']}\n\n"

        keyboard.append([InlineKeyboardButton(
            f"{merc['emoji']} {merc['name']} ({merc['price']}💰)",
            callback_data=f"hire_merc_{merc_id}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def hire_mercenary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Нанять наёмника"""
    query = update.callback_query

    merc_id = query.data.replace("hire_merc_", "")
    player = get_player(query.from_user.id)

    if merc_id not in MERCENARIES:
        await query.answer("Наёмник не найден!", show_alert=True)
        return

    merc = MERCENARIES[merc_id]

    if player.gold < merc["price"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    player.gold -= merc["price"]
    player.stats["gold_spent"] = player.stats.get("gold_spent", 0) + merc["price"]

    player.mercenary = {
        "id": merc_id,
        "fights": merc["duration"]
    }

    save_data()
    await query.answer(f"Нанят: {merc['name']} на {merc['duration']} боёв!")

    await show_mercenaries(update, context)


async def show_blacksmith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать кузнеца"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"⚒️ КУЗНЕЦ\n\n💰 Золото: {player.gold}\n\n"

    keyboard = []

    for upgrade_id, upgrade in BLACKSMITH_UPGRADES.items():
        current_level = player.blacksmith_upgrades.get(upgrade_id, 0)
        resource_type, resource_amount = upgrade["resource"]
        player_resource = player.inventory.get(resource_type, 0)
        resource_name = resource_type.replace('_', ' ')

        text += f"{upgrade['emoji']} {upgrade['name']} [{current_level}/{upgrade['max_level']}]\n"
        text += f"  {upgrade['desc']}\n"
        text += f"  💰 {upgrade['cost']} + {resource_amount} {resource_name} ({player_resource})\n\n"

        if current_level < upgrade["max_level"]:
            keyboard.append([InlineKeyboardButton(
                f"{upgrade['emoji']} {upgrade['name']}",
                callback_data=f"smith_{upgrade_id}"
            )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def blacksmith_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Улучшить у кузнеца"""
    query = update.callback_query

    upgrade_id = query.data.replace("smith_", "")
    player = get_player(query.from_user.id)

    if upgrade_id not in BLACKSMITH_UPGRADES:
        await query.answer("Улучшение не найдено!", show_alert=True)
        return

    upgrade = BLACKSMITH_UPGRADES[upgrade_id]
    current_level = player.blacksmith_upgrades.get(upgrade_id, 0)

    if current_level >= upgrade["max_level"]:
        await query.answer("Максимальный уровень!", show_alert=True)
        return

    if player.gold < upgrade["cost"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    resource_type, resource_amount = upgrade["resource"]
    if player.inventory.get(resource_type, 0) < resource_amount:
        await query.answer(f"Недостаточно {resource_type}!", show_alert=True)
        return

    # Списать ресурсы
    player.gold -= upgrade["cost"]
    player.inventory[resource_type] -= resource_amount
    player.stats["gold_spent"] = player.stats.get("gold_spent", 0) + upgrade["cost"]

    # Применить улучшение
    player.blacksmith_upgrades[upgrade_id] = current_level + 1

    save_data()
    await query.answer(f"Улучшено: {upgrade['name']}!")

    await show_blacksmith(update, context)


async def show_alchemist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать алхимика"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"🧪 АЛХИМИК\n\n💰 Золото: {player.gold}\n\n"

    keyboard = []

    for recipe_id, recipe in ALCHEMY_RECIPES.items():
        ingredients_text = ", ".join([
            f"{amount} {ing.replace('_', ' ')} ({player.inventory.get(ing, 0)})"
            for ing, amount in recipe["ingredients"].items()
        ])

        text += f"{recipe['emoji']} {recipe['name']}\n"
        text += f"  {recipe['desc']}\n"
        text += f"  💰 {recipe['cost']} | {ingredients_text}\n\n"

        keyboard.append([InlineKeyboardButton(
            f"{recipe['emoji']} {recipe['name']}",
            callback_data=f"craft_{recipe_id}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def craft_potion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать зелье"""
    query = update.callback_query

    recipe_id = query.data.replace("craft_", "")
    player = get_player(query.from_user.id)

    if recipe_id not in ALCHEMY_RECIPES:
        await query.answer("Рецепт не найден!", show_alert=True)
        return

    recipe = ALCHEMY_RECIPES[recipe_id]

    if player.gold < recipe["cost"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    # Проверить ингредиенты
    for ingredient, amount in recipe["ingredients"].items():
        if player.inventory.get(ingredient, 0) < amount:
            await query.answer(f"Недостаточно {ingredient}!", show_alert=True)
            return

    # Списать ресурсы
    player.gold -= recipe["cost"]
    player.stats["gold_spent"] = player.stats.get("gold_spent", 0) + recipe["cost"]

    for ingredient, amount in recipe["ingredients"].items():
        player.inventory[ingredient] -= amount

    # Выдать результат
    result_item, result_amount = recipe["result"]
    player.inventory[result_item] = player.inventory.get(result_item, 0) + result_amount

    save_data()
    await query.answer(f"Создано: {recipe['name']} x{result_amount}!")

    await show_alchemist(update, context)


async def show_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать квесты"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "📜 **КВЕСТЫ**\n\n"

    keyboard = []

    # Ежедневные квесты
    text += "**📅 Ежедневные:**\n"
    for quest_id, quest in QUESTS.items():
        if quest["type"] != "daily":
            continue

        progress = player.quest_progress.get(quest_id, 0)
        target = quest["target"]
        completed = progress >= target

        status = "✅" if completed else f"{progress}/{target}"
        text += f"{quest['emoji']} {quest['name']} - {status}\n"
        text += f"  _{quest['desc']}_\n"

        if completed and quest_id not in player.completed_quests:
            keyboard.append([InlineKeyboardButton(
                f"🎁 {quest['name']}",
                callback_data=f"claim_quest_{quest_id}"
            )])

    # Еженедельные квесты
    text += "\n**📆 Еженедельные:**\n"
    for quest_id, quest in QUESTS.items():
        if quest["type"] != "weekly":
            continue

        progress = player.quest_progress.get(quest_id, 0)
        target = quest["target"]
        completed = progress >= target

        status = "✅" if completed else f"{progress}/{target}"
        text += f"{quest['emoji']} {quest['name']} - {status}\n"
        text += f"  _{quest['desc']}_\n"

        if completed and quest_id not in player.completed_quests:
            keyboard.append([InlineKeyboardButton(
                f"🎁 {quest['name']}",
                callback_data=f"claim_quest_{quest_id}"
            )])

    # Сюжетные квесты
    text += "\n**📖 Сюжетные:**\n"
    for quest_id, quest in QUESTS.items():
        if quest["type"] != "story":
            continue

        completed = quest_id in player.completed_quests
        status = "✅" if completed else "❌"
        text += f"{quest['emoji']} {quest['name']} - {status}\n"
        text += f"  _{quest['desc']}_\n"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def claim_quest_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить награду за квест"""
    query = update.callback_query

    quest_id = query.data.replace("claim_quest_", "")
    player = get_player(query.from_user.id)

    if quest_id not in QUESTS:
        await query.answer("Квест не найден!", show_alert=True)
        return

    quest = QUESTS[quest_id]

    # Проверить выполнение
    progress = player.quest_progress.get(quest_id, 0)
    if progress < quest["target"]:
        await query.answer("Квест не выполнен!", show_alert=True)
        return

    if quest_id in player.completed_quests:
        await query.answer("Награда уже получена!", show_alert=True)
        return

    # Выдать награды
    rewards = quest["rewards"]
    reward_text = []

    if "gold" in rewards:
        player.gold += rewards["gold"]
        player.stats["gold_earned"] = player.stats.get("gold_earned", 0) + rewards["gold"]
        reward_text.append(f"💰 {rewards['gold']} золота")

    if "exp" in rewards:
        player.exp += rewards["exp"]
        reward_text.append(f"⭐ {rewards['exp']} опыта")

    if "item" in rewards:
        item_id = rewards["item"]
        player.inventory[item_id] = player.inventory.get(item_id, 0) + 1
        item_name = ITEMS.get(item_id, {}).get("name", item_id)
        reward_text.append(f"📦 {item_name}")

    if "title" in rewards:
        if rewards["title"] not in player.titles:
            player.titles.append(rewards["title"])
        reward_text.append(f"🏷️ Титул: {rewards['title']}")

    player.completed_quests.append(quest_id)
    player.stats["quests_done"] = player.stats.get("quests_done", 0) + 1

    save_data()
    await query.answer(f"Награда: {', '.join(reward_text)}")

    await show_quests(update, context)
