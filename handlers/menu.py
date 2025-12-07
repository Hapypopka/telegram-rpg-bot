"""
Обработчики главного меню и профиля
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from data import CLASSES
from utils.storage import get_player, save_data
from utils.helpers import create_hp_bar, create_mana_bar

# Состояния для ConversationHandler
WAITING_NAME = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    player = get_player(user.id)

    save_data()

    if not player.name:
        # Запросить никнейм
        await update.message.reply_text(
            "🏰 **Добро пожаловать в Тени Подземелий!**\n\n"
            "Как тебя зовут, герой?\n\n"
            "_Введи своё имя (3-20 символов):_",
            parse_mode="Markdown"
        )
        return WAITING_NAME
    elif not player.player_class:
        await show_class_selection(update, context)
    else:
        await main_menu(update, context)
    return ConversationHandler.END


async def set_player_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить имя игрока"""
    name = update.message.text.strip()

    if len(name) < 3:
        await update.message.reply_text(
            "❌ Имя слишком короткое! Минимум 3 символа.\n"
            "Попробуй ещё раз:"
        )
        return WAITING_NAME

    if len(name) > 20:
        await update.message.reply_text(
            "❌ Имя слишком длинное! Максимум 20 символов.\n"
            "Попробуй ещё раз:"
        )
        return WAITING_NAME

    player = get_player(update.effective_user.id)
    player.name = name
    save_data()

    await update.message.reply_text(
        f"✨ Отлично, **{name}**! Теперь выбери свой класс.",
        parse_mode="Markdown"
    )

    await show_class_selection(update, context)
    return ConversationHandler.END


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать главное меню"""
    user_id = update.effective_user.id
    player = get_player(user_id)

    hp_bar = create_hp_bar(player.hp, player.get_max_hp())
    mana_bar = create_mana_bar(player.mana, player.get_max_mana())

    title_text = f"『{player.title}』 " if player.title else ""
    class_data = CLASSES.get(player.player_class, {})
    class_name = class_data.get("name", "Неизвестно")
    class_emoji = class_data.get("emoji", "")

    text = f"""🏰 **ТЕНИ ПОДЗЕМЕЛИЙ** 🏰

{title_text}**{player.name}**
{class_emoji} {class_name} | Ур. {player.level}

❤️ HP: [{hp_bar}] {player.hp}/{player.get_max_hp()}
💙 MP: [{mana_bar}] {player.mana}/{player.get_max_mana()}
⭐ Опыт: {player.exp}/{player.exp_to_level}
💰 Золото: {player.gold}

📍 Текущее подземелье: {player.current_dungeon or "Нет"}
🏠 Этаж: {player.current_floor}"""

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Подземелья", callback_data="dungeons"),
            InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")
        ],
        [
            InlineKeyboardButton("👤 Профиль", callback_data="profile"),
            InlineKeyboardButton("🏆 Достижения", callback_data="achievements")
        ],
        [
            InlineKeyboardButton("🍺 Таверна", callback_data="tavern"),
            InlineKeyboardButton("🛒 Магазин", callback_data="shop")
        ],
        [
            InlineKeyboardButton("📜 Квесты", callback_data="quests"),
            InlineKeyboardButton("🎁 Ежедневка", callback_data="daily")
        ],
        [
            InlineKeyboardButton("💤 Отдых", callback_data="rest")
        ]
    ]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def show_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать выбор класса"""
    text = """🎮 **ВЫБОР КЛАССА**

Выбери свой путь, герой!

"""
    keyboard = []

    for class_id, class_data in CLASSES.items():
        text += f"{class_data['emoji']} **{class_data['name']}**\n"
        text += f"_{class_data['description']}_\n"
        text += f"❤️ HP: {class_data['base_hp']} | ⚔️ ATK: {class_data['base_damage']} | 🛡️ DEF: {class_data['base_defense']}\n\n"

        keyboard.append([InlineKeyboardButton(
            f"{class_data['emoji']} {class_data['name']}",
            callback_data=f"select_class_{class_id}"
        )])

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def select_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбрать класс"""
    query = update.callback_query
    await query.answer()

    class_id = query.data.replace("select_class_", "")
    player = get_player(query.from_user.id)

    if class_id in CLASSES:
        class_data = CLASSES[class_id]
        player.player_class = class_id
        player.hp = class_data["base_hp"]
        player.mana = class_data["base_mana"]
        save_data()

        await query.edit_message_text(
            f"✨ Ты выбрал класс **{class_data['name']}**!\n\n"
            f"Твои навыки:\n" +
            "\n".join([f"{s['emoji']} {s['name']} - {s['description']}" for s in class_data['skills'].values()]) +
            "\n\nДобро пожаловать в мир Теней Подземелий!",
            parse_mode="Markdown"
        )

        # Показать меню через секунду
        await main_menu(update, context)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать профиль игрока"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)
    class_data = CLASSES.get(player.player_class, {})

    # Подсчёт статов
    total_damage = player.get_total_damage()
    total_defense = player.get_total_defense()
    total_crit = player.get_crit_chance()

    # Легендарный сет
    set_pieces = player.count_legendary_pieces()
    set_bonus_text = ""
    if set_pieces >= 2:
        from data import LEGENDARY_SETS
        if player.player_class in LEGENDARY_SETS:
            set_data = LEGENDARY_SETS[player.player_class]
            set_bonus_text = f"\n\n✨ Бонус сета ({set_pieces}/4):\n"
            set_bonus_text += f"  2 части: {set_data['bonus_2']}\n"
            if set_pieces >= 4:
                set_bonus_text += f"  4 части: {set_data['bonus_4']}"

    title_text = f"『{player.title}』\n" if player.title else ""

    text = f"""👤 **ПРОФИЛЬ**

{title_text}**{player.name}**
{class_data.get('emoji', '')} {class_data.get('name', 'Неизвестно')}

📊 **Статистика:**
Уровень: {player.level}
Опыт: {player.exp}/{player.exp_to_level}
Золото: {player.gold} 💰

⚔️ **Боевые характеристики:**
❤️ HP: {player.hp}/{player.get_max_hp()}
💙 Мана: {player.mana}/{player.get_max_mana()}
⚔️ Урон: {total_damage}
🛡️ Защита: {total_defense}
🎯 Крит: {total_crit}%

📈 **Прогресс:**
Убито врагов: {player.stats.get('kills', 0)}
Убито боссов: {player.stats.get('boss_kills', 0)}
Пройдено этажей: {player.stats.get('floors', 0)}
Квестов выполнено: {player.stats.get('quests_done', 0)}{set_bonus_text}"""

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Снаряжение", callback_data="equipment"),
            InlineKeyboardButton("🏷️ Титулы", callback_data="titles")
        ],
        [
            InlineKeyboardButton("✨ Умения", callback_data="skills"),
            InlineKeyboardButton("📊 Статистика", callback_data="stats")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu")]
    ]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


# Уровни открытия умений
SKILL_LEVELS = {
    0: 1,   # Первое умение - с 1 уровня
    1: 3,   # Второе - с 3 уровня
    2: 6,   # Третье - с 6 уровня
    3: 10   # Ульта - с 10 уровня
}


async def show_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать умения игрока"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)
    class_data = CLASSES.get(player.player_class, {})

    text = f"✨ **УМЕНИЯ** ({class_data.get('name', '')})\n\n"
    text += f"📖 Пассивка: _{class_data.get('passive', 'Нет')}_\n\n"

    skills = list(class_data.get("skills", {}).items())

    for i, (skill_id, skill) in enumerate(skills):
        req_level = SKILL_LEVELS.get(i, 1)
        is_unlocked = player.level >= req_level
        is_ultimate = skill.get("ultimate", False)

        status = "✅" if is_unlocked else f"🔒 Ур.{req_level}"
        ult_mark = " ⭐УЛЬТА" if is_ultimate else ""

        text += f"{skill['emoji']} **{skill['name']}**{ult_mark} {status}\n"

        if is_unlocked:
            text += f"  _{skill['description']}_\n"
            text += f"  💙 Мана: {skill.get('mana', 0)} | ⏱ КД: {skill.get('cooldown', 0)} ходов\n"

            # Детальное описание эффектов
            effects = []
            if "damage_mult" in skill:
                hits = skill.get("hits", 1)
                if hits > 1:
                    effects.append(f"x{skill['damage_mult']} урон ({hits} ударов)")
                else:
                    effects.append(f"x{skill['damage_mult']} урон")
            if "heal" in skill:
                effects.append(f"+{skill['heal']} HP")
            if "stun" in skill:
                effects.append(f"оглушение {skill['stun']} хода")
            if "poison" in skill:
                effects.append(f"яд {skill['poison']} урона")
            if skill.get("block"):
                effects.append("блок атаки")
            if skill.get("dodge"):
                effects.append("уклонение")
            if "absorb" in skill:
                effects.append(f"барьер {skill['absorb']} HP")
            if "lifesteal" in skill:
                effects.append(f"вампиризм {int(skill['lifesteal']*100)}%")
            if "invulnerable" in skill:
                effects.append(f"неуязвимость {skill['invulnerable']} хода")
            if "invisibility" in skill:
                effects.append(f"невидимость {skill['invisibility']} хода")

            if effects:
                text += f"  📌 Эффекты: {', '.join(effects)}\n"
        else:
            text += f"  _Откроется на {req_level} уровне_\n"

        text += "\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать подробную статистику"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    text = f"""📊 **СТАТИСТИКА**

⚔️ **Бой:**
Убито врагов: {player.stats.get('kills', 0)}
Убито боссов: {player.stats.get('boss_kills', 0)}
Критических ударов: {player.stats.get('crits', 0)}
Смертей: {player.stats.get('deaths', 0)}

🏰 **Подземелья:**
Пройдено этажей: {player.stats.get('floors', 0)}
Максимальный этаж: {player.stats.get('max_floor', 0)}

💰 **Экономика:**
Заработано золота: {player.stats.get('gold_earned', 0)}
Потрачено золота: {player.stats.get('gold_spent', 0)}

📜 **Квесты:**
Выполнено квестов: {player.stats.get('quests_done', 0)}
Ежедневок получено: {player.stats.get('dailies_claimed', 0)}"""

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="profile")]]

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )
