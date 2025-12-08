"""
Класс игрока
"""

from data import CLASSES, ITEMS, EPIC_SETS


class Player:
    """Класс игрока"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.name = None
        self.player_class = None
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        self.gold = 100

        # HP/Мана (базовые, до выбора класса)
        self.hp = 100
        self.mana = 50

        # Инвентарь
        self.inventory = {"hp_potion_small": 3, "mana_potion_small": 2}

        # Экипировка (новая система слотов)
        self.equipment = {
            "weapon": None,      # Оружие
            "helmet": None,      # Шлем
            "shoulders": None,   # Плечи
            "chest": None,       # Грудь
            "belt": None,        # Пояс
            "gloves": None,      # Перчатки
            "leggings": None,    # Поножи
            "boots": None,       # Сапоги
            "ring": None,        # Кольцо
            "necklace": None     # Ожерелье
        }

        # Улучшения кузнеца
        self.blacksmith_upgrades = {}

        # Прогресс
        self.current_dungeon = None
        self.current_floor = 0

        # Статистика
        self.stats = {
            "kills": 0,
            "boss_kills": 0,
            "deaths": 0,
            "floors": 0,
            "max_floor": 0,
            "crits": 0,
            "gold_earned": 0,
            "gold_spent": 0,
            "quests_done": 0,
            "dailies_claimed": 0
        }

        # Квесты
        self.quest_progress = {}
        self.completed_quests = []

        # Достижения
        self.achievements = []

        # Титулы
        self.titles = []
        self.title = None

        # Ежедневка
        self.last_daily = None
        self.daily_streak = 0

        # Бафы от еды
        self.food_buffs = {}

        # Наёмник
        self.mercenary = None

        # Слоты для зелий в бою (2 слота)
        self.potion_slots = {
            "slot_1": "hp_potion_small",    # По умолчанию HP зелье
            "slot_2": "mana_potion_small"   # По умолчанию Мана зелье
        }

        # Сокеты в экипировке (slot -> socket_id)
        self.item_sockets = {}

        # Таланты (список выбранных талант-id)
        self.talents = []
        # Уровни, на которых нужно выбрать талант (очередь)
        self.pending_talent_levels = []

        # Процедурные предметы (id -> item_data)
        self.procedural_items = {}

        # PvP статистика
        self.pvp_rating = 1000  # Начальный рейтинг
        self.pvp_wins = 0
        self.pvp_losses = 0
        self.pvp_win_streak = 0

    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "player_class": self.player_class,
            "level": self.level,
            "exp": self.exp,
            "exp_to_level": self.exp_to_level,
            "gold": self.gold,
            "hp": self.hp,
            "mana": self.mana,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "blacksmith_upgrades": self.blacksmith_upgrades,
            "current_dungeon": self.current_dungeon,
            "current_floor": self.current_floor,
            "stats": self.stats,
            "quest_progress": self.quest_progress,
            "completed_quests": self.completed_quests,
            "achievements": self.achievements,
            "titles": self.titles,
            "title": self.title,
            "last_daily": self.last_daily,
            "daily_streak": self.daily_streak,
            "food_buffs": self.food_buffs,
            "mercenary": self.mercenary,
            "potion_slots": self.potion_slots,
            "item_sockets": self.item_sockets,
            "talents": self.talents,
            "pending_talent_levels": self.pending_talent_levels,
            "procedural_items": self.procedural_items,
            "pvp_rating": self.pvp_rating,
            "pvp_wins": self.pvp_wins,
            "pvp_losses": self.pvp_losses,
            "pvp_win_streak": self.pvp_win_streak
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Десериализация из словаря"""
        player = cls(data.get("user_id", 0))

        # Миграция старых данных
        if "equipped" in data and "equipment" not in data:
            data["equipment"] = {
                "weapon": data["equipped"].get("weapon"),
                "helmet": None, "shoulders": None, "chest": None,
                "belt": None, "gloves": None, "leggings": None,
                "boots": None, "ring": None, "necklace": None
            }

        # Миграция старой системы equipment (armor/accessory -> новые слоты)
        if "equipment" in data:
            old_eq = data["equipment"]
            # Если есть старые ключи armor/accessory
            if "armor" in old_eq or "accessory" in old_eq:
                new_eq = {
                    "weapon": old_eq.get("weapon"),
                    "helmet": None, "shoulders": None,
                    "chest": old_eq.get("armor"),  # armor -> chest
                    "belt": None, "gloves": None, "leggings": None,
                    "boots": None,
                    "ring": old_eq.get("accessory"),  # accessory -> ring
                    "necklace": None
                }
                data["equipment"] = new_eq

            # Миграция legendary_equipment в equipment
            if "legendary_equipment" in data:
                leg_eq = data["legendary_equipment"]
                for slot in ["helmet", "chest", "gloves", "boots"]:
                    if leg_eq.get(slot) and not data["equipment"].get(slot):
                        data["equipment"][slot] = leg_eq[slot]

            # Добавить недостающие слоты
            default_slots = ["weapon", "helmet", "shoulders", "chest", "belt",
                             "gloves", "leggings", "boots", "ring", "necklace"]
            for slot in default_slots:
                if slot not in data["equipment"]:
                    data["equipment"][slot] = None

        if "exp_needed" in data and "exp_to_level" not in data:
            data["exp_to_level"] = data["exp_needed"]

        if "active_title" in data and "title" not in data:
            data["title"] = data["active_title"]

        # Если inventory - список, конвертируем в словарь
        if isinstance(data.get("inventory"), list):
            data["inventory"] = {"hp_potion_small": 3, "mana_potion_small": 2}

        # Если stats неполный, дополняем
        if "stats" in data:
            default_stats = {
                "kills": 0, "boss_kills": 0, "deaths": 0, "floors": 0,
                "max_floor": 0, "crits": 0, "gold_earned": 0,
                "gold_spent": 0, "quests_done": 0, "dailies_claimed": 0
            }
            for key, val in default_stats.items():
                if key not in data["stats"]:
                    data["stats"][key] = val

        # Миграция: добавить слоты зелий для старых игроков
        if "potion_slots" not in data:
            data["potion_slots"] = {
                "slot_1": "hp_potion_small",
                "slot_2": "mana_potion_small"
            }

        # Миграция: добавить сокеты для старых игроков
        if "item_sockets" not in data:
            data["item_sockets"] = {}

        # Миграция: добавить таланты для старых игроков
        if "talents" not in data:
            data["talents"] = []
        if "pending_talent_levels" not in data:
            data["pending_talent_levels"] = []

        # Миграция: добавить процедурные предметы для старых игроков
        if "procedural_items" not in data:
            data["procedural_items"] = {}

        # Миграция: добавить PvP статистику для старых игроков
        if "pvp_rating" not in data:
            data["pvp_rating"] = 1000
        if "pvp_wins" not in data:
            data["pvp_wins"] = 0
        if "pvp_losses" not in data:
            data["pvp_losses"] = 0
        if "pvp_win_streak" not in data:
            data["pvp_win_streak"] = 0

        for key, value in data.items():
            if hasattr(player, key):
                setattr(player, key, value)

        return player

    def get_item_data(self, item_id: str) -> dict:
        """Получить данные предмета (обычного или процедурного)"""
        # Сначала проверяем процедурные предметы
        if item_id and item_id.startswith("proc_"):
            return self.procedural_items.get(item_id, {})
        # Иначе берём из обычных предметов
        return ITEMS.get(item_id, {})

    def get_equipped_stats(self) -> dict:
        """Получить суммарные статы от всей экипировки"""
        stats = {
            "hp": 0, "mana": 0, "damage": 0, "defense": 0,
            "crit": 0, "dodge": 0, "lifesteal": 0, "block": 0,
            "fire_res": 0, "poison_res": 0, "mana_regen": 0, "double_hit": 0
        }

        for slot, item_id in self.equipment.items():
            if not item_id:
                continue
            item = self.get_item_data(item_id)
            stats["hp"] += item.get("hp_bonus", 0) + item.get("hp", 0)
            stats["mana"] += item.get("mana_bonus", 0) + item.get("mana", 0)
            stats["damage"] += item.get("damage", 0) + item.get("damage_bonus", 0)
            stats["defense"] += item.get("defense", 0) + item.get("defense_bonus", 0)
            stats["crit"] += item.get("crit_bonus", 0) + item.get("crit", 0)
            stats["dodge"] += item.get("dodge_bonus", 0) + item.get("dodge", 0)
            stats["lifesteal"] += item.get("lifesteal", 0)
            stats["block"] += item.get("block", 0)
            stats["fire_res"] += item.get("fire_res", 0)
            stats["poison_res"] += item.get("poison_res", 0)
            stats["mana_regen"] += item.get("mana_regen", 0)
            stats["double_hit"] += item.get("double_hit", 0)

        # Бонус от эпического сета
        set_bonus = self.get_epic_set_bonus()
        if set_bonus:
            stats["hp"] += set_bonus.get("hp", 0)
            stats["mana"] += set_bonus.get("mana", 0)
            stats["damage"] += set_bonus.get("damage", 0)
            stats["defense"] += set_bonus.get("defense", 0)
            stats["crit"] += set_bonus.get("crit", 0)

        # Бонус от сокетов
        stats = self.add_socket_bonuses(stats)

        return stats

    def add_socket_bonuses(self, stats: dict) -> dict:
        """Добавить бонусы от сокетов"""
        from data.tavern import SOCKETS

        for slot, socket_id in self.item_sockets.items():
            if not socket_id:
                continue
            # Проверить что в слоте есть предмет
            if not self.equipment.get(slot):
                continue
            socket = SOCKETS.get(socket_id, {})
            bonus = socket.get("bonus", {})
            for stat, value in bonus.items():
                if stat in stats:
                    stats[stat] += value
        return stats

    def get_socket_stats(self) -> dict:
        """Получить суммарные бонусы от всех сокетов"""
        from data.tavern import SOCKETS

        stats = {
            "hp": 0, "mana": 0, "damage": 0, "defense": 0,
            "crit": 0, "dodge": 0, "lifesteal": 0, "block": 0,
            "fire_res": 0, "poison_res": 0, "mana_regen": 0, "double_hit": 0
        }
        for slot, socket_id in self.item_sockets.items():
            if not socket_id or not self.equipment.get(slot):
                continue
            socket = SOCKETS.get(socket_id, {})
            bonus = socket.get("bonus", {})
            for stat, value in bonus.items():
                if stat in stats:
                    stats[stat] += value
        return stats

    def get_max_hp(self) -> int:
        """Максимальное HP"""
        if not self.player_class:
            return 100

        class_data = CLASSES[self.player_class]
        base_hp = class_data["base_hp"]

        # Бонус за уровень
        hp = base_hp + (self.level - 1) * 10

        # Бонус от экипировки
        hp += self.get_equipped_stats()["hp"]

        # Бонус от талантов
        hp += self.get_talent_stats().get("hp", 0)

        return hp

    def get_max_mana(self) -> int:
        """Максимальная мана"""
        if not self.player_class:
            return 50

        class_data = CLASSES[self.player_class]
        base_mana = class_data["base_mana"]

        # Бонус за уровень
        mana = base_mana + (self.level - 1) * 5

        # Бонус от экипировки
        mana += self.get_equipped_stats()["mana"]

        # Бонус от талантов
        mana += self.get_talent_stats().get("mana", 0)

        return mana

    def get_total_damage(self) -> int:
        """Общий урон"""
        if not self.player_class:
            return 10

        class_data = CLASSES[self.player_class]
        damage = class_data["base_damage"]

        # Бонус за уровень
        damage += (self.level - 1) * 2

        # Бонус от экипировки
        damage += self.get_equipped_stats()["damage"]

        # Бонус от кузнеца
        sharpen = self.blacksmith_upgrades.get("sharpen", 0)
        damage += sharpen * 3

        # Бонус от талантов
        damage += self.get_talent_stats().get("damage", 0)

        return damage

    def get_total_defense(self) -> int:
        """Общая защита"""
        if not self.player_class:
            return 5

        class_data = CLASSES[self.player_class]
        defense = class_data["base_defense"]

        # Бонус за уровень
        defense += (self.level - 1)

        # Бонус от экипировки
        defense += self.get_equipped_stats()["defense"]

        # Бонус от кузнеца
        reinforce = self.blacksmith_upgrades.get("reinforce", 0)
        defense += reinforce * 3

        # Бонус от талантов
        defense += self.get_talent_stats().get("defense", 0)

        return defense

    def get_crit_chance(self) -> int:
        """Шанс крита"""
        if not self.player_class:
            return 5

        class_data = CLASSES[self.player_class]
        crit = class_data["base_crit"]

        # Бонус от экипировки
        crit += self.get_equipped_stats()["crit"]

        # Бонус от талантов
        crit += self.get_talent_stats().get("crit", 0)

        return crit

    def get_crit_multiplier(self) -> float:
        """Множитель критического урона (зависит от оружия)"""
        base_mult = 1.5

        # Бонус от оружия
        weapon_id = self.equipment.get("weapon")
        if weapon_id:
            weapon = self.get_item_data(weapon_id)
            base_mult = weapon.get("crit_mult", 1.5)

        return base_mult

    def get_dodge_chance(self) -> int:
        """Шанс уклонения"""
        dodge = 0

        # Бонус от экипировки
        dodge += self.get_equipped_stats().get("dodge", 0)

        # Бонус от талантов
        dodge += self.get_talent_stats().get("dodge", 0)

        return dodge

    def get_block_chance(self) -> int:
        """Шанс блока (парирования)"""
        block = 0

        # Бонус от экипировки
        block += self.get_equipped_stats().get("block", 0)

        # Бонус от талантов
        block += self.get_talent_stats().get("block", 0)

        return block

    def get_fire_resistance(self) -> int:
        """Сопротивление огню"""
        res = self.get_equipped_stats().get("fire_res", 0)
        res += self.get_talent_stats().get("fire_res", 0)
        return res

    def get_poison_resistance(self) -> int:
        """Сопротивление яду"""
        res = self.get_equipped_stats().get("poison_res", 0)
        res += self.get_talent_stats().get("poison_res", 0)
        return res

    def get_lifesteal(self) -> float:
        """Вампиризм"""
        lifesteal = 0.0

        # От зачарования кузнеца
        if self.blacksmith_upgrades.get("enchant_life"):
            lifesteal += 0.1

        # От экипировки
        lifesteal += self.get_equipped_stats()["lifesteal"]

        # От талантов
        lifesteal += self.get_talent_stats().get("lifesteal", 0)

        return lifesteal

    def get_talent_stats(self) -> dict:
        """Получить суммарные бонусы от всех талантов"""
        from data import TALENTS

        stats = {
            "hp": 0, "mana": 0, "damage": 0, "defense": 0,
            "crit": 0, "dodge": 0, "lifesteal": 0, "block": 0,
            "fire_res": 0, "poison_res": 0, "mana_regen": 0, "double_hit": 0
        }

        if not self.player_class or self.player_class not in TALENTS:
            return stats

        class_talents = TALENTS[self.player_class]

        # Пройти по всем уровням талантов
        for level, talent_options in class_talents.items():
            for talent in talent_options:
                if talent["id"] in self.talents:
                    bonus = talent.get("bonus", {})
                    for stat, value in bonus.items():
                        if stat in stats:
                            stats[stat] += value
        return stats

    def get_epic_set_bonus(self) -> dict:
        """Получить бонус от эпического сета"""
        # Подсчитать надетые части каждого сета
        set_counts = {}
        for slot, item_id in self.equipment.items():
            if not item_id:
                continue
            item = ITEMS.get(item_id, {})
            set_id = item.get("set")
            if set_id:
                set_counts[set_id] = set_counts.get(set_id, 0) + 1

        # Найти лучший бонус
        best_bonus = {}
        for set_id, count in set_counts.items():
            if set_id in EPIC_SETS:
                epic_set = EPIC_SETS[set_id]
                if count >= 2 and "bonus_2_stats" in epic_set:
                    best_bonus = epic_set.get("bonus_2_stats", {})
                if count >= 4 and "bonus_4_stats" in epic_set:
                    best_bonus = epic_set.get("bonus_4_stats", best_bonus)
                if count >= 6 and "bonus_6_stats" in epic_set:
                    best_bonus = epic_set.get("bonus_6_stats", best_bonus)
                if count >= 8 and "bonus_8_stats" in epic_set:
                    best_bonus = epic_set.get("bonus_8_stats", best_bonus)

        return best_bonus

    def count_epic_pieces(self, set_id: str) -> int:
        """Подсчёт частей эпического сета"""
        count = 0
        for slot, item_id in self.equipment.items():
            if not item_id:
                continue
            item = ITEMS.get(item_id, {})
            if item.get("set") == set_id:
                count += 1
        return count

    def count_legendary_pieces(self) -> int:
        """Подсчёт экипированных легендарных предметов"""
        count = 0
        for slot, item_id in self.equipment.items():
            if not item_id:
                continue
            item = ITEMS.get(item_id, {})
            if item.get("rarity") == "legendary":
                count += 1
        return count

    def update_quest_progress(self):
        """Обновить прогресс квестов на основе статистики"""
        from data import QUESTS

        for quest_id, quest in QUESTS.items():
            if quest["type"] in ("daily", "weekly"):
                stat_key = quest.get("stat")
                if stat_key and stat_key in self.stats:
                    self.quest_progress[quest_id] = self.stats[stat_key]

    def check_achievements(self):
        """Проверить и выдать достижения"""
        from data import ACHIEVEMENTS

        new_achievements = []

        # Первая кровь
        if "first_blood" not in self.achievements and self.stats.get("kills", 0) >= 1:
            self.achievements.append("first_blood")
            new_achievements.append(ACHIEVEMENTS["first_blood"])

        # Убийства
        if "slayer_100" not in self.achievements and self.stats.get("kills", 0) >= 100:
            self.achievements.append("slayer_100")
            new_achievements.append(ACHIEVEMENTS["slayer_100"])

        if "slayer_1000" not in self.achievements and self.stats.get("kills", 0) >= 1000:
            self.achievements.append("slayer_1000")
            new_achievements.append(ACHIEVEMENTS["slayer_1000"])

        # Боссы
        if "boss_hunter" not in self.achievements and self.stats.get("boss_kills", 0) >= 5:
            self.achievements.append("boss_hunter")
            new_achievements.append(ACHIEVEMENTS["boss_hunter"])

        if "boss_slayer" not in self.achievements and self.stats.get("boss_kills", 0) >= 20:
            self.achievements.append("boss_slayer")
            new_achievements.append(ACHIEVEMENTS["boss_slayer"])

        # Уровень
        if "veteran" not in self.achievements and self.level >= 10:
            self.achievements.append("veteran")
            new_achievements.append(ACHIEVEMENTS["veteran"])

        if "master" not in self.achievements and self.level >= 20:
            self.achievements.append("master")
            new_achievements.append(ACHIEVEMENTS["master"])

        if "grandmaster" not in self.achievements and self.level >= 30:
            self.achievements.append("grandmaster")
            new_achievements.append(ACHIEVEMENTS["grandmaster"])

        # Золото
        if "rich" not in self.achievements and self.gold >= 1000:
            self.achievements.append("rich")
            new_achievements.append(ACHIEVEMENTS["rich"])

        if "wealthy" not in self.achievements and self.gold >= 10000:
            self.achievements.append("wealthy")
            new_achievements.append(ACHIEVEMENTS["wealthy"])

        if "magnate" not in self.achievements and self.gold >= 100000:
            self.achievements.append("magnate")
            new_achievements.append(ACHIEVEMENTS["magnate"])

        # Квесты
        if "quester" not in self.achievements and self.stats.get("quests_done", 0) >= 50:
            self.achievements.append("quester")
            new_achievements.append(ACHIEVEMENTS["quester"])

        # Полный эпический сет (любой)
        for set_id in EPIC_SETS:
            if "legend" not in self.achievements and self.count_epic_pieces(set_id) >= 4:
                self.achievements.append("legend")
                new_achievements.append(ACHIEVEMENTS["legend"])
                break

        return new_achievements
