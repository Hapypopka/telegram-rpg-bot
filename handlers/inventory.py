"""
Обработчики инвентаря, снаряжения и магазина
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import ITEMS, EPIC_SETS, RARITY_EMOJI, SLOT_NAMES
from utils.storage import get_player, save_data
from utils.helpers import safe_edit_message


def get_item_stats_text(item: dict) -> str:
    """Получить текст бонусов предмета"""
    stats = []
    if "damage" in item:
        stats.append(f"⚔️+{item['damage']}")
    if "damage_bonus" in item:
        stats.append(f"⚔️+{item['damage_bonus']}")
    if "defense" in item:
        stats.append(f"🛡️+{item['defense']}")
    if "defense_bonus" in item:
        stats.append(f"🛡️+{item['defense_bonus']}")
    if "hp_bonus" in item:
        stats.append(f"❤️+{item['hp_bonus']}")
    if "mana_bonus" in item:
        stats.append(f"💙+{item['mana_bonus']}")
    if "crit_bonus" in item:
        stats.append(f"🎯+{item['crit_bonus']}%")
    if "dodge_bonus" in item:
        stats.append(f"💨+{item['dodge_bonus']}%")
    if "lifesteal" in item:
        stats.append(f"🩸{int(item['lifesteal']*100)}%")
    if item.get("berserker"):
        stats.append("🔥берсерк")
    if "heal" in item:
        stats.append(f"❤️+{item['heal']}")
    if "mana" in item and item.get("type") == "consumable":
        stats.append(f"💙+{item['mana']}")
    return " ".join(stats)


def get_rarity_name(rarity: str) -> str:
    """Получить название редкости"""
    names = {
        "common": "Обычный",
        "rare": "Редкий",
        "epic": "Эпический",
        "legendary": "Легендарный"
    }
    return names.get(rarity, "")


def format_item_name(item: dict, item_id: str) -> str:
    """Форматировать имя предмета с редкостью"""
    rarity = item.get("rarity", "common")
    emoji = RARITY_EMOJI.get(rarity, "")
    name = item.get("name", item_id)
    return f"{emoji}{item.get('emoji', '')} {name}".strip()


async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать инвентарь"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "🎒 ИНВЕНТАРЬ\n\n"

    # Группировать по типам
    resources = []
    consumables = []
    equipment = []

    for item_id, count in player.inventory.items():
        if count <= 0:
            continue

        # Проверить в ITEMS, затем в процедурных предметах
        item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
        item_type = item.get("type", "unknown")
        emoji = item.get("emoji", "📦")
        name = item.get("name", item_id)
        rarity_emoji = RARITY_EMOJI.get(item.get("rarity", ""), "")

        if item_type == "resource":
            resources.append(f"{emoji} {name}: {count}")
        elif item_type == "consumable":
            consumables.append(f"{emoji} {name}: {count}")
        elif item_type in ["weapon", "armor", "accessory"]:
            equipment.append(f"{rarity_emoji}{emoji} {name}: {count}")

    if resources:
        text += "🌿 Ресурсы:\n" + "\n".join(resources) + "\n\n"
    if consumables:
        text += "🧪 Расходники:\n" + "\n".join(consumables) + "\n\n"
    if equipment:
        text += "⚔️ Снаряжение:\n" + "\n".join(equipment) + "\n\n"

    if not resources and not consumables and not equipment:
        text += "Инвентарь пуст"

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Снаряжение", callback_data="equipment"),
            InlineKeyboardButton("⚗️ Зелья", callback_data="potion_slots")
        ],
        [
            InlineKeyboardButton("💰 Продать", callback_data="sell_menu")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
    ]

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать снаряжение (10 слотов)"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = "⚔️ СНАРЯЖЕНИЕ\n\n"

    # Показать все слоты
    slot_emojis = {
        "weapon": "🗡️", "helmet": "⛑️", "shoulders": "🦺",
        "chest": "🎽", "belt": "🎗️", "gloves": "🧤",
        "leggings": "👖", "boots": "👢", "ring": "💍", "necklace": "📿"
    }

    for slot, slot_name in SLOT_NAMES.items():
        item_id = player.equipment.get(slot)
        emoji = slot_emojis.get(slot, "📦")

        if item_id:
            item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
            rarity = item.get("rarity", "common")
            rarity_emoji = RARITY_EMOJI.get(rarity, "")
            item_emoji = item.get("emoji", "")
            name = item.get("name", item_id)
            text += f"{emoji} {slot_name}: {rarity_emoji}{item_emoji} {name}\n"
        else:
            text += f"{emoji} {slot_name}: Пусто\n"

    # Статы
    total_damage = player.get_total_damage()
    total_defense = player.get_total_defense()
    total_crit = player.get_crit_chance()
    total_dodge = player.get_dodge_chance()
    total_hp = player.get_max_hp()
    total_mana = player.get_max_mana()

    text += f"""
📊 Итоговые статы:
❤️ HP: {total_hp} | 💙 Мана: {total_mana}
⚔️ Урон: {total_damage} | 🛡️ Защита: {total_defense}
🎯 Крит: {total_crit}% | 💨 Уклон: {total_dodge}%"""

    # Проверить сетовые бонусы
    set_text = ""
    for set_id, epic_set in EPIC_SETS.items():
        count = player.count_epic_pieces(set_id)
        if count > 0:
            set_text += f"\n\n🟣 {epic_set['name']} ({count}/8)"
            if count >= 2:
                set_text += f"\n  ✅ 2шт: {epic_set['bonus_2']}"
            if count >= 4:
                set_text += f"\n  ✅ 4шт: {epic_set['bonus_4']}"
            if count >= 6 and "bonus_6" in epic_set:
                set_text += f"\n  ✅ 6шт: {epic_set['bonus_6']}"
            if count >= 8 and "bonus_8" in epic_set:
                set_text += f"\n  👑 8шт: {epic_set['bonus_8']}"

    text += set_text

    # Кнопки по категориям
    keyboard = [
        [
            InlineKeyboardButton("🗡️ Оружие", callback_data="slot_weapon"),
            InlineKeyboardButton("⛑️ Голова", callback_data="slot_helmet")
        ],
        [
            InlineKeyboardButton("🦺 Плечи", callback_data="slot_shoulders"),
            InlineKeyboardButton("🎽 Грудь", callback_data="slot_chest")
        ],
        [
            InlineKeyboardButton("🎗️ Пояс", callback_data="slot_belt"),
            InlineKeyboardButton("🧤 Перчатки", callback_data="slot_gloves")
        ],
        [
            InlineKeyboardButton("👖 Поножи", callback_data="slot_leggings"),
            InlineKeyboardButton("👢 Сапоги", callback_data="slot_boots")
        ],
        [
            InlineKeyboardButton("💍 Кольцо", callback_data="slot_ring"),
            InlineKeyboardButton("📿 Ожерелье", callback_data="slot_necklace")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="inventory")]
    ]

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_slot_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать предметы для конкретного слота"""
    query = update.callback_query
    await query.answer()

    slot = query.data.replace("slot_", "")
    player = get_player(query.from_user.id)

    slot_name = SLOT_NAMES.get(slot, slot)
    text = f"📦 {slot_name}\n\n"

    # Текущий предмет
    current_item_id = player.equipment.get(slot)
    if current_item_id:
        current_item = ITEMS.get(current_item_id, {})
        rarity_emoji = RARITY_EMOJI.get(current_item.get("rarity", ""), "")
        item_name = current_item.get('name', current_item_id)
        item_emoji = current_item.get('emoji', '📦')
        text += f"Надето: {rarity_emoji}{item_emoji} {item_name}\n"
        stats = get_item_stats_text(current_item)
        if stats:
            text += f"  {stats}\n"
    else:
        text += "Надето: Ничего\n"

    text += "\nДоступно в инвентаре:\n"

    keyboard = []
    found = False

    for item_id, count in player.inventory.items():
        if count <= 0:
            continue

        item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
        item_slot = item.get("slot")

        # Проверить совместимость слота
        if item_slot != slot:
            continue

        found = True
        rarity = item.get("rarity", "common")
        rarity_emoji = RARITY_EMOJI.get(rarity, "")
        name = item.get("name", item_id)
        emoji = item.get("emoji", "📦")
        stats = get_item_stats_text(item)
        rarity_name = get_rarity_name(rarity)

        text += f"\n{rarity_emoji}{emoji} {name} ({count})"
        if stats:
            text += f"\n  {stats}"

        keyboard.append([InlineKeyboardButton(
            f"{rarity_emoji}{emoji} {name}",
            callback_data=f"equip_{slot}_{item_id}"
        )])

    if not found:
        text += "Нет подходящих предметов"

    # Кнопка снять
    if current_item_id:
        keyboard.append([InlineKeyboardButton(
            "❌ Снять",
            callback_data=f"unequip_{slot}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="equipment")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def equip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экипировать предмет"""
    query = update.callback_query

    data = query.data

    # Формат: equip_SLOT_ITEMID
    parts = data.split("_", 2)
    if len(parts) < 3:
        await query.answer()
        return

    slot = parts[1]
    item_id = parts[2]

    player = get_player(query.from_user.id)

    # Проверить наличие предмета
    if player.inventory.get(item_id, 0) <= 0:
        await query.answer("Нет такого предмета!", show_alert=True)
        return

    # Проверить совместимость слота
    item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
    if item.get("slot") != slot:
        await query.answer("Предмет не подходит для этого слота!", show_alert=True)
        return

    # Снять текущее
    current = player.equipment.get(slot)
    if current:
        player.inventory[current] = player.inventory.get(current, 0) + 1

    # Надеть новое
    player.equipment[slot] = item_id
    player.inventory[item_id] = player.inventory.get(item_id, 1) - 1

    save_data()
    await query.answer(f"Экипировано: {item.get('name', item_id)}")

    # Вернуться к списку слота
    context.user_data["slot"] = slot
    await show_slot_items_direct(query, player, slot)


async def unequip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Снять предмет"""
    query = update.callback_query

    slot = query.data.replace("unequip_", "")
    player = get_player(query.from_user.id)

    current = player.equipment.get(slot)
    if current:
        player.inventory[current] = player.inventory.get(current, 0) + 1
        player.equipment[slot] = None
        save_data()
        await query.answer("Предмет снят")
    else:
        await query.answer()

    # Вернуться к списку слота
    context.user_data["slot"] = slot
    await show_slot_items_direct(query, player, slot)


async def show_slot_items_direct(query, player, slot):
    """Показать предметы для слота (прямой вызов)"""
    slot_name = SLOT_NAMES.get(slot, slot)
    text = f"📦 {slot_name}\n\n"

    # Текущий предмет
    current_item_id = player.equipment.get(slot)
    if current_item_id:
        current_item = ITEMS.get(current_item_id, {})
        rarity_emoji = RARITY_EMOJI.get(current_item.get("rarity", ""), "")
        item_name = current_item.get('name', current_item_id)
        item_emoji = current_item.get('emoji', '📦')
        text += f"Надето: {rarity_emoji}{item_emoji} {item_name}\n"
        stats = get_item_stats_text(current_item)
        if stats:
            text += f"  {stats}\n"
    else:
        text += "Надето: Ничего\n"

    text += "\nДоступно в инвентаре:\n"

    keyboard = []
    found = False

    for item_id, count in player.inventory.items():
        if count <= 0:
            continue

        item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
        item_slot = item.get("slot")

        if item_slot != slot:
            continue

        found = True
        rarity = item.get("rarity", "common")
        rarity_emoji = RARITY_EMOJI.get(rarity, "")
        name = item.get("name", item_id)
        emoji = item.get("emoji", "📦")
        stats = get_item_stats_text(item)

        text += f"\n{rarity_emoji}{emoji} {name} ({count})"
        if stats:
            text += f"\n  {stats}"

        keyboard.append([InlineKeyboardButton(
            f"{rarity_emoji}{emoji} {name}",
            callback_data=f"equip_{slot}_{item_id}"
        )])

    if not found:
        text += "Нет подходящих предметов"

    if current_item_id:
        keyboard.append([InlineKeyboardButton(
            "❌ Снять",
            callback_data=f"unequip_{slot}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="equipment")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать магазин (только обычные предметы)"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"""🛒 МАГАЗИН

💰 Золото: {player.gold}

В магазине продаются только обычные предметы.
Редкие можно скрафтить в кузнице."""

    keyboard = [
        [
            InlineKeyboardButton("🗡️ Оружие", callback_data="shop_weapon"),
            InlineKeyboardButton("⛑️ Шлемы", callback_data="shop_helmet")
        ],
        [
            InlineKeyboardButton("🦺 Плечи", callback_data="shop_shoulders"),
            InlineKeyboardButton("🎽 Грудь", callback_data="shop_chest")
        ],
        [
            InlineKeyboardButton("🎗️ Пояса", callback_data="shop_belt"),
            InlineKeyboardButton("🧤 Перчатки", callback_data="shop_gloves")
        ],
        [
            InlineKeyboardButton("👖 Поножи", callback_data="shop_leggings"),
            InlineKeyboardButton("👢 Сапоги", callback_data="shop_boots")
        ],
        [
            InlineKeyboardButton("💍 Кольца", callback_data="shop_ring"),
            InlineKeyboardButton("📿 Ожерелья", callback_data="shop_necklace")
        ],
        [InlineKeyboardButton("🧪 Зелья", callback_data="shop_consumable")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
    ]

    await safe_edit_message(query, context, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать категорию магазина"""
    query = update.callback_query
    await query.answer()

    category = query.data.replace("shop_", "")
    player = get_player(query.from_user.id)

    # Для зелий ищем по type, для остальных по slot
    is_consumable = category == "consumable"

    slot_name = "Зелья" if is_consumable else SLOT_NAMES.get(category, category)
    text = f"🛒 {slot_name}\n\n💰 Золото: {player.gold}\n\n"

    keyboard = []

    for item_id, item in ITEMS.items():
        # Только обычные предметы (common) в магазине
        if item.get("rarity", "common") != "common":
            continue

        # Фильтр по категории
        if is_consumable:
            if item.get("type") != "consumable":
                continue
        else:
            if item.get("slot") != category:
                continue

        # Должна быть цена
        if "price" not in item or item["price"] <= 0:
            continue

        emoji = item.get("emoji", "📦")
        name = item.get("name", item_id)
        price = item["price"]
        stats = get_item_stats_text(item)

        text += f"{emoji} {name} - {price}💰\n"
        if stats:
            text += f"  {stats}\n"

        keyboard.append([InlineKeyboardButton(
            f"{emoji} {name} ({price}💰)",
            callback_data=f"buy_{item_id}"
        )])

    if not keyboard:
        text += "Нет товаров"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Купить предмет"""
    query = update.callback_query

    item_id = query.data.replace("buy_", "")
    player = get_player(query.from_user.id)

    if item_id not in ITEMS:
        await query.answer("Предмет не найден!", show_alert=True)
        return

    item = ITEMS[item_id]

    # Только обычные можно купить в магазине
    if item.get("rarity", "common") != "common" and item.get("type") != "consumable":
        await query.answer("Этот предмет нельзя купить в магазине!", show_alert=True)
        return

    price = item.get("price", 0)

    if player.gold < price:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    player.gold -= price
    player.stats["gold_spent"] = player.stats.get("gold_spent", 0) + price
    player.inventory[item_id] = player.inventory.get(item_id, 0) + 1

    save_data()
    await query.answer(f"Куплено: {item['name']}")


async def show_sell_menu(query, player):
    """Показать меню продажи (прямой вызов)"""
    text = f"💰 ПРОДАЖА\n\n💰 Золото: {player.gold}\n\n"

    keyboard = []

    for item_id, count in player.inventory.items():
        if count <= 0:
            continue

        item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
        price = item.get("price", 0)
        if price <= 0:
            continue

        rarity = item.get("rarity", "common")
        rarity_emoji = RARITY_EMOJI.get(rarity, "")
        emoji = item.get("emoji", "📦")
        name = item.get("name", item_id)

        sell_mult = {"common": 0.5, "rare": 0.6, "epic": 0.7, "legendary": 0.8}
        sell_price = int(price * sell_mult.get(rarity, 0.5))

        text += f"{rarity_emoji}{emoji} {name} ({count}) - {sell_price}💰\n"

        keyboard.append([InlineKeyboardButton(
            f"Продать {name} ({sell_price}💰)",
            callback_data=f"sell_{item_id}"
        )])

    if not keyboard:
        text += "Нечего продавать"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="inventory")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def sell_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продать предмет"""
    query = update.callback_query

    data = query.data
    player = get_player(query.from_user.id)

    # Меню продажи
    if data == "sell_menu":
        await query.answer()
        await show_sell_menu(query, player)
        return

    # Продажа конкретного предмета
    if data.startswith("sell_"):
        item_id = data.replace("sell_", "")

        if player.inventory.get(item_id, 0) <= 0:
            await query.answer("Нет такого предмета!", show_alert=True)
            return

        item = ITEMS.get(item_id) or player.procedural_items.get(item_id, {})
        price = item.get("price", 0)
        rarity = item.get("rarity", "common")

        sell_mult = {"common": 0.5, "rare": 0.6, "epic": 0.7, "legendary": 0.8}
        sell_price = int(price * sell_mult.get(rarity, 0.5))

        player.inventory[item_id] -= 1
        player.gold += sell_price
        player.stats["gold_earned"] = player.stats.get("gold_earned", 0) + sell_price

        # Удалить процедурный предмет если продан последний
        if player.inventory.get(item_id, 0) <= 0 and item_id in player.procedural_items:
            del player.procedural_items[item_id]

        save_data()
        await query.answer(f"Продано за {sell_price} золота")

        # Обновить меню продажи
        await show_sell_menu(query, player)


# =====================
# НАСТРОЙКА ЗЕЛИЙ ДЛЯ БОЯ
# =====================

# Список всех зелий которые можно использовать в бою
BATTLE_POTIONS = {
    "hp_potion_small": {"name": "Малое зелье HP", "emoji": "❤️", "effect": "heal", "value": 50},
    "hp_potion_medium": {"name": "Среднее зелье HP", "emoji": "💖", "effect": "heal", "value": 120},
    "hp_potion_large": {"name": "Большое зелье HP", "emoji": "💗", "effect": "heal", "value": 250},
    "mana_potion_small": {"name": "Малое зелье маны", "emoji": "💙", "effect": "mana", "value": 30},
    "mana_potion_medium": {"name": "Среднее зелье маны", "emoji": "💎", "effect": "mana", "value": 70},
    "elixir_power": {"name": "Эликсир силы", "emoji": "💪", "effect": "buff_damage", "value": 0.2},
    "elixir_defense": {"name": "Эликсир защиты", "emoji": "🛡️", "effect": "buff_defense", "value": 0.2},
    "antidote": {"name": "Противоядие", "emoji": "🧪", "effect": "cleanse", "value": 0},
}


async def show_potion_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню настройки слотов зелий"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    # Получить текущие зелья в слотах
    slot1_id = player.potion_slots.get("slot_1")
    slot2_id = player.potion_slots.get("slot_2")

    slot1_item = ITEMS.get(slot1_id, {})
    slot2_item = ITEMS.get(slot2_id, {})

    slot1_name = slot1_item.get("name", "Пусто") if slot1_id else "Пусто"
    slot2_name = slot2_item.get("name", "Пусто") if slot2_id else "Пусто"
    slot1_emoji = slot1_item.get("emoji", "❓") if slot1_id else "❓"
    slot2_emoji = slot2_item.get("emoji", "❓") if slot2_id else "❓"

    # Подсчитать зелья в инвентаре
    slot1_count = player.inventory.get(slot1_id, 0) if slot1_id else 0
    slot2_count = player.inventory.get(slot2_id, 0) if slot2_id else 0

    text = f"""⚗️ СЛОТЫ ЗЕЛИЙ

Выбери какие зелья использовать в бою.
В бою будут доступны 2 кнопки с выбранными зельями.

📌 Слот 1: {slot1_emoji} {slot1_name}
   В инвентаре: {slot1_count} шт.

📌 Слот 2: {slot2_emoji} {slot2_name}
   В инвентаре: {slot2_count} шт.

Нажми на слот чтобы изменить зелье."""

    keyboard = [
        [InlineKeyboardButton(f"📌 Слот 1: {slot1_emoji} {slot1_name}", callback_data="set_potion_1")],
        [InlineKeyboardButton(f"📌 Слот 2: {slot2_emoji} {slot2_name}", callback_data="set_potion_2")],
        [InlineKeyboardButton("🔙 Назад", callback_data="inventory")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_potion_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать выбор зелья для слота"""
    query = update.callback_query
    await query.answer()

    slot_num = query.data.replace("set_potion_", "")
    player = get_player(query.from_user.id)

    text = f"⚗️ ВЫБОР ЗЕЛЬЯ ДЛЯ СЛОТА {slot_num}\n\n"
    text += "Доступные зелья:\n\n"

    keyboard = []

    for potion_id, potion_info in BATTLE_POTIONS.items():
        count = player.inventory.get(potion_id, 0)
        emoji = potion_info["emoji"]
        name = potion_info["name"]

        # Описание эффекта
        effect = potion_info["effect"]
        if effect == "heal":
            effect_text = f"+{potion_info['value']} HP"
        elif effect == "mana":
            effect_text = f"+{potion_info['value']} маны"
        elif effect == "buff_damage":
            effect_text = f"+{int(potion_info['value']*100)}% урона (1 бой)"
        elif effect == "buff_defense":
            effect_text = f"+{int(potion_info['value']*100)}% защиты (1 бой)"
        elif effect == "cleanse":
            effect_text = "Снимает яд"
        else:
            effect_text = ""

        text += f"{emoji} {name} ({count} шт.)\n"
        text += f"   {effect_text}\n\n"

        # Кнопка выбора
        btn_text = f"{emoji} {name} ({count})"
        keyboard.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"select_potion_{slot_num}_{potion_id}"
        )])

    # Кнопка очистить слот
    keyboard.append([InlineKeyboardButton("❌ Очистить слот", callback_data=f"select_potion_{slot_num}_none")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="potion_slots")])

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_potion_for_slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбрать зелье для слота"""
    query = update.callback_query

    # Формат: select_potion_SLOT_POTIONID
    parts = query.data.split("_", 3)
    if len(parts) < 4:
        await query.answer()
        return

    slot_num = parts[2]
    potion_id = parts[3]

    player = get_player(query.from_user.id)

    slot_key = f"slot_{slot_num}"

    if potion_id == "none":
        player.potion_slots[slot_key] = None
        await query.answer("Слот очищен")
    else:
        # Проверить что это валидное зелье
        if potion_id not in BATTLE_POTIONS:
            await query.answer("Неизвестное зелье!", show_alert=True)
            return

        player.potion_slots[slot_key] = potion_id
        potion_name = BATTLE_POTIONS[potion_id]["name"]
        await query.answer(f"Слот {slot_num}: {potion_name}")

    save_data()

    # Вернуться к меню слотов
    await show_potion_slots_direct(query, player)


async def show_potion_slots_direct(query, player):
    """Показать меню слотов зелий (прямой вызов)"""
    slot1_id = player.potion_slots.get("slot_1")
    slot2_id = player.potion_slots.get("slot_2")

    slot1_item = ITEMS.get(slot1_id, {})
    slot2_item = ITEMS.get(slot2_id, {})

    slot1_name = slot1_item.get("name", "Пусто") if slot1_id else "Пусто"
    slot2_name = slot2_item.get("name", "Пусто") if slot2_id else "Пусто"
    slot1_emoji = slot1_item.get("emoji", "❓") if slot1_id else "❓"
    slot2_emoji = slot2_item.get("emoji", "❓") if slot2_id else "❓"

    slot1_count = player.inventory.get(slot1_id, 0) if slot1_id else 0
    slot2_count = player.inventory.get(slot2_id, 0) if slot2_id else 0

    text = f"""⚗️ СЛОТЫ ЗЕЛИЙ

Выбери какие зелья использовать в бою.
В бою будут доступны 2 кнопки с выбранными зельями.

📌 Слот 1: {slot1_emoji} {slot1_name}
   В инвентаре: {slot1_count} шт.

📌 Слот 2: {slot2_emoji} {slot2_name}
   В инвентаре: {slot2_count} шт.

Нажми на слот чтобы изменить зелье."""

    keyboard = [
        [InlineKeyboardButton(f"📌 Слот 1: {slot1_emoji} {slot1_name}", callback_data="set_potion_1")],
        [InlineKeyboardButton(f"📌 Слот 2: {slot2_emoji} {slot2_name}", callback_data="set_potion_2")],
        [InlineKeyboardButton("🔙 Назад", callback_data="inventory")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
