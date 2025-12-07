"""
Подземелья и враги
"""

DUNGEONS = {
    "forest": {
        "name": "🌲 Проклятый лес",
        "emoji": "🌲",
        "min_level": 1,
        "floors": 10,
        "boss": "Древний Энт",
        "boss_emoji": "🌳",
        "description": "Тёмный лес, полный ядовитых тварей",
        "mechanic": "poison",
        "mechanic_desc": "Враги накладывают яд",
        "enemies": ["wolf", "spirit", "dryad", "dark_elf"],
        "boss_hp": 300,
        "boss_damage": 25,
        "exp_mult": 1.0,
        "gold_mult": 1.0,
        "drop_resource": "herb"
    },
    "mines": {
        "name": "⛏️ Забытые шахты",
        "emoji": "⛏️",
        "min_level": 5,
        "floors": 15,
        "boss": "Король гоблинов",
        "boss_emoji": "👑",
        "description": "Древние шахты, захваченные гоблинами",
        "mechanic": "collapse",
        "mechanic_desc": "Обвалы каждые 30 сек",
        "enemies": ["goblin", "troll", "golem", "ghost_miner"],
        "boss_hp": 500,
        "boss_damage": 35,
        "exp_mult": 1.5,
        "gold_mult": 1.5,
        "drop_resource": "ore"
    },
    "crypt": {
        "name": "🏚️ Склеп Проклятых",
        "emoji": "🏚️",
        "min_level": 10,
        "floors": 20,
        "boss": "Лич-Некромант",
        "boss_emoji": "💀",
        "description": "Проклятый склеп с восставшими мертвецами",
        "mechanic": "undead",
        "mechanic_desc": "Враги воскресают 1 раз с 30% HP",
        "enemies": ["skeleton", "zombie", "vampire", "banshee", "bone_knight"],
        "boss_hp": 700,
        "boss_damage": 45,
        "exp_mult": 2.0,
        "gold_mult": 2.0,
        "drop_resource": "essence"
    },
    "abyss": {
        "name": "🌋 Огненная бездна",
        "emoji": "🌋",
        "min_level": 15,
        "floors": 25,
        "boss": "Инфернальный Демон",
        "boss_emoji": "😈",
        "description": "Пылающие глубины ада",
        "mechanic": "heat",
        "mechanic_desc": "Постоянный урон 2 HP/сек",
        "enemies": ["fire_elemental", "demon", "hellhound", "fallen_angel"],
        "boss_hp": 1000,
        "boss_damage": 60,
        "exp_mult": 3.0,
        "gold_mult": 3.0,
        "drop_resource": "demon_soul"
    },
    "chaos": {
        "name": "🌑 Бездна Хаоса",
        "emoji": "🌑",
        "min_level": 20,
        "floors": 30,
        "boss": "Владыка Хаоса",
        "boss_emoji": "👁️",
        "description": "Царство чистого хаоса. Финальное испытание.",
        "mechanic": "chaos",
        "mechanic_desc": "Случайные эффекты",
        "enemies": ["chaos_spawn", "twisted", "shadow", "ancient_horror"],
        "boss_hp": 1500,
        "boss_damage": 80,
        "exp_mult": 5.0,
        "gold_mult": 5.0,
        "drop_resource": "chaos_essence",
        "legendary_drop": True
    }
}

ENEMIES = {
    # Проклятый лес
    "wolf": {"name": "Волк", "emoji": "🐺", "hp": 40, "damage": 8, "exp": 10, "gold": 15},
    "spirit": {"name": "Лесной дух", "emoji": "👻", "hp": 30, "damage": 12, "exp": 12, "gold": 20},
    "dryad": {"name": "Отравленная дриада", "emoji": "🧚", "hp": 50, "damage": 10, "exp": 15, "gold": 25, "poison": 3},
    "dark_elf": {"name": "Тёмный эльф", "emoji": "🧝", "hp": 60, "damage": 15, "exp": 20, "gold": 30},

    # Забытые шахты
    "goblin": {"name": "Гоблин", "emoji": "👺", "hp": 50, "damage": 12, "exp": 18, "gold": 25},
    "troll": {"name": "Пещерный тролль", "emoji": "👹", "hp": 100, "damage": 20, "exp": 30, "gold": 40},
    "golem": {"name": "Каменный голем", "emoji": "🗿", "hp": 150, "damage": 15, "exp": 35, "gold": 50},
    "ghost_miner": {"name": "Призрак шахтёра", "emoji": "⛏️", "hp": 60, "damage": 18, "exp": 25, "gold": 35},

    # Склеп Проклятых
    "skeleton": {"name": "Скелет", "emoji": "💀", "hp": 70, "damage": 20, "exp": 35, "gold": 45},
    "zombie": {"name": "Зомби", "emoji": "🧟", "hp": 100, "damage": 15, "exp": 30, "gold": 40},
    "vampire": {"name": "Вампир", "emoji": "🧛", "hp": 90, "damage": 25, "exp": 45, "gold": 60, "lifesteal": 0.2},
    "banshee": {"name": "Банши", "emoji": "👻", "hp": 60, "damage": 35, "exp": 50, "gold": 55},
    "bone_knight": {"name": "Костяной рыцарь", "emoji": "🦴", "hp": 130, "damage": 28, "exp": 55, "gold": 70},

    # Огненная бездна
    "fire_elemental": {"name": "Огненный элементаль", "emoji": "🔥", "hp": 100, "damage": 35, "exp": 60, "gold": 80, "burn": 5},
    "demon": {"name": "Демон", "emoji": "😈", "hp": 150, "damage": 40, "exp": 75, "gold": 100},
    "hellhound": {"name": "Адская гончая", "emoji": "🐕", "hp": 120, "damage": 45, "exp": 70, "gold": 90},
    "fallen_angel": {"name": "Падший ангел", "emoji": "😇", "hp": 140, "damage": 50, "exp": 90, "gold": 120},

    # Бездна Хаоса
    "chaos_spawn": {"name": "Порождение хаоса", "emoji": "🌀", "hp": 180, "damage": 50, "exp": 100, "gold": 150},
    "twisted": {"name": "Искажённый", "emoji": "🎭", "hp": 160, "damage": 55, "exp": 110, "gold": 160},
    "shadow": {"name": "Тень", "emoji": "🌑", "hp": 140, "damage": 60, "exp": 120, "gold": 170},
    "ancient_horror": {"name": "Древний ужас", "emoji": "👁️", "hp": 220, "damage": 65, "exp": 150, "gold": 200}
}
