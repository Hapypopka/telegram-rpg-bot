"""
Таверна - еда, наёмники, кузнец, алхимик
"""

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

MERCENARIES = {
    "guard": {
        "name": "Стражник",
        "emoji": "🛡️",
        "price": 200,
        "duration": 3,
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
