"""
Вспомогательные функции для UI и генерации предметов
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest


def create_hp_bar(current: int, maximum: int, length: int = 10) -> str:
    """Создать полоску HP"""
    filled = int(length * current / maximum) if maximum > 0 else 0
    filled = max(0, min(filled, length))
    return "█" * filled + "░" * (length - filled)


def create_mana_bar(current: int, maximum: int, length: int = 10) -> str:
    """Создать полоску маны"""
    filled = int(length * current / maximum) if maximum > 0 else 0
    filled = max(0, min(filled, length))
    return "▓" * filled + "░" * (length - filled)


async def safe_edit_message(query, context, text: str, reply_markup=None, parse_mode=None):
    """Безопасное редактирование сообщения (обрабатывает фото-сообщения)"""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except BadRequest as e:
        if "no text" in str(e).lower():
            # Сообщение с фото - удаляем и отправляем новое
            await query.message.delete()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            raise


# Уровни открытия умений
SKILL_LEVELS = {0: 1, 1: 3, 2: 6, 3: 10}


def get_fight_keyboard(fight, player) -> InlineKeyboardMarkup:
    """Создать клавиатуру для боя"""
    from data import CLASSES

    buttons = []

    # Основные действия
    row1 = [
        InlineKeyboardButton("⚔️ Атака", callback_data="fight_attack"),
        InlineKeyboardButton("🛡️ Блок", callback_data="fight_block"),
    ]
    buttons.append(row1)

    # Скиллы класса (только открытые)
    if player.player_class:
        class_data = CLASSES[player.player_class]
        skills = class_data.get("skills", {})
        skill_row = []
        for i, (skill_id, skill) in enumerate(skills.items()):
            req_level = SKILL_LEVELS.get(i, 1)

            # Пропускаем заблокированные умения
            if player.level < req_level:
                continue

            cd = fight.cooldowns.get(skill_id, 0)
            if cd > 0:
                btn_text = f"{skill['emoji']} ({cd})"
            else:
                btn_text = f"{skill['emoji']} {skill['name']}"
            skill_row.append(InlineKeyboardButton(btn_text, callback_data=f"fight_skill_{skill_id}"))
        if skill_row:
            buttons.append(skill_row)

    # Зелья из слотов игрока
    from data import ITEMS
    row3 = []

    slot1_id = player.potion_slots.get("slot_1") if hasattr(player, 'potion_slots') else "hp_potion_small"
    slot2_id = player.potion_slots.get("slot_2") if hasattr(player, 'potion_slots') else "mana_potion_small"

    if slot1_id:
        slot1_item = ITEMS.get(slot1_id, {})
        slot1_emoji = slot1_item.get("emoji", "❓")
        slot1_name = slot1_item.get("name", "Зелье 1")
        # Короткое имя для кнопки
        short_name1 = slot1_name.replace("Малое ", "").replace("Среднее ", "").replace("Большое ", "")
        row3.append(InlineKeyboardButton(f"{slot1_emoji} {short_name1}", callback_data="fight_potion_1"))

    if slot2_id:
        slot2_item = ITEMS.get(slot2_id, {})
        slot2_emoji = slot2_item.get("emoji", "❓")
        slot2_name = slot2_item.get("name", "Зелье 2")
        short_name2 = slot2_name.replace("Малое ", "").replace("Среднее ", "").replace("Большое ", "")
        row3.append(InlineKeyboardButton(f"{slot2_emoji} {short_name2}", callback_data="fight_potion_2"))

    if row3:
        buttons.append(row3)

    # Побег
    buttons.append([InlineKeyboardButton("🏃 Сбежать", callback_data="fight_flee")])

    return InlineKeyboardMarkup(buttons)


async def update_fight_ui(query, fight, player, extra_text: str = ""):
    """Обновить интерфейс боя"""
    # Статус игрока
    player_hp_bar = create_hp_bar(fight.player_hp, fight.player_max_hp)
    player_mana_bar = create_mana_bar(fight.player_mana, player.get_max_mana())

    # Статус врага
    enemy_hp_bar = create_hp_bar(fight.enemy_hp, fight.enemy_max_hp)

    # Эффекты
    player_effects = ""
    if fight.player_effects:
        effects = []
        for eff, val in fight.player_effects.items():
            if eff == "poison":
                effects.append(f"🤢 Яд ({val})")
            elif eff == "burn":
                effects.append(f"🔥 Горение ({val})")
            elif eff == "bleed":
                effects.append(f"🩸 Кровотечение ({val})")
        if effects:
            player_effects = f"\n⚠️ Эффекты: {', '.join(effects)}"

    enemy_effects = ""
    if fight.enemy_effects:
        effects = []
        for eff, val in fight.enemy_effects.items():
            if eff == "poison":
                effects.append(f"🤢 ({val})")
            elif eff == "burn":
                effects.append(f"🔥 ({val})")
            elif eff == "slow":
                effects.append("❄️")
            elif eff == "bleed":
                effects.append(f"🩸 ({val})")
        if effects:
            enemy_effects = f" [{', '.join(effects)}]"

    # Защитные эффекты
    defense_status = ""
    if fight.block_next:
        defense_status += "\n🛡️ Блок активен!"
    if fight.dodge_next:
        defense_status += "\n💨 Уклонение!"
    if fight.barrier > 0:
        defense_status += f"\n🔮 Барьер: {fight.barrier}"
    if fight.invisible > 0:
        defense_status += f"\n👁️ Невидимость: {fight.invisible} ходов"
    if fight.invulnerable > 0:
        defense_status += f"\n✨ Неуязвимость: {fight.invulnerable} ходов"

    # Лог боя (последние 3 записи)
    log_text = ""
    if fight.fight_log:
        log_text = "\n\n📜 " + "\n".join(fight.fight_log[-3:])

    text = f"""⚔️ **БОЙ** ⚔️

{fight.enemy_emoji} **{fight.enemy_name}**{enemy_effects}
HP: [{enemy_hp_bar}] {fight.enemy_hp}/{fight.enemy_max_hp}

👤 **{player.name}**
HP: [{player_hp_bar}] {fight.player_hp}/{fight.player_max_hp}
MP: [{player_mana_bar}] {fight.player_mana}/{player.get_max_mana()}{player_effects}{defense_status}{log_text}"""

    if extra_text:
        text += f"\n\n{extra_text}"

    keyboard = get_fight_keyboard(fight, player)

    try:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        # Если не удалось с Markdown, попробуем без
        try:
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception:
            print(f"Ошибка обновления UI: {e}")


# =====================
# ПРОЦЕДУРНАЯ ГЕНЕРАЦИЯ ПРЕДМЕТОВ
# =====================

# Префиксы для имён предметов по редкости
ITEM_PREFIXES = {
    "common": ["Простой", "Обычный", "Старый", "Потёртый"],
    "uncommon": ["Добротный", "Крепкий", "Надёжный", "Прочный"],
    "rare": ["Отличный", "Искусный", "Мастерский", "Закалённый"],
    "epic": ["Великий", "Могучий", "Легендарный", "Древний"]
}

# Суффиксы для бонусов
ITEM_SUFFIXES = {
    "damage": ["Силы", "Мощи", "Ярости", "Разрушения"],
    "defense": ["Защиты", "Стойкости", "Крепости", "Брони"],
    "hp": ["Жизни", "Здоровья", "Выносливости", "Витальности"],
    "crit": ["Точности", "Меткости", "Удачи", "Везения"],
    "dodge": ["Уклонения", "Ловкости", "Тени", "Ветра"],
    "lifesteal": ["Вампиризма", "Крови", "Жажды", "Похищения"],
    "block": ["Щита", "Парирования", "Отражения", "Стража"],
    "mana": ["Магии", "Мудрости", "Интеллекта", "Знания"]
}

# Базовые типы предметов
ITEM_BASE_TYPES = {
    "weapon": {
        "sword": {"name": "Меч", "emoji": "⚔️", "base_damage": 10},
        "staff": {"name": "Посох", "emoji": "🪄", "base_damage": 8, "base_mana": 10},
        "dagger": {"name": "Кинжал", "emoji": "🗡️", "base_damage": 7, "base_crit": 5},
        "bow": {"name": "Лук", "emoji": "🏹", "base_damage": 9, "base_crit": 3},
        "axe": {"name": "Топор", "emoji": "🪓", "base_damage": 12},
    },
    "helmet": {
        "helm": {"name": "Шлем", "emoji": "⛑️", "base_defense": 4, "base_hp": 10},
        "hood": {"name": "Капюшон", "emoji": "🎭", "base_defense": 2, "base_mana": 15},
        "crown": {"name": "Корона", "emoji": "👑", "base_defense": 3, "base_crit": 2},
    },
    "chest": {
        "armor": {"name": "Броня", "emoji": "🛡️", "base_defense": 8, "base_hp": 20},
        "robe": {"name": "Мантия", "emoji": "🧥", "base_defense": 4, "base_mana": 25},
        "vest": {"name": "Жилет", "emoji": "🥋", "base_defense": 5, "base_dodge": 3},
    },
    "gloves": {
        "gauntlets": {"name": "Рукавицы", "emoji": "🤜", "base_defense": 3, "base_damage": 2},
        "gloves": {"name": "Перчатки", "emoji": "🧤", "base_defense": 2, "base_crit": 2},
    },
    "boots": {
        "boots": {"name": "Сапоги", "emoji": "👢", "base_defense": 3, "base_hp": 10},
        "shoes": {"name": "Ботинки", "emoji": "👟", "base_defense": 2, "base_dodge": 3},
    },
    "ring": {
        "ring": {"name": "Кольцо", "emoji": "💍", "base_crit": 3},
        "band": {"name": "Перстень", "emoji": "💎", "base_damage": 3},
    },
    "necklace": {
        "amulet": {"name": "Амулет", "emoji": "📿", "base_hp": 15},
        "pendant": {"name": "Кулон", "emoji": "🔗", "base_mana": 15},
    }
}

# Множители статов по редкости
RARITY_MULTIPLIERS = {
    "common": {"stat_mult": 1.0, "bonus_count": 0, "price_mult": 1.0},
    "uncommon": {"stat_mult": 1.3, "bonus_count": 1, "price_mult": 1.5},
    "rare": {"stat_mult": 1.7, "bonus_count": 2, "price_mult": 2.5},
    "epic": {"stat_mult": 2.2, "bonus_count": 3, "price_mult": 4.0}
}

# Возможные бонусы по типу слота
SLOT_BONUS_POOLS = {
    "weapon": ["damage", "crit", "lifesteal"],
    "helmet": ["hp", "mana", "defense"],
    "chest": ["hp", "defense", "block"],
    "gloves": ["damage", "crit", "dodge"],
    "boots": ["dodge", "hp", "defense"],
    "ring": ["crit", "damage", "lifesteal"],
    "necklace": ["hp", "mana", "defense"]
}

# Значения бонусов по уровню подземелья
DUNGEON_LEVEL_BONUS = {
    "forest": 1,
    "mines": 2,
    "crypt": 3,
    "abyss": 4,
    "chaos": 5
}


def generate_procedural_item(dungeon_id: str, slot: str = None, forced_rarity: str = None) -> dict:
    """
    Генерирует случайный предмет на основе подземелья.

    Args:
        dungeon_id: ID подземелья (forest, mines, crypt, abyss, chaos)
        slot: Тип слота (weapon, helmet, chest, etc). Если None - выбирается случайно
        forced_rarity: Принудительная редкость. Если None - определяется случайно

    Returns:
        Словарь с данными предмета
    """
    dungeon_level = DUNGEON_LEVEL_BONUS.get(dungeon_id, 1)

    # Выбрать слот
    if slot is None:
        slot = random.choice(list(ITEM_BASE_TYPES.keys()))

    # Выбрать базовый тип предмета
    base_types = ITEM_BASE_TYPES.get(slot, {})
    if not base_types:
        return None

    base_type_id = random.choice(list(base_types.keys()))
    base_type = base_types[base_type_id]

    # Определить редкость
    if forced_rarity:
        rarity = forced_rarity
    else:
        rarity_roll = random.randint(1, 100)
        if rarity_roll <= 50:
            rarity = "common"
        elif rarity_roll <= 80:
            rarity = "uncommon"
        elif rarity_roll <= 95:
            rarity = "rare"
        else:
            rarity = "epic"

    rarity_data = RARITY_MULTIPLIERS[rarity]
    stat_mult = rarity_data["stat_mult"] * (1 + (dungeon_level - 1) * 0.2)
    bonus_count = rarity_data["bonus_count"]

    # Базовые статы
    item = {
        "type": "weapon" if slot == "weapon" else "armor" if slot in ["helmet", "chest", "gloves", "boots", "shoulders", "leggings", "belt"] else "accessory",
        "slot": slot,
        "rarity": rarity,
        "emoji": base_type["emoji"],
        "procedural": True,  # Метка процедурного предмета
        "dungeon_source": dungeon_id
    }

    # Применить базовые статы с множителями
    if "base_damage" in base_type:
        item["damage"] = int(base_type["base_damage"] * stat_mult)
    if "base_defense" in base_type:
        item["defense"] = int(base_type["base_defense"] * stat_mult)
    if "base_hp" in base_type:
        item["hp_bonus"] = int(base_type["base_hp"] * stat_mult)
    if "base_mana" in base_type:
        item["mana_bonus"] = int(base_type["base_mana"] * stat_mult)
    if "base_crit" in base_type:
        item["crit_bonus"] = int(base_type["base_crit"] * stat_mult)
    if "base_dodge" in base_type:
        item["dodge_bonus"] = int(base_type["base_dodge"] * stat_mult)

    # Добавить случайные бонусы
    bonus_pool = SLOT_BONUS_POOLS.get(slot, ["hp", "defense"])
    applied_bonuses = []

    for _ in range(bonus_count):
        available_bonuses = [b for b in bonus_pool if b not in applied_bonuses]
        if not available_bonuses:
            break

        bonus_type = random.choice(available_bonuses)
        applied_bonuses.append(bonus_type)

        bonus_value = int(dungeon_level * stat_mult * random.uniform(1.5, 3.0))

        if bonus_type == "damage":
            item["damage_bonus"] = item.get("damage_bonus", 0) + bonus_value
        elif bonus_type == "defense":
            item["defense"] = item.get("defense", 0) + bonus_value
        elif bonus_type == "hp":
            item["hp_bonus"] = item.get("hp_bonus", 0) + bonus_value * 5
        elif bonus_type == "mana":
            item["mana_bonus"] = item.get("mana_bonus", 0) + bonus_value * 3
        elif bonus_type == "crit":
            item["crit_bonus"] = item.get("crit_bonus", 0) + max(1, bonus_value // 2)
        elif bonus_type == "dodge":
            item["dodge_bonus"] = item.get("dodge_bonus", 0) + max(1, bonus_value // 2)
        elif bonus_type == "lifesteal":
            item["lifesteal"] = item.get("lifesteal", 0) + round(bonus_value * 0.01, 2)
        elif bonus_type == "block":
            item["block"] = item.get("block", 0) + max(1, bonus_value // 2)

    # Сгенерировать имя
    prefix = random.choice(ITEM_PREFIXES.get(rarity, ["Обычный"]))

    # Выбрать суффикс на основе главного бонуса
    main_stat = None
    if applied_bonuses:
        main_stat = applied_bonuses[0]
    elif item.get("damage") or item.get("damage_bonus"):
        main_stat = "damage"
    elif item.get("defense"):
        main_stat = "defense"

    suffix = ""
    if main_stat and main_stat in ITEM_SUFFIXES:
        suffix = " " + random.choice(ITEM_SUFFIXES[main_stat])

    item["name"] = f"{prefix} {base_type['name']}{suffix}"

    # Рассчитать цену
    base_price = 50 * dungeon_level
    total_stats = sum([
        item.get("damage", 0) * 5,
        item.get("damage_bonus", 0) * 5,
        item.get("defense", 0) * 4,
        item.get("hp_bonus", 0),
        item.get("mana_bonus", 0),
        item.get("crit_bonus", 0) * 10,
        item.get("dodge_bonus", 0) * 10,
        item.get("lifesteal", 0) * 500,
        item.get("block", 0) * 10
    ])
    item["price"] = int((base_price + total_stats) * rarity_data["price_mult"])

    # Сгенерировать уникальный ID
    item["id"] = f"proc_{dungeon_id}_{slot}_{random.randint(10000, 99999)}"

    return item


def get_item_description(item: dict) -> str:
    """Получить описание предмета со всеми статами"""
    from data import RARITY_EMOJI

    lines = []

    rarity_emoji = RARITY_EMOJI.get(item.get("rarity", "common"), "")
    lines.append(f"{rarity_emoji}{item['emoji']} **{item['name']}**")

    stats = []
    if item.get("damage"):
        stats.append(f"⚔️ {item['damage']} урона")
    if item.get("damage_bonus"):
        stats.append(f"⚔️ +{item['damage_bonus']} урона")
    if item.get("defense"):
        stats.append(f"🛡️ {item['defense']} защиты")
    if item.get("hp_bonus"):
        stats.append(f"❤️ +{item['hp_bonus']} HP")
    if item.get("mana_bonus"):
        stats.append(f"💙 +{item['mana_bonus']} маны")
    if item.get("crit_bonus"):
        stats.append(f"🎯 +{item['crit_bonus']}% крита")
    if item.get("dodge_bonus"):
        stats.append(f"💨 +{item['dodge_bonus']}% уклонения")
    if item.get("lifesteal"):
        stats.append(f"🩸 +{int(item['lifesteal'] * 100)}% вампиризма")
    if item.get("block"):
        stats.append(f"🛡️ +{item['block']}% блока")

    if stats:
        lines.append(", ".join(stats))

    if item.get("price"):
        lines.append(f"💰 {item['price']} золота")

    return "\n".join(lines)
