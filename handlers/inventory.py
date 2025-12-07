"""
Обработчики инвентаря, снаряжения и магазина
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import ITEMS, LEGENDARY_SETS, CLASSES
from utils.storage import get_player, save_data


async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать инвентарь"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "🎒 **ИНВЕНТАРЬ**\n\n"

    # Группировать по типам
    resources = []
    consumables = []
    equipment = []

    for item_id, count in player.inventory.items():
        if count <= 0:
            continue

        item = ITEMS.get(item_id, {})
        item_type = item.get("type", "unknown")
        emoji = item.get("emoji", "📦")
        name = item.get("name", item_id)

        if item_type == "resource":
            resources.append(f"{emoji} {name}: {count}")
        elif item_type == "consumable":
            consumables.append(f"{emoji} {name}: {count}")
        elif item_type in ["weapon", "armor", "accessory"]:
            equipment.append(f"{emoji} {name}: {count}")

    if resources:
        text += "**🌿 Ресурсы:**\n" + "\n".join(resources) + "\n\n"
    if consumables:
        text += "**🧪 Расходники:**\n" + "\n".join(consumables) + "\n\n"
    if equipment:
        text += "**⚔️ Снаряжение:**\n" + "\n".join(equipment) + "\n\n"

    if not resources and not consumables and not equipment:
        text += "_Инвентарь пуст_"

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Снаряжение", callback_data="equipment"),
            InlineKeyboardButton("💰 Продать", callback_data="sell_menu")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def show_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать снаряжение"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    # Текущее снаряжение
    weapon = player.equipment.get("weapon")
    armor = player.equipment.get("armor")
    accessory = player.equipment.get("accessory")

    weapon_text = "Пусто"
    if weapon:
        item = ITEMS.get(weapon, {})
        weapon_text = f"{item.get('emoji', '')} {item.get('name', weapon)}"

    armor_text = "Пусто"
    if armor:
        item = ITEMS.get(armor, {})
        armor_text = f"{item.get('emoji', '')} {item.get('name', armor)}"

    accessory_text = "Пусто"
    if accessory:
        item = ITEMS.get(accessory, {})
        accessory_text = f"{item.get('emoji', '')} {item.get('name', accessory)}"

    # Легендарное снаряжение
    legendary_text = ""
    pieces = player.count_legendary_pieces()
    if pieces > 0:
        legendary_text = f"\n\n✨ **Легендарный сет:** {pieces}/4 частей"
        for slot, item_id in player.legendary_equipment.items():
            if item_id:
                legendary_text += f"\n  {slot}: {item_id}"

    # Статы
    total_damage = player.get_total_damage()
    total_defense = player.get_total_defense()
    total_crit = player.get_crit_chance()

    text = f"""⚔️ **СНАРЯЖЕНИЕ**

🗡️ Оружие: {weapon_text}
🛡️ Броня: {armor_text}
💍 Аксессуар: {accessory_text}{legendary_text}

📊 **Итоговые статы:**
⚔️ Урон: {total_damage}
🛡️ Защита: {total_defense}
🎯 Крит: {total_crit}%"""

    keyboard = [
        [
            InlineKeyboardButton("🗡️ Оружие", callback_data="equip_weapon"),
            InlineKeyboardButton("🛡️ Броня", callback_data="equip_armor")
        ],
        [
            InlineKeyboardButton("💍 Аксессуар", callback_data="equip_accessory"),
            InlineKeyboardButton("✨ Легендарки", callback_data="equip_legendary")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="inventory")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def equip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экипировать предмет"""
    query = update.callback_query

    data = query.data
    player = get_player(query.from_user.id)

    # Определить тип слота
    if data.startswith("equip_weapon_"):
        slot = "weapon"
        item_type = "weapon"
        item_id = data.replace("equip_weapon_", "")
    elif data.startswith("equip_armor_"):
        slot = "armor"
        item_type = "armor"
        item_id = data.replace("equip_armor_", "")
    elif data.startswith("equip_accessory_"):
        slot = "accessory"
        item_type = "accessory"
        item_id = data.replace("equip_accessory_", "")
    elif data == "equip_weapon":
        await query.answer()
        slot = "weapon"
        item_type = "weapon"
        item_id = None
    elif data == "equip_armor":
        await query.answer()
        slot = "armor"
        item_type = "armor"
        item_id = None
    elif data == "equip_accessory":
        await query.answer()
        slot = "accessory"
        item_type = "accessory"
        item_id = None
    elif data.startswith("equip_legendary"):
        await query.answer()
        await show_legendary_menu(query, player)
        return
    else:
        await query.answer()
        return

    # Если это команда экипировки конкретного предмета
    if item_id and item_id in ITEMS:
        # Снять текущее
        current = player.equipment.get(slot)
        if current:
            player.inventory[current] = player.inventory.get(current, 0) + 1

        # Надеть новое
        player.equipment[slot] = item_id
        player.inventory[item_id] = player.inventory.get(item_id, 1) - 1

        save_data()
        await query.answer(f"Экипировано: {ITEMS[item_id]['name']}")
        await show_equipment(update, context)
        return

    # Показать список предметов для экипировки
    text = f"**Выбери {item_type}:**\n\n"

    keyboard = []

    for item_id, count in player.inventory.items():
        if count <= 0:
            continue

        item = ITEMS.get(item_id, {})
        if item.get("type") != item_type:
            continue

        name = item.get("name", item_id)
        emoji = item.get("emoji", "📦")

        stats = []
        if "damage" in item:
            stats.append(f"⚔️{item['damage']}")
        if "defense" in item:
            stats.append(f"🛡️{item['defense']}")
        if "crit_bonus" in item:
            stats.append(f"🎯{item['crit_bonus']}%")

        stats_text = " ".join(stats) if stats else ""

        text += f"{emoji} {name} ({count}) {stats_text}\n"

        keyboard.append([InlineKeyboardButton(
            f"{emoji} {name}",
            callback_data=f"equip_{item_type}_{item_id}"
        )])

    if not keyboard:
        text += "_Нет доступных предметов_"

    # Кнопка снять
    if player.equipment.get(slot):
        keyboard.append([InlineKeyboardButton(
            "❌ Снять",
            callback_data=f"unequip_{slot}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="equipment")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def show_legendary_menu(query, player):
    """Показать меню легендарного снаряжения"""
    class_data = CLASSES.get(player.player_class, {})

    if player.player_class not in LEGENDARY_SETS:
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="equipment")]]
        await query.edit_message_text(
            "У твоего класса нет легендарного сета.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    set_data = LEGENDARY_SETS[player.player_class]

    text = f"✨ **{set_data['name']}**\n\n"

    pieces = player.count_legendary_pieces()
    text += f"Собрано: {pieces}/4\n\n"

    if pieces >= 2:
        text += f"✅ 2 части: {set_data['bonus_2']}\n"
    else:
        text += f"❌ 2 части: {set_data['bonus_2']}\n"

    if pieces >= 4:
        text += f"✅ 4 части: {set_data['bonus_4']}\n"
    else:
        text += f"❌ 4 части: {set_data['bonus_4']}\n"

    text += "\n**Части сета:**\n"

    keyboard = []

    for slot, piece in set_data["pieces"].items():
        equipped = player.legendary_equipment.get(slot)
        has_piece = player.inventory.get(f"legendary_{player.player_class}_{slot}", 0) > 0

        status = "✅" if equipped else ("📦" if has_piece else "❌")
        text += f"{status} {piece['emoji']} {piece['name']}\n"

        if has_piece and not equipped:
            keyboard.append([InlineKeyboardButton(
                f"Надеть {piece['name']}",
                callback_data=f"equip_leg_{slot}"
            )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="equipment")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def unequip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Снять предмет"""
    query = update.callback_query
    await query.answer()

    slot = query.data.replace("unequip_", "")
    player = get_player(query.from_user.id)

    current = player.equipment.get(slot)
    if current:
        player.inventory[current] = player.inventory.get(current, 0) + 1
        player.equipment[slot] = None
        save_data()
        await query.answer("Предмет снят")

    await show_equipment(update, context)


async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать магазин"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"🛒 **МАГАЗИН**\n\n💰 Золото: {player.gold}\n\n"

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Оружие", callback_data="shop_weapons"),
            InlineKeyboardButton("🛡️ Броня", callback_data="shop_armor")
        ],
        [
            InlineKeyboardButton("💍 Аксессуары", callback_data="shop_accessories"),
            InlineKeyboardButton("🧪 Зелья", callback_data="shop_potions")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Купить предмет"""
    query = update.callback_query

    # Проверить, это категория или покупка
    data = query.data

    player = get_player(query.from_user.id)

    # Категории магазина
    if data in ["shop_weapons", "shop_armor", "shop_accessories", "shop_potions"]:
        await query.answer()

        category_map = {
            "shop_weapons": "weapon",
            "shop_armor": "armor",
            "shop_accessories": "accessory",
            "shop_potions": "consumable"
        }
        category = category_map[data]

        text = f"🛒 **МАГАЗИН**\n\n💰 Золото: {player.gold}\n\n"

        keyboard = []

        for item_id, item in ITEMS.items():
            if item.get("type") != category:
                continue
            if "price" not in item:
                continue

            emoji = item.get("emoji", "📦")
            name = item.get("name", item_id)
            price = item["price"]

            stats = []
            if "damage" in item:
                stats.append(f"⚔️{item['damage']}")
            if "defense" in item:
                stats.append(f"🛡️{item['defense']}")
            if "heal" in item:
                stats.append(f"❤️{item['heal']}")
            if "mana" in item:
                stats.append(f"💙{item['mana']}")

            stats_text = " ".join(stats) if stats else ""

            text += f"{emoji} {name} - {price}💰 {stats_text}\n"

            keyboard.append([InlineKeyboardButton(
                f"{emoji} {name} ({price}💰)",
                callback_data=f"buy_{item_id}"
            )])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop")])

        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
        return

    # Покупка конкретного предмета
    if data.startswith("buy_"):
        item_id = data.replace("buy_", "")

        if item_id not in ITEMS:
            await query.answer("Предмет не найден!", show_alert=True)
            return

        item = ITEMS[item_id]
        price = item.get("price", 0)

        if player.gold < price:
            await query.answer("Недостаточно золота!", show_alert=True)
            return

        player.gold -= price
        player.stats["gold_spent"] = player.stats.get("gold_spent", 0) + price
        player.inventory[item_id] = player.inventory.get(item_id, 0) + 1

        save_data()
        await query.answer(f"Куплено: {item['name']}")


async def sell_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продать предмет"""
    query = update.callback_query

    data = query.data
    player = get_player(query.from_user.id)

    # Меню продажи
    if data == "sell_menu":
        await query.answer()

        text = f"💰 **ПРОДАЖА**\n\n💰 Золото: {player.gold}\n\n"

        keyboard = []

        for item_id, count in player.inventory.items():
            if count <= 0:
                continue

            item = ITEMS.get(item_id, {})
            if "price" not in item:
                continue

            emoji = item.get("emoji", "📦")
            name = item.get("name", item_id)
            sell_price = item["price"] // 2

            text += f"{emoji} {name} ({count}) - {sell_price}💰\n"

            keyboard.append([InlineKeyboardButton(
                f"Продать {name} ({sell_price}💰)",
                callback_data=f"sell_{item_id}"
            )])

        if not keyboard:
            text += "_Нечего продавать_"

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="inventory")])

        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
        return

    # Продажа конкретного предмета
    if data.startswith("sell_"):
        item_id = data.replace("sell_", "")

        if player.inventory.get(item_id, 0) <= 0:
            await query.answer("Нет такого предмета!", show_alert=True)
            return

        item = ITEMS.get(item_id, {})
        sell_price = item.get("price", 0) // 2

        player.inventory[item_id] -= 1
        player.gold += sell_price
        player.stats["gold_earned"] = player.stats.get("gold_earned", 0) + sell_price

        save_data()
        await query.answer(f"Продано за {sell_price} золота")

        # Обновить меню продажи
        await sell_item(update, context)
