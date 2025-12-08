"""
Классы персонажей
"""

# Таланты для каждого класса
# Каждые 3 уровня игрок выбирает 1 талант из 2-3 вариантов
TALENTS = {
    "warrior": {
        # Уровень 3: первый выбор
        3: [
            {"id": "w_tough", "name": "Закалка", "emoji": "💪", "desc": "+30 HP", "bonus": {"hp": 30}},
            {"id": "w_power", "name": "Сила", "emoji": "⚔️", "desc": "+5 урона", "bonus": {"damage": 5}},
            {"id": "w_armor", "name": "Броня", "emoji": "🛡️", "desc": "+5 защиты", "bonus": {"defense": 5}},
        ],
        # Уровень 6
        6: [
            {"id": "w_berserker", "name": "Берсерк", "emoji": "🔥", "desc": "+10% крита", "bonus": {"crit": 10}},
            {"id": "w_tank", "name": "Танк", "emoji": "🧱", "desc": "+50 HP, +3 защиты", "bonus": {"hp": 50, "defense": 3}},
        ],
        # Уровень 9
        9: [
            {"id": "w_vampire", "name": "Вампиризм", "emoji": "🩸", "desc": "+5% вампиризма", "bonus": {"lifesteal": 0.05}},
            {"id": "w_iron", "name": "Железная воля", "emoji": "🪨", "desc": "+8 защиты", "bonus": {"defense": 8}},
            {"id": "w_fury", "name": "Ярость", "emoji": "💢", "desc": "+8 урона", "bonus": {"damage": 8}},
        ],
        # Уровень 12
        12: [
            {"id": "w_block", "name": "Мастер блока", "emoji": "🛡️", "desc": "+10% шанса блока", "bonus": {"block": 10}},
            {"id": "w_crit_dmg", "name": "Разрушитель", "emoji": "💥", "desc": "+15% урона криты", "bonus": {"crit": 8, "damage": 5}},
        ],
        # Уровень 15
        15: [
            {"id": "w_titan", "name": "Титан", "emoji": "👑", "desc": "+100 HP, +5 урона", "bonus": {"hp": 100, "damage": 5}},
            {"id": "w_warlord", "name": "Полководец", "emoji": "⚔️", "desc": "+12 урона, +5% крита", "bonus": {"damage": 12, "crit": 5}},
        ],
    },
    "mage": {
        3: [
            {"id": "m_intellect", "name": "Интеллект", "emoji": "🧠", "desc": "+30 маны", "bonus": {"mana": 30}},
            {"id": "m_power", "name": "Мощь", "emoji": "✨", "desc": "+5 урона", "bonus": {"damage": 5}},
            {"id": "m_focus", "name": "Концентрация", "emoji": "🎯", "desc": "+7% крита", "bonus": {"crit": 7}},
        ],
        6: [
            {"id": "m_scholar", "name": "Учёный", "emoji": "📚", "desc": "+50 маны, +3 урона", "bonus": {"mana": 50, "damage": 3}},
            {"id": "m_battlemage", "name": "Боевой маг", "emoji": "⚡", "desc": "+20 HP, +5 урона", "bonus": {"hp": 20, "damage": 5}},
        ],
        9: [
            {"id": "m_regen", "name": "Реген маны", "emoji": "💠", "desc": "+5 маны за ход", "bonus": {"mana_regen": 5}},
            {"id": "m_fire_master", "name": "Огненный мастер", "emoji": "🔥", "desc": "+25% сопр. огню, +5 урона", "bonus": {"fire_res": 25, "damage": 5}},
            {"id": "m_arcane", "name": "Тайная магия", "emoji": "🔮", "desc": "+10 урона", "bonus": {"damage": 10}},
        ],
        12: [
            {"id": "m_lifetap", "name": "Кража жизни", "emoji": "🩸", "desc": "+5% вампиризма", "bonus": {"lifesteal": 0.05}},
            {"id": "m_barrier", "name": "Защитник", "emoji": "🛡️", "desc": "+40 HP, +5 защиты", "bonus": {"hp": 40, "defense": 5}},
        ],
        15: [
            {"id": "m_archmage", "name": "Архимаг", "emoji": "👑", "desc": "+80 маны, +10 урона", "bonus": {"mana": 80, "damage": 10}},
            {"id": "m_destroyer", "name": "Разрушитель миров", "emoji": "☄️", "desc": "+15 урона, +10% крита", "bonus": {"damage": 15, "crit": 10}},
        ],
    },
    "archer": {
        3: [
            {"id": "a_agility", "name": "Ловкость", "emoji": "💨", "desc": "+5% уклонения", "bonus": {"dodge": 5}},
            {"id": "a_precision", "name": "Точность", "emoji": "🎯", "desc": "+8% крита", "bonus": {"crit": 8}},
            {"id": "a_power", "name": "Сила лука", "emoji": "🏹", "desc": "+5 урона", "bonus": {"damage": 5}},
        ],
        6: [
            {"id": "a_swift", "name": "Скорость", "emoji": "⚡", "desc": "+5% двойного удара", "bonus": {"double_hit": 5}},
            {"id": "a_survivor", "name": "Выживание", "emoji": "❤️", "desc": "+40 HP, +3% уклонения", "bonus": {"hp": 40, "dodge": 3}},
        ],
        9: [
            {"id": "a_poison_master", "name": "Мастер ядов", "emoji": "☠️", "desc": "+25% сопр. яду, +5 урона", "bonus": {"poison_res": 25, "damage": 5}},
            {"id": "a_crit_master", "name": "Мастер критов", "emoji": "💥", "desc": "+12% крита", "bonus": {"crit": 12}},
            {"id": "a_stealth", "name": "Тень", "emoji": "🌑", "desc": "+8% уклонения", "bonus": {"dodge": 8}},
        ],
        12: [
            {"id": "a_double_master", "name": "Скорострел", "emoji": "⚡", "desc": "+10% двойного удара", "bonus": {"double_hit": 10}},
            {"id": "a_vampire", "name": "Вампир", "emoji": "🩸", "desc": "+7% вампиризма", "bonus": {"lifesteal": 0.07}},
        ],
        15: [
            {"id": "a_assassin", "name": "Убийца", "emoji": "🗡️", "desc": "+15% крита, +8 урона", "bonus": {"crit": 15, "damage": 8}},
            {"id": "a_phantom", "name": "Фантом", "emoji": "👻", "desc": "+12% уклонения, +5% двойного удара", "bonus": {"dodge": 12, "double_hit": 5}},
        ],
    },
}

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
    }
}
