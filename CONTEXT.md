# RPG Telegram Bot - "Тени Подземелий"

## Структура проекта

```
БОТ/
├── bot.py              # Главный файл, регистрация хэндлеров
├── config.py           # BOT_TOKEN и DATA_FILE
├── data/
│   ├── __init__.py     # Экспорт всех данных
│   ├── classes.py      # CLASSES - классы персонажей (воин, маг, лучник)
│   ├── dungeons.py     # DUNGEONS - подземелья
│   ├── items.py        # ITEMS, LEGENDARY_SETS - предметы и сеты
│   ├── quests.py       # QUESTS - квесты
│   └── tavern.py       # FOOD_MENU, MERCENARIES, BLACKSMITH_UPGRADES, ALCHEMY_RECIPES
├── handlers/
│   ├── menu.py         # start, main_menu, show_profile, show_skills, set_player_name
│   ├── combat.py       # fight_attack, fight_block, fight_skill, fight_potion, fight_flee
│   ├── dungeon.py      # show_dungeons, enter_dungeon, next_floor, active_fights
│   ├── tavern.py       # show_tavern, show_blacksmith, show_alchemist, show_quests
│   ├── inventory.py    # show_inventory, show_equipment, equip_item, show_shop
│   └── misc.py         # show_achievements, show_daily, claim_daily, rest, show_titles
├── models/
│   ├── player.py       # Player класс с сериализацией и методами статов
│   └── fight.py        # Fight класс - состояние боя
├── utils/
│   ├── storage.py      # load_data, save_data, get_player, players_data
│   └── helpers.py      # create_hp_bar, get_fight_keyboard, update_fight_ui
└── CONTEXT.md          # Этот файл
```

## Основные механики

### Регистрация (handlers/menu.py)
- ConversationHandler для ввода никнейма (3-20 символов)
- Затем выбор класса
- Состояние WAITING_NAME = 1

### Классы (data/classes.py)
Только 3 класса: warrior, mage, archer
- У каждого 4 умения
- Умения открываются по уровням: 1, 3, 6, 10 (ульта)
- SKILL_LEVELS = {0: 1, 1: 3, 2: 6, 3: 10}

### Боевая система (handlers/combat.py, models/fight.py)
- Пошаговый бой
- Атака, блок, умения, зелья, побег
- Эффекты: яд, оглушение, замедление, невидимость, барьер
- После победы: опыт, золото, лут

### Подземелья (data/dungeons.py)
- 5 подземелий с разными уровнями сложности
- Каждое имеет этажи и босса
- Враги генерируются по dungeon["enemies"]

### Инвентарь (handlers/inventory.py)
- equipment: weapon, armor, accessory
- legendary_equipment: helmet, chest, gloves, boots
- inventory: dict {item_id: count}

### Аксессуары (data/items.py)
- crit_bonus, damage_bonus, defense_bonus, hp_bonus
- lifesteal, mana_bonus, dodge_bonus
- berserker (больше урона при низком HP)

### Player класс (models/player.py)
```python
class Player:
    user_id, name, player_class
    level, exp, exp_to_level, gold
    hp, mana
    inventory: dict
    equipment: {weapon, armor, accessory}
    legendary_equipment: {helmet, chest, gloves, boots}
    blacksmith_upgrades: dict
    current_dungeon, current_floor
    stats: {kills, boss_kills, deaths, floors, max_floor, crits, gold_earned, gold_spent, quests_done, dailies_claimed}
    quest_progress, completed_quests, achievements, titles, title
    last_daily, daily_streak, food_buffs, mercenary
```

### Сохранение (utils/storage.py)
- players_data: dict {user_id: Player}
- save_data() сохраняет в players_data.json
- get_player(user_id) создает нового если нет

## GitHub
- Репозиторий: https://github.com/Hapypopka/telegram-rpg-bot.git
- Сервер: /root/telegram_rpg/

## Команды на сервере
```bash
cd /root/telegram_rpg
git pull origin main
rm players_data.json  # сбросить игроков
python bot.py
```

## TODO / Известные проблемы
- Квесты не засчитываются (нужно добавить вызовы обновления прогресса)
- Ачивки не засчитываются (нужно добавить проверки при действиях)
