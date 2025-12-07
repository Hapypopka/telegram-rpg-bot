"""
Тени Подземелий - RPG Telegram Bot
Часть 1: База (классы, сохранение, главное меню)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import random
import json
import os
from datetime import datetime, timedelta

# ============ СОХРАНЕНИЕ ============
DATA_FILE = "players_data.json"
players = {}

def save_data():
    """Сохраняет всех игроков в JSON файл"""
    data = {}
    for uid, player in players.items():
        data[str(uid)] = player.to_dict()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    """Загружает игроков из JSON файла"""
    global players
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for uid, pdata in data.items():
                    players[int(uid)] = Player.from_dict(pdata)
            print(f"Загружено {len(players)} игроков")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

# ============ КЛАССЫ ПЕРСОНАЖЕЙ ============
CLASSES = {
    "warrior": {
        "name": "⚔️ Воин",
        "emoji": "⚔️",
        "description": "Высокое HP и защита. Мощные физические атаки.",
        "base_hp": 200,
        "base_mana": 40,
        "base_damage": 12,
        "base_defense": 15,
        "base_crit": 5,
        "passive": "Стойкость - получает на 10% меньше урона",
        "skills": {
            "power_strike": {
                "name": "Мощный удар",
                "emoji": "💥",
                "damage_mult": 2.0,
                "mana": 8,
                "cooldown": 2,
                "description": "Наносит двойной урон"
            },
            "shield": {
                "name": "Щит веры",
                "emoji": "🛡️",
                "block": True,
                "mana": 15,
                "cooldown": 10,
                "description": "Блокирует следующую атаку"
            },
            "charge": {
                "name": "Рывок",
                "emoji": "🏃",
                "damage_mult": 1.5,
                "stun": 2,
                "mana": 12,
                "cooldown": 6,
                "description": "Урон + оглушение 2с"
            },
            "whirlwind": {
                "name": "Вихрь стали",
                "emoji": "🌀",
                "damage_mult": 3.0,
                "mana": 25,
                "cooldown": 15,
                "description": "УЛЬТА: Тройной урон",
                "ultimate": True
            }
        }
    },
    "mage": {
        "name": "🔮 Маг",
        "emoji": "🔮",
        "description": "Высокий урон магией. Много маны, мало HP.",
        "base_hp": 100,
        "base_mana": 150,
        "base_damage": 20,
        "base_defense": 5,
        "base_crit": 10,
        "passive": "Медитация - +5 маны каждые 3 сек в бою",
        "skills": {
            "ice_arrow": {
                "name": "Ледяная стрела",
                "emoji": "❄️",
                "damage_mult": 1.8,
                "slow": 2,
                "mana": 10,
                "cooldown": 2,
                "description": "Урон + замедление"
            },
            "fire_pillar": {
                "name": "Огненный столп",
                "emoji": "🔥",
                "damage_mult": 2.5,
                "mana": 20,
                "cooldown": 4,
                "description": "Мощный огненный урон"
            },
            "barrier": {
                "name": "Магический барьер",
                "emoji": "🔮",
                "absorb": 50,
                "mana": 30,
                "cooldown": 12,
                "description": "Поглощает 50 урона"
            },
            "armageddon": {
                "name": "Армагеддон",
                "emoji": "☄️",
                "damage_mult": 5.0,
                "mana": 60,
                "cooldown": 20,
                "description": "УЛЬТА: x5 урон",
                "ultimate": True
            }
        }
    },
    "archer": {
        "name": "🏹 Лучник",
        "emoji": "🏹",
        "description": "Высокий шанс крита. Быстрые атаки.",
        "base_hp": 130,
        "base_mana": 80,
        "base_damage": 18,
        "base_defense": 8,
        "base_crit": 20,
        "passive": "Острый глаз - +15% шанс крита",
        "skills": {
            "double_shot": {
                "name": "Двойной выстрел",
                "emoji": "🎯",
                "damage_mult": 1.2,
                "hits": 2,
                "mana": 8,
                "cooldown": 2,
                "description": "2 удара по x1.2"
            },
            "poison_arrow": {
                "name": "Отравленная стрела",
                "emoji": "☠️",
                "damage_mult": 1.0,
                "poison": 5,
                "poison_duration": 4,
                "mana": 12,
                "cooldown": 5,
                "description": "Яд 5 урона/сек 4с"
            },
            "dodge": {
                "name": "Уклонение",
                "emoji": "💨",
                "dodge": True,
                "mana": 10,
                "cooldown": 8,
                "description": "Уворот от следующей атаки"
            },
            "arrow_rain": {
                "name": "Град стрел",
                "emoji": "🌧️",
                "damage_mult": 1.5,
                "hits": 5,
                "mana": 40,
                "cooldown": 18,
                "description": "УЛЬТА: 5 ударов x1.5",
                "ultimate": True
            }
        }
    },
    "rogue": {
        "name": "🗡️ Разбойник",
        "emoji": "🗡️",
        "description": "Огромный крит. Первый удар из тени.",
        "base_hp": 110,
        "base_mana": 60,
        "base_damage": 22,
        "base_defense": 6,
        "base_crit": 25,
        "passive": "Из тени - первая атака в бою x2 урон",
        "skills": {
            "backstab": {
                "name": "Удар в спину",
                "emoji": "🔪",
                "damage_mult": 2.5,
                "mana": 10,
                "cooldown": 3,
                "description": "x2.5 урон"
            },
            "fan_of_knives": {
                "name": "Веер ножей",
                "emoji": "🌀",
                "damage_mult": 0.8,
                "hits": 3,
                "mana": 15,
                "cooldown": 4,
                "description": "3 удара по x0.8"
            },
            "vanish": {
                "name": "Исчезновение",
                "emoji": "👻",
                "invisibility": 3,
                "mana": 20,
                "cooldown": 15,
                "description": "Невидимость 3с"
            },
            "dance_of_blades": {
                "name": "Танец клинков",
                "emoji": "⚔️",
                "damage_mult": 6.0,
                "mana": 50,
                "cooldown": 20,
                "description": "УЛЬТА: x6 урон",
                "ultimate": True
            }
        }
    },
    "paladin": {
        "name": "🛡️ Паладин",
        "emoji": "🛡️",
        "description": "Танк с лечением. Самовосстановление.",
        "base_hp": 180,
        "base_mana": 70,
        "base_damage": 14,
        "base_defense": 12,
        "base_crit": 8,
        "passive": "Святость - хил 3% HP каждые 5 сек",
        "skills": {
            "holy_strike": {
                "name": "Святой удар",
                "emoji": "✨",
                "damage_mult": 1.8,
                "lifesteal": 0.1,
                "mana": 12,
                "cooldown": 3,
                "description": "Урон + хил 10% от урона"
            },
            "cleanse": {
                "name": "Очищение",
                "emoji": "💚",
                "heal": 30,
                "cleanse": True,
                "mana": 20,
                "cooldown": 10,
                "description": "Снимает дебаффы + 30 HP"
            },
            "divine_shield": {
                "name": "Божественный щит",
                "emoji": "👼",
                "invulnerable": 2,
                "mana": 35,
                "cooldown": 20,
                "description": "Неуязвимость 2с"
            },
            "wrath_of_heaven": {
                "name": "Гнев небес",
                "emoji": "⚡",
                "damage_mult": 4.0,
                "heal": 50,
                "mana": 55,
                "cooldown": 22,
                "description": "УЛЬТА: x4 урон + 50 HP",
                "ultimate": True
            }
        }
    }
}

# ============ ПОДЗЕМЕЛЬЯ ============
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

# ============ ВРАГИ ============
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

# ============ ПРЕДМЕТЫ ============
ITEMS = {
    # Ресурсы
    "herb": {"name": "Лесная трава", "type": "resource", "emoji": "🌿", "price": 5},
    "ore": {"name": "Железная руда", "type": "resource", "emoji": "�ite", "price": 10},
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

# ============ ЛЕГЕНДАРНЫЕ СЕТЫ ============
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

# ============ ДОСТИЖЕНИЯ ============
ACHIEVEMENTS = {
    "first_blood": {"name": "Первая кровь", "desc": "Убей первого врага", "emoji": "🩸"},
    "slayer_100": {"name": "Истребитель", "desc": "Убей 100 врагов", "emoji": "⚔️"},
    "slayer_1000": {"name": "Геноцид", "desc": "Убей 1000 врагов", "emoji": "💀"},
    "boss_hunter": {"name": "Охотник на боссов", "desc": "Убей 5 боссов", "emoji": "👑"},
    "boss_slayer": {"name": "Убийца боссов", "desc": "Убей 20 боссов", "emoji": "🏆"},
    "explorer": {"name": "Исследователь", "desc": "Пройди все 5 подземелий", "emoji": "🗺️"},
    "conqueror": {"name": "Покоритель", "desc": "Победи всех 5 боссов", "emoji": "👑"},
    "chaos_master": {"name": "Мастер бездны", "desc": "Пройди 30 этажей Бездны Хаоса", "emoji": "🌑"},
    "legend": {"name": "Легенда", "desc": "Получи полный легендарный сет", "emoji": "✨"},
    "veteran": {"name": "Ветеран", "desc": "Достигни 10 уровня", "emoji": "⭐"},
    "master": {"name": "Мастер", "desc": "Достигни 20 уровня", "emoji": "🌟"},
    "grandmaster": {"name": "Грандмастер", "desc": "Достигни 30 уровня", "emoji": "💫"},
    "rich": {"name": "Зажиточный", "desc": "Накопи 1000 золота", "emoji": "💰"},
    "wealthy": {"name": "Богач", "desc": "Накопи 10000 золота", "emoji": "💎"},
    "magnate": {"name": "Магнат", "desc": "Накопи 100000 золота", "emoji": "👑"},
    "survivor": {"name": "Выживший", "desc": "Победи с 1 HP", "emoji": "💪"},
    "perfect": {"name": "Совершенство", "desc": "Пройди подземелье без урона", "emoji": "🎯"},
    "speedrun": {"name": "Скоростной", "desc": "Убей босса за 30 секунд", "emoji": "⚡"},
    "collector": {"name": "Коллекционер", "desc": "Собери 50 уникальных предметов", "emoji": "📦"},
    "quester": {"name": "Искатель", "desc": "Выполни 50 квестов", "emoji": "📜"}
}

# ============ ЕЖЕДНЕВНЫЕ НАГРАДЫ ============
DAILY_REWARDS = [
    {"day": 1, "gold": 50, "items": []},
    {"day": 2, "gold": 0, "items": [("hp_potion_small", 3)]},
    {"day": 3, "gold": 100, "items": []},
    {"day": 4, "gold": 50, "items": [("mana_potion_small", 2)]},
    {"day": 5, "gold": 200, "items": []},
    {"day": 6, "gold": 100, "items": [("hp_potion_medium", 2)]},
    {"day": 7, "gold": 500, "items": [("elixir_power", 1), ("elixir_defense", 1)]}
]

# ============ КВЕСТЫ ============
QUESTS = {
    # Ежедневные квесты
    "daily_kills_10": {
        "name": "Охота на монстров",
        "type": "daily",
        "desc": "Убей 10 врагов",
        "emoji": "⚔️",
        "target": 10,
        "stat": "kills",
        "rewards": {"gold": 100, "exp": 50}
    },
    "daily_dungeons_3": {
        "name": "Исследователь",
        "type": "daily",
        "desc": "Пройди 3 этажа подземелий",
        "emoji": "🏰",
        "target": 3,
        "stat": "floors",
        "rewards": {"gold": 150, "exp": 75}
    },
    "daily_crits_5": {
        "name": "Точные удары",
        "type": "daily",
        "desc": "Нанеси 5 критических ударов",
        "emoji": "🎯",
        "target": 5,
        "stat": "crits",
        "rewards": {"gold": 80, "exp": 40}
    },
    "daily_boss_1": {
        "name": "Охотник на боссов",
        "type": "daily",
        "desc": "Убей 1 босса",
        "emoji": "👑",
        "target": 1,
        "stat": "boss_kills",
        "rewards": {"gold": 200, "exp": 100}
    },

    # Еженедельные квесты
    "weekly_kills_100": {
        "name": "Истребитель",
        "type": "weekly",
        "desc": "Убей 100 врагов",
        "emoji": "💀",
        "target": 100,
        "stat": "kills",
        "rewards": {"gold": 500, "exp": 250, "item": "hp_potion_large"}
    },
    "weekly_boss_5": {
        "name": "Убийца боссов",
        "type": "weekly",
        "desc": "Убей 5 боссов",
        "emoji": "👹",
        "target": 5,
        "stat": "boss_kills",
        "rewards": {"gold": 800, "exp": 400, "item": "elixir_power"}
    },
    "weekly_gold_1000": {
        "name": "Золотоискатель",
        "type": "weekly",
        "desc": "Заработай 1000 золота",
        "emoji": "💰",
        "target": 1000,
        "stat": "gold_earned",
        "rewards": {"gold": 300, "exp": 150, "item": "lucky_ring"}
    },

    # Сюжетные квесты (уникальные)
    "story_forest": {
        "name": "Тень леса",
        "type": "story",
        "desc": "Победи Древнего Энта",
        "emoji": "🌲",
        "target": "forest_boss",
        "rewards": {"gold": 500, "exp": 300, "title": "Хранитель леса"}
    },
    "story_mines": {
        "name": "Король горы",
        "type": "story",
        "desc": "Победи Короля гоблинов",
        "emoji": "⛏️",
        "target": "mines_boss",
        "rewards": {"gold": 800, "exp": 500, "title": "Повелитель шахт"}
    },
    "story_crypt": {
        "name": "Упокоитель",
        "type": "story",
        "desc": "Победи Лича-Некроманта",
        "emoji": "🏚️",
        "target": "crypt_boss",
        "rewards": {"gold": 1200, "exp": 800, "title": "Изгоняющий нежить"}
    },
    "story_abyss": {
        "name": "Пламя ада",
        "type": "story",
        "desc": "Победи Инфернального Демона",
        "emoji": "🌋",
        "target": "abyss_boss",
        "rewards": {"gold": 2000, "exp": 1200, "title": "Покоритель бездны"}
    },
    "story_chaos": {
        "name": "Конец хаоса",
        "type": "story",
        "desc": "Победи Владыку Хаоса",
        "emoji": "🌑",
        "target": "chaos_boss",
        "rewards": {"gold": 5000, "exp": 3000, "title": "Властелин теней"}
    }
}

# ============ ЕДА ТАВЕРНЫ ============
TAVERN_FOOD = {
    "bread": {
        "name": "Хлеб с сыром",
        "emoji": "🍞",
        "price": 20,
        "heal": 30,
        "desc": "Простая еда. Восстанавливает 30 HP"
    },
    "soup": {
        "name": "Мясная похлёбка",
        "emoji": "🍲",
        "price": 50,
        "heal": 80,
        "buff": {"hp": 20, "duration": 300},
        "desc": "Сытная еда. +80 HP, +20 макс HP на 5 мин"
    },
    "steak": {
        "name": "Жареный стейк",
        "emoji": "🥩",
        "price": 100,
        "heal": 150,
        "buff": {"damage": 5, "duration": 300},
        "desc": "Мясо придаёт силы. +150 HP, +5 урона на 5 мин"
    },
    "feast": {
        "name": "Пир героя",
        "emoji": "🍖",
        "price": 250,
        "heal_full": True,
        "buff": {"hp": 50, "damage": 10, "defense": 5, "duration": 600},
        "desc": "Королевская трапеза. Полный хил + бафы на 10 мин"
    },
    "ale": {
        "name": "Эль",
        "emoji": "🍺",
        "price": 30,
        "buff": {"crit": 10, "defense": -3, "duration": 300},
        "desc": "Жидкая храбрость. +10% крита, -3 защиты на 5 мин"
    },
    "elven_wine": {
        "name": "Эльфийское вино",
        "emoji": "🍷",
        "price": 150,
        "mana_full": True,
        "buff": {"mana_regen": 5, "duration": 300},
        "desc": "Редкий напиток. Полная мана + реген на 5 мин"
    }
}

# ============ НАЁМНИКИ ============
MERCENARIES = {
    "guard": {
        "name": "Стражник",
        "emoji": "🛡️",
        "price": 200,
        "duration": 3,  # 3 боя
        "bonus": {"defense": 10},
        "desc": "Защищает тебя. +10 защиты на 3 боя"
    },
    "archer_merc": {
        "name": "Наёмный лучник",
        "emoji": "🏹",
        "price": 300,
        "duration": 3,
        "bonus": {"damage": 8, "crit": 5},
        "desc": "Метко стреляет. +8 урона, +5% крита на 3 боя"
    },
    "healer": {
        "name": "Целитель",
        "emoji": "💚",
        "price": 400,
        "duration": 3,
        "bonus": {"heal_per_turn": 10},
        "desc": "Лечит раны. +10 HP каждый ход на 3 боя"
    },
    "berserker": {
        "name": "Берсерк",
        "emoji": "🪓",
        "price": 500,
        "duration": 2,
        "bonus": {"damage": 20, "defense": -5},
        "desc": "Безумная ярость. +20 урона, -5 защиты на 2 боя"
    },
    "mage_merc": {
        "name": "Боевой маг",
        "emoji": "🔮",
        "price": 600,
        "duration": 2,
        "bonus": {"damage": 15, "mana_regen": 10},
        "desc": "Владеет магией. +15 урона, +10 маны/ход на 2 боя"
    }
}

# ============ КУЗНЕЦ ============
BLACKSMITH_UPGRADES = {
    "sharpen": {
        "name": "Заточка",
        "emoji": "🔪",
        "cost": 100,
        "resource": ("ore", 5),
        "bonus": {"damage": 3},
        "max_level": 5,
        "desc": "+3 урона к оружию"
    },
    "reinforce": {
        "name": "Укрепление",
        "emoji": "🛡️",
        "cost": 100,
        "resource": ("ore", 5),
        "bonus": {"defense": 3},
        "max_level": 5,
        "desc": "+3 защиты к броне"
    },
    "enchant_fire": {
        "name": "Огненное зачарование",
        "emoji": "🔥",
        "cost": 500,
        "resource": ("demon_soul", 3),
        "bonus": {"burn": 5},
        "max_level": 1,
        "desc": "Оружие поджигает врагов"
    },
    "enchant_ice": {
        "name": "Ледяное зачарование",
        "emoji": "❄️",
        "cost": 500,
        "resource": ("essence", 5),
        "bonus": {"slow": True},
        "max_level": 1,
        "desc": "Оружие замедляет врагов"
    },
    "enchant_life": {
        "name": "Зачарование жизни",
        "emoji": "💚",
        "cost": 800,
        "resource": ("chaos_essence", 2),
        "bonus": {"lifesteal": 0.1},
        "max_level": 1,
        "desc": "Вампиризм 10%"
    }
}

# ============ АЛХИМИК ============
ALCHEMY_RECIPES = {
    "hp_potion_medium": {
        "name": "Среднее зелье HP",
        "emoji": "💖",
        "cost": 30,
        "ingredients": {"herb": 5},
        "result": ("hp_potion_medium", 1),
        "desc": "Создать зелье на 120 HP"
    },
    "hp_potion_large": {
        "name": "Большое зелье HP",
        "emoji": "💗",
        "cost": 60,
        "ingredients": {"herb": 10, "essence": 2},
        "result": ("hp_potion_large", 1),
        "desc": "Создать зелье на 250 HP"
    },
    "mana_potion_medium": {
        "name": "Среднее зелье маны",
        "emoji": "💎",
        "cost": 25,
        "ingredients": {"herb": 3, "essence": 1},
        "result": ("mana_potion_medium", 1),
        "desc": "Создать зелье на 70 маны"
    },
    "elixir_power": {
        "name": "Эликсир силы",
        "emoji": "💪",
        "cost": 100,
        "ingredients": {"essence": 5, "demon_soul": 1},
        "result": ("elixir_power", 1),
        "desc": "+20% урона"
    },
    "elixir_defense": {
        "name": "Эликсир защиты",
        "emoji": "🛡️",
        "cost": 100,
        "ingredients": {"ore": 10, "essence": 3},
        "result": ("elixir_defense", 1),
        "desc": "+20% защиты"
    },
    "antidote": {
        "name": "Противоядие",
        "emoji": "🧪",
        "cost": 20,
        "ingredients": {"herb": 3},
        "result": ("antidote", 2),
        "desc": "Очищает яд"
    },
    "chaos_elixir": {
        "name": "Эликсир хаоса",
        "emoji": "🌀",
        "cost": 300,
        "ingredients": {"chaos_essence": 5, "demon_soul": 3},
        "result": ("chaos_elixir", 1),
        "special": True,
        "desc": "Случайный мощный эффект в бою"
    }
}

# Добавляем эликсир хаоса в ITEMS
ITEMS["chaos_elixir"] = {
    "name": "Эликсир хаоса",
    "type": "consumable",
    "emoji": "🌀",
    "special": "chaos",
    "price": 500
}

# ============ КЛАСС ИГРОКА ============
class Player:
    def __init__(self, player_class="warrior"):
        class_data = CLASSES[player_class]
        self.player_class = player_class
        self.level = 1
        self.exp = 0
        self.exp_needed = 100

        # Базовые статы
        self.max_hp = class_data["base_hp"]
        self.hp = self.max_hp
        self.max_mana = class_data["base_mana"]
        self.mana = self.max_mana
        self.base_damage = class_data["base_damage"]
        self.base_defense = class_data["base_defense"]
        self.base_crit = class_data["base_crit"]

        # Экономика
        self.gold = 100

        # Инвентарь
        self.inventory = {"hp_potion_small": 3, "mana_potion_small": 2}

        # Экипировка
        self.equipped = {
            "weapon": None,
            "armor": None,
            "accessory": None,
            "helmet": None,  # Легендарный сет
            "chest": None,
            "gloves": None,
            "boots": None
        }

        # Ресурсы
        self.resources = {
            "herb": 0,
            "ore": 0,
            "essence": 0,
            "demon_soul": 0,
            "chaos_essence": 0
        }

        # Прогресс подземелий
        self.dungeon_progress = {
            "forest": {"unlocked": True, "max_floor": 0, "boss_killed": False},
            "mines": {"unlocked": False, "max_floor": 0, "boss_killed": False},
            "crypt": {"unlocked": False, "max_floor": 0, "boss_killed": False},
            "abyss": {"unlocked": False, "max_floor": 0, "boss_killed": False},
            "chaos": {"unlocked": False, "max_floor": 0, "boss_killed": False}
        }

        # Статистика
        self.stats = {
            "kills": 0,
            "boss_kills": 0,
            "deaths": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "gold_earned": 0,
            "quests_completed": 0,
            "crits": 0
        }

        # Достижения
        self.achievements = []

        # Квесты
        self.active_quests = []
        self.completed_quests = 0

        # Ежедневки
        self.last_daily = None
        self.daily_streak = 0

        # Таланты (будущее)
        self.talent_points = 0
        self.talents = {}

        # Легендарные части
        self.legendary_pieces = []

        # Квесты (часть 3)
        self.quest_progress = {}  # {"quest_id": current_progress}
        self.completed_story_quests = []  # Сюжетные квесты
        self.quest_stats = {  # Статы для квестов (сбрасываются)
            "kills": 0,
            "floors": 0,
            "crits": 0,
            "boss_kills": 0,
            "gold_earned": 0
        }
        self.last_quest_reset = None  # Для ежедневных квестов
        self.last_weekly_reset = None  # Для еженедельных

        # Бафы от еды
        self.food_buffs = {}  # {"buff_type": {"value": X, "expires": timestamp}}

        # Наёмник
        self.mercenary = None  # {"id": "guard", "fights_left": 3}

        # Улучшения кузнеца
        self.weapon_upgrades = {}  # {"sharpen": 3, "enchant_fire": 1}
        self.armor_upgrades = {}

        # Титулы
        self.titles = []
        self.active_title = None

    def to_dict(self):
        """Сериализация для сохранения"""
        return {
            "player_class": self.player_class,
            "level": self.level,
            "exp": self.exp,
            "exp_needed": self.exp_needed,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_mana": self.max_mana,
            "mana": self.mana,
            "base_damage": self.base_damage,
            "base_defense": self.base_defense,
            "base_crit": self.base_crit,
            "gold": self.gold,
            "inventory": self.inventory,
            "equipped": self.equipped,
            "resources": self.resources,
            "dungeon_progress": self.dungeon_progress,
            "stats": self.stats,
            "achievements": self.achievements,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "last_daily": self.last_daily,
            "daily_streak": self.daily_streak,
            "talent_points": self.talent_points,
            "talents": self.talents,
            "legendary_pieces": self.legendary_pieces,
            "quest_progress": self.quest_progress,
            "completed_story_quests": self.completed_story_quests,
            "quest_stats": self.quest_stats,
            "last_quest_reset": self.last_quest_reset,
            "last_weekly_reset": self.last_weekly_reset,
            "food_buffs": self.food_buffs,
            "mercenary": self.mercenary,
            "weapon_upgrades": self.weapon_upgrades,
            "armor_upgrades": self.armor_upgrades,
            "titles": self.titles,
            "active_title": self.active_title
        }

    @classmethod
    def from_dict(cls, data):
        """Десериализация из сохранения"""
        player = cls(data.get("player_class", "warrior"))
        for key, value in data.items():
            if hasattr(player, key):
                setattr(player, key, value)
        return player

    def get_total_damage(self):
        """Общий урон с учётом экипировки"""
        damage = self.base_damage
        if self.equipped["weapon"]:
            item = ITEMS.get(self.equipped["weapon"], {})
            damage += item.get("damage", 0)
        if self.equipped["accessory"]:
            item = ITEMS.get(self.equipped["accessory"], {})
            damage += item.get("damage_bonus", 0)
        # Легендарный сет
        for piece in ["helmet", "chest", "gloves", "boots"]:
            if self.equipped[piece]:
                # Проверяем легендарные бонусы
                pass
        return damage

    def get_total_defense(self):
        """Общая защита"""
        defense = self.base_defense
        if self.equipped["armor"]:
            item = ITEMS.get(self.equipped["armor"], {})
            defense += item.get("defense", 0)
        if self.equipped["accessory"]:
            item = ITEMS.get(self.equipped["accessory"], {})
            defense += item.get("defense_bonus", 0)
        return defense

    def get_total_crit(self):
        """Общий шанс крита"""
        crit = self.base_crit
        if self.player_class == "archer":
            crit += 15  # Пассивка
        if self.equipped["weapon"]:
            item = ITEMS.get(self.equipped["weapon"], {})
            crit += item.get("crit_bonus", 0)
        if self.equipped["accessory"]:
            item = ITEMS.get(self.equipped["accessory"], {})
            crit += item.get("crit_bonus", 0)
        return crit

    def get_max_hp(self):
        """Максимальное HP с бонусами"""
        hp = self.max_hp
        if self.equipped["armor"]:
            item = ITEMS.get(self.equipped["armor"], {})
            hp += item.get("hp_bonus", 0)
        if self.equipped["accessory"]:
            item = ITEMS.get(self.equipped["accessory"], {})
            hp += item.get("hp_bonus", 0)
        return hp

    def get_max_mana(self):
        """Максимальная мана с бонусами"""
        mana = self.max_mana
        if self.equipped["weapon"]:
            item = ITEMS.get(self.equipped["weapon"], {})
            mana += item.get("mana_bonus", 0)
        return mana

    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.exp = 0
        self.exp_needed = int(100 * (self.level ** 1.5))

        # Бонусы за уровень
        self.max_hp += 10
        self.max_mana += 5
        self.base_damage += 2
        self.base_defense += 1

        # Полное восстановление
        self.hp = self.get_max_hp()
        self.mana = self.get_max_mana()

        # Очко таланта каждые 5 уровней
        if self.level % 5 == 0:
            self.talent_points += 1

        # Проверка разблокировки подземелий
        self.check_dungeon_unlocks()

        return True

    def check_dungeon_unlocks(self):
        """Проверяет и разблокирует подземелья"""
        for dungeon_id, dungeon in DUNGEONS.items():
            if self.level >= dungeon["min_level"]:
                self.dungeon_progress[dungeon_id]["unlocked"] = True

    def add_exp(self, amount):
        """Добавляет опыт и проверяет левел-ап"""
        self.exp += amount
        leveled = False
        while self.exp >= self.exp_needed:
            self.level_up()
            leveled = True
        return leveled

    def check_achievements(self):
        """Проверяет и выдаёт достижения"""
        new_achievements = []

        # Убийства
        if self.stats["kills"] >= 1 and "first_blood" not in self.achievements:
            self.achievements.append("first_blood")
            new_achievements.append("first_blood")
        if self.stats["kills"] >= 100 and "slayer_100" not in self.achievements:
            self.achievements.append("slayer_100")
            new_achievements.append("slayer_100")
        if self.stats["kills"] >= 1000 and "slayer_1000" not in self.achievements:
            self.achievements.append("slayer_1000")
            new_achievements.append("slayer_1000")

        # Боссы
        if self.stats["boss_kills"] >= 5 and "boss_hunter" not in self.achievements:
            self.achievements.append("boss_hunter")
            new_achievements.append("boss_hunter")
        if self.stats["boss_kills"] >= 20 and "boss_slayer" not in self.achievements:
            self.achievements.append("boss_slayer")
            new_achievements.append("boss_slayer")

        # Уровни
        if self.level >= 10 and "veteran" not in self.achievements:
            self.achievements.append("veteran")
            new_achievements.append("veteran")
        if self.level >= 20 and "master" not in self.achievements:
            self.achievements.append("master")
            new_achievements.append("master")
        if self.level >= 30 and "grandmaster" not in self.achievements:
            self.achievements.append("grandmaster")
            new_achievements.append("grandmaster")

        # Золото
        if self.gold >= 1000 and "rich" not in self.achievements:
            self.achievements.append("rich")
            new_achievements.append("rich")
        if self.gold >= 10000 and "wealthy" not in self.achievements:
            self.achievements.append("wealthy")
            new_achievements.append("wealthy")
        if self.gold >= 100000 and "magnate" not in self.achievements:
            self.achievements.append("magnate")
            new_achievements.append("magnate")

        # Квесты
        if self.completed_quests >= 50 and "quester" not in self.achievements:
            self.achievements.append("quester")
            new_achievements.append("quester")

        return new_achievements

    def rest(self):
        """Полный отдых"""
        self.hp = self.get_max_hp()
        self.mana = self.get_max_mana()

# ============ ОБРАБОТЧИКИ ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало игры или главное меню"""
    user_id = update.effective_user.id

    if user_id in players:
        await show_main_menu(update, context)
    else:
        # Новый игрок - выбор класса
        await show_class_selection(update, context)

async def show_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает выбор класса для нового игрока"""
    text = "🎮 **ТЕНИ ПОДЗЕМЕЛИЙ**\n\n"
    text += "Добро пожаловать, странник!\n"
    text += "Выбери свой класс:\n\n"

    keyboard = []
    for class_id, class_data in CLASSES.items():
        text += f"{class_data['emoji']} **{class_data['name']}**\n"
        text += f"_{class_data['description']}_\n"
        text += f"❤️ {class_data['base_hp']} HP | 💙 {class_data['base_mana']} Мана\n"
        text += f"⚔️ {class_data['base_damage']} Урон | 🛡️ {class_data['base_defense']} Защита\n"
        text += f"🎯 {class_data['base_crit']}% Крит\n"
        text += f"✨ _{class_data['passive']}_\n\n"
        keyboard.append([InlineKeyboardButton(f"{class_data['emoji']} {class_data['name']}", callback_data=f"class_{class_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def select_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор класса"""
    query = update.callback_query
    user_id = update.effective_user.id
    class_id = query.data.replace("class_", "")

    players[user_id] = Player(class_id)
    save_data()

    class_name = CLASSES[class_id]["name"]
    await query.answer(f"Ты выбрал класс: {class_name}!")
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    user_id = update.effective_user.id
    player = players.get(user_id)

    if not player:
        await show_class_selection(update, context)
        return

    class_data = CLASSES[player.player_class]

    # Прогресс-бар опыта
    exp_progress = int((player.exp / player.exp_needed) * 10)
    exp_bar = "█" * exp_progress + "░" * (10 - exp_progress)

    text = f"🏰 **ТЕНИ ПОДЗЕМЕЛИЙ**\n\n"
    text += f"{class_data['emoji']} **{class_data['name']}** | Уровень {player.level}\n"
    text += f"[{exp_bar}] {player.exp}/{player.exp_needed} XP\n\n"
    text += f"❤️ HP: {player.hp}/{player.get_max_hp()}\n"
    text += f"💙 Мана: {player.mana}/{player.get_max_mana()}\n"
    text += f"⚔️ Урон: {player.get_total_damage()} | 🛡️ Защита: {player.get_total_defense()}\n"
    text += f"🎯 Крит: {player.get_total_crit()}%\n"
    text += f"💰 Золото: {player.gold}\n\n"
    text += f"📊 Убийств: {player.stats['kills']} | 👑 Боссов: {player.stats['boss_kills']}\n"

    keyboard = [
        [InlineKeyboardButton("🏰 Подземелья", callback_data="dungeons")],
        [InlineKeyboardButton("🍺 Таверна", callback_data="tavern")],
        [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory"),
         InlineKeyboardButton("⚔️ Экипировка", callback_data="equipment")],
        [InlineKeyboardButton("🏆 Достижения", callback_data="achievements"),
         InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("💤 Отдых", callback_data="rest"),
         InlineKeyboardButton("🎁 Ежедневка", callback_data="daily")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        await update.callback_query.answer()
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    await show_main_menu(update, context)

async def show_dungeons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список подземелий"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "🏰 **ПОДЗЕМЕЛЬЯ**\n\n"
    keyboard = []

    for dungeon_id, dungeon in DUNGEONS.items():
        progress = player.dungeon_progress[dungeon_id]

        if progress["unlocked"]:
            status = f"Этаж {progress['max_floor']}/{dungeon['floors']}"
            if progress["boss_killed"]:
                status += " ✅"
            text += f"{dungeon['emoji']} **{dungeon['name']}** (Ур.{dungeon['min_level']}+)\n"
            text += f"_{dungeon['description']}_\n"
            text += f"⚠️ {dungeon['mechanic_desc']}\n"
            text += f"📊 {status}\n\n"
            keyboard.append([InlineKeyboardButton(f"{dungeon['emoji']} {dungeon['name']}", callback_data=f"dungeon_{dungeon_id}")])
        else:
            text += f"🔒 **{dungeon['name']}** (Ур.{dungeon['min_level']}+)\n"
            text += f"_Требуется уровень {dungeon['min_level']}_\n\n"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def show_dungeon_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о подземелье и вход"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]
    dungeon_id = query.data.replace("dungeon_", "")
    dungeon = DUNGEONS[dungeon_id]
    progress = player.dungeon_progress[dungeon_id]

    text = f"{dungeon['emoji']} **{dungeon['name']}**\n\n"
    text += f"_{dungeon['description']}_\n\n"
    text += f"📊 **Прогресс:** {progress['max_floor']}/{dungeon['floors']} этажей\n"
    text += f"👹 **Босс:** {dungeon['boss_emoji']} {dungeon['boss']}"
    if progress["boss_killed"]:
        text += " ✅ Побеждён"
    text += f"\n\n"
    text += f"⚠️ **Особенность:** {dungeon['mechanic_desc']}\n"
    text += f"💰 Множитель наград: x{dungeon['gold_mult']}\n"
    text += f"⭐ Множитель опыта: x{dungeon['exp_mult']}\n"
    text += f"🌿 Ресурс: {ITEMS[dungeon['drop_resource']]['emoji']} {ITEMS[dungeon['drop_resource']]['name']}\n"

    if player.hp <= 0:
        text += "\n⚠️ _У тебя нет HP! Отдохни сначала._"

    next_floor = progress['max_floor'] + 1
    if next_floor > dungeon['floors']:
        next_floor = dungeon['floors']

    keyboard = [
        [InlineKeyboardButton(f"⚔️ Войти на этаж {next_floor}", callback_data=f"enter_{dungeon_id}_{next_floor}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="dungeons")]
    ]

    # Если есть прогресс, можно выбрать этаж
    if progress['max_floor'] > 1:
        keyboard.insert(1, [InlineKeyboardButton("📋 Выбрать этаж", callback_data=f"floors_{dungeon_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def rest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отдых - восстановление HP и маны"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    player.rest()
    save_data()

    await query.answer("💤 Ты отдохнул и восстановил силы!")
    await show_main_menu(update, context)

async def show_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ежедневная награда"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    today = datetime.now().strftime("%Y-%m-%d")

    if player.last_daily == today:
        await query.answer("Ты уже получил награду сегодня! Приходи завтра.", show_alert=True)
        return

    # Проверяем стрик
    if player.last_daily:
        last = datetime.strptime(player.last_daily, "%Y-%m-%d")
        diff = (datetime.now() - last).days
        if diff == 1:
            player.daily_streak = min(player.daily_streak + 1, 7)
        elif diff > 1:
            player.daily_streak = 1
    else:
        player.daily_streak = 1

    player.last_daily = today

    # Выдаём награду
    reward = DAILY_REWARDS[player.daily_streak - 1]

    text = f"🎁 **ЕЖЕДНЕВНАЯ НАГРАДА**\n\n"
    text += f"📅 День {player.daily_streak}/7\n\n"

    if reward["gold"] > 0:
        player.gold += reward["gold"]
        text += f"💰 +{reward['gold']} золота\n"

    for item_id, count in reward["items"]:
        item = ITEMS[item_id]
        player.inventory[item_id] = player.inventory.get(item_id, 0) + count
        text += f"{item['emoji']} +{count} {item['name']}\n"

    text += f"\n_Приходи завтра за новой наградой!_"

    save_data()

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer("🎁 Награда получена!")

async def show_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список достижений"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"🏆 **ДОСТИЖЕНИЯ** ({len(player.achievements)}/{len(ACHIEVEMENTS)})\n\n"

    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in player.achievements:
            text += f"✅ {ach['emoji']} **{ach['name']}**\n"
            text += f"   _{ach['desc']}_\n\n"
        else:
            text += f"❌ {ach['emoji']} **{ach['name']}**\n"
            text += f"   _{ach['desc']}_\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика игрока"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"📊 **СТАТИСТИКА**\n\n"
    text += f"⚔️ Убито врагов: {player.stats['kills']}\n"
    text += f"👑 Убито боссов: {player.stats['boss_kills']}\n"
    text += f"💀 Смертей: {player.stats['deaths']}\n"
    text += f"💥 Нанесено урона: {player.stats['damage_dealt']}\n"
    text += f"🩸 Получено урона: {player.stats['damage_taken']}\n"
    text += f"🎯 Критических ударов: {player.stats['crits']}\n"
    text += f"💰 Заработано золота: {player.stats['gold_earned']}\n"
    text += f"📜 Выполнено квестов: {player.completed_quests}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инвентарь игрока"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"🎒 **ИНВЕНТАРЬ**\n\n"
    text += f"💰 Золото: {player.gold}\n\n"

    # Зелья и расходники
    text += "**Расходники:**\n"
    consumables = {k: v for k, v in player.inventory.items() if ITEMS.get(k, {}).get("type") == "consumable"}
    if consumables:
        for item_id, count in consumables.items():
            item = ITEMS[item_id]
            text += f"{item['emoji']} {item['name']} x{count}\n"
    else:
        text += "_Пусто_\n"

    text += "\n**Ресурсы:**\n"
    has_resources = False
    for res_id, count in player.resources.items():
        if count > 0:
            item = ITEMS[res_id]
            text += f"{item['emoji']} {item['name']} x{count}\n"
            has_resources = True
    if not has_resources:
        text += "_Пусто_\n"

    text += "\n**Снаряжение:**\n"
    equipment = {k: v for k, v in player.inventory.items() if ITEMS.get(k, {}).get("type") in ["weapon", "armor", "accessory"]}
    if equipment:
        for item_id, count in equipment.items():
            item = ITEMS[item_id]
            rarity_emoji = {"common": "⚪", "uncommon": "🟢", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}.get(item.get("rarity", "common"), "⚪")
            text += f"{rarity_emoji} {item['emoji']} {item['name']} x{count}\n"
    else:
        text += "_Пусто_\n"

    # Легендарные части
    if player.legendary_pieces:
        text += "\n**✨ Легендарные части:**\n"
        for piece_name in player.legendary_pieces:
            text += f"✨ {piece_name}\n"

    keyboard = [
        [InlineKeyboardButton("⚔️ Экипировать", callback_data="equip_menu")],
        [InlineKeyboardButton("🏪 Магазин", callback_data="shop")],
        [InlineKeyboardButton("💰 Продать", callback_data="sell_menu")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def show_equip_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню экипировки предметов"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "⚔️ **ЭКИПИРОВАТЬ ПРЕДМЕТ**\n\n"
    text += "Выбери предмет для экипировки:\n\n"

    keyboard = []

    # Оружие
    weapons = {k: v for k, v in player.inventory.items()
               if ITEMS.get(k, {}).get("type") == "weapon" and v > 0}
    for item_id, count in weapons.items():
        item = ITEMS[item_id]
        equipped = "✅" if player.equipped["weapon"] == item_id else ""
        btn_text = f"🗡️ {item['name']} (+{item.get('damage', 0)} урон) {equipped}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"equip_weapon_{item_id}")])

    # Броня
    armors = {k: v for k, v in player.inventory.items()
              if ITEMS.get(k, {}).get("type") == "armor" and v > 0}
    for item_id, count in armors.items():
        item = ITEMS[item_id]
        equipped = "✅" if player.equipped["armor"] == item_id else ""
        btn_text = f"🛡️ {item['name']} (+{item.get('defense', 0)} защита) {equipped}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"equip_armor_{item_id}")])

    # Аксессуары
    accessories = {k: v for k, v in player.inventory.items()
                   if ITEMS.get(k, {}).get("type") == "accessory" and v > 0}
    for item_id, count in accessories.items():
        item = ITEMS[item_id]
        equipped = "✅" if player.equipped["accessory"] == item_id else ""
        stats = []
        if item.get("damage_bonus"):
            stats.append(f"+{item['damage_bonus']} урон")
        if item.get("defense_bonus"):
            stats.append(f"+{item['defense_bonus']} защита")
        if item.get("crit_bonus"):
            stats.append(f"+{item['crit_bonus']}% крит")
        if item.get("hp_bonus"):
            stats.append(f"+{item['hp_bonus']} HP")
        btn_text = f"💍 {item['name']} ({', '.join(stats)}) {equipped}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"equip_accessory_{item_id}")])

    # Легендарные части
    if player.legendary_pieces:
        legendary_set = LEGENDARY_SETS.get(player.player_class, {})
        for piece_name in player.legendary_pieces:
            for slot, piece in legendary_set.get("pieces", {}).items():
                if piece["name"] == piece_name:
                    equipped = "✅" if player.equipped[slot] == piece_name else ""
                    btn_text = f"✨ {piece['emoji']} {piece_name} {equipped}"
                    keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"equip_legendary_{slot}_{piece_name}")])

    if not keyboard:
        text += "_У тебя нет предметов для экипировки_"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="inventory")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def equip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экипировка предмета"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    data = query.data.replace("equip_", "")
    parts = data.split("_", 1)
    slot = parts[0]
    item_id = parts[1] if len(parts) > 1 else None

    if slot == "legendary":
        # Легендарный предмет: equip_legendary_helmet_ИмяПредмета
        parts = data.split("_", 2)
        slot = parts[1]
        item_name = parts[2]

        # Проверяем что предмет есть
        if item_name in player.legendary_pieces:
            # Снимаем старый если есть
            old = player.equipped.get(slot)
            player.equipped[slot] = item_name
            save_data()
            await query.answer(f"Экипировано: {item_name}")
        else:
            await query.answer("У тебя нет этого предмета!", show_alert=True)
            return
    else:
        # Обычный предмет
        if player.inventory.get(item_id, 0) <= 0:
            await query.answer("У тебя нет этого предмета!", show_alert=True)
            return

        item = ITEMS.get(item_id)
        if not item:
            await query.answer("Предмет не найден!", show_alert=True)
            return

        # Определяем слот
        item_type = item.get("type")
        if item_type == "weapon":
            slot = "weapon"
        elif item_type == "armor":
            slot = "armor"
        elif item_type == "accessory":
            slot = "accessory"
        else:
            await query.answer("Этот предмет нельзя экипировать!", show_alert=True)
            return

        # Экипируем
        player.equipped[slot] = item_id
        save_data()
        await query.answer(f"Экипировано: {item['name']}")

    await show_equip_menu(update, context)

async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Магазин"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "🏪 **МАГАЗИН**\n\n"
    text += f"💰 Твоё золото: {player.gold}\n\n"

    # Товары по категориям
    text += "**Зелья:**\n"
    potions = ["hp_potion_small", "hp_potion_medium", "hp_potion_large",
               "mana_potion_small", "mana_potion_medium", "antidote"]
    for item_id in potions:
        item = ITEMS.get(item_id, {})
        text += f"  {item.get('emoji', '🧪')} {item.get('name', item_id)} - {item.get('price', 0)}💰\n"

    keyboard = [
        [InlineKeyboardButton("❤️ Зелья HP", callback_data="shop_cat_hp")],
        [InlineKeyboardButton("💙 Зелья маны", callback_data="shop_cat_mana")],
        [InlineKeyboardButton("⚔️ Оружие", callback_data="shop_cat_weapon")],
        [InlineKeyboardButton("🛡️ Броня", callback_data="shop_cat_armor")],
        [InlineKeyboardButton("💍 Аксессуары", callback_data="shop_cat_accessory")],
        [InlineKeyboardButton("🔙 Назад", callback_data="inventory")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def show_shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Категория магазина"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    category = query.data.replace("shop_cat_", "")

    text = f"🏪 **МАГАЗИН**\n\n"
    text += f"💰 Твоё золото: {player.gold}\n\n"

    keyboard = []

    if category == "hp":
        text += "**Зелья здоровья:**\n"
        items_list = ["hp_potion_small", "hp_potion_medium", "hp_potion_large"]
    elif category == "mana":
        text += "**Зелья маны:**\n"
        items_list = ["mana_potion_small", "mana_potion_medium", "antidote"]
    elif category == "weapon":
        text += "**Оружие:**\n"
        items_list = [k for k, v in ITEMS.items() if v.get("type") == "weapon"]
    elif category == "armor":
        text += "**Броня:**\n"
        items_list = [k for k, v in ITEMS.items() if v.get("type") == "armor"]
    elif category == "accessory":
        text += "**Аксессуары:**\n"
        items_list = [k for k, v in ITEMS.items() if v.get("type") == "accessory"]
    else:
        items_list = []

    for item_id in items_list:
        item = ITEMS.get(item_id, {})
        price = item.get("price", 0)
        owned = player.inventory.get(item_id, 0)

        # Формируем описание
        desc_parts = []
        if item.get("heal"):
            desc_parts.append(f"+{item['heal']} HP")
        if item.get("mana"):
            desc_parts.append(f"+{item['mana']} мана")
        if item.get("damage"):
            desc_parts.append(f"+{item['damage']} урон")
        if item.get("defense"):
            desc_parts.append(f"+{item['defense']} защита")
        if item.get("crit_bonus"):
            desc_parts.append(f"+{item['crit_bonus']}% крит")
        desc = ", ".join(desc_parts) if desc_parts else ""

        btn_text = f"{item.get('emoji', '📦')} {item.get('name', item_id)} - {price}💰"
        if owned > 0:
            btn_text += f" (x{owned})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_{item_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покупка предмета"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    item_id = query.data.replace("buy_", "")
    item = ITEMS.get(item_id)

    if not item:
        await query.answer("Предмет не найден!", show_alert=True)
        return

    price = item.get("price", 0)
    if player.gold < price:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    player.gold -= price
    player.inventory[item_id] = player.inventory.get(item_id, 0) + 1
    save_data()

    await query.answer(f"Куплено: {item['name']} за {price} золота")

    # Возвращаемся в категорию
    item_type = item.get("type", "")
    if item_type == "consumable":
        if "hp" in item_id or "heal" in item:
            query.data = "shop_cat_hp"
        else:
            query.data = "shop_cat_mana"
    else:
        query.data = f"shop_cat_{item_type}"
    await show_shop_category(update, context)

async def show_sell_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню продажи"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "💰 **ПРОДАЖА**\n\n"
    text += f"💰 Твоё золото: {player.gold}\n\n"
    text += "_Выбери предмет для продажи (50% от цены):_\n\n"

    keyboard = []

    # Все продаваемые предметы
    for item_id, count in player.inventory.items():
        if count <= 0:
            continue
        item = ITEMS.get(item_id)
        if not item or item.get("type") == "resource":
            continue

        sell_price = item.get("price", 0) // 2
        if sell_price <= 0:
            continue

        btn_text = f"{item['emoji']} {item['name']} x{count} → {sell_price}💰"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"sell_{item_id}")])

    if not keyboard:
        text += "_Нет предметов для продажи_"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="inventory")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def sell_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продажа предмета"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    item_id = query.data.replace("sell_", "")

    if player.inventory.get(item_id, 0) <= 0:
        await query.answer("У тебя нет этого предмета!", show_alert=True)
        return

    item = ITEMS.get(item_id)
    if not item:
        await query.answer("Предмет не найден!", show_alert=True)
        return

    sell_price = item.get("price", 0) // 2
    player.gold += sell_price
    player.inventory[item_id] -= 1
    if player.inventory[item_id] <= 0:
        del player.inventory[item_id]

    # Снимаем экипировку если продали
    for slot, equipped_id in player.equipped.items():
        if equipped_id == item_id and player.inventory.get(item_id, 0) <= 0:
            player.equipped[slot] = None

    save_data()
    await query.answer(f"Продано: {item['name']} за {sell_price} золота")
    await show_sell_menu(update, context)

async def show_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экипировка игрока"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    class_data = CLASSES[player.player_class]
    text = f"⚔️ **ЭКИПИРОВКА**\n\n"

    # Общие статы
    text += f"**📊 Характеристики:**\n"
    text += f"❤️ HP: {player.hp}/{player.get_max_hp()}\n"
    text += f"💙 Мана: {player.mana}/{player.get_max_mana()}\n"
    text += f"⚔️ Урон: {player.get_total_damage()}\n"
    text += f"🛡️ Защита: {player.get_total_defense()}\n"
    text += f"🎯 Крит: {player.get_total_crit()}%\n\n"

    slots = [
        ("weapon", "🗡️ Оружие"),
        ("armor", "🛡️ Броня"),
        ("accessory", "💍 Аксессуар"),
        ("helmet", "⛑️ Шлем"),
        ("chest", "🎽 Нагрудник"),
        ("gloves", "🧤 Перчатки"),
        ("boots", "👢 Сапоги")
    ]

    text += "**🎽 Слоты:**\n"
    keyboard = []

    for slot_id, slot_name in slots:
        equipped_id = player.equipped[slot_id]
        if equipped_id:
            item = ITEMS.get(equipped_id) or {}
            # Проверяем легендарные части
            if not item:
                legendary_set = LEGENDARY_SETS.get(player.player_class, {})
                for piece_slot, piece in legendary_set.get("pieces", {}).items():
                    if piece["name"] == equipped_id:
                        text += f"{slot_name}: {piece['emoji']} **{piece['name']}** ✨\n"
                        keyboard.append([InlineKeyboardButton(f"❌ Снять {piece['name']}", callback_data=f"unequip_{slot_id}")])
                        break
            else:
                stats = []
                if item.get("damage"):
                    stats.append(f"+{item['damage']}⚔️")
                if item.get("defense"):
                    stats.append(f"+{item['defense']}🛡️")
                if item.get("crit_bonus"):
                    stats.append(f"+{item['crit_bonus']}%🎯")
                if item.get("hp_bonus"):
                    stats.append(f"+{item['hp_bonus']}❤️")
                if item.get("mana_bonus"):
                    stats.append(f"+{item['mana_bonus']}💙")
                stats_text = f" ({', '.join(stats)})" if stats else ""
                text += f"{slot_name}: {item['emoji']} **{item['name']}**{stats_text}\n"
                keyboard.append([InlineKeyboardButton(f"❌ Снять {item['name']}", callback_data=f"unequip_{slot_id}")])
        else:
            text += f"{slot_name}: _Пусто_\n"

    # Подсчёт бонусов от сета
    legendary_set = LEGENDARY_SETS.get(player.player_class, {})
    legendary_count = sum(1 for slot in ["helmet", "chest", "gloves", "boots"] if player.equipped[slot])
    if legendary_count >= 2:
        text += f"\n✨ **Бонус сета (2):** {legendary_set.get('bonus_2', 'Активен')}"
    if legendary_count >= 4:
        text += f"\n✨ **Бонус сета (4):** {legendary_set.get('bonus_4', 'Активен')}"

    # Титул
    if player.titles:
        text += f"\n\n**🏅 Титул:** {player.active_title or 'Не выбран'}"

    keyboard.append([InlineKeyboardButton("⚔️ Экипировать", callback_data="equip_menu")])
    if player.titles:
        keyboard.append([InlineKeyboardButton("🏅 Сменить титул", callback_data="titles_menu")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def unequip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Снять экипировку"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    slot = query.data.replace("unequip_", "")

    if player.equipped.get(slot):
        item_name = player.equipped[slot]
        player.equipped[slot] = None
        save_data()
        await query.answer(f"Снято: {item_name}")
    else:
        await query.answer("Слот уже пуст!")

    await show_equipment(update, context)

async def show_titles_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора титула"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "🏅 **ТИТУЛЫ**\n\n"
    text += f"Текущий титул: **{player.active_title or 'Нет'}**\n\n"
    text += "Доступные титулы:\n"

    keyboard = []

    # Снять титул
    keyboard.append([InlineKeyboardButton("❌ Без титула", callback_data="set_title_none")])

    for title in player.titles:
        is_active = "✅" if player.active_title == title else ""
        keyboard.append([InlineKeyboardButton(f"🏅 {title} {is_active}", callback_data=f"set_title_{title}")])

    if not player.titles:
        text += "_У тебя пока нет титулов. Выполняй сюжетные квесты!_"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="equipment")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить титул"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    title = query.data.replace("set_title_", "")

    if title == "none":
        player.active_title = None
        await query.answer("Титул снят")
    elif title in player.titles:
        player.active_title = title
        await query.answer(f"Титул установлен: {title}")
    else:
        await query.answer("У тебя нет этого титула!", show_alert=True)
        return

    save_data()
    await show_titles_menu(update, context)

async def show_tavern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Таверна - главное меню таверны"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players.get(user_id)

    text = "🍺 **ТАВЕРНА 'ПРИЮТ СТРАННИКА'**\n\n"
    text += "_Добро пожаловать, путник! Чем могу помочь?_\n\n"

    # Показываем активного наёмника
    if player and player.mercenary:
        merc = MERCENARIES.get(player.mercenary["id"])
        if merc:
            text += f"🤝 Наёмник: {merc['emoji']} {merc['name']} ({player.mercenary['fights_left']} боёв)\n"

    # Показываем активные бафы
    if player and player.food_buffs:
        active_buffs = []
        now = datetime.now().timestamp()
        for buff_type, buff_data in list(player.food_buffs.items()):
            if buff_data.get("expires", 0) > now:
                remaining = int((buff_data["expires"] - now) / 60)
                active_buffs.append(f"+{buff_data['value']} {buff_type} ({remaining}м)")
            else:
                del player.food_buffs[buff_type]
        if active_buffs:
            text += f"✨ Бафы: {', '.join(active_buffs)}\n"

    keyboard = [
        [InlineKeyboardButton("📜 Доска квестов", callback_data="quests")],
        [InlineKeyboardButton("🍖 Трактирщик (еда)", callback_data="food")],
        [InlineKeyboardButton("⚔️ Наёмники", callback_data="mercenaries")],
        [InlineKeyboardButton("🔨 Кузнец", callback_data="blacksmith")],
        [InlineKeyboardButton("🧪 Алхимик", callback_data="alchemist")],
        [InlineKeyboardButton("🏆 Доска славы", callback_data="leaderboard")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

# ============ КВЕСТЫ ============

def reset_daily_quests(player: Player):
    """Сбрасывает ежедневные квесты"""
    today = datetime.now().strftime("%Y-%m-%d")
    if player.last_quest_reset != today:
        player.last_quest_reset = today
        player.quest_stats = {
            "kills": 0,
            "floors": 0,
            "crits": 0,
            "boss_kills": 0,
            "gold_earned": 0
        }
        # Удаляем прогресс ежедневных квестов
        player.quest_progress = {k: v for k, v in player.quest_progress.items()
                                  if not k.startswith("daily_")}

def reset_weekly_quests(player: Player):
    """Сбрасывает еженедельные квесты"""
    # Проверяем начало недели (понедельник)
    today = datetime.now()
    monday = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    if player.last_weekly_reset != monday:
        player.last_weekly_reset = monday
        # Удаляем прогресс еженедельных квестов
        player.quest_progress = {k: v for k, v in player.quest_progress.items()
                                  if not k.startswith("weekly_")}

async def show_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Доска квестов"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    # Сбрасываем квесты если нужно
    reset_daily_quests(player)
    reset_weekly_quests(player)

    text = "📜 **ДОСКА КВЕСТОВ**\n\n"

    # Ежедневные квесты
    text += "**📅 Ежедневные:**\n"
    daily_quests = {k: v for k, v in QUESTS.items() if v["type"] == "daily"}
    for quest_id, quest in daily_quests.items():
        progress = player.quest_stats.get(quest["stat"], 0)
        target = quest["target"]
        completed = progress >= target
        status = "✅" if completed else f"({progress}/{target})"
        rewards = f"+{quest['rewards']['gold']}💰 +{quest['rewards']['exp']}⭐"
        text += f"  {quest['emoji']} {quest['name']} {status}\n"
        text += f"    _{quest['desc']}_ | {rewards}\n"

    # Еженедельные квесты
    text += "\n**📆 Еженедельные:**\n"
    weekly_quests = {k: v for k, v in QUESTS.items() if v["type"] == "weekly"}
    for quest_id, quest in weekly_quests.items():
        progress = player.quest_progress.get(quest_id, 0)
        target = quest["target"]
        completed = progress >= target
        status = "✅" if completed else f"({progress}/{target})"
        rewards = f"+{quest['rewards']['gold']}💰"
        if "item" in quest["rewards"]:
            item = ITEMS.get(quest["rewards"]["item"], {})
            rewards += f" {item.get('emoji', '🎁')}"
        text += f"  {quest['emoji']} {quest['name']} {status}\n"
        text += f"    _{quest['desc']}_ | {rewards}\n"

    # Сюжетные квесты
    text += "\n**📖 Сюжетные:**\n"
    story_quests = {k: v for k, v in QUESTS.items() if v["type"] == "story"}
    for quest_id, quest in story_quests.items():
        if quest_id in player.completed_story_quests:
            text += f"  ✅ {quest['emoji']} {quest['name']}\n"
        else:
            # Проверяем выполнение
            dungeon_id = quest["target"].replace("_boss", "")
            if player.dungeon_progress.get(dungeon_id, {}).get("boss_killed"):
                text += f"  🎁 {quest['emoji']} {quest['name']} (забери награду!)\n"
            else:
                text += f"  ⬜ {quest['emoji']} {quest['name']}\n"
                text += f"    _{quest['desc']}_\n"

    keyboard = [
        [InlineKeyboardButton("🎁 Забрать награды", callback_data="claim_quests")],
        [InlineKeyboardButton("🔙 Назад", callback_data="tavern")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def claim_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Забрать награды за квесты"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    rewards_text = []
    total_gold = 0
    total_exp = 0

    # Ежедневные квесты
    for quest_id, quest in QUESTS.items():
        if quest["type"] == "daily":
            progress = player.quest_stats.get(quest["stat"], 0)
            if progress >= quest["target"] and quest_id not in player.quest_progress:
                player.quest_progress[quest_id] = "claimed"
                total_gold += quest["rewards"]["gold"]
                total_exp += quest["rewards"]["exp"]
                rewards_text.append(f"✅ {quest['name']}")

    # Еженедельные квесты
    for quest_id, quest in QUESTS.items():
        if quest["type"] == "weekly":
            progress = player.quest_progress.get(quest_id, 0)
            if isinstance(progress, int) and progress >= quest["target"]:
                player.quest_progress[quest_id] = "claimed"
                total_gold += quest["rewards"]["gold"]
                total_exp += quest["rewards"]["exp"]
                if "item" in quest["rewards"]:
                    item_id = quest["rewards"]["item"]
                    player.inventory[item_id] = player.inventory.get(item_id, 0) + 1
                rewards_text.append(f"✅ {quest['name']}")

    # Сюжетные квесты
    for quest_id, quest in QUESTS.items():
        if quest["type"] == "story" and quest_id not in player.completed_story_quests:
            dungeon_id = quest["target"].replace("_boss", "")
            if player.dungeon_progress.get(dungeon_id, {}).get("boss_killed"):
                player.completed_story_quests.append(quest_id)
                total_gold += quest["rewards"]["gold"]
                total_exp += quest["rewards"]["exp"]
                if "title" in quest["rewards"]:
                    player.titles.append(quest["rewards"]["title"])
                    rewards_text.append(f"✅ {quest['name']} (+титул: {quest['rewards']['title']})")
                else:
                    rewards_text.append(f"✅ {quest['name']}")
                player.completed_quests += 1

    if rewards_text:
        player.gold += total_gold
        player.add_exp(total_exp)
        save_data()
        text = f"🎁 **НАГРАДЫ ПОЛУЧЕНЫ!**\n\n"
        text += "\n".join(rewards_text)
        text += f"\n\n💰 +{total_gold} золота\n⭐ +{total_exp} опыта"
        await query.answer("Награды получены!")
    else:
        text = "❌ Нет доступных наград.\n\nВыполни квесты, чтобы получить награды!"
        await query.answer("Нет доступных наград", show_alert=True)

    keyboard = [[InlineKeyboardButton("🔙 К квестам", callback_data="quests")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# ============ ЕДА ============

async def show_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню трактирщика"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "🍖 **ТРАКТИРЩИК**\n\n"
    text += f"_'Чего изволите, путник? Лучшая еда в округе!'_\n\n"
    text += f"💰 Твоё золото: {player.gold}\n\n"

    keyboard = []
    for food_id, food in TAVERN_FOOD.items():
        btn_text = f"{food['emoji']} {food['name']} - {food['price']}💰"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buy_food_{food_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def buy_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покупка еды"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    food_id = query.data.replace("buy_food_", "")
    food = TAVERN_FOOD.get(food_id)

    if not food:
        await query.answer("Еда не найдена!")
        return

    if player.gold < food["price"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    player.gold -= food["price"]

    # Лечение
    if "heal" in food:
        player.hp = min(player.get_max_hp(), player.hp + food["heal"])
    if food.get("heal_full"):
        player.hp = player.get_max_hp()
    if food.get("mana_full"):
        player.mana = player.get_max_mana()

    # Бафы
    if "buff" in food:
        buff = food["buff"]
        expires = datetime.now().timestamp() + buff.get("duration", 300)
        for buff_type, value in buff.items():
            if buff_type != "duration":
                player.food_buffs[buff_type] = {"value": value, "expires": expires}

    save_data()

    text = f"🍽️ **{food['name']}**\n\n"
    text += f"_{food['desc']}_\n\n"
    text += f"❤️ HP: {player.hp}/{player.get_max_hp()}\n"
    text += f"💙 Мана: {player.mana}/{player.get_max_mana()}\n"

    if "buff" in food:
        text += "\n✨ Бафы активированы!"

    keyboard = [
        [InlineKeyboardButton("🍖 Ещё еды", callback_data="food")],
        [InlineKeyboardButton("🔙 В таверну", callback_data="tavern")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer(f"Куплено: {food['name']}")

# ============ НАЁМНИКИ ============

async def show_mercenaries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню наёмников"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "⚔️ **НАЁМНИКИ**\n\n"
    text += f"_'Лучшие бойцы за ваши деньги!'_\n\n"
    text += f"💰 Твоё золото: {player.gold}\n"

    if player.mercenary:
        merc = MERCENARIES.get(player.mercenary["id"])
        text += f"\n🤝 Текущий наёмник: {merc['emoji']} {merc['name']}\n"
        text += f"   Осталось боёв: {player.mercenary['fights_left']}\n"

    text += "\n"

    keyboard = []
    for merc_id, merc in MERCENARIES.items():
        btn_text = f"{merc['emoji']} {merc['name']} - {merc['price']}💰"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"hire_{merc_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def hire_mercenary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Найм наёмника"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    merc_id = query.data.replace("hire_", "")
    merc = MERCENARIES.get(merc_id)

    if not merc:
        await query.answer("Наёмник не найден!")
        return

    if player.gold < merc["price"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    if player.mercenary and player.mercenary["fights_left"] > 0:
        await query.answer("У тебя уже есть наёмник! Дождись окончания контракта.", show_alert=True)
        return

    player.gold -= merc["price"]
    player.mercenary = {"id": merc_id, "fights_left": merc["duration"]}
    save_data()

    text = f"🤝 **НАЁМНИК НАНЯТ!**\n\n"
    text += f"{merc['emoji']} **{merc['name']}**\n"
    text += f"_{merc['desc']}_\n\n"
    text += f"Контракт на {merc['duration']} боёв.\n"

    keyboard = [[InlineKeyboardButton("🔙 В таверну", callback_data="tavern")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer(f"Нанят: {merc['name']}")

# ============ КУЗНЕЦ ============

async def show_blacksmith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню кузнеца"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "🔨 **КУЗНЕЦ**\n\n"
    text += f"_'Выковываю лучшее оружие в королевстве!'_\n\n"
    text += f"💰 Золото: {player.gold}\n"
    text += f"🌿 Ресурсы: "
    res_list = [f"{ITEMS[r]['emoji']}{c}" for r, c in player.resources.items() if c > 0]
    text += ", ".join(res_list) if res_list else "нет"
    text += "\n\n**Улучшения:**\n"

    keyboard = []
    for upg_id, upg in BLACKSMITH_UPGRADES.items():
        current_level = player.weapon_upgrades.get(upg_id, 0)
        if upg_id == "reinforce":
            current_level = player.armor_upgrades.get(upg_id, 0)

        if current_level >= upg["max_level"]:
            btn_text = f"✅ {upg['emoji']} {upg['name']} (МАКС)"
        else:
            res_name, res_count = upg["resource"]
            btn_text = f"{upg['emoji']} {upg['name']} [{upg['cost']}💰 + {res_count}{ITEMS[res_name]['emoji']}]"

        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"upgrade_{upg_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def blacksmith_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Улучшение у кузнеца"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    upg_id = query.data.replace("upgrade_", "")
    upg = BLACKSMITH_UPGRADES.get(upg_id)

    if not upg:
        await query.answer("Улучшение не найдено!")
        return

    # Определяем куда применяется улучшение
    is_armor = upg_id == "reinforce"
    upgrades = player.armor_upgrades if is_armor else player.weapon_upgrades
    current_level = upgrades.get(upg_id, 0)

    if current_level >= upg["max_level"]:
        await query.answer("Максимальный уровень!", show_alert=True)
        return

    if player.gold < upg["cost"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    res_name, res_count = upg["resource"]
    if player.resources.get(res_name, 0) < res_count:
        await query.answer(f"Недостаточно {ITEMS[res_name]['name']}!", show_alert=True)
        return

    # Применяем улучшение
    player.gold -= upg["cost"]
    player.resources[res_name] -= res_count
    upgrades[upg_id] = current_level + 1

    # Применяем бонус к базовым статам
    if "damage" in upg["bonus"]:
        player.base_damage += upg["bonus"]["damage"]
    if "defense" in upg["bonus"]:
        player.base_defense += upg["bonus"]["defense"]

    save_data()

    new_level = upgrades[upg_id]
    text = f"🔨 **УЛУЧШЕНИЕ ПРИМЕНЕНО!**\n\n"
    text += f"{upg['emoji']} **{upg['name']}** → Уровень {new_level}\n"
    text += f"_{upg['desc']}_\n"

    keyboard = [
        [InlineKeyboardButton("🔨 Ещё улучшения", callback_data="blacksmith")],
        [InlineKeyboardButton("🔙 В таверну", callback_data="tavern")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer(f"Улучшено: {upg['name']}")

# ============ АЛХИМИК ============

async def show_alchemist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню алхимика"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = "🧪 **АЛХИМИК**\n\n"
    text += f"_'Секреты зельеварения раскрыты!'_\n\n"
    text += f"💰 Золото: {player.gold}\n"
    text += f"🌿 Ресурсы: "
    res_list = [f"{ITEMS[r]['emoji']}{c}" for r, c in player.resources.items() if c > 0]
    text += ", ".join(res_list) if res_list else "нет"
    text += "\n\n**Рецепты:**\n"

    keyboard = []
    for recipe_id, recipe in ALCHEMY_RECIPES.items():
        ingredients_text = ", ".join([f"{c}{ITEMS[r]['emoji']}" for r, c in recipe["ingredients"].items()])
        btn_text = f"{recipe['emoji']} {recipe['name']} [{recipe['cost']}💰 + {ingredients_text}]"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"craft_{recipe_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="tavern")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def craft_potion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание зелья"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    recipe_id = query.data.replace("craft_", "")
    recipe = ALCHEMY_RECIPES.get(recipe_id)

    if not recipe:
        await query.answer("Рецепт не найден!")
        return

    if player.gold < recipe["cost"]:
        await query.answer("Недостаточно золота!", show_alert=True)
        return

    # Проверяем ингредиенты
    for res_name, res_count in recipe["ingredients"].items():
        if player.resources.get(res_name, 0) < res_count:
            await query.answer(f"Недостаточно {ITEMS[res_name]['name']}!", show_alert=True)
            return

    # Тратим ресурсы
    player.gold -= recipe["cost"]
    for res_name, res_count in recipe["ingredients"].items():
        player.resources[res_name] -= res_count

    # Создаём предмет
    item_id, count = recipe["result"]
    player.inventory[item_id] = player.inventory.get(item_id, 0) + count

    save_data()

    item = ITEMS.get(item_id, {})
    text = f"🧪 **ЗЕЛЬЕ СОЗДАНО!**\n\n"
    text += f"{item.get('emoji', '🧪')} **{recipe['name']}** x{count}\n"
    text += f"_{recipe['desc']}_\n"

    keyboard = [
        [InlineKeyboardButton("🧪 Ещё зелья", callback_data="alchemist")],
        [InlineKeyboardButton("🔙 В таверну", callback_data="tavern")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer(f"Создано: {recipe['name']}")

# ============ ДОСКА СЛАВЫ ============

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Доска славы"""
    query = update.callback_query

    # Сортируем игроков по уровню и опыту
    sorted_players = sorted(
        players.items(),
        key=lambda x: (x[1].level, x[1].exp),
        reverse=True
    )[:10]  # Топ 10

    text = "🏆 **ДОСКА СЛАВЫ**\n\n"

    if not sorted_players:
        text += "_Пока никто не попал в таблицу лидеров_"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, player) in enumerate(sorted_players):
            medal = medals[i] if i < 3 else f"{i+1}."
            class_emoji = CLASSES[player.player_class]["emoji"]
            title = f" [{player.active_title}]" if player.active_title else ""
            text += f"{medal} {class_emoji} Уровень {player.level}{title}\n"
            text += f"   👹 Убийств: {player.stats['kills']} | 👑 Боссов: {player.stats['boss_kills']}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="tavern")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

# ============ БОЕВАЯ СИСТЕМА ============

class Fight:
    """Класс для управления боем"""
    def __init__(self, player: Player, dungeon_id: str, floor: int, is_boss: bool = False):
        self.player = player
        self.dungeon_id = dungeon_id
        self.dungeon = DUNGEONS[dungeon_id]
        self.floor = floor
        self.is_boss = is_boss

        # Бонусы от еды (проверяем срок действия)
        self.food_bonus_hp = 0
        self.food_bonus_damage = 0
        self.food_bonus_defense = 0
        self.food_bonus_crit = 0
        self.food_bonus_mana_regen = 0
        now = datetime.now().timestamp()
        if player.food_buffs:
            for buff_type, buff_data in list(player.food_buffs.items()):
                if buff_data.get("expires", 0) > now:
                    if buff_type == "hp":
                        self.food_bonus_hp = buff_data["value"]
                    elif buff_type == "damage":
                        self.food_bonus_damage = buff_data["value"]
                    elif buff_type == "defense":
                        self.food_bonus_defense = buff_data["value"]
                    elif buff_type == "crit":
                        self.food_bonus_crit = buff_data["value"]
                    elif buff_type == "mana_regen":
                        self.food_bonus_mana_regen = buff_data["value"]

        # Бонусы от наёмника
        self.merc_bonus_damage = 0
        self.merc_bonus_defense = 0
        self.merc_bonus_crit = 0
        self.merc_bonus_heal = 0
        self.merc_bonus_mana_regen = 0
        if player.mercenary:
            merc = MERCENARIES.get(player.mercenary["id"])
            if merc:
                bonus = merc.get("bonus", {})
                self.merc_bonus_damage = bonus.get("damage", 0)
                self.merc_bonus_defense = bonus.get("defense", 0)
                self.merc_bonus_crit = bonus.get("crit", 0)
                self.merc_bonus_heal = bonus.get("heal_per_turn", 0)
                self.merc_bonus_mana_regen = bonus.get("mana_regen", 0)

        # HP/Мана в бою (с бонусами)
        self.player_hp = player.hp
        self.player_mana = player.mana
        self.player_max_hp = player.get_max_hp() + self.food_bonus_hp

        # Враг
        if is_boss:
            self.enemy_name = self.dungeon["boss"]
            self.enemy_emoji = self.dungeon["boss_emoji"]
            self.enemy_hp = int(self.dungeon["boss_hp"] * (1 + floor * 0.05))
            self.enemy_max_hp = self.enemy_hp
            self.enemy_damage = int(self.dungeon["boss_damage"] * (1 + floor * 0.03))
            self.exp_reward = int(100 * self.dungeon["exp_mult"] * (1 + floor * 0.1))
            self.gold_reward = int(150 * self.dungeon["gold_mult"] * (1 + floor * 0.1))
        else:
            enemy_id = random.choice(self.dungeon["enemies"])
            enemy = ENEMIES[enemy_id]
            self.enemy_id = enemy_id
            self.enemy_name = enemy["name"]
            self.enemy_emoji = enemy["emoji"]
            self.enemy_hp = int(enemy["hp"] * (1 + floor * 0.1))
            self.enemy_max_hp = self.enemy_hp
            self.enemy_damage = int(enemy["damage"] * (1 + floor * 0.05))
            self.exp_reward = int(enemy["exp"] * self.dungeon["exp_mult"])
            self.gold_reward = int(enemy["gold"] * self.dungeon["gold_mult"])
            self.enemy_special = {k: v for k, v in enemy.items() if k in ["poison", "burn", "lifesteal"]}

        # Состояния боя
        self.cooldowns = {}
        self.player_effects = {}  # яд, горение и т.д.
        self.enemy_effects = {}
        self.block_next = False
        self.dodge_next = False
        self.invisible = 0
        self.invulnerable = 0
        self.barrier = 0
        self.first_attack = True  # для пассивки разбойника

        # Механика подземелья
        self.mechanic_timer = 0
        self.enemy_resurrected = False  # для нежити

        # Лог боя
        self.fight_log = []

        # Таск атаки врага
        self.enemy_attack_task = None
        self.fight_active = True

        # Время начала (для достижения скорости)
        self.start_time = datetime.now()

def create_hp_bar(current, maximum, length=10):
    """Создаёт HP бар"""
    if maximum <= 0:
        return "[░░░░░░░░░░]"
    filled = max(0, int((current / maximum) * length))
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}]"

def get_fight_keyboard(fight: Fight):
    """Создаёт клавиатуру для боя"""
    player = fight.player
    skills = CLASSES[player.player_class]["skills"]

    keyboard = [[InlineKeyboardButton("⚔️ Атака", callback_data="fight_attack")]]

    # Скиллы
    for skill_id, skill in skills.items():
        cd = fight.cooldowns.get(skill_id, 0)
        mana_ok = fight.player_mana >= skill["mana"]

        if cd > 0:
            btn_text = f"{skill['emoji']} {skill['name']} ({cd}с)"
        elif not mana_ok:
            btn_text = f"{skill['emoji']} {skill['name']} (мана)"
        else:
            btn_text = f"{skill['emoji']} {skill['name']} [{skill['mana']}💙]"

        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"fight_skill_{skill_id}")])

    # Зелья
    potions = {k: v for k, v in player.inventory.items()
               if ITEMS.get(k, {}).get("type") == "consumable" and v > 0}
    if potions:
        potion_btns = []
        for potion_id, count in list(potions.items())[:2]:  # Макс 2 зелья в ряд
            item = ITEMS[potion_id]
            potion_btns.append(InlineKeyboardButton(
                f"{item['emoji']} x{count}",
                callback_data=f"fight_potion_{potion_id}"
            ))
        if potion_btns:
            keyboard.append(potion_btns)

    keyboard.append([InlineKeyboardButton("🏃 Сбежать", callback_data="fight_flee")])

    return InlineKeyboardMarkup(keyboard)

async def update_fight_ui(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
    """Обновляет интерфейс боя"""
    fight: Fight = context.user_data.get('fight')
    if not fight:
        return

    player_bar = create_hp_bar(fight.player_hp, fight.player_max_hp)
    enemy_bar = create_hp_bar(fight.enemy_hp, fight.enemy_max_hp)

    boss_text = " 👑 БОСС" if fight.is_boss else ""

    text = f"⚔️ **БОЙ** - {fight.dungeon['emoji']} Этаж {fight.floor}{boss_text}\n\n"
    text += f"🧑 **Ты** {player_bar}\n"
    text += f"❤️ {max(0, fight.player_hp)}/{fight.player_max_hp} | 💙 {fight.player_mana}/{fight.player.get_max_mana()}\n"

    # Эффекты игрока
    effects = []
    if fight.block_next:
        effects.append("🛡️")
    if fight.dodge_next:
        effects.append("💨")
    if fight.invisible > 0:
        effects.append(f"👻{fight.invisible}")
    if fight.invulnerable > 0:
        effects.append(f"👼{fight.invulnerable}")
    if fight.barrier > 0:
        effects.append(f"🔮{fight.barrier}")
    if "poison" in fight.player_effects:
        effects.append(f"☠️{fight.player_effects['poison']}")
    if "burn" in fight.player_effects:
        effects.append(f"🔥{fight.player_effects['burn']}")
    if effects:
        text += f"Эффекты: {' '.join(effects)}\n"

    text += f"\n{fight.enemy_emoji} **{fight.enemy_name}** {enemy_bar}\n"
    text += f"❤️ {max(0, fight.enemy_hp)}/{fight.enemy_max_hp}\n"

    # Эффекты врага
    enemy_effects = []
    if "poison" in fight.enemy_effects:
        enemy_effects.append(f"☠️{fight.enemy_effects['poison']}")
    if "burn" in fight.enemy_effects:
        enemy_effects.append(f"🔥{fight.enemy_effects['burn']}")
    if "stun" in fight.enemy_effects:
        enemy_effects.append(f"💫{fight.enemy_effects['stun']}")
    if "slow" in fight.enemy_effects:
        enemy_effects.append(f"❄️{fight.enemy_effects['slow']}")
    if enemy_effects:
        text += f"Эффекты: {' '.join(enemy_effects)}\n"

    text += "\n"

    # Лог боя
    if fight.fight_log:
        text += "📜 **Лог:**\n"
        for log in fight.fight_log[-4:]:
            text += f"• {log}\n"

    if message:
        text += f"\n{message}"

    try:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=get_fight_keyboard(fight),
            parse_mode="Markdown"
        )
    except Exception as e:
        pass

async def enemy_attack_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Цикл атак врага"""
    fight: Fight = context.user_data.get('fight')
    if not fight:
        return

    # Интервал атаки (боссы медленнее)
    base_interval = 2.5 if fight.is_boss else 2.0

    while fight.fight_active and fight.player_hp > 0 and fight.enemy_hp > 0:
        # Замедление
        interval = base_interval
        if "slow" in fight.enemy_effects:
            interval *= 1.5

        await asyncio.sleep(interval)

        if not fight.fight_active or fight.player_hp <= 0 or fight.enemy_hp <= 0:
            break

        # Уменьшаем кулдауны
        for skill_id in list(fight.cooldowns.keys()):
            fight.cooldowns[skill_id] -= 1
            if fight.cooldowns[skill_id] <= 0:
                del fight.cooldowns[skill_id]

        # Уменьшаем эффекты
        for effect in list(fight.player_effects.keys()):
            fight.player_effects[effect] -= 1
            if fight.player_effects[effect] <= 0:
                del fight.player_effects[effect]

        for effect in list(fight.enemy_effects.keys()):
            fight.enemy_effects[effect] -= 1
            if fight.enemy_effects[effect] <= 0:
                del fight.enemy_effects[effect]

        # Уменьшаем спецэффекты игрока
        if fight.invisible > 0:
            fight.invisible -= 1
        if fight.invulnerable > 0:
            fight.invulnerable -= 1

        # Яд на игроке
        if "poison" in fight.player_effects:
            poison_dmg = 5
            fight.player_hp -= poison_dmg
            fight.fight_log.append(f"☠️ Яд: -{poison_dmg} HP")

        # Горение на игроке
        if "burn" in fight.player_effects:
            burn_dmg = 5
            fight.player_hp -= burn_dmg
            fight.fight_log.append(f"🔥 Горение: -{burn_dmg} HP")

        # Яд на враге
        if "poison" in fight.enemy_effects:
            poison_dmg = 5
            fight.enemy_hp -= poison_dmg
            fight.fight_log.append(f"☠️ Яд врагу: -{poison_dmg}")

        # Горение на враге
        if "burn" in fight.enemy_effects:
            burn_dmg = 5
            fight.enemy_hp -= burn_dmg
            fight.fight_log.append(f"🔥 Горение врагу: -{burn_dmg}")

        # Пассивка мага - регенерация маны
        if fight.player.player_class == "mage":
            fight.player_mana = min(fight.player.get_max_mana(), fight.player_mana + 5)

        # Пассивка паладина - регенерация HP
        if fight.player.player_class == "paladin":
            heal = int(fight.player_max_hp * 0.03)
            fight.player_hp = min(fight.player_max_hp, fight.player_hp + heal)

        # Хил от наёмника
        if fight.merc_bonus_heal > 0:
            fight.player_hp = min(fight.player_max_hp, fight.player_hp + fight.merc_bonus_heal)
            fight.fight_log.append(f"💚 Целитель: +{fight.merc_bonus_heal} HP")

        # Мана от наёмника
        if fight.merc_bonus_mana_regen > 0:
            fight.player_mana = min(fight.player.get_max_mana(), fight.player_mana + fight.merc_bonus_mana_regen)

        # Мана от еды
        if fight.food_bonus_mana_regen > 0:
            fight.player_mana = min(fight.player.get_max_mana(), fight.player_mana + fight.food_bonus_mana_regen)

        # Проверка смерти врага от эффектов
        if fight.enemy_hp <= 0:
            # Механика нежити - воскрешение
            if fight.dungeon["mechanic"] == "undead" and not fight.enemy_resurrected and not fight.is_boss:
                fight.enemy_hp = int(fight.enemy_max_hp * 0.3)
                fight.enemy_resurrected = True
                fight.fight_log.append(f"💀 {fight.enemy_name} воскрес!")
            else:
                await end_fight(update, context, victory=True)
                return

        # Проверка смерти игрока от эффектов
        if fight.player_hp <= 0:
            await end_fight(update, context, victory=False)
            return

        # Оглушение - враг пропускает ход
        if "stun" in fight.enemy_effects:
            fight.fight_log.append(f"💫 {fight.enemy_name} оглушён!")
            await update_fight_ui(update, context)
            continue

        # Невидимость - враг не атакует
        if fight.invisible > 0:
            fight.fight_log.append(f"👻 Ты невидим, враг не атакует")
            await update_fight_ui(update, context)
            continue

        # Атака врага
        damage = fight.enemy_damage

        # Неуязвимость
        if fight.invulnerable > 0:
            fight.fight_log.append(f"👼 Божественный щит! Урон заблокирован")
            await update_fight_ui(update, context)
            continue

        # Блок
        if fight.block_next:
            fight.block_next = False
            fight.fight_log.append(f"🛡️ Удар заблокирован!")
            await update_fight_ui(update, context)
            continue

        # Уклонение
        if fight.dodge_next:
            fight.dodge_next = False
            fight.fight_log.append(f"💨 Ты увернулся!")
            await update_fight_ui(update, context)
            continue

        # Барьер поглощает урон
        if fight.barrier > 0:
            absorbed = min(fight.barrier, damage)
            fight.barrier -= absorbed
            damage -= absorbed
            if absorbed > 0:
                fight.fight_log.append(f"🔮 Барьер поглотил {absorbed} урона")

        # Пассивка воина - меньше урона
        if fight.player.player_class == "warrior":
            damage = int(damage * 0.9)

        # Защита уменьшает урон (с бонусами от еды и наёмника)
        defense = fight.player.get_total_defense() + fight.food_bonus_defense + fight.merc_bonus_defense
        damage = max(1, damage - defense // 3)

        fight.player_hp -= damage
        fight.player.stats["damage_taken"] += damage
        fight.fight_log.append(f"👹 {fight.enemy_name}: -{damage} HP")

        # Спецэффекты врага
        if hasattr(fight, 'enemy_special'):
            if "poison" in fight.enemy_special and random.random() < 0.3:
                fight.player_effects["poison"] = 3
                fight.fight_log.append(f"☠️ Ты отравлен!")
            if "burn" in fight.enemy_special and random.random() < 0.3:
                fight.player_effects["burn"] = 3
                fight.fight_log.append(f"🔥 Ты горишь!")

        # Механика подземелья - жар
        if fight.dungeon["mechanic"] == "heat":
            heat_dmg = max(1, 2 - defense // 10)
            fight.player_hp -= heat_dmg
            fight.fight_log.append(f"🌋 Жар: -{heat_dmg} HP")

        # Механика - обвалы
        if fight.dungeon["mechanic"] == "collapse":
            fight.mechanic_timer += 1
            if fight.mechanic_timer >= 15:  # Каждые 30 сек (15 тиков)
                fight.mechanic_timer = 0
                collapse_dmg = random.randint(10, 30)
                fight.player_hp -= collapse_dmg
                fight.fight_log.append(f"⛏️ Обвал: -{collapse_dmg} HP")

        # Механика - хаос (случайные эффекты)
        if fight.dungeon["mechanic"] == "chaos" and random.random() < 0.1:
            chaos_effect = random.choice(["damage", "heal", "mana", "stun"])
            if chaos_effect == "damage":
                chaos_dmg = random.randint(10, 30)
                fight.player_hp -= chaos_dmg
                fight.fight_log.append(f"🌀 Хаос: -{chaos_dmg} HP")
            elif chaos_effect == "heal":
                chaos_heal = random.randint(10, 30)
                fight.player_hp = min(fight.player_max_hp, fight.player_hp + chaos_heal)
                fight.fight_log.append(f"🌀 Хаос: +{chaos_heal} HP")
            elif chaos_effect == "mana":
                fight.player_mana = max(0, fight.player_mana - 20)
                fight.fight_log.append(f"🌀 Хаос: -20 маны")
            elif chaos_effect == "stun":
                fight.enemy_effects["stun"] = 2
                fight.fight_log.append(f"🌀 Хаос: враг оглушён!")

        # Ограничиваем лог
        fight.fight_log = fight.fight_log[-6:]

        if fight.player_hp <= 0:
            await end_fight(update, context, victory=False)
            return

        try:
            await update_fight_ui(update, context)
        except:
            pass

async def enter_dungeon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вход в подземелье"""
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    # Парсим данные: enter_dungeonid_floor
    parts = query.data.split("_")
    dungeon_id = parts[1]
    floor = int(parts[2])

    if player.hp <= 0:
        await query.answer("У тебя нет HP! Отдохни сначала.", show_alert=True)
        return

    dungeon = DUNGEONS[dungeon_id]
    is_boss = (floor == dungeon["floors"])

    # Создаём бой
    fight = Fight(player, dungeon_id, floor, is_boss)
    context.user_data['fight'] = fight

    # Запускаем атаки врага
    fight.enemy_attack_task = asyncio.create_task(enemy_attack_loop(update, context))

    await update_fight_ui(update, context)
    await query.answer("Бой начался!")

async def fight_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обычная атака"""
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if not fight or not fight.fight_active:
        await query.answer()
        return

    player = fight.player
    damage = player.get_total_damage() + fight.food_bonus_damage + fight.merc_bonus_damage

    # Пассивка разбойника - первый удар x2
    if player.player_class == "rogue" and fight.first_attack:
        damage *= 2
        fight.fight_log.append(f"🗡️ Удар из тени!")
    fight.first_attack = False

    # Крит (с бонусами от еды и наёмника)
    crit_chance = player.get_total_crit() + fight.food_bonus_crit + fight.merc_bonus_crit
    is_crit = random.randint(1, 100) <= crit_chance
    if is_crit:
        damage = int(damage * 1.5)
        player.stats["crits"] += 1
        player.quest_stats["crits"] = player.quest_stats.get("crits", 0) + 1
        fight.fight_log.append(f"💥 КРИТ! -{damage} врагу")
        await query.answer("💥 КРИТИЧЕСКИЙ УДАР!")
    else:
        fight.fight_log.append(f"⚔️ Атака: -{damage} врагу")
        await query.answer(f"Атака: -{damage}")

    fight.enemy_hp -= damage
    player.stats["damage_dealt"] += damage

    # Проверка победы
    if fight.enemy_hp <= 0:
        # Механика нежити
        if fight.dungeon["mechanic"] == "undead" and not fight.enemy_resurrected and not fight.is_boss:
            fight.enemy_hp = int(fight.enemy_max_hp * 0.3)
            fight.enemy_resurrected = True
            fight.fight_log.append(f"💀 {fight.enemy_name} воскрес!")
        else:
            await end_fight(update, context, victory=True)
            return

    await update_fight_ui(update, context)

async def fight_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использование скилла"""
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if not fight or not fight.fight_active:
        await query.answer()
        return

    skill_id = query.data.replace("fight_skill_", "")
    player = fight.player
    skills = CLASSES[player.player_class]["skills"]
    skill = skills.get(skill_id)

    if not skill:
        await query.answer("Скилл не найден!")
        return

    # Проверка кулдауна
    if fight.cooldowns.get(skill_id, 0) > 0:
        await query.answer(f"Кулдаун: {fight.cooldowns[skill_id]} сек!")
        return

    # Проверка маны
    if fight.player_mana < skill["mana"]:
        await query.answer("Недостаточно маны!")
        return

    # Тратим ману и ставим кулдаун
    fight.player_mana -= skill["mana"]
    fight.cooldowns[skill_id] = skill["cooldown"]

    # Обрабатываем эффекты скилла
    damage = 0

    # Урон (с бонусами от еды и наёмника)
    if "damage_mult" in skill:
        base_damage = player.get_total_damage() + fight.food_bonus_damage + fight.merc_bonus_damage
        damage = int(base_damage * skill["damage_mult"])

        # Крит (с бонусами)
        crit_chance = player.get_total_crit() + fight.food_bonus_crit + fight.merc_bonus_crit
        if "crit_bonus" in skill:
            crit_chance += skill.get("crit_bonus", 0)

        is_crit = random.randint(1, 100) <= crit_chance
        if is_crit:
            damage = int(damage * 1.5)
            player.stats["crits"] += 1
            player.quest_stats["crits"] = player.quest_stats.get("crits", 0) + 1
            fight.fight_log.append(f"{skill['emoji']} {skill['name']}: -{damage} (КРИТ!)")
        else:
            fight.fight_log.append(f"{skill['emoji']} {skill['name']}: -{damage}")

        # Множественные удары
        hits = skill.get("hits", 1)
        total_damage = damage * hits

        fight.enemy_hp -= total_damage
        player.stats["damage_dealt"] += total_damage

        if hits > 1:
            fight.fight_log[-1] = f"{skill['emoji']} {skill['name']}: -{total_damage} ({hits}x)"

    # Блок
    if skill.get("block"):
        fight.block_next = True
        fight.fight_log.append(f"{skill['emoji']} Щит активирован!")

    # Уклонение
    if skill.get("dodge"):
        fight.dodge_next = True
        fight.fight_log.append(f"{skill['emoji']} Готов к уклонению!")

    # Невидимость
    if "invisibility" in skill:
        fight.invisible = skill["invisibility"]
        fight.fight_log.append(f"{skill['emoji']} Ты исчез в тенях!")

    # Неуязвимость
    if "invulnerable" in skill:
        fight.invulnerable = skill["invulnerable"]
        fight.fight_log.append(f"{skill['emoji']} Божественная защита!")

    # Барьер
    if "absorb" in skill:
        fight.barrier = skill["absorb"]
        fight.fight_log.append(f"{skill['emoji']} Барьер: {fight.barrier} HP")

    # Оглушение
    if "stun" in skill:
        fight.enemy_effects["stun"] = skill["stun"]
        fight.fight_log.append(f"💫 Враг оглушён на {skill['stun']} сек!")

    # Замедление
    if "slow" in skill:
        fight.enemy_effects["slow"] = skill["slow"]
        fight.fight_log.append(f"❄️ Враг замедлен!")

    # Яд
    if "poison" in skill:
        fight.enemy_effects["poison"] = skill.get("poison_duration", 4)
        fight.fight_log.append(f"☠️ Враг отравлен!")

    # Лечение
    if "heal" in skill:
        heal = skill["heal"]
        fight.player_hp = min(fight.player_max_hp, fight.player_hp + heal)
        fight.fight_log.append(f"💚 +{heal} HP")

    # Вампиризм
    if "lifesteal" in skill and damage > 0:
        heal = int(damage * skill["lifesteal"])
        fight.player_hp = min(fight.player_max_hp, fight.player_hp + heal)
        fight.fight_log.append(f"🩸 Вампиризм: +{heal} HP")

    # Очищение
    if skill.get("cleanse"):
        fight.player_effects.clear()
        fight.fight_log.append(f"✨ Эффекты сняты!")

    await query.answer(f"{skill['name']}!")

    # Проверка победы
    if fight.enemy_hp <= 0:
        if fight.dungeon["mechanic"] == "undead" and not fight.enemy_resurrected and not fight.is_boss:
            fight.enemy_hp = int(fight.enemy_max_hp * 0.3)
            fight.enemy_resurrected = True
            fight.fight_log.append(f"💀 {fight.enemy_name} воскрес!")
        else:
            await end_fight(update, context, victory=True)
            return

    await update_fight_ui(update, context)

async def fight_potion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использование зелья в бою"""
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if not fight or not fight.fight_active:
        await query.answer()
        return

    potion_id = query.data.replace("fight_potion_", "")
    player = fight.player

    if player.inventory.get(potion_id, 0) <= 0:
        await query.answer("У тебя нет этого зелья!")
        return

    item = ITEMS.get(potion_id)
    if not item:
        await query.answer("Предмет не найден!")
        return

    player.inventory[potion_id] -= 1
    if player.inventory[potion_id] <= 0:
        del player.inventory[potion_id]

    # Лечение
    if "heal" in item:
        heal = item["heal"]
        fight.player_hp = min(fight.player_max_hp, fight.player_hp + heal)
        fight.fight_log.append(f"❤️ +{heal} HP")

    # Мана
    if "mana" in item:
        mana = item["mana"]
        fight.player_mana = min(player.get_max_mana(), fight.player_mana + mana)
        fight.fight_log.append(f"💙 +{mana} маны")

    # Противоядие
    if item.get("cleanse_poison"):
        if "poison" in fight.player_effects:
            del fight.player_effects["poison"]
            fight.fight_log.append(f"🧪 Яд нейтрализован!")

    await query.answer(f"Использовано: {item['name']}")
    await update_fight_ui(update, context)

async def fight_flee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Побег из боя"""
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if fight:
        fight.fight_active = False
        if fight.enemy_attack_task:
            fight.enemy_attack_task.cancel()

        # Сохраняем HP
        fight.player.hp = max(1, fight.player_hp)
        fight.player.mana = fight.player_mana
        save_data()

    context.user_data.pop('fight', None)
    await query.answer("Ты сбежал!")
    await show_main_menu(update, context)

async def end_fight(update: Update, context: ContextTypes.DEFAULT_TYPE, victory: bool):
    """Завершение боя"""
    fight: Fight = context.user_data.get('fight')
    if not fight:
        return

    fight.fight_active = False
    if fight.enemy_attack_task:
        fight.enemy_attack_task.cancel()

    player = fight.player

    # Уменьшаем контракт наёмника
    if player.mercenary:
        player.mercenary["fights_left"] -= 1
        if player.mercenary["fights_left"] <= 0:
            player.mercenary = None

    if victory:
        # Награды
        exp_gain = fight.exp_reward
        gold_gain = fight.gold_reward

        player.exp += exp_gain
        player.gold += gold_gain
        player.stats["kills"] += 1
        player.stats["gold_earned"] += gold_gain

        # Обновляем статы для квестов
        player.quest_stats["kills"] = player.quest_stats.get("kills", 0) + 1
        player.quest_stats["floors"] = player.quest_stats.get("floors", 0) + 1
        player.quest_stats["gold_earned"] = player.quest_stats.get("gold_earned", 0) + gold_gain

        if fight.is_boss:
            player.stats["boss_kills"] += 1
            player.quest_stats["boss_kills"] = player.quest_stats.get("boss_kills", 0) + 1
            player.dungeon_progress[fight.dungeon_id]["boss_killed"] = True

        # Обновляем прогресс
        if fight.floor > player.dungeon_progress[fight.dungeon_id]["max_floor"]:
            player.dungeon_progress[fight.dungeon_id]["max_floor"] = fight.floor

        # Сохраняем HP/ману
        player.hp = max(1, fight.player_hp)
        player.mana = fight.player_mana

        text = f"🎉 **ПОБЕДА!**\n\n"
        text += f"Враг: {fight.enemy_emoji} {fight.enemy_name}\n\n"
        text += f"⭐ +{exp_gain} опыта\n"
        text += f"💰 +{gold_gain} золота\n"

        # Дроп ресурсов
        resource = fight.dungeon["drop_resource"]
        resource_count = random.randint(1, 3) if not fight.is_boss else random.randint(3, 7)
        player.resources[resource] = player.resources.get(resource, 0) + resource_count
        text += f"{ITEMS[resource]['emoji']} +{resource_count} {ITEMS[resource]['name']}\n"

        # Левел ап
        leveled = False
        while player.exp >= player.exp_needed:
            player.level_up()
            leveled = True

        if leveled:
            text += f"\n🎊 **УРОВЕНЬ ПОВЫШЕН!** Теперь ты {player.level} уровня!\n"

        # Дроп предметов (шанс)
        drop_chance = 15 + (15 if fight.is_boss else 0)
        if random.randint(1, 100) <= drop_chance:
            # Выбираем предмет по уровню
            possible_items = [k for k, v in ITEMS.items()
                           if v.get("type") in ["weapon", "armor", "accessory"]
                           and v.get("price", 0) <= player.level * 60 + 200]
            if possible_items:
                drop_id = random.choice(possible_items)
                drop_item = ITEMS[drop_id]
                player.inventory[drop_id] = player.inventory.get(drop_id, 0) + 1
                text += f"\n🎁 Выпал: {drop_item['emoji']} {drop_item['name']}!"

        # Легендарный дроп с финального босса
        if fight.is_boss and fight.dungeon.get("legendary_drop") and random.randint(1, 100) <= 5:
            legendary_set = LEGENDARY_SETS.get(player.player_class)
            if legendary_set:
                piece_type = random.choice(list(legendary_set["pieces"].keys()))
                piece = legendary_set["pieces"][piece_type]
                if piece["name"] not in player.legendary_pieces:
                    player.legendary_pieces.append(piece["name"])
                    text += f"\n✨ **ЛЕГЕНДАРНЫЙ ДРОП!** {piece['emoji']} {piece['name']}!"

        # Достижения
        new_achievements = player.check_achievements()
        for ach_id in new_achievements:
            ach = ACHIEVEMENTS[ach_id]
            text += f"\n🏆 Достижение: {ach['emoji']} {ach['name']}!"

        # Проверка достижения скорости
        fight_time = (datetime.now() - fight.start_time).total_seconds()
        if fight.is_boss and fight_time <= 30 and "speedrun" not in player.achievements:
            player.achievements.append("speedrun")
            text += f"\n🏆 Достижение: ⚡ Скоростной!"

        # Проверка выживания с 1 HP
        if player.hp == 1 and "survivor" not in player.achievements:
            player.achievements.append("survivor")
            text += f"\n🏆 Достижение: 💪 Выживший!"

        text += f"\n\n❤️ HP: {player.hp}/{player.get_max_hp()}"

        # Кнопки
        keyboard = []
        next_floor = fight.floor + 1
        if next_floor <= fight.dungeon["floors"]:
            keyboard.append([InlineKeyboardButton(f"⚔️ Следующий этаж ({next_floor})",
                           callback_data=f"enter_{fight.dungeon_id}_{next_floor}")])
        keyboard.append([InlineKeyboardButton("🔙 В меню", callback_data="main_menu")])

    else:
        # Поражение
        player.stats["deaths"] += 1
        gold_lost = int(player.gold * 0.1)
        player.gold -= gold_lost
        player.hp = 0
        player.mana = fight.player_mana

        text = f"💀 **ПОРАЖЕНИЕ**\n\n"
        text += f"Враг: {fight.enemy_emoji} {fight.enemy_name}\n\n"
        text += f"💸 Потеряно: {gold_lost} золота\n"
        text += f"\n_Отдохни и попробуй снова!_"

        keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="main_menu")]]

    save_data()
    context.user_data.pop('fight', None)

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        pass

# ============ MAIN ============

def main():
    """Запуск бота"""
    load_data()

    app = ApplicationBuilder().token("8550867725:AAHAhxhwn8Fu_6_m-fj5io5I0cjAUzCXlM4").build()

    # Команды
    app.add_handler(CommandHandler("start", start))

    # Выбор класса
    app.add_handler(CallbackQueryHandler(select_class, pattern="^class_"))

    # Главное меню
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))

    # Подземелья
    app.add_handler(CallbackQueryHandler(show_dungeons, pattern="^dungeons$"))
    app.add_handler(CallbackQueryHandler(show_dungeon_info, pattern="^dungeon_"))
    app.add_handler(CallbackQueryHandler(enter_dungeon, pattern="^enter_"))

    # Бой
    app.add_handler(CallbackQueryHandler(fight_attack, pattern="^fight_attack$"))
    app.add_handler(CallbackQueryHandler(fight_skill, pattern="^fight_skill_"))
    app.add_handler(CallbackQueryHandler(fight_potion, pattern="^fight_potion_"))
    app.add_handler(CallbackQueryHandler(fight_flee, pattern="^fight_flee$"))

    # Таверна
    app.add_handler(CallbackQueryHandler(show_tavern, pattern="^tavern$"))
    app.add_handler(CallbackQueryHandler(show_quests, pattern="^quests$"))
    app.add_handler(CallbackQueryHandler(claim_quests, pattern="^claim_quests$"))
    app.add_handler(CallbackQueryHandler(show_food, pattern="^food$"))
    app.add_handler(CallbackQueryHandler(buy_food, pattern="^buy_food_"))
    app.add_handler(CallbackQueryHandler(show_mercenaries, pattern="^mercenaries$"))
    app.add_handler(CallbackQueryHandler(hire_mercenary, pattern="^hire_"))
    app.add_handler(CallbackQueryHandler(show_blacksmith, pattern="^blacksmith$"))
    app.add_handler(CallbackQueryHandler(blacksmith_upgrade, pattern="^upgrade_"))
    app.add_handler(CallbackQueryHandler(show_alchemist, pattern="^alchemist$"))
    app.add_handler(CallbackQueryHandler(craft_potion, pattern="^craft_"))
    app.add_handler(CallbackQueryHandler(show_leaderboard, pattern="^leaderboard$"))

    # Инвентарь и экипировка
    app.add_handler(CallbackQueryHandler(show_inventory, pattern="^inventory$"))
    app.add_handler(CallbackQueryHandler(show_equipment, pattern="^equipment$"))
    app.add_handler(CallbackQueryHandler(show_equip_menu, pattern="^equip_menu$"))
    app.add_handler(CallbackQueryHandler(equip_item, pattern="^equip_(weapon|armor|accessory|legendary)_"))
    app.add_handler(CallbackQueryHandler(unequip_item, pattern="^unequip_"))
    app.add_handler(CallbackQueryHandler(show_shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(show_shop_category, pattern="^shop_cat_"))
    app.add_handler(CallbackQueryHandler(buy_item, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(show_sell_menu, pattern="^sell_menu$"))
    app.add_handler(CallbackQueryHandler(sell_item, pattern="^sell_"))
    app.add_handler(CallbackQueryHandler(show_titles_menu, pattern="^titles_menu$"))
    app.add_handler(CallbackQueryHandler(set_title, pattern="^set_title_"))

    # Остальное
    app.add_handler(CallbackQueryHandler(rest, pattern="^rest$"))
    app.add_handler(CallbackQueryHandler(show_daily, pattern="^daily$"))
    app.add_handler(CallbackQueryHandler(show_achievements, pattern="^achievements$"))
    app.add_handler(CallbackQueryHandler(show_stats, pattern="^stats$"))

    print("🎮 Бот 'Тени Подземелий' запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
