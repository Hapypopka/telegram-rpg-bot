"""
Предметы и снаряжение

Редкости:
- common (белый) - продаётся в магазине
- rare (синий) - крафт или дроп с мобов
- epic (фиолетовый) - дроп с боссов, есть сетовые бонусы
- legendary (оранжевый) - только оружие, квестовое

Слоты брони: helmet, shoulders, chest, belt, gloves, leggings, boots
Слоты аксессуаров: ring, necklace
"""

# Цвета редкостей для отображения
RARITY_COLORS = {
    "common": "",        # белый (без цвета)
    "rare": "[R]",       # синий
    "epic": "[E]",       # фиолетовый
    "legendary": "[L]"   # оранжевый
}

RARITY_EMOJI = {
    "common": "",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟠"
}

# Названия слотов на русском
SLOT_NAMES = {
    "weapon": "Оружие",
    "helmet": "Шлем",
    "shoulders": "Плечи",
    "chest": "Грудь",
    "belt": "Пояс",
    "gloves": "Перчатки",
    "leggings": "Поножи",
    "boots": "Сапоги",
    "ring": "Кольцо",
    "necklace": "Ожерелье"
}

ITEMS = {
    # =====================
    # РЕСУРСЫ
    # =====================
    "herb": {"name": "Лесная трава", "type": "resource", "emoji": "🌿", "price": 5},
    "ore": {"name": "Железная руда", "type": "resource", "emoji": "ite", "price": 10},
    "leather": {"name": "Грубая кожа", "type": "resource", "emoji": "🦴", "price": 8},
    "cloth": {"name": "Ткань", "type": "resource", "emoji": "🧵", "price": 6},
    "essence": {"name": "Тёмная эссенция", "type": "resource", "emoji": "💜", "price": 20},
    "crystal": {"name": "Магический кристалл", "type": "resource", "emoji": "💎", "price": 30},
    "demon_soul": {"name": "Душа демона", "type": "resource", "emoji": "👿", "price": 50},
    "chaos_essence": {"name": "Эссенция хаоса", "type": "resource", "emoji": "🌀", "price": 100},
    "dragon_scale": {"name": "Чешуя дракона", "type": "resource", "emoji": "🐉", "price": 200},
    "boss_trophy": {"name": "Трофей босса", "type": "resource", "emoji": "🏆", "price": 500},

    # Рецепты легендарного оружия (выдаются за квесты)
    "excalibur_recipe": {
        "name": "Чертёж: Экскалибур", "type": "recipe", "emoji": "📜",
        "description": "Древний чертёж легендарного меча"
    },
    "staff_of_eternity_recipe": {
        "name": "Чертёж: Посох Вечности", "type": "recipe", "emoji": "📜",
        "description": "Магический свиток с описанием создания посоха"
    },
    "bow_of_the_wind_recipe": {
        "name": "Чертёж: Лук Ветра", "type": "recipe", "emoji": "📜",
        "description": "Эльфийский рецепт создания лука"
    },

    # =====================
    # ЗЕЛЬЯ (consumable)
    # =====================
    "hp_potion_small": {"name": "Малое зелье HP", "type": "consumable", "emoji": "❤️", "heal": 50, "price": 30},
    "hp_potion_medium": {"name": "Среднее зелье HP", "type": "consumable", "emoji": "💖", "heal": 120, "price": 70},
    "hp_potion_large": {"name": "Большое зелье HP", "type": "consumable", "emoji": "💗", "heal": 250, "price": 150},
    "mana_potion_small": {"name": "Малое зелье маны", "type": "consumable", "emoji": "💙", "mana": 30, "price": 25},
    "mana_potion_medium": {"name": "Среднее зелье маны", "type": "consumable", "emoji": "💎", "mana": 70, "price": 60},
    "elixir_power": {"name": "Эликсир силы", "type": "consumable", "emoji": "💪", "buff_damage": 0.2, "price": 100},
    "elixir_defense": {"name": "Эликсир защиты", "type": "consumable", "emoji": "🛡️", "buff_defense": 0.2, "price": 100},
    "antidote": {"name": "Противоядие", "type": "consumable", "emoji": "🧪", "cleanse_poison": True, "price": 40},

    # =====================
    # ОРУЖИЕ (weapon)
    # =====================

    # --- COMMON (белое, в магазине) ---
    "rusty_sword": {
        "name": "Ржавый меч", "type": "weapon", "slot": "weapon",
        "emoji": "🗡️", "damage": 5, "price": 50, "rarity": "common"
    },
    "iron_sword": {
        "name": "Железный меч", "type": "weapon", "slot": "weapon",
        "emoji": "⚔️", "damage": 12, "price": 150, "rarity": "common"
    },
    "wooden_staff": {
        "name": "Деревянный посох", "type": "weapon", "slot": "weapon",
        "emoji": "🪵", "damage": 8, "mana_bonus": 15, "price": 120, "rarity": "common"
    },
    "short_bow": {
        "name": "Короткий лук", "type": "weapon", "slot": "weapon",
        "emoji": "🏹", "damage": 10, "crit_bonus": 3, "price": 130, "rarity": "common"
    },

    # --- RARE (синее, крафт/дроп) ---
    "steel_sword": {
        "name": "Стальной меч", "type": "weapon", "slot": "weapon",
        "emoji": "🔪", "damage": 20, "crit_bonus": 5, "price": 350, "rarity": "rare",
        "craft": {"ore": 10, "leather": 5}
    },
    "magic_staff": {
        "name": "Магический посох", "type": "weapon", "slot": "weapon",
        "emoji": "🪄", "damage": 18, "mana_bonus": 30, "price": 400, "rarity": "rare",
        "craft": {"crystal": 5, "essence": 3}
    },
    "hunter_bow": {
        "name": "Охотничий лук", "type": "weapon", "slot": "weapon",
        "emoji": "🎯", "damage": 15, "crit_bonus": 10, "price": 380, "rarity": "rare",
        "craft": {"leather": 8, "herb": 5}
    },
    "flame_sword": {
        "name": "Пламенный меч", "type": "weapon", "slot": "weapon",
        "emoji": "🔥", "damage": 35, "burn": 3, "crit_mult": 1.7, "price": 800, "rarity": "rare",
        "craft": {"ore": 15, "essence": 10, "demon_soul": 2}
    },
    "frost_staff": {
        "name": "Ледяной посох", "type": "weapon", "slot": "weapon",
        "emoji": "❄️", "damage": 30, "mana_bonus": 40, "slow": True, "price": 900, "rarity": "rare",
        "craft": {"crystal": 10, "essence": 8}
    },
    "shadow_dagger": {
        "name": "Теневой кинжал", "type": "weapon", "slot": "weapon",
        "emoji": "🌑", "damage": 28, "crit_bonus": 15, "crit_mult": 2.0, "price": 750, "rarity": "rare",
        "craft": {"ore": 8, "essence": 12}
    },

    # --- EPIC (фиолетовое, с боссов) ---
    "titans_blade": {
        "name": "Клинок Титана", "type": "weapon", "slot": "weapon",
        "emoji": "⚔️", "damage": 45, "hp_bonus": 30, "crit_mult": 1.8, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_staff": {
        "name": "Посох Архимага", "type": "weapon", "slot": "weapon",
        "emoji": "🔮", "damage": 40, "mana_bonus": 60, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_bow": {
        "name": "Фантомный лук", "type": "weapon", "slot": "weapon",
        "emoji": "👻", "damage": 38, "crit_bonus": 20, "crit_mult": 2.2, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # ШЛЕМЫ (helmet)
    # =====================

    # --- COMMON ---
    "leather_cap": {
        "name": "Кожаная шапка", "type": "armor", "slot": "helmet",
        "emoji": "🧢", "defense": 3, "price": 40, "rarity": "common"
    },
    "iron_helm": {
        "name": "Железный шлем", "type": "armor", "slot": "helmet",
        "emoji": "⛑️", "defense": 6, "hp_bonus": 10, "price": 100, "rarity": "common"
    },

    # --- RARE ---
    "steel_helm": {
        "name": "Стальной шлем", "type": "armor", "slot": "helmet",
        "emoji": "🪖", "defense": 10, "hp_bonus": 20, "price": 250, "rarity": "rare",
        "craft": {"ore": 8, "leather": 3}
    },
    "mage_hood": {
        "name": "Капюшон мага", "type": "armor", "slot": "helmet",
        "emoji": "🎭", "defense": 5, "mana_bonus": 25, "price": 230, "rarity": "rare",
        "craft": {"cloth": 10, "crystal": 3}
    },

    # --- EPIC ---
    "titan_helm": {
        "name": "Шлем Титана", "type": "armor", "slot": "helmet",
        "emoji": "👑", "defense": 15, "hp_bonus": 40, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_crown": {
        "name": "Корона Архимага", "type": "armor", "slot": "helmet",
        "emoji": "👑", "defense": 8, "mana_bonus": 50, "damage_bonus": 10, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_mask": {
        "name": "Маска Фантома", "type": "armor", "slot": "helmet",
        "emoji": "🎭", "defense": 10, "crit_bonus": 12, "dodge_bonus": 8, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # ПЛЕЧИ (shoulders)
    # =====================

    # --- COMMON ---
    "leather_pads": {
        "name": "Кожаные наплечники", "type": "armor", "slot": "shoulders",
        "emoji": "🦺", "defense": 2, "price": 35, "rarity": "common"
    },
    "iron_pauldrons": {
        "name": "Железные наплечи", "type": "armor", "slot": "shoulders",
        "emoji": "🛡️", "defense": 5, "price": 90, "rarity": "common"
    },

    # --- RARE ---
    "steel_pauldrons": {
        "name": "Стальные наплечи", "type": "armor", "slot": "shoulders",
        "emoji": "⚙️", "defense": 9, "hp_bonus": 15, "price": 220, "rarity": "rare",
        "craft": {"ore": 6, "leather": 4}
    },

    # --- EPIC ---
    "titan_shoulders": {
        "name": "Наплечи Титана", "type": "armor", "slot": "shoulders",
        "emoji": "💪", "defense": 14, "hp_bonus": 30, "damage_bonus": 5, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_mantle": {
        "name": "Оплечье Архимага", "type": "armor", "slot": "shoulders",
        "emoji": "✨", "defense": 7, "mana_bonus": 35, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_cape": {
        "name": "Накидка Фантома", "type": "armor", "slot": "shoulders",
        "emoji": "🌫️", "defense": 8, "dodge_bonus": 10, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # ГРУДЬ (chest)
    # =====================

    # --- COMMON ---
    "leather_vest": {
        "name": "Кожаный жилет", "type": "armor", "slot": "chest",
        "emoji": "🥋", "defense": 5, "price": 60, "rarity": "common"
    },
    "chainmail": {
        "name": "Кольчуга", "type": "armor", "slot": "chest",
        "emoji": "⛓️", "defense": 10, "price": 180, "rarity": "common"
    },
    # --- LEGACY (старые предметы для совместимости) ---
    "firearmor": {
        "name": "Огненная броня", "type": "armor", "slot": "chest",
        "emoji": "🔥", "defense": 15, "hp_bonus": 25, "fire_res": 30, "price": 400, "rarity": "rare"
    },

    # --- RARE ---
    "plate_armor": {
        "name": "Латный доспех", "type": "armor", "slot": "chest",
        "emoji": "🛡️", "defense": 18, "hp_bonus": 25, "block": 5, "price": 450, "rarity": "rare",
        "craft": {"ore": 15, "leather": 5}
    },
    "mage_robe": {
        "name": "Мантия мага", "type": "armor", "slot": "chest",
        "emoji": "🧥", "defense": 8, "mana_bonus": 40, "price": 400, "rarity": "rare",
        "craft": {"cloth": 15, "crystal": 5}
    },

    # --- EPIC ---
    "titan_plate": {
        "name": "Латы Титана", "type": "armor", "slot": "chest",
        "emoji": "🎽", "defense": 25, "hp_bonus": 60, "block": 10, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_robe": {
        "name": "Мантия Архимага", "type": "armor", "slot": "chest",
        "emoji": "🧥", "defense": 12, "mana_bonus": 70, "mana_regen": 5, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_cloak": {
        "name": "Плащ Фантома", "type": "armor", "slot": "chest",
        "emoji": "🌑", "defense": 15, "dodge_bonus": 15, "crit_bonus": 10, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # ПОЯС (belt)
    # =====================

    # --- COMMON ---
    "leather_belt": {
        "name": "Кожаный пояс", "type": "armor", "slot": "belt",
        "emoji": "🎗️", "defense": 2, "price": 30, "rarity": "common"
    },
    "iron_belt": {
        "name": "Железный пояс", "type": "armor", "slot": "belt",
        "emoji": "⚙️", "defense": 4, "hp_bonus": 10, "price": 80, "rarity": "common"
    },

    # --- RARE ---
    "steel_belt": {
        "name": "Стальной пояс", "type": "armor", "slot": "belt",
        "emoji": "🔗", "defense": 7, "hp_bonus": 20, "price": 200, "rarity": "rare",
        "craft": {"ore": 5, "leather": 3}
    },

    # =====================
    # ПЕРЧАТКИ (gloves)
    # =====================

    # --- COMMON ---
    "leather_gloves": {
        "name": "Кожаные перчатки", "type": "armor", "slot": "gloves",
        "emoji": "🧤", "defense": 2, "price": 35, "rarity": "common"
    },
    "iron_gauntlets": {
        "name": "Железные рукавицы", "type": "armor", "slot": "gloves",
        "emoji": "🥊", "defense": 4, "damage_bonus": 3, "price": 95, "rarity": "common"
    },

    # --- RARE ---
    "steel_gauntlets": {
        "name": "Стальные латные перчатки", "type": "armor", "slot": "gloves",
        "emoji": "🤜", "defense": 8, "damage_bonus": 8, "price": 240, "rarity": "rare",
        "craft": {"ore": 6, "leather": 4}
    },
    "mage_gloves": {
        "name": "Перчатки чародея", "type": "armor", "slot": "gloves",
        "emoji": "🪬", "defense": 4, "mana_bonus": 20, "crit_bonus": 5, "price": 220, "rarity": "rare",
        "craft": {"cloth": 8, "crystal": 3}
    },

    # --- EPIC ---
    "titan_gauntlets": {
        "name": "Рукавицы Титана", "type": "armor", "slot": "gloves",
        "emoji": "🤜", "defense": 12, "damage_bonus": 15, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_gloves": {
        "name": "Перчатки Архимага", "type": "armor", "slot": "gloves",
        "emoji": "✋", "defense": 6, "mana_bonus": 30, "damage_bonus": 12, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_gloves": {
        "name": "Перчатки Фантома", "type": "armor", "slot": "gloves",
        "emoji": "🧤", "defense": 8, "crit_bonus": 18, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # ПОНОЖИ (leggings)
    # =====================

    # --- COMMON ---
    "leather_pants": {
        "name": "Кожаные штаны", "type": "armor", "slot": "leggings",
        "emoji": "👖", "defense": 3, "price": 45, "rarity": "common"
    },
    "chainmail_legs": {
        "name": "Кольчужные поножи", "type": "armor", "slot": "leggings",
        "emoji": "⛓️", "defense": 7, "price": 130, "rarity": "common"
    },

    # --- RARE ---
    "plate_legs": {
        "name": "Латные поножи", "type": "armor", "slot": "leggings",
        "emoji": "🦿", "defense": 12, "hp_bonus": 20, "price": 320, "rarity": "rare",
        "craft": {"ore": 10, "leather": 4}
    },

    # =====================
    # САПОГИ (boots)
    # =====================

    # --- COMMON ---
    "leather_boots": {
        "name": "Кожаные сапоги", "type": "armor", "slot": "boots",
        "emoji": "👢", "defense": 2, "price": 40, "rarity": "common"
    },
    "iron_boots": {
        "name": "Железные сапоги", "type": "armor", "slot": "boots",
        "emoji": "🥾", "defense": 5, "price": 110, "rarity": "common"
    },

    # --- RARE ---
    "steel_boots": {
        "name": "Стальные сапоги", "type": "armor", "slot": "boots",
        "emoji": "🦶", "defense": 9, "hp_bonus": 15, "price": 270, "rarity": "rare",
        "craft": {"ore": 7, "leather": 5}
    },
    "swift_boots": {
        "name": "Быстрые сапоги", "type": "armor", "slot": "boots",
        "emoji": "💨", "defense": 5, "dodge_bonus": 8, "price": 300, "rarity": "rare",
        "craft": {"leather": 10, "herb": 5}
    },

    # --- EPIC ---
    "titan_boots": {
        "name": "Сапоги Титана", "type": "armor", "slot": "boots",
        "emoji": "👢", "defense": 14, "hp_bonus": 35, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_boots": {
        "name": "Сапоги Архимага", "type": "armor", "slot": "boots",
        "emoji": "👟", "defense": 7, "mana_bonus": 25, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_boots": {
        "name": "Сапоги Фантома", "type": "armor", "slot": "boots",
        "emoji": "👣", "defense": 9, "dodge_bonus": 12, "crit_bonus": 5, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # КОЛЬЦА (ring)
    # =====================

    # --- COMMON ---
    "copper_ring": {
        "name": "Медное кольцо", "type": "accessory", "slot": "ring",
        "emoji": "💍", "crit_bonus": 3, "price": 50, "rarity": "common"
    },
    "iron_ring": {
        "name": "Железное кольцо", "type": "accessory", "slot": "ring",
        "emoji": "💍", "damage_bonus": 5, "price": 80, "rarity": "common"
    },
    # --- LEGACY (старые предметы для совместимости) ---
    "berserkercharm": {
        "name": "Амулет берсерка", "type": "accessory", "slot": "ring",
        "emoji": "💢", "damage_bonus": 10, "berserker": True, "price": 350, "rarity": "rare"
    },

    # --- RARE ---
    "lucky_ring": {
        "name": "Кольцо удачи", "type": "accessory", "slot": "ring",
        "emoji": "🍀", "crit_bonus": 12, "price": 400, "rarity": "rare",
        "craft": {"crystal": 5, "essence": 3}
    },
    "vampire_ring": {
        "name": "Кольцо вампира", "type": "accessory", "slot": "ring",
        "emoji": "🩸", "lifesteal": 0.1, "price": 600, "rarity": "rare",
        "craft": {"essence": 10, "demon_soul": 2}
    },
    "berserker_ring": {
        "name": "Кольцо берсерка", "type": "accessory", "slot": "ring",
        "emoji": "🔥", "damage_bonus": 12, "berserker": True, "price": 550, "rarity": "rare",
        "craft": {"ore": 8, "demon_soul": 3}
    },

    # --- EPIC ---
    "titan_ring": {
        "name": "Кольцо Титана", "type": "accessory", "slot": "ring",
        "emoji": "💍", "hp_bonus": 50, "damage_bonus": 10, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_ring": {
        "name": "Кольцо Архимага", "type": "accessory", "slot": "ring",
        "emoji": "💍", "mana_bonus": 50, "damage_bonus": 8, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_ring": {
        "name": "Кольцо Фантома", "type": "accessory", "slot": "ring",
        "emoji": "💍", "crit_bonus": 15, "dodge_bonus": 10, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },

    # =====================
    # ОЖЕРЕЛЬЯ (necklace)
    # =====================

    # --- COMMON ---
    "bone_necklace": {
        "name": "Костяное ожерелье", "type": "accessory", "slot": "necklace",
        "emoji": "📿", "hp_bonus": 15, "price": 60, "rarity": "common"
    },
    "silver_pendant": {
        "name": "Серебряный кулон", "type": "accessory", "slot": "necklace",
        "emoji": "🔗", "defense_bonus": 5, "price": 90, "rarity": "common"
    },

    # --- RARE ---
    "power_amulet": {
        "name": "Амулет силы", "type": "accessory", "slot": "necklace",
        "emoji": "📿", "damage_bonus": 15, "price": 450, "rarity": "rare",
        "craft": {"crystal": 5, "ore": 5}
    },
    "life_pendant": {
        "name": "Кулон жизни", "type": "accessory", "slot": "necklace",
        "emoji": "💚", "hp_bonus": 60, "price": 500, "rarity": "rare",
        "craft": {"herb": 15, "crystal": 3}
    },
    "mana_crystal_necklace": {
        "name": "Ожерелье маны", "type": "accessory", "slot": "necklace",
        "emoji": "💎", "mana_bonus": 50, "price": 480, "rarity": "rare",
        "craft": {"crystal": 8, "essence": 5}
    },
    "shadow_medallion": {
        "name": "Медальон теней", "type": "accessory", "slot": "necklace",
        "emoji": "🌑", "dodge_bonus": 15, "crit_bonus": 8, "price": 700, "rarity": "rare",
        "craft": {"essence": 12, "demon_soul": 3}
    },

    # --- EPIC ---
    "titan_amulet": {
        "name": "Амулет Титана", "type": "accessory", "slot": "necklace",
        "emoji": "🏅", "hp_bonus": 40, "defense_bonus": 10, "price": 0, "rarity": "epic",
        "set": "titan", "boss_drop": "forest"
    },
    "archmage_pendant": {
        "name": "Кулон Архимага", "type": "accessory", "slot": "necklace",
        "emoji": "🔮", "mana_bonus": 60, "damage_bonus": 15, "price": 0, "rarity": "epic",
        "set": "archmage", "boss_drop": "mines"
    },
    "phantom_necklace": {
        "name": "Ожерелье Фантома", "type": "accessory", "slot": "necklace",
        "emoji": "👻", "crit_bonus": 20, "lifesteal": 0.08, "price": 0, "rarity": "epic",
        "set": "phantom", "boss_drop": "crypt"
    },
}

# =====================
# ЭПИЧЕСКИЕ СЕТЫ
# =====================
EPIC_SETS = {
    "titan": {
        "name": "Гнев Титана",
        "emoji": "⚔️",
        "pieces": ["titans_blade", "titan_helm", "titan_shoulders", "titan_plate",
                   "titan_gauntlets", "titan_boots", "titan_ring", "titan_amulet"],
        "bonus_2": "+15% HP",
        "bonus_2_stats": {"hp": 30},
        "bonus_4": "+20% урона, при HP <30% урон +50%",
        "bonus_4_stats": {"hp": 50, "damage": 15},
        "boss": "forest"
    },
    "archmage": {
        "name": "Покров Архимага",
        "emoji": "🔮",
        "pieces": ["archmage_staff", "archmage_crown", "archmage_mantle", "archmage_robe",
                   "archmage_gloves", "archmage_boots", "archmage_ring", "archmage_pendant"],
        "bonus_2": "+25% маны",
        "bonus_2_stats": {"mana": 40},
        "bonus_4": "Скиллы стоят на 30% меньше маны",
        "bonus_4_stats": {"mana": 80, "damage": 10},
        "boss": "mines"
    },
    "phantom": {
        "name": "Тень Фантома",
        "emoji": "👻",
        "pieces": ["phantom_bow", "phantom_mask", "phantom_cape", "phantom_cloak",
                   "phantom_gloves", "phantom_boots", "phantom_ring", "phantom_necklace"],
        "bonus_2": "+20% шанс крита",
        "bonus_2_stats": {"crit": 15},
        "bonus_4": "Криты наносят +75% урона и восстанавливают HP",
        "bonus_4_stats": {"crit": 25, "dodge": 10},
        "boss": "crypt"
    }
}

# =====================
# ЛЕГЕНДАРНОЕ ОРУЖИЕ (квестовое)
# =====================
LEGENDARY_WEAPONS = {
    "excalibur": {
        "name": "Экскалибур",
        "type": "weapon",
        "slot": "weapon",
        "emoji": "⚔️",
        "damage": 80,
        "hp_bonus": 50,
        "crit_bonus": 15,
        "crit_mult": 2.0,
        "lifesteal": 0.15,
        "rarity": "legendary",
        "class": "warrior",
        "quest_chain": "warrior_legend",
        "description": "Легендарный меч, выкованный в пламени древних драконов"
    },
    "staff_of_eternity": {
        "name": "Посох Вечности",
        "type": "weapon",
        "slot": "weapon",
        "emoji": "🌟",
        "damage": 70,
        "mana_bonus": 100,
        "crit_bonus": 20,
        "crit_mult": 1.8,
        "mana_regen": 10,
        "rarity": "legendary",
        "class": "mage",
        "quest_chain": "mage_legend",
        "description": "Древний посох, хранящий мудрость тысячелетий"
    },
    "bow_of_the_wind": {
        "name": "Лук Ветра",
        "type": "weapon",
        "slot": "weapon",
        "emoji": "🌪️",
        "damage": 65,
        "crit_bonus": 30,
        "crit_mult": 2.5,
        "dodge_bonus": 15,
        "double_hit": 10,
        "rarity": "legendary",
        "class": "archer",
        "quest_chain": "archer_legend",
        "description": "Лук, стреляющий со скоростью ветра"
    }
}

# Добавим легендарки в ITEMS для совместимости
ITEMS.update(LEGENDARY_WEAPONS)
