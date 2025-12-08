"""
Обработчики боевой системы
"""

import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import CLASSES, DUNGEONS, ITEMS, RARITY_EMOJI, EPIC_SETS
from utils.storage import get_player, save_data

# Редкие предметы, которые могут выпасть с мобов (по подземельям)
RARE_DROPS = {
    "forest": [
        "steel_sword", "steel_helm", "leather_gloves", "steel_boots",
        "lucky_ring", "life_pendant"
    ],
    "mines": [
        "steel_sword", "magic_staff", "steel_helm", "mage_hood",
        "plate_armor", "steel_gauntlets", "power_amulet"
    ],
    "crypt": [
        "shadow_dagger", "frost_staff", "steel_pauldrons", "mage_robe",
        "plate_legs", "vampire_ring", "shadow_medallion"
    ],
    "abyss": [
        "flame_sword", "frost_staff", "shadow_dagger",
        "steel_gauntlets", "mage_gloves", "swift_boots",
        "berserker_ring", "mana_crystal_necklace"
    ],
    "chaos": [
        "flame_sword", "frost_staff", "shadow_dagger",
        "vampire_ring", "berserker_ring", "shadow_medallion"
    ]
}

# Эпические предметы с боссов (по подземельям)
# Босс гарантированно дропает 1 эпик из своего сета
EPIC_BOSS_DROPS = {
    "forest": ["titans_blade", "titan_helm", "titan_shoulders", "titan_plate",
               "titan_gauntlets", "titan_boots", "titan_ring", "titan_amulet"],
    "mines": ["archmage_staff", "archmage_crown", "archmage_mantle", "archmage_robe",
              "archmage_gloves", "archmage_boots", "archmage_ring", "archmage_pendant"],
    "crypt": ["phantom_bow", "phantom_mask", "phantom_cape", "phantom_cloak",
              "phantom_gloves", "phantom_boots", "phantom_ring", "phantom_necklace"]
}
from utils.helpers import update_fight_ui, create_hp_bar
from .dungeon import get_active_fight, remove_active_fight, active_fights


async def fight_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обычная атака"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)
    fight = get_active_fight(query.from_user.id)

    if not fight or not fight.fight_active:
        await query.answer("Бой не активен!", show_alert=True)
        return

    # Рассчитать урон
    base_damage = player.get_total_damage()

    # Бонусы от еды и наёмника
    base_damage += fight.food_bonus_damage + fight.merc_bonus_damage

    # Бонус от эликсира силы
    if hasattr(fight, 'potion_buff_damage') and fight.potion_buff_damage > 0:
        base_damage = int(base_damage * (1 + fight.potion_buff_damage))

    # Вариативность урона ±10%
    damage_variance = random.uniform(0.9, 1.1)
    base_damage = int(base_damage * damage_variance)

    # Крит
    crit_chance = player.get_crit_chance() + fight.food_bonus_crit + fight.merc_bonus_crit
    is_crit = random.randint(1, 100) <= crit_chance

    if is_crit:
        # Крит мультипликатор от оружия (по умолчанию 1.5)
        crit_mult = player.get_crit_multiplier()
        damage = int(base_damage * crit_mult)
        fight.fight_log.append(f"💥 Крит x{crit_mult}! -{damage} HP")
        player.stats["crits"] = player.stats.get("crits", 0) + 1
    else:
        damage = base_damage
        fight.fight_log.append(f"⚔️ Атака! -{damage} HP")

    fight.first_attack = False

    # Нанести урон
    fight.enemy_hp -= damage

    # Шанс двойного удара (от экипировки/сокетов)
    double_hit_chance = player.get_equipped_stats().get("double_hit", 0)
    if double_hit_chance > 0 and random.randint(1, 100) <= double_hit_chance:
        # Второй удар с 50% урона
        second_hit = int(damage * 0.5)
        fight.enemy_hp -= second_hit
        fight.fight_log.append(f"⚔️⚔️ Двойной удар! -{second_hit} HP")

    # Проверить смерть врага
    if fight.enemy_hp <= 0:
        await end_fight(query, fight, player, victory=True)
        return

    # Вампиризм
    lifesteal = player.get_lifesteal()
    if lifesteal > 0:
        heal = int(damage * lifesteal)
        fight.player_hp = min(fight.player_hp + heal, fight.player_max_hp)
        fight.fight_log.append(f"🩸 Вампиризм +{heal} HP")

    # Эффекты от оружия
    weapon = player.equipment.get("weapon")
    if weapon:
        item_data = ITEMS.get(weapon, {})
        if "burn" in item_data:
            fight.enemy_effects["burn"] = item_data["burn"]

    # Атака врага
    await process_enemy_attack(query, fight, player)


async def fight_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Блок"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)
    fight = get_active_fight(query.from_user.id)

    if not fight or not fight.fight_active:
        return

    fight.block_next = True
    fight.fight_log.append("🛡️ Готовишь блок...")

    await process_enemy_attack(query, fight, player)


# Уровни открытия умений
SKILL_LEVELS = {0: 1, 1: 3, 2: 6, 3: 10}


async def fight_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использовать скилл"""
    query = update.callback_query

    skill_id = query.data.replace("fight_skill_", "")
    player = get_player(query.from_user.id)
    fight = get_active_fight(query.from_user.id)

    if not fight or not fight.fight_active:
        await query.answer("Бой не активен!", show_alert=True)
        return

    # Проверить класс и скилл
    if not player.player_class:
        return

    class_data = CLASSES[player.player_class]
    skills = class_data.get("skills", {})

    if skill_id not in skills:
        await query.answer("Скилл не найден!", show_alert=True)
        return

    skill = skills[skill_id]

    # Проверить уровень для открытия умения
    skill_list = list(skills.keys())
    skill_index = skill_list.index(skill_id) if skill_id in skill_list else 0
    req_level = SKILL_LEVELS.get(skill_index, 1)

    if player.level < req_level:
        await query.answer(f"Откроется на {req_level} уровне!", show_alert=True)
        return

    # Проверить кулдаун
    if fight.cooldowns.get(skill_id, 0) > 0:
        await query.answer(f"Кулдаун: {fight.cooldowns[skill_id]} ходов", show_alert=True)
        return

    # Проверить ману
    mana_cost = skill.get("mana", 0)

    # Бонус сета мага
    if player.player_class == "mage" and player.count_legendary_pieces() >= 4:
        mana_cost = int(mana_cost * 0.7)

    if fight.player_mana < mana_cost:
        await query.answer("Недостаточно маны!", show_alert=True)
        return

    await query.answer()

    # Потратить ману
    fight.player_mana -= mana_cost

    # Установить кулдаун
    fight.cooldowns[skill_id] = skill.get("cooldown", 0)

    # Применить эффект скилла
    fight.fight_log.append(f"{skill['emoji']} {skill['name']}!")

    base_damage = player.get_total_damage()
    total_damage = 0

    # Урон с множителем
    if "damage_mult" in skill:
        mult = skill["damage_mult"]
        hits = skill.get("hits", 1)

        for _ in range(hits):
            damage = int(base_damage * mult)
            total_damage += damage

        fight.enemy_hp -= total_damage

        if hits > 1:
            fight.fight_log.append(f"💥 {hits} ударов, всего -{total_damage} HP")
        else:
            fight.fight_log.append(f"💥 -{total_damage} HP")

    # Оглушение
    if "stun" in skill:
        fight.enemy_effects["stun"] = skill["stun"]
        fight.fight_log.append(f"⚡ Оглушение {skill['stun']} ходов")

    # Замедление
    if "slow" in skill:
        fight.enemy_effects["slow"] = skill["slow"]
        fight.fight_log.append("❄️ Враг замедлен")

    # Яд
    if "poison" in skill:
        fight.enemy_effects["poison"] = skill.get("poison_duration", 3)
        fight.fight_log.append(f"☠️ Яд {skill['poison']} урона")

    # Блок
    if skill.get("block"):
        fight.block_next = True
        fight.fight_log.append("🛡️ Блок активирован!")

    # Уклонение
    if skill.get("dodge"):
        fight.dodge_next = True
        fight.fight_log.append("💨 Готов к уклонению!")

    # Барьер/поглощение
    if "absorb" in skill:
        fight.barrier += skill["absorb"]
        fight.fight_log.append(f"🔮 Барьер +{skill['absorb']}")

    # Лечение
    if "heal" in skill:
        heal = skill["heal"]
        fight.player_hp = min(fight.player_hp + heal, fight.player_max_hp)
        fight.fight_log.append(f"💚 +{heal} HP")

    # Очищение дебаффов
    if skill.get("cleanse"):
        fight.player_effects.clear()
        fight.fight_log.append("✨ Дебаффы сняты!")

    # Невидимость
    if "invisibility" in skill:
        fight.invisible = skill["invisibility"]
        fight.fight_log.append(f"👻 Невидимость {fight.invisible} ходов")

    # Неуязвимость
    if "invulnerable" in skill:
        fight.invulnerable = skill["invulnerable"]
        fight.fight_log.append(f"👼 Неуязвимость {fight.invulnerable} ходов")

    # Вампиризм
    if "lifesteal" in skill and total_damage > 0:
        heal = int(total_damage * skill["lifesteal"])
        fight.player_hp = min(fight.player_hp + heal, fight.player_max_hp)
        fight.fight_log.append(f"🩸 +{heal} HP от вампиризма")

    # Проверить смерть врага
    if fight.enemy_hp <= 0:
        await end_fight(query, fight, player, victory=True)
        return

    # Атака врага
    await process_enemy_attack(query, fight, player)


async def fight_potion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Использовать зелье из слота"""
    query = update.callback_query

    slot_num = query.data.replace("fight_potion_", "")
    player = get_player(query.from_user.id)
    fight = get_active_fight(query.from_user.id)

    if not fight or not fight.fight_active:
        return

    # Получить ID зелья из слота
    slot_key = f"slot_{slot_num}"
    potion_id = player.potion_slots.get(slot_key) if hasattr(player, 'potion_slots') else None

    # Fallback для старой системы
    if not potion_id:
        if slot_num == "1" or slot_num == "hp":
            potion_id = "hp_potion_small"
        elif slot_num == "2" or slot_num == "mana":
            potion_id = "mana_potion_small"

    if not potion_id:
        await query.answer("Слот пуст!", show_alert=True)
        return

    # Проверить наличие зелья
    if player.inventory.get(potion_id, 0) <= 0:
        item_name = ITEMS.get(potion_id, {}).get("name", "Зелье")
        await query.answer(f"Нет {item_name}!", show_alert=True)
        return

    # Использовать зелье
    item = ITEMS.get(potion_id, {})
    item_name = item.get("name", "Зелье")
    item_emoji = item.get("emoji", "🧪")

    player.inventory[potion_id] -= 1

    # Применить эффект зелья
    if "heal" in item:
        heal = item["heal"]
        fight.player_hp = min(fight.player_hp + heal, fight.player_max_hp)
        fight.fight_log.append(f"{item_emoji} {item_name} +{heal} HP")
        await query.answer(f"+{heal} HP!")

    elif "mana" in item:
        mana = item["mana"]
        fight.player_mana = min(fight.player_mana + mana, player.get_max_mana())
        fight.fight_log.append(f"{item_emoji} {item_name} +{mana} маны")
        await query.answer(f"+{mana} маны!")

    elif "buff_damage" in item:
        # Бафф урона на весь бой
        bonus = item["buff_damage"]
        if not hasattr(fight, 'potion_buff_damage'):
            fight.potion_buff_damage = 0
        fight.potion_buff_damage += bonus
        fight.fight_log.append(f"{item_emoji} Урон +{int(bonus*100)}%!")
        await query.answer(f"Урон +{int(bonus*100)}%!")

    elif "buff_defense" in item:
        # Бафф защиты на весь бой
        bonus = item["buff_defense"]
        if not hasattr(fight, 'potion_buff_defense'):
            fight.potion_buff_defense = 0
        fight.potion_buff_defense += bonus
        fight.fight_log.append(f"{item_emoji} Защита +{int(bonus*100)}%!")
        await query.answer(f"Защита +{int(bonus*100)}%!")

    elif "cleanse_poison" in item:
        # Снять яд
        if "poison" in fight.player_effects:
            del fight.player_effects["poison"]
            fight.fight_log.append(f"{item_emoji} Яд снят!")
            await query.answer("Яд снят!")
        else:
            fight.fight_log.append(f"{item_emoji} Нет яда для снятия")
            await query.answer("Нет яда!")

    else:
        fight.fight_log.append(f"{item_emoji} Использовано {item_name}")
        await query.answer(f"Использовано: {item_name}")

    save_data()
    await process_enemy_attack(query, fight, player)


async def fight_flee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбежать из боя"""
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)
    fight = get_active_fight(query.from_user.id)

    if not fight:
        return

    # 50% шанс побега
    if random.randint(1, 100) <= 50:
        fight.fight_active = False
        remove_active_fight(query.from_user.id)

        player.current_dungeon = None
        player.current_floor = 0
        save_data()

        keyboard = [[InlineKeyboardButton("🏠 В меню", callback_data="menu")]]
        await query.edit_message_text(
            "🏃 Ты успешно сбежал!\n\nПрогресс подземелья потерян.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        fight.fight_log.append("🏃 Побег не удался!")
        await process_enemy_attack(query, fight, player)


async def process_enemy_attack(query, fight, player):
    """Обработать атаку врага"""
    if not fight.fight_active:
        return

    # Уменьшить кулдауны
    for skill_id in list(fight.cooldowns.keys()):
        if fight.cooldowns[skill_id] > 0:
            fight.cooldowns[skill_id] -= 1

    # Регенерация маны (базовая + от еды + от наёмника + от экипировки)
    equip_mana_regen = player.get_equipped_stats().get("mana_regen", 0)
    mana_regen = 5 + fight.food_bonus_mana_regen + fight.merc_bonus_mana_regen + equip_mana_regen
    fight.player_mana = min(fight.player_mana + mana_regen, player.get_max_mana())

    # Хил от наёмника
    if fight.merc_bonus_heal > 0:
        fight.player_hp = min(fight.player_hp + fight.merc_bonus_heal, fight.player_max_hp)

    # Эффекты на враге
    if "burn" in fight.enemy_effects:
        burn_dmg = fight.enemy_effects["burn"] * 3
        fight.enemy_hp -= burn_dmg
        fight.enemy_effects["burn"] -= 1
        if fight.enemy_effects["burn"] <= 0:
            del fight.enemy_effects["burn"]
        fight.fight_log.append(f"🔥 Враг горит -{burn_dmg} HP")

    if "bleed" in fight.enemy_effects:
        bleed_dmg = fight.enemy_effects["bleed"] * 5
        fight.enemy_hp -= bleed_dmg
        fight.enemy_effects["bleed"] -= 1
        if fight.enemy_effects["bleed"] <= 0:
            del fight.enemy_effects["bleed"]
        fight.fight_log.append(f"🩸 Кровотечение -{bleed_dmg} HP")

    # Проверить смерть врага от эффектов
    if fight.enemy_hp <= 0:
        await end_fight(query, fight, player, victory=True)
        return

    # Оглушение врага
    if "stun" in fight.enemy_effects:
        fight.enemy_effects["stun"] -= 1
        if fight.enemy_effects["stun"] <= 0:
            del fight.enemy_effects["stun"]
        fight.fight_log.append("⚡ Враг оглушён!")
        await update_fight_ui(query, fight, player)
        return

    # Невидимость - враг не атакует
    if fight.invisible > 0:
        fight.invisible -= 1
        fight.fight_log.append("👁️ Враг не видит тебя!")
        await update_fight_ui(query, fight, player)
        return

    # Неуязвимость
    if fight.invulnerable > 0:
        fight.invulnerable -= 1
        fight.fight_log.append("✨ Ты неуязвим!")
        await update_fight_ui(query, fight, player)
        return

    # Атака врага
    enemy_damage = fight.enemy_damage

    # Вариативность урона врага ±10%
    enemy_variance = random.uniform(0.9, 1.1)
    enemy_damage = int(enemy_damage * enemy_variance)

    # Замедление
    if "slow" in fight.enemy_effects:
        enemy_damage = int(enemy_damage * 0.7)

    # Блок
    if fight.block_next:
        enemy_damage = int(enemy_damage * 0.3)
        fight.block_next = False
        fight.fight_log.append(f"🛡️ Блок! Получено {enemy_damage} урона")
    # Активное уклонение (от скилла)
    elif fight.dodge_next:
        enemy_damage = 0
        fight.dodge_next = False
        fight.fight_log.append("💨 Уклонился!")
    # Пассивное уклонение (от экипировки)
    elif random.randint(1, 100) <= player.get_dodge_chance():
        enemy_damage = 0
        fight.fight_log.append("💨 Уворот!")
    # Шанс блока (от экипировки)
    elif random.randint(1, 100) <= player.get_block_chance():
        enemy_damage = int(enemy_damage * 0.5)
        fight.fight_log.append(f"🛡️ Парирование! -{enemy_damage} HP")
    else:
        # Барьер
        if fight.barrier > 0:
            if fight.barrier >= enemy_damage:
                fight.barrier -= enemy_damage
                enemy_damage = 0
                fight.fight_log.append(f"🔮 Барьер поглотил удар")
            else:
                enemy_damage -= fight.barrier
                fight.barrier = 0
                fight.fight_log.append(f"🔮 Барьер разрушен!")

        # Защита
        defense = player.get_total_defense() + fight.food_bonus_defense + fight.merc_bonus_defense

        # Бонус от эликсира защиты
        if hasattr(fight, 'potion_buff_defense') and fight.potion_buff_defense > 0:
            defense = int(defense * (1 + fight.potion_buff_defense))

        enemy_damage = max(1, enemy_damage - defense)
        fight.fight_log.append(f"👊 Враг атакует -{enemy_damage} HP")

    # Нанести урон игроку
    fight.player_hp -= enemy_damage

    # Эффекты от способностей врага
    if hasattr(fight, 'enemy_special'):
        if "poison" in fight.enemy_special and random.randint(1, 100) <= 30:
            fight.player_effects["poison"] = fight.enemy_special["poison"]
            fight.fight_log.append("🤢 Ты отравлен!")
        if "burn" in fight.enemy_special and random.randint(1, 100) <= 30:
            fight.player_effects["burn"] = fight.enemy_special["burn"]
            fight.fight_log.append("🔥 Ты горишь!")
        if "lifesteal" in fight.enemy_special:
            heal = int(enemy_damage * fight.enemy_special["lifesteal"])
            fight.enemy_hp = min(fight.enemy_hp + heal, fight.enemy_max_hp)
            fight.fight_log.append(f"🩸 Враг восстановил {heal} HP")

    # Эффекты на игроке
    if "poison" in fight.player_effects:
        poison_dmg = fight.player_effects["poison"] * 3
        # Сопротивление яду уменьшает урон
        poison_res = player.get_poison_resistance()
        if poison_res > 0:
            poison_dmg = int(poison_dmg * (1 - poison_res / 100))
        fight.player_hp -= poison_dmg
        fight.player_effects["poison"] -= 1
        if fight.player_effects["poison"] <= 0:
            del fight.player_effects["poison"]
        fight.fight_log.append(f"🤢 Яд -{poison_dmg} HP")

    if "burn" in fight.player_effects:
        burn_dmg = fight.player_effects["burn"] * 3
        # Сопротивление огню уменьшает урон
        fire_res = player.get_fire_resistance()
        if fire_res > 0:
            burn_dmg = int(burn_dmg * (1 - fire_res / 100))
        fight.player_hp -= burn_dmg
        fight.player_effects["burn"] -= 1
        if fight.player_effects["burn"] <= 0:
            del fight.player_effects["burn"]
        fight.fight_log.append(f"🔥 Горение -{burn_dmg} HP")

    # Проверить смерть игрока
    if fight.player_hp <= 0:
        await end_fight(query, fight, player, victory=False)
        return

    await update_fight_ui(query, fight, player)


async def end_fight(query, fight, player, victory: bool):
    """Завершить бой"""
    fight.fight_active = False

    if victory:
        # Награды
        exp_gained = fight.exp_reward
        gold_gained = fight.gold_reward

        player.exp += exp_gained
        player.gold += gold_gained
        player.stats["gold_earned"] = player.stats.get("gold_earned", 0) + gold_gained
        player.stats["kills"] = player.stats.get("kills", 0) + 1

        if fight.is_boss:
            player.stats["boss_kills"] = player.stats.get("boss_kills", 0) + 1

            # Завершить сюжетный квест для этого босса
            boss_to_quest = {
                "forest": "story_forest",
                "mines": "story_mines",
                "crypt": "story_crypt",
                "abyss": "story_abyss",
                "chaos": "story_chaos"
            }
            quest_id = boss_to_quest.get(fight.dungeon_id)
            if quest_id and quest_id not in player.completed_quests:
                player.completed_quests.append(quest_id)

        # Дроп ресурса
        dungeon = DUNGEONS[fight.dungeon_id]
        resource = dungeon.get("drop_resource")
        resource_amount = random.randint(1, 3)
        if resource:
            player.inventory[resource] = player.inventory.get(resource, 0) + resource_amount

        # Шанс дропа редкого предмета (5% обычный моб, 15% босс)
        rare_drop = None
        drop_chance = 15 if fight.is_boss else 5
        if random.randint(1, 100) <= drop_chance:
            dungeon_id = fight.dungeon_id
            if dungeon_id in RARE_DROPS and RARE_DROPS[dungeon_id]:
                rare_drop = random.choice(RARE_DROPS[dungeon_id])
                player.inventory[rare_drop] = player.inventory.get(rare_drop, 0) + 1

        # Шанс дропа процедурного предмета (10% обычный моб, 30% босс)
        from utils.helpers import generate_procedural_item
        proc_drop = None
        proc_drop_chance = 30 if fight.is_boss else 10
        if random.randint(1, 100) <= proc_drop_chance:
            dungeon_id = fight.dungeon_id
            # Боссы дропают более качественные предметы
            forced_rarity = "rare" if fight.is_boss and random.randint(1, 100) <= 50 else None
            proc_item = generate_procedural_item(dungeon_id, forced_rarity=forced_rarity)
            if proc_item:
                proc_drop = proc_item
                # Сохранить процедурный предмет
                player.procedural_items[proc_item["id"]] = proc_item
                # Добавить в инвентарь (количество = 1)
                player.inventory[proc_item["id"]] = 1

        # Эпический дроп с босса (гарантированно 1 предмет сета)
        epic_drop = None
        dragon_scale_drop = 0
        if fight.is_boss:
            dungeon_id = fight.dungeon_id
            if dungeon_id in EPIC_BOSS_DROPS and EPIC_BOSS_DROPS[dungeon_id]:
                # Выбрать случайный эпик из сета босса
                epic_drop = random.choice(EPIC_BOSS_DROPS[dungeon_id])
                player.inventory[epic_drop] = player.inventory.get(epic_drop, 0) + 1

            # Дроп чешуи дракона с боссов (для легендарок)
            # Шанс зависит от подземелья
            dragon_scale_chance = {
                "forest": 5, "mines": 10, "crypt": 15, "abyss": 25, "chaos": 50
            }
            if random.randint(1, 100) <= dragon_scale_chance.get(dungeon_id, 0):
                dragon_scale_drop = random.randint(1, 3)
                player.inventory["dragon_scale"] = player.inventory.get("dragon_scale", 0) + dragon_scale_drop

        # Проверить повышение уровня
        level_up_text = ""
        talent_text = ""
        while player.exp >= player.exp_to_level:
            player.exp -= player.exp_to_level
            player.level += 1
            player.exp_to_level = int(player.exp_to_level * 1.2)

            # Восстановить HP и ману при левел-апе
            player.hp = player.get_max_hp()
            player.mana = player.get_max_mana()

            level_up_text = f"\n\n🎉 **УРОВЕНЬ {player.level}!**"

            # Проверить, доступен ли талант на этом уровне
            from data import TALENTS
            if player.player_class and player.player_class in TALENTS:
                if player.level in TALENTS[player.player_class]:
                    player.pending_talent_levels.append(player.level)
                    talent_text = "\n🌟 Доступен новый талант! (Профиль → Таланты)"

        # Обновить HP игрока
        player.hp = fight.player_hp
        player.mana = fight.player_mana

        # Уменьшить счётчик наёмника
        if player.mercenary:
            player.mercenary["fights"] = player.mercenary.get("fights", 0) - 1
            if player.mercenary["fights"] <= 0:
                player.mercenary = None

        player.stats["floors"] = player.stats.get("floors", 0) + 1

        # Обновить прогресс квестов и проверить достижения
        player.update_quest_progress()
        new_achievements = player.check_achievements()

        # Текст о новых достижениях
        achievement_text = ""
        if new_achievements:
            achievement_text = "\n\n🏆 НОВЫЕ ДОСТИЖЕНИЯ:\n"
            for ach in new_achievements:
                achievement_text += f"{ach['emoji']} {ach['name']}\n"

        # Текст о редком дропе
        rare_drop_text = ""
        if rare_drop:
            item_data = ITEMS.get(rare_drop, {})
            rare_emoji = RARITY_EMOJI.get(item_data.get("rarity", "common"), "")
            rare_drop_text = f"\n{rare_emoji} РЕДКИЙ ДРОП: {item_data.get('name', rare_drop)}!"

        # Текст о эпическом дропе с босса
        epic_drop_text = ""
        if epic_drop:
            item_data = ITEMS.get(epic_drop, {})
            set_id = item_data.get("set", "")
            set_name = ""
            if set_id and set_id in EPIC_SETS:
                set_name = f" (сет: {EPIC_SETS[set_id]['name']})"
            epic_drop_text = f"\n🟣 ЭПИЧЕСКИЙ ДРОП: {item_data.get('name', epic_drop)}!{set_name}"

        # Текст о дропе чешуи дракона
        dragon_text = ""
        if fight.is_boss and dragon_scale_drop > 0:
            dragon_text = f"\n🐉 Чешуя дракона: +{dragon_scale_drop}"

        # Процедурные предметы добавляются молча (без текста)

        text = f"""🎉 ПОБЕДА!

{fight.enemy_emoji} {fight.enemy_name} повержен!

💰 Золото: +{gold_gained}
⭐ Опыт: +{exp_gained}
📦 {resource}: +{resource_amount}{dragon_text}{rare_drop_text}{epic_drop_text}{level_up_text}{talent_text}{achievement_text}"""

        # Кнопки
        if fight.is_boss:
            # Босс побеждён - подземелье пройдено
            player.current_dungeon = None
            player.current_floor = 0

            text += "\n\n👑 Подземелье пройдено!"
            keyboard = [[InlineKeyboardButton("🏠 В меню", callback_data="menu")]]
        else:
            # Продолжить или выйти
            keyboard = [
                [InlineKeyboardButton("➡️ Дальше", callback_data="next_floor")],
                [InlineKeyboardButton("🏠 Выйти", callback_data="menu")]
            ]

    else:
        # Поражение
        player.stats["deaths"] = player.stats.get("deaths", 0) + 1
        player.hp = int(player.get_max_hp() * 0.3)
        player.mana = int(player.get_max_mana() * 0.5)
        player.current_dungeon = None
        player.current_floor = 0

        text = f"""💀 ПОРАЖЕНИЕ

{fight.enemy_emoji} {fight.enemy_name} победил тебя...

Ты очнулся в таверне с 30% здоровья."""

        keyboard = [[InlineKeyboardButton("🏠 В меню", callback_data="menu")]]

    remove_active_fight(query.from_user.id)
    save_data()

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
