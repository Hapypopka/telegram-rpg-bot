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
            "mercenary": self.mercenary
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

        for key, value in data.items():
            if hasattr(player, key):
                setattr(player, key, value)

        return player

    def get_equipped_stats(self) -> dict:
        """Получить суммарные статы от всей экипировки"""
        stats = {
            "hp": 0, "mana": 0, "damage": 0, "defense": 0,
            "crit": 0, "dodge": 0, "lifesteal": 0
        }

        for slot, item_id in self.equipment.items():
            if not item_id:
                continue
            item = ITEMS.get(item_id, {})
            stats["hp"] += item.get("hp_bonus", 0) + item.get("hp", 0)
            stats["mana"] += item.get("mana_bonus", 0) + item.get("mana", 0)
            stats["damage"] += item.get("damage", 0) + item.get("damage_bonus", 0)
            stats["defense"] += item.get("defense", 0) + item.get("defense_bonus", 0)
            stats["crit"] += item.get("crit_bonus", 0) + item.get("crit", 0)
            stats["dodge"] += item.get("dodge_bonus", 0) + item.get("dodge", 0)
            stats["lifesteal"] += item.get("lifesteal", 0)

        # Бонус от эпического сета
        set_bonus = self.get_epic_set_bonus()
        if set_bonus:
            stats["hp"] += set_bonus.get("hp", 0)
            stats["mana"] += set_bonus.get("mana", 0)
            stats["damage"] += set_bonus.get("damage", 0)
            stats["defense"] += set_bonus.get("defense", 0)
            stats["crit"] += set_bonus.get("crit", 0)

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

        return defense

    def get_crit_chance(self) -> int:
        """Шанс крита"""
        if not self.player_class:
            return 5

        class_data = CLASSES[self.player_class]
        crit = class_data["base_crit"]

        # Бонус от экипировки
        crit += self.get_equipped_stats()["crit"]

        return crit

    def get_dodge_chance(self) -> int:
        """Шанс уклонения"""
        dodge = 0

        # Бонус от экипировки
        dodge += self.get_equipped_stats()["dodge"]

        return dodge

    def get_lifesteal(self) -> float:
        """Вампиризм"""
        lifesteal = 0.0

        # От зачарования кузнеца
        if self.blacksmith_upgrades.get("enchant_life"):
            lifesteal += 0.1

        # От экипировки
        lifesteal += self.get_equipped_stats()["lifesteal"]

        return lifesteal

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
                if count >= 2 and "bonus_2" in epic_set:
                    best_bonus = epic_set.get("bonus_2_stats", {})
                if count >= 4 and "bonus_4" in epic_set:
                    best_bonus = epic_set.get("bonus_4_stats", best_bonus)

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
