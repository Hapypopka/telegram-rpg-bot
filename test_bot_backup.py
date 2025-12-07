from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import random
import json
import os

# База данных игроков
DATA_FILE = "players_data.json"
players = {}

def save_data():
    data = {}
    for uid, player in players.items():
        data[str(uid)] = player.to_dict()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    global players
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for uid, pdata in data.items():
                players[int(uid)] = Player.from_dict(pdata)

# ============ ПРЕДМЕТЫ ============
ITEMS = {
    # Оружие
    "wooden_sword": {"name": "Деревянный меч", "type": "weapon", "damage": 5, "price": 50, "emoji": "🗡️"},
    "iron_sword": {"name": "Железный меч", "type": "weapon", "damage": 15, "price": 200, "emoji": "⚔️"},
    "fire_sword": {"name": "Огненный меч", "type": "weapon", "damage": 30, "price": 500, "emoji": "🔥"},
    "legendary_blade": {"name": "Легендарный клинок", "type": "weapon", "damage": 50, "price": 1500, "emoji": "✨"},
    "staff_apprentice": {"name": "Посох ученика", "type": "weapon", "damage": 8, "price": 80, "emoji": "🪄"},
    "crystal_staff": {"name": "Кристальный посох", "type": "weapon", "damage": 25, "price": 400, "emoji": "💎"},
    "arcane_staff": {"name": "Тайный посох", "type": "weapon", "damage": 45, "price": 1200, "emoji": "🌟"},
    "hunting_bow": {"name": "Охотничий лук", "type": "weapon", "damage": 10, "price": 100, "emoji": "🏹"},
    "elven_bow": {"name": "Эльфийский лук", "type": "weapon", "damage": 28, "price": 450, "emoji": "🌿"},
    "shadow_bow": {"name": "Теневой лук", "type": "weapon", "damage": 48, "price": 1400, "emoji": "🌑"},

    # Броня
    "leather_armor": {"name": "Кожаная броня", "type": "armor", "defense": 5, "price": 60, "emoji": "🥋"},
    "chainmail": {"name": "Кольчуга", "type": "armor", "defense": 15, "price": 250, "emoji": "⛓️"},
    "plate_armor": {"name": "Латы", "type": "armor", "defense": 30, "price": 600, "emoji": "🛡️"},
    "dragon_armor": {"name": "Драконья броня", "type": "armor", "defense": 50, "price": 2000, "emoji": "🐉"},

    # Зелья
    "health_potion": {"name": "Зелье здоровья", "type": "consumable", "heal": 50, "price": 30, "emoji": "❤️"},
    "greater_health": {"name": "Большое зелье здоровья", "type": "consumable", "heal": 150, "price": 80, "emoji": "💖"},
    "mana_potion": {"name": "Зелье маны", "type": "consumable", "mana": 30, "price": 25, "emoji": "💙"},
    "elixir": {"name": "Эликсир", "type": "consumable", "heal": 100, "mana": 50, "price": 120, "emoji": "🧪"},

    # Аксессуары
    "lucky_ring": {"name": "Кольцо удачи", "type": "accessory", "crit_chance": 10, "price": 300, "emoji": "💍"},
    "power_amulet": {"name": "Амулет силы", "type": "accessory", "damage_bonus": 15, "price": 400, "emoji": "📿"},
    "shield_charm": {"name": "Защитный оберег", "type": "accessory", "defense_bonus": 10, "price": 350, "emoji": "🔮"},
}

# ============ ВРАГИ ============
ENEMIES = {
    # Обычные враги (по уровням сложности)
    "slime": {"name": "Слизень", "emoji": "🟢", "hp": 30, "damage": 3, "exp": 5, "gold": 10, "tier": 1},
    "goblin": {"name": "Гоблин", "emoji": "👺", "hp": 50, "damage": 5, "exp": 10, "gold": 20, "tier": 1},
    "wolf": {"name": "Волк", "emoji": "🐺", "hp": 60, "damage": 8, "exp": 15, "gold": 25, "tier": 1},
    "skeleton": {"name": "Скелет", "emoji": "💀", "hp": 80, "damage": 10, "exp": 20, "gold": 35, "tier": 2},
    "orc": {"name": "Орк", "emoji": "👹", "hp": 120, "damage": 15, "exp": 30, "gold": 50, "tier": 2},
    "dark_mage": {"name": "Тёмный маг", "emoji": "🧙‍♂️", "hp": 100, "damage": 20, "exp": 40, "gold": 60, "tier": 2},
    "vampire": {"name": "Вампир", "emoji": "🧛", "hp": 150, "damage": 25, "exp": 50, "gold": 80, "tier": 3},
    "golem": {"name": "Голем", "emoji": "🗿", "hp": 250, "damage": 20, "exp": 60, "gold": 100, "tier": 3},
    "demon": {"name": "Демон", "emoji": "😈", "hp": 200, "damage": 35, "exp": 80, "gold": 150, "tier": 3},

    # Боссы
    "boss_dragon": {"name": "🐲 ДРАКОН", "emoji": "🐲", "hp": 500, "damage": 40, "exp": 200, "gold": 500, "tier": 4, "boss": True},
    "boss_lich": {"name": "👑 ЛИЧ-КОРОЛЬ", "emoji": "👑", "hp": 400, "damage": 50, "exp": 250, "gold": 600, "tier": 4, "boss": True},
    "boss_titan": {"name": "⚡ ТИТАН", "emoji": "⚡", "hp": 800, "damage": 60, "exp": 500, "gold": 1000, "tier": 5, "boss": True},
}

# ============ КЛАССЫ ПЕРСОНАЖЕЙ ============
CLASSES = {
    "warrior": {
        "name": "⚔️ Воин",
        "description": "Высокое HP и защита. Мощные физические атаки.",
        "base_hp": 150,
        "base_mana": 30,
        "base_damage": 15,
        "base_defense": 10,
        "skills": {
            "power_strike": {"name": "Мощный удар", "damage_mult": 2.0, "mana": 10, "cooldown": 3, "emoji": "💥"},
            "shield_bash": {"name": "Удар щитом", "damage_mult": 1.2, "stun": 2, "mana": 15, "cooldown": 5, "emoji": "🛡️"},
            "battle_cry": {"name": "Боевой клич", "buff": "damage", "buff_value": 20, "buff_duration": 3, "mana": 20, "cooldown": 8, "emoji": "📢"},
            "berserk": {"name": "Берсерк", "damage_mult": 3.0, "self_damage": 20, "mana": 25, "cooldown": 10, "emoji": "🔴"},
        }
    },
    "mage": {
        "name": "🔮 Маг",
        "description": "Высокий урон магией. Много маны, но мало HP.",
        "base_hp": 80,
        "base_mana": 100,
        "base_damage": 25,
        "base_defense": 3,
        "skills": {
            "fireball": {"name": "Огненный шар", "damage_mult": 2.5, "mana": 15, "cooldown": 2, "emoji": "🔥"},
            "ice_spike": {"name": "Ледяной шип", "damage_mult": 1.8, "slow": 2, "mana": 12, "cooldown": 3, "emoji": "❄️"},
            "lightning": {"name": "Молния", "damage_mult": 3.0, "mana": 25, "cooldown": 5, "emoji": "⚡"},
            "meteor": {"name": "Метеор", "damage_mult": 5.0, "mana": 50, "cooldown": 12, "emoji": "☄️"},
        }
    },
    "archer": {
        "name": "🏹 Лучник",
        "description": "Высокий шанс крита. Быстрые атаки.",
        "base_hp": 100,
        "base_mana": 50,
        "base_damage": 18,
        "base_defense": 5,
        "skills": {
            "precise_shot": {"name": "Точный выстрел", "damage_mult": 2.2, "crit_bonus": 30, "mana": 10, "cooldown": 2, "emoji": "🎯"},
            "arrow_rain": {"name": "Дождь стрел", "damage_mult": 1.5, "hits": 3, "mana": 20, "cooldown": 5, "emoji": "🌧️"},
            "poison_arrow": {"name": "Отравленная стрела", "damage_mult": 1.0, "poison": 10, "poison_duration": 5, "mana": 15, "cooldown": 4, "emoji": "☠️"},
            "headshot": {"name": "Выстрел в голову", "damage_mult": 4.0, "mana": 30, "cooldown": 8, "emoji": "💀"},
        }
    }
}

# ============ ДОСТИЖЕНИЯ ============
ACHIEVEMENTS = {
    "first_blood": {"name": "Первая кровь", "description": "Победи первого врага", "emoji": "🩸"},
    "slayer_10": {"name": "Убийца", "description": "Победи 10 врагов", "emoji": "⚔️"},
    "slayer_100": {"name": "Истребитель", "description": "Победи 100 врагов", "emoji": "🏆"},
    "boss_hunter": {"name": "Охотник на боссов", "description": "Победи босса", "emoji": "👑"},
    "rich": {"name": "Богач", "description": "Накопи 1000 золота", "emoji": "💰"},
    "max_level": {"name": "Мастер", "description": "Достигни 20 уровня", "emoji": "⭐"},
    "survivor": {"name": "Выживший", "description": "Выживи с 1 HP", "emoji": "💪"},
    "critical_master": {"name": "Критический мастер", "description": "Нанеси 10 критических ударов", "emoji": "💥"},
    "dungeon_10": {"name": "Исследователь", "description": "Пройди 10 этаж подземелья", "emoji": "🏰"},
}

class Player:
    def __init__(self, player_class="warrior"):
        class_data = CLASSES[player_class]
        self.player_class = player_class
        self.level = 1
        self.exp = 0
        self.exp_needed = 20

        self.max_hp = class_data["base_hp"]
        self.hp = self.max_hp
        self.max_mana = class_data["base_mana"]
        self.mana = self.max_mana
        self.base_damage = class_data["base_damage"]
        self.base_defense = class_data["base_defense"]

        self.gold = 50
        self.crit_chance = 10

        # Инвентарь и экипировка
        self.inventory = ["health_potion", "health_potion"]
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_accessory = None

        # Статистика
        self.kills = 0
        self.bosses_killed = 0
        self.crits_dealt = 0
        self.dungeon_floor = 1
        self.max_dungeon_floor = 1

        # Достижения
        self.achievements = []

    def to_dict(self):
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
            "gold": self.gold,
            "crit_chance": self.crit_chance,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "equipped_armor": self.equipped_armor,
            "equipped_accessory": self.equipped_accessory,
            "kills": self.kills,
            "bosses_killed": self.bosses_killed,
            "crits_dealt": self.crits_dealt,
            "dungeon_floor": self.dungeon_floor,
            "max_dungeon_floor": self.max_dungeon_floor,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data.get("player_class", "warrior"))
        for key, value in data.items():
            if hasattr(player, key):
                setattr(player, key, value)
        return player

    def get_total_damage(self):
        damage = self.base_damage
        if self.equipped_weapon:
            damage += ITEMS[self.equipped_weapon]["damage"]
        if self.equipped_accessory and "damage_bonus" in ITEMS.get(self.equipped_accessory, {}):
            damage += ITEMS[self.equipped_accessory]["damage_bonus"]
        return damage

    def get_total_defense(self):
        defense = self.base_defense
        if self.equipped_armor:
            defense += ITEMS[self.equipped_armor]["defense"]
        if self.equipped_accessory and "defense_bonus" in ITEMS.get(self.equipped_accessory, {}):
            defense += ITEMS[self.equipped_accessory]["defense_bonus"]
        return defense

    def get_crit_chance(self):
        crit = self.crit_chance
        if self.equipped_accessory and "crit_chance" in ITEMS.get(self.equipped_accessory, {}):
            crit += ITEMS[self.equipped_accessory]["crit_chance"]
        return crit

    def level_up(self):
        self.level += 1
        self.exp = 0
        self.exp_needed = int(self.exp_needed * 1.5)

        class_data = CLASSES[self.player_class]
        self.max_hp += 10 + (5 if self.player_class == "warrior" else 0)
        self.max_mana += 5 + (10 if self.player_class == "mage" else 0)
        self.base_damage += 3
        self.base_defense += 2

        self.hp = self.max_hp
        self.mana = self.max_mana

        return True

    def check_achievements(self):
        new_achievements = []

        if self.kills >= 1 and "first_blood" not in self.achievements:
            self.achievements.append("first_blood")
            new_achievements.append("first_blood")
        if self.kills >= 10 and "slayer_10" not in self.achievements:
            self.achievements.append("slayer_10")
            new_achievements.append("slayer_10")
        if self.kills >= 100 and "slayer_100" not in self.achievements:
            self.achievements.append("slayer_100")
            new_achievements.append("slayer_100")
        if self.bosses_killed >= 1 and "boss_hunter" not in self.achievements:
            self.achievements.append("boss_hunter")
            new_achievements.append("boss_hunter")
        if self.gold >= 1000 and "rich" not in self.achievements:
            self.achievements.append("rich")
            new_achievements.append("rich")
        if self.level >= 20 and "max_level" not in self.achievements:
            self.achievements.append("max_level")
            new_achievements.append("max_level")
        if self.crits_dealt >= 10 and "critical_master" not in self.achievements:
            self.achievements.append("critical_master")
            new_achievements.append("critical_master")
        if self.max_dungeon_floor >= 10 and "dungeon_10" not in self.achievements:
            self.achievements.append("dungeon_10")
            new_achievements.append("dungeon_10")

        return new_achievements

class Fight:
    def __init__(self, player: Player, enemy_id: str):
        self.player = player
        self.enemy_id = enemy_id
        enemy = ENEMIES[enemy_id]

        self.player_hp = player.hp
        self.player_mana = player.mana
        self.player_max_hp = player.max_hp

        self.enemy_hp = enemy["hp"]
        self.enemy_max_hp = enemy["hp"]
        self.enemy_damage = enemy["damage"]

        self.enemy_attack_task = None
        self.cooldowns = {}
        self.buffs = {}
        self.debuffs = {}
        self.poison_damage = 0
        self.poison_duration = 0
        self.stun_duration = 0
        self.fight_log = []

# ============ ОБРАБОТЧИКИ ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in players:
        player = players[user_id]
        await show_main_menu(update, context, player)
    else:
        # Новый игрок - выбор класса
        keyboard = [
            [InlineKeyboardButton("⚔️ Воин", callback_data="class_warrior")],
            [InlineKeyboardButton("🔮 Маг", callback_data="class_mage")],
            [InlineKeyboardButton("🏹 Лучник", callback_data="class_archer")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = "🎮 **ДОБРО ПОЖАЛОВАТЬ В RPG БИТВУ!**\n\n"
        text += "Выбери свой класс:\n\n"
        for cls_id, cls_data in CLASSES.items():
            text += f"{cls_data['name']}\n{cls_data['description']}\n\n"

        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, player: Player, message=None):
    class_name = CLASSES[player.player_class]["name"]

    text = f"🎮 **ГЛАВНОЕ МЕНЮ**\n\n"
    text += f"Класс: {class_name}\n"
    text += f"Уровень: {player.level} | Опыт: {player.exp}/{player.exp_needed}\n"
    text += f"❤️ HP: {player.hp}/{player.max_hp}\n"
    text += f"💙 Мана: {player.mana}/{player.max_mana}\n"
    text += f"⚔️ Урон: {player.get_total_damage()} | 🛡️ Защита: {player.get_total_defense()}\n"
    text += f"💰 Золото: {player.gold}\n"
    text += f"🏆 Убийств: {player.kills} | 👑 Боссов: {player.bosses_killed}\n"

    if message:
        text += f"\n{message}\n"

    keyboard = [
        [InlineKeyboardButton("⚔️ В бой!", callback_data="fight_menu")],
        [InlineKeyboardButton("🏰 Подземелье", callback_data="dungeon")],
        [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
        [InlineKeyboardButton("🏪 Магазин", callback_data="shop")],
        [InlineKeyboardButton("🏆 Достижения", callback_data="achievements")],
        [InlineKeyboardButton("💤 Отдых (восстановить HP/Ману)", callback_data="rest")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def select_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    class_id = query.data.replace("class_", "")

    players[user_id] = Player(class_id)
    save_data()

    await query.answer(f"Ты выбрал класс: {CLASSES[class_id]['name']}!")
    await show_main_menu(update, context, players[user_id])

async def fight_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    # Показываем врагов по tier
    max_tier = min(3, 1 + player.level // 5)

    text = "⚔️ **ВЫБЕРИ ПРОТИВНИКА**\n\n"
    keyboard = []

    for enemy_id, enemy in ENEMIES.items():
        if enemy.get("boss"):
            continue
        if enemy["tier"] <= max_tier:
            text += f"{enemy['emoji']} {enemy['name']} - HP: {enemy['hp']}, Урон: {enemy['damage']}\n"
            text += f"   💰 {enemy['gold']} золота | ⭐ {enemy['exp']} опыта\n\n"
            keyboard.append([InlineKeyboardButton(f"{enemy['emoji']} {enemy['name']}", callback_data=f"fight_{enemy_id}")])

    # Босс доступен каждые 5 уровней
    if player.level >= 5:
        keyboard.append([InlineKeyboardButton("🐲 БОСС: Дракон (Lvl 5+)", callback_data="fight_boss_dragon")])
    if player.level >= 10:
        keyboard.append([InlineKeyboardButton("👑 БОСС: Лич-Король (Lvl 10+)", callback_data="fight_boss_lich")])
    if player.level >= 15:
        keyboard.append([InlineKeyboardButton("⚡ БОСС: Титан (Lvl 15+)", callback_data="fight_boss_titan")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def start_fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]
    enemy_id = query.data.replace("fight_", "")

    if player.hp <= 0:
        await query.answer("У тебя нет HP! Отдохни сначала.")
        return

    fight = Fight(player, enemy_id)
    context.user_data['fight'] = fight

    # Запускаем врага
    fight.enemy_attack_task = asyncio.create_task(enemy_attack_loop(update, context))

    await update_fight_ui(update, context)
    await query.answer("Бой начался!")

async def enemy_attack_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fight: Fight = context.user_data.get('fight')
    if not fight:
        return

    enemy = ENEMIES[fight.enemy_id]
    attack_interval = 2.0 if enemy.get("boss") else 1.5

    while fight.player_hp > 0 and fight.enemy_hp > 0:
        await asyncio.sleep(attack_interval)

        if fight.player_hp <= 0 or fight.enemy_hp <= 0:
            break

        # Уменьшаем кулдауны
        for skill in list(fight.cooldowns.keys()):
            fight.cooldowns[skill] -= 1
            if fight.cooldowns[skill] <= 0:
                del fight.cooldowns[skill]

        # Яд
        if fight.poison_duration > 0:
            fight.enemy_hp -= fight.poison_damage
            fight.poison_duration -= 1
            fight.fight_log.append(f"☠️ Яд нанёс {fight.poison_damage} урона")

        # Оглушение врага
        if fight.stun_duration > 0:
            fight.stun_duration -= 1
            fight.fight_log.append("💫 Враг оглушён!")
        else:
            # Атака врага
            damage = max(1, enemy["damage"] - fight.player.get_total_defense() // 2)
            fight.player_hp -= damage
            fight.fight_log.append(f"👹 Враг атакует: -{damage} HP")

        if fight.player_hp <= 0:
            await end_fight(update, context, victory=False)
            return

        # Ограничиваем лог
        fight.fight_log = fight.fight_log[-5:]

        try:
            await update_fight_ui(update, context)
        except:
            pass

def get_fight_keyboard(fight: Fight):
    player = fight.player
    skills = CLASSES[player.player_class]["skills"]

    keyboard = [[InlineKeyboardButton("⚔️ Атака", callback_data="action_attack")]]

    # Добавляем скиллы
    for skill_id, skill in skills.items():
        cd = fight.cooldowns.get(skill_id, 0)
        mana_ok = fight.player_mana >= skill["mana"]

        if cd > 0:
            btn_text = f"{skill['emoji']} {skill['name']} ({cd}с)"
        elif not mana_ok:
            btn_text = f"{skill['emoji']} {skill['name']} (нет маны)"
        else:
            btn_text = f"{skill['emoji']} {skill['name']} [{skill['mana']}💙]"

        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"skill_{skill_id}")])

    # Зелья из инвентаря
    potions = [item for item in player.inventory if ITEMS.get(item, {}).get("type") == "consumable"]
    if potions:
        potion_counts = {}
        for p in potions:
            potion_counts[p] = potion_counts.get(p, 0) + 1

        for potion_id, count in potion_counts.items():
            item = ITEMS[potion_id]
            keyboard.append([InlineKeyboardButton(f"{item['emoji']} {item['name']} x{count}", callback_data=f"use_{potion_id}")])

    keyboard.append([InlineKeyboardButton("🏃 Сбежать", callback_data="flee")])

    return InlineKeyboardMarkup(keyboard)

async def update_fight_ui(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fight: Fight = context.user_data.get('fight')
    if not fight:
        return

    enemy = ENEMIES[fight.enemy_id]

    # HP бары
    player_hp_bar = create_hp_bar(fight.player_hp, fight.player_max_hp)
    enemy_hp_bar = create_hp_bar(fight.enemy_hp, fight.enemy_max_hp)

    text = f"⚔️ **БОЙ** ⚔️\n\n"
    text += f"🧑 **Ты** {player_hp_bar}\n"
    text += f"❤️ {fight.player_hp}/{fight.player_max_hp} | 💙 {fight.player_mana}/{fight.player.max_mana}\n\n"
    text += f"{enemy['emoji']} **{enemy['name']}** {enemy_hp_bar}\n"
    text += f"❤️ {fight.enemy_hp}/{fight.enemy_max_hp}\n\n"

    if fight.fight_log:
        text += "📜 **Лог боя:**\n"
        for log in fight.fight_log[-3:]:
            text += f"• {log}\n"

    try:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=get_fight_keyboard(fight),
            parse_mode="Markdown"
        )
    except:
        pass

def create_hp_bar(current, maximum, length=10):
    filled = int((current / maximum) * length) if maximum > 0 else 0
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}]"

async def action_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if not fight or fight.enemy_hp <= 0 or fight.player_hp <= 0:
        await query.answer()
        return

    player = fight.player
    damage = player.get_total_damage()

    # Крит
    is_crit = random.randint(1, 100) <= player.get_crit_chance()
    if is_crit:
        damage = int(damage * 1.5)
        player.crits_dealt += 1
        fight.fight_log.append(f"💥 КРИТ! Ты нанёс {damage} урона!")
        await query.answer("💥 КРИТИЧЕСКИЙ УДАР!")
    else:
        fight.fight_log.append(f"⚔️ Ты атакуешь: {damage} урона")
        await query.answer(f"Атака: {damage} урона")

    fight.enemy_hp -= damage

    if fight.enemy_hp <= 0:
        await end_fight(update, context, victory=True)
    else:
        await update_fight_ui(update, context)

async def use_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if not fight or fight.enemy_hp <= 0 or fight.player_hp <= 0:
        await query.answer()
        return

    skill_id = query.data.replace("skill_", "")
    player = fight.player
    skills = CLASSES[player.player_class]["skills"]
    skill = skills.get(skill_id)

    if not skill:
        await query.answer("Скилл не найден!")
        return

    # Проверки
    if fight.cooldowns.get(skill_id, 0) > 0:
        await query.answer(f"Кулдаун ещё {fight.cooldowns[skill_id]} сек!")
        return

    if fight.player_mana < skill["mana"]:
        await query.answer("Недостаточно маны!")
        return

    # Используем скилл
    fight.player_mana -= skill["mana"]
    fight.cooldowns[skill_id] = skill["cooldown"]

    base_damage = player.get_total_damage()
    damage = int(base_damage * skill["damage_mult"])

    # Крит (с бонусом от скилла)
    crit_chance = player.get_crit_chance() + skill.get("crit_bonus", 0)
    is_crit = random.randint(1, 100) <= crit_chance
    if is_crit:
        damage = int(damage * 1.5)
        player.crits_dealt += 1

    # Множественные удары
    hits = skill.get("hits", 1)
    total_damage = damage * hits

    fight.enemy_hp -= total_damage

    log_msg = f"{skill['emoji']} {skill['name']}: {total_damage} урона"
    if is_crit:
        log_msg += " (КРИТ!)"
    if hits > 1:
        log_msg += f" ({hits} удара)"

    fight.fight_log.append(log_msg)

    # Эффекты
    if "stun" in skill:
        fight.stun_duration = skill["stun"]
        fight.fight_log.append(f"💫 Враг оглушён на {skill['stun']} сек!")

    if "poison" in skill:
        fight.poison_damage = skill["poison"]
        fight.poison_duration = skill["poison_duration"]
        fight.fight_log.append(f"☠️ Враг отравлен!")

    if "self_damage" in skill:
        fight.player_hp -= skill["self_damage"]
        fight.fight_log.append(f"🩸 Ты потерял {skill['self_damage']} HP")

    await query.answer(f"{skill['name']}!")

    if fight.enemy_hp <= 0:
        await end_fight(update, context, victory=True)
    elif fight.player_hp <= 0:
        await end_fight(update, context, victory=False)
    else:
        await update_fight_ui(update, context)

async def use_potion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if not fight:
        await query.answer()
        return

    potion_id = query.data.replace("use_", "")
    player = fight.player

    if potion_id not in player.inventory:
        await query.answer("У тебя нет этого зелья!")
        return

    item = ITEMS[potion_id]
    player.inventory.remove(potion_id)

    heal = item.get("heal", 0)
    mana = item.get("mana", 0)

    if heal:
        fight.player_hp = min(fight.player_max_hp, fight.player_hp + heal)
        fight.fight_log.append(f"❤️ +{heal} HP")
    if mana:
        fight.player_mana = min(player.max_mana, fight.player_mana + mana)
        fight.fight_log.append(f"💙 +{mana} маны")

    await query.answer(f"Использовано: {item['name']}")
    await update_fight_ui(update, context)

async def flee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    fight: Fight = context.user_data.get('fight')

    if fight and fight.enemy_attack_task:
        fight.enemy_attack_task.cancel()

    player = players[update.effective_user.id]
    await query.answer("Ты сбежал!")
    await show_main_menu(update, context, player, "🏃 Ты сбежал с поля боя!")

async def end_fight(update: Update, context: ContextTypes.DEFAULT_TYPE, victory: bool):
    fight: Fight = context.user_data.get('fight')
    if not fight:
        return

    if fight.enemy_attack_task:
        fight.enemy_attack_task.cancel()

    player = fight.player
    enemy = ENEMIES[fight.enemy_id]

    # Обновляем HP игрока
    player.hp = max(0, fight.player_hp)
    player.mana = fight.player_mana

    if victory:
        player.kills += 1
        if enemy.get("boss"):
            player.bosses_killed += 1

        exp_gain = enemy["exp"]
        gold_gain = enemy["gold"]
        player.exp += exp_gain
        player.gold += gold_gain

        text = f"🎉 **ПОБЕДА!**\n\n"
        text += f"Враг: {enemy['emoji']} {enemy['name']}\n"
        text += f"⭐ +{exp_gain} опыта\n"
        text += f"💰 +{gold_gain} золота\n\n"

        # Левел ап
        level_ups = 0
        while player.exp >= player.exp_needed:
            player.level_up()
            level_ups += 1

        if level_ups:
            text += f"🎊 **УРОВЕНЬ ПОВЫШЕН!** Теперь ты {player.level} уровня!\n"
            text += f"Все характеристики улучшены!\n\n"

        # Достижения
        new_achievements = player.check_achievements()
        for ach_id in new_achievements:
            ach = ACHIEVEMENTS[ach_id]
            text += f"🏆 Достижение: {ach['emoji']} {ach['name']}!\n"

        # Проверка выживания с 1 HP
        if player.hp == 1 and "survivor" not in player.achievements:
            player.achievements.append("survivor")
            text += f"🏆 Достижение: 💪 Выживший!\n"

        # Дроп предмета (шанс)
        if random.randint(1, 100) <= 20 + (10 if enemy.get("boss") else 0):
            possible_drops = [k for k, v in ITEMS.items() if v.get("price", 0) <= player.level * 50 + 100]
            if possible_drops:
                drop = random.choice(possible_drops)
                player.inventory.append(drop)
                text += f"\n🎁 Выпал предмет: {ITEMS[drop]['emoji']} {ITEMS[drop]['name']}!"
    else:
        text = f"💀 **ПОРАЖЕНИЕ**\n\n"
        text += f"Враг: {enemy['emoji']} {enemy['name']}\n"
        text += "Отдохни и попробуй снова!\n"

    text += f"\n❤️ HP: {player.hp}/{player.max_hp}"

    save_data()

    keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        pass

# ============ ПОДЗЕМЕЛЬЕ ============

async def dungeon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"🏰 **ПОДЗЕМЕЛЬЕ**\n\n"
    text += f"Текущий этаж: {player.dungeon_floor}\n"
    text += f"Максимальный этаж: {player.max_dungeon_floor}\n\n"
    text += "Чем глубже спускаешься, тем сильнее враги,\n"
    text += "но и награды лучше!\n"

    keyboard = [
        [InlineKeyboardButton(f"⚔️ Войти на этаж {player.dungeon_floor}", callback_data="dungeon_enter")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def dungeon_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    if player.hp <= 0:
        await query.answer("У тебя нет HP! Отдохни сначала.")
        return

    # Выбираем врага в зависимости от этажа
    floor = player.dungeon_floor

    if floor % 10 == 0:  # Каждый 10-й этаж - босс
        boss_list = ["boss_dragon", "boss_lich", "boss_titan"]
        enemy_id = boss_list[min(floor // 10 - 1, len(boss_list) - 1)]
    else:
        tier = min(3, 1 + floor // 3)
        possible_enemies = [eid for eid, e in ENEMIES.items() if e["tier"] == tier and not e.get("boss")]
        enemy_id = random.choice(possible_enemies) if possible_enemies else "goblin"

    # Усиливаем врага в зависимости от этажа
    fight = Fight(player, enemy_id)
    fight.enemy_hp = int(ENEMIES[enemy_id]["hp"] * (1 + floor * 0.1))
    fight.enemy_max_hp = fight.enemy_hp
    fight.enemy_damage = int(ENEMIES[enemy_id]["damage"] * (1 + floor * 0.05))

    context.user_data['fight'] = fight
    context.user_data['dungeon_mode'] = True

    fight.enemy_attack_task = asyncio.create_task(enemy_attack_loop(update, context))

    await update_fight_ui(update, context)
    await query.answer(f"Этаж {floor}!")

# ============ ИНВЕНТАРЬ ============

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"🎒 **ИНВЕНТАРЬ**\n\n"

    # Экипировка
    text += "📦 **Экипировка:**\n"
    if player.equipped_weapon:
        w = ITEMS[player.equipped_weapon]
        text += f"⚔️ Оружие: {w['emoji']} {w['name']} (+{w['damage']} урона)\n"
    else:
        text += "⚔️ Оружие: Нет\n"

    if player.equipped_armor:
        a = ITEMS[player.equipped_armor]
        text += f"🛡️ Броня: {a['emoji']} {a['name']} (+{a['defense']} защиты)\n"
    else:
        text += "🛡️ Броня: Нет\n"

    if player.equipped_accessory:
        acc = ITEMS[player.equipped_accessory]
        text += f"💍 Аксессуар: {acc['emoji']} {acc['name']}\n"
    else:
        text += "💍 Аксессуар: Нет\n"

    text += "\n📜 **Предметы:**\n"

    keyboard = []

    if player.inventory:
        item_counts = {}
        for item_id in player.inventory:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        for item_id, count in item_counts.items():
            item = ITEMS.get(item_id, {"name": "???", "emoji": "❓"})
            text += f"{item['emoji']} {item['name']} x{count}\n"
            keyboard.append([InlineKeyboardButton(f"Экипировать/Использовать: {item['name']}", callback_data=f"equip_{item_id}")])
    else:
        text += "Пусто\n"

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def equip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]
    item_id = query.data.replace("equip_", "")

    if item_id not in player.inventory:
        await query.answer("У тебя нет этого предмета!")
        return

    item = ITEMS.get(item_id)
    if not item:
        await query.answer("Предмет не найден!")
        return

    item_type = item.get("type")

    if item_type == "weapon":
        if player.equipped_weapon:
            player.inventory.append(player.equipped_weapon)
        player.inventory.remove(item_id)
        player.equipped_weapon = item_id
        await query.answer(f"Экипировано: {item['name']}")

    elif item_type == "armor":
        if player.equipped_armor:
            player.inventory.append(player.equipped_armor)
        player.inventory.remove(item_id)
        player.equipped_armor = item_id
        await query.answer(f"Экипировано: {item['name']}")

    elif item_type == "accessory":
        if player.equipped_accessory:
            player.inventory.append(player.equipped_accessory)
        player.inventory.remove(item_id)
        player.equipped_accessory = item_id
        await query.answer(f"Экипировано: {item['name']}")

    elif item_type == "consumable":
        # Вне боя используем зелья
        player.inventory.remove(item_id)
        heal = item.get("heal", 0)
        mana = item.get("mana", 0)
        if heal:
            player.hp = min(player.max_hp, player.hp + heal)
        if mana:
            player.mana = min(player.max_mana, player.mana + mana)
        await query.answer(f"Использовано: {item['name']}")

    save_data()
    await inventory(update, context)

# ============ МАГАЗИН ============

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"🏪 **МАГАЗИН**\n\n"
    text += f"💰 Твоё золото: {player.gold}\n\n"

    keyboard = [
        [InlineKeyboardButton("⚔️ Оружие", callback_data="shop_weapons")],
        [InlineKeyboardButton("🛡️ Броня", callback_data="shop_armor")],
        [InlineKeyboardButton("🧪 Зелья", callback_data="shop_potions")],
        [InlineKeyboardButton("💍 Аксессуары", callback_data="shop_accessories")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]
    category = query.data.replace("shop_", "")

    type_map = {
        "weapons": "weapon",
        "armor": "armor",
        "potions": "consumable",
        "accessories": "accessory"
    }
    item_type = type_map.get(category)

    text = f"🏪 **МАГАЗИН - {category.upper()}**\n\n"
    text += f"💰 Твоё золото: {player.gold}\n\n"

    keyboard = []

    for item_id, item in ITEMS.items():
        if item.get("type") == item_type:
            price = item["price"]
            can_buy = "✅" if player.gold >= price else "❌"
            text += f"{item['emoji']} {item['name']} - {price}💰 {can_buy}\n"

            # Показываем характеристики
            if "damage" in item:
                text += f"   +{item['damage']} урона\n"
            if "defense" in item:
                text += f"   +{item['defense']} защиты\n"
            if "heal" in item:
                text += f"   +{item['heal']} HP\n"
            if "mana" in item:
                text += f"   +{item['mana']} маны\n"

            keyboard.append([InlineKeyboardButton(f"Купить {item['name']} ({price}💰)", callback_data=f"buy_{item_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]
    item_id = query.data.replace("buy_", "")

    item = ITEMS.get(item_id)
    if not item:
        await query.answer("Предмет не найден!")
        return

    if player.gold < item["price"]:
        await query.answer("Недостаточно золота!")
        return

    player.gold -= item["price"]
    player.inventory.append(item_id)
    save_data()

    await query.answer(f"Куплено: {item['name']}!")

    # Возвращаемся в категорию
    type_map = {
        "weapon": "weapons",
        "armor": "armor",
        "consumable": "potions",
        "accessory": "accessories"
    }
    query.data = f"shop_{type_map[item['type']]}"
    await shop_category(update, context)

# ============ ДОСТИЖЕНИЯ ============

async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    text = f"🏆 **ДОСТИЖЕНИЯ** ({len(player.achievements)}/{len(ACHIEVEMENTS)})\n\n"

    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in player.achievements:
            text += f"✅ {ach['emoji']} **{ach['name']}**\n"
            text += f"   {ach['description']}\n\n"
        else:
            text += f"❌ ??? **{ach['name']}**\n"
            text += f"   {ach['description']}\n\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    await query.answer()

# ============ ОТДЫХ ============

async def rest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    player.hp = player.max_hp
    player.mana = player.max_mana
    save_data()

    await query.answer("Ты полностью восстановился!")
    await show_main_menu(update, context, player, "💤 Ты отдохнул и восстановил все силы!")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    player = players[user_id]

    # Очищаем данные боя
    context.user_data.pop('fight', None)
    context.user_data.pop('dungeon_mode', None)

    await show_main_menu(update, context, player)
    await query.answer()

def main():
    load_data()

    app = ApplicationBuilder().token("8550867725:AAHAhxhwn8Fu_6_m-fj5io5I0cjAUzCXlM4").build()

    app.add_handler(CommandHandler("start", start))

    # Выбор класса
    app.add_handler(CallbackQueryHandler(select_class, pattern="^class_"))

    # Главное меню
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(fight_menu, pattern="^fight_menu$"))
    app.add_handler(CallbackQueryHandler(start_fight, pattern="^fight_"))
    app.add_handler(CallbackQueryHandler(dungeon, pattern="^dungeon$"))
    app.add_handler(CallbackQueryHandler(dungeon_enter, pattern="^dungeon_enter$"))
    app.add_handler(CallbackQueryHandler(inventory, pattern="^inventory$"))
    app.add_handler(CallbackQueryHandler(equip_item, pattern="^equip_"))
    app.add_handler(CallbackQueryHandler(shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(shop_category, pattern="^shop_"))
    app.add_handler(CallbackQueryHandler(buy_item, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(achievements, pattern="^achievements$"))
    app.add_handler(CallbackQueryHandler(rest, pattern="^rest$"))

    # Бой
    app.add_handler(CallbackQueryHandler(action_attack, pattern="^action_attack$"))
    app.add_handler(CallbackQueryHandler(use_skill, pattern="^skill_"))
    app.add_handler(CallbackQueryHandler(use_potion, pattern="^use_"))
    app.add_handler(CallbackQueryHandler(flee, pattern="^flee$"))

    app.run_polling()

if __name__ == "__main__":
    main()
