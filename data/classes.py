"""
Классы персонажей
"""

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
