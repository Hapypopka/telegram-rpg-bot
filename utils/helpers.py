"""
Вспомогательные функции для UI
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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

    # Скиллы класса
    if player.player_class:
        class_data = CLASSES[player.player_class]
        skills = class_data.get("skills", {})
        skill_row = []
        for i, (skill_id, skill) in enumerate(skills.items()):
            req_level = SKILL_LEVELS.get(i, 1)
            is_locked = player.level < req_level
            cd = fight.cooldowns.get(skill_id, 0)

            if is_locked:
                btn_text = f"🔒 Ур.{req_level}"
            elif cd > 0:
                btn_text = f"{skill['emoji']} ({cd})"
            else:
                btn_text = f"{skill['emoji']} {skill['name']}"
            skill_row.append(InlineKeyboardButton(btn_text, callback_data=f"fight_skill_{skill_id}"))
        if skill_row:
            buttons.append(skill_row)

    # Зелья
    row3 = [
        InlineKeyboardButton("❤️ HP зелье", callback_data="fight_potion_hp"),
        InlineKeyboardButton("💙 Мана зелье", callback_data="fight_potion_mana"),
    ]
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
