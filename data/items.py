"""
Предметы и легендарные сеты
"""

ITEMS = {
    # Ресурсы
    "herb": {"name": "Лесная трава", "type": "resource", "emoji": "🌿", "price": 5},
    "ore": {"name": "Железная руда", "type": "resource", "emoji": "ite", "price": 10},
    "essence": {"name": "Тёмная эссенция", "type": "resource", "emoji": "💜", "price": 20},
    "demon_soul": {"name": "Душа демона", "type": "resource", "emoji": "👿", "price": 50},
    "chaos_essence": {"name": "Эссенция хаоса", "type": "resource", "emoji": "🌀", "price": 100},

    # Зелья
    "hp_potion_small": {"name": "Малое зелье HP", "type": "consumable", "emoji": "❤️", "heal": 50, "price": 30},
    "hp_potion_medium": {"name": "Среднее зелье HP", "type": "consumable", "emoji": "💖", "heal": 120, "price": 70},
    "hp_potion_large": {"name": "Большое зелье HP", "type": "consumable", "emoji": "💗", "heal": 250, "price": 150},
    "mana_potion_small": {"name": "Малое зелье маны", "type": "consumable", "emoji": "💙", "mana": 30, "price": 25},
    "mana_potion_medium": {"name": "Среднее зелье маны", "type": "consumable", "emoji": "💎", "mana": 70, "price": 60},
    "elixir_power": {"name": "Эликсир силы", "type": "consumable", "emoji": "💪", "buff_damage": 0.2, "price": 100},
    "elixir_defense": {"name": "Эликсир защиты", "type": "consumable", "emoji": "🛡️", "buff_defense": 0.2, "price": 100},
    "antidote": {"name": "Противоядие", "type": "consumable", "emoji": "🧪", "cleanse_poison": True, "price": 40},
    "chaos_elixir": {"name": "Эликсир хаоса", "type": "consumable", "emoji": "🌀", "special": "chaos", "price": 500},

    # Обычное оружие
    "rusty_sword": {"name": "Ржавый меч", "type": "weapon", "emoji": "🗡️", "damage": 5, "price": 50, "rarity": "common"},
    "iron_sword": {"name": "Железный меч", "type": "weapon", "emoji": "⚔️", "damage": 12, "price": 150, "rarity": "common"},
    "steel_sword": {"name": "Стальной меч", "type": "weapon", "emoji": "🔪", "damage": 20, "price": 350, "rarity": "uncommon"},
    "magic_staff": {"name": "Магический посох", "type": "weapon", "emoji": "🪄", "damage": 18, "mana_bonus": 20, "price": 400, "rarity": "uncommon"},
    "hunter_bow": {"name": "Охотничий лук", "type": "weapon", "emoji": "🏹", "damage": 15, "crit_bonus": 5, "price": 300, "rarity": "uncommon"},

    # Редкое оружие
    "flame_sword": {"name": "Пламенный меч", "type": "weapon", "emoji": "🔥", "damage": 35, "burn": 3, "price": 800, "rarity": "rare"},
    "frost_staff": {"name": "Ледяной посох", "type": "weapon", "emoji": "❄️", "damage": 30, "mana_bonus": 40, "slow": True, "price": 900, "rarity": "rare"},
    "shadow_dagger": {"name": "Теневой кинжал", "type": "weapon", "emoji": "🌑", "damage": 28, "crit_bonus": 15, "price": 750, "rarity": "rare"},

    # Обычная броня
    "leather_armor": {"name": "Кожаная броня", "type": "armor", "emoji": "🥋", "defense": 5, "price": 60, "rarity": "common"},
    "chainmail": {"name": "Кольчуга", "type": "armor", "emoji": "⛓️", "defense": 12, "price": 200, "rarity": "common"},
    "plate_armor": {"name": "Латный доспех", "type": "armor", "emoji": "🛡️", "defense": 22, "price": 500, "rarity": "uncommon"},

    # Редкая броня
    "fire_armor": {"name": "Огненная броня", "type": "armor", "emoji": "🔥", "defense": 30, "hp_bonus": 30, "price": 1000, "rarity": "rare"},
    "shadow_cloak": {"name": "Плащ теней", "type": "armor", "emoji": "🌑", "defense": 20, "dodge_bonus": 10, "price": 900, "rarity": "rare"},

    # Аксессуары
    "lucky_ring": {"name": "Кольцо удачи", "type": "accessory", "emoji": "💍", "crit_bonus": 10, "price": 400, "rarity": "uncommon"},
    "power_amulet": {"name": "Амулет силы", "type": "accessory", "emoji": "📿", "damage_bonus": 10, "price": 500, "rarity": "uncommon"},
    "shield_charm": {"name": "Защитный оберег", "type": "accessory", "emoji": "🔮", "defense_bonus": 8, "price": 450, "rarity": "uncommon"},
    "life_pendant": {"name": "Кулон жизни", "type": "accessory", "emoji": "💚", "hp_bonus": 50, "price": 600, "rarity": "rare"},
}

LEGENDARY_SETS = {
    "warrior": {
        "name": "Гнев Титана",
        "pieces": {
            "helmet": {"name": "Шлем Титана", "emoji": "⛑️", "hp": 30, "defense": 5},
            "chest": {"name": "Латы Титана", "emoji": "🎽", "hp": 50, "defense": 10},
            "gloves": {"name": "Перчатки Титана", "emoji": "🧤", "damage": 8, "crit": 5},
            "boots": {"name": "Сапоги Титана", "emoji": "👢", "hp": 20, "defense": 3}
        },
        "bonus_2": "+10% HP",
        "bonus_4": "При HP <30% урон +50%"
    },
    "mage": {
        "name": "Покров Архимага",
        "pieces": {
            "helmet": {"name": "Корона Архимага", "emoji": "👑", "mana": 40, "damage": 8},
            "chest": {"name": "Мантия Архимага", "emoji": "🧥", "mana": 60, "defense": 5},
            "gloves": {"name": "Перчатки Архимага", "emoji": "🧤", "damage": 12, "crit": 10},
            "boots": {"name": "Сапоги Архимага", "emoji": "👢", "mana": 30, "defense": 3}
        },
        "bonus_2": "+20% маны",
        "bonus_4": "Скиллы стоят на 30% меньше маны"
    },
    "archer": {
        "name": "Тень Охотника",
        "pieces": {
            "helmet": {"name": "Капюшон Охотника", "emoji": "🎭", "hp": 15, "crit": 10},
            "chest": {"name": "Плащ Охотника", "emoji": "🧥", "hp": 25, "defense": 8},
            "gloves": {"name": "Перчатки Охотника", "emoji": "🧤", "damage": 15, "crit": 15},
            "boots": {"name": "Сапоги Охотника", "emoji": "👢", "hp": 10, "dodge": 10}
        },
        "bonus_2": "+25% крит урона",
        "bonus_4": "Криты накладывают кровотечение"
    },
    "rogue": {
        "name": "Одеяния Убийцы",
        "pieces": {
            "helmet": {"name": "Маска Убийцы", "emoji": "🎭", "hp": 10, "crit": 15},
            "chest": {"name": "Кираса Убийцы", "emoji": "🧥", "hp": 20, "damage": 10},
            "gloves": {"name": "Клинки Убийцы", "emoji": "🧤", "damage": 20, "crit": 10},
            "boots": {"name": "Сапоги Убийцы", "emoji": "👢", "dodge": 15, "damage": 5}
        },
        "bonus_2": "Первый удар x3 урона",
        "bonus_4": "Убивает врагов с <10% HP"
    },
    "paladin": {
        "name": "Свет Небес",
        "pieces": {
            "helmet": {"name": "Нимб Света", "emoji": "😇", "hp": 25, "mana": 15},
            "chest": {"name": "Доспех Света", "emoji": "🎽", "hp": 60, "defense": 8},
            "gloves": {"name": "Рукавицы Света", "emoji": "🧤", "damage": 10, "mana": 10},
            "boots": {"name": "Поножи Света", "emoji": "👢", "hp": 30, "defense": 5}
        },
        "bonus_2": "Хил усилен на 30%",
        "bonus_4": "При смерти воскрешение с 30% HP"
    }
}
