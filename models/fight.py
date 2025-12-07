"""
Класс боя
"""

import random
from datetime import datetime

from data import DUNGEONS, ENEMIES, MERCENARIES


class Fight:
    """Класс для управления боем"""

    def __init__(self, player, dungeon_id: str, floor: int, is_boss: bool = False):
        self.player = player
        self.dungeon_id = dungeon_id
        self.dungeon = DUNGEONS[dungeon_id]
        self.floor = floor
        self.is_boss = is_boss

        # Бонусы от еды (проверяем срок действия)
        self.food_bonus_hp = 0
        self.food_bonus_damage = 0
        self.food_bonus_defense = 0
        self.food_bonus_crit = 0
        self.food_bonus_mana_regen = 0
        now = datetime.now().timestamp()
        if player.food_buffs:
            for buff_type, buff_data in list(player.food_buffs.items()):
                if buff_data.get("expires", 0) > now:
                    if buff_type == "hp":
                        self.food_bonus_hp = buff_data["value"]
                    elif buff_type == "damage":
                        self.food_bonus_damage = buff_data["value"]
                    elif buff_type == "defense":
                        self.food_bonus_defense = buff_data["value"]
                    elif buff_type == "crit":
                        self.food_bonus_crit = buff_data["value"]
                    elif buff_type == "mana_regen":
                        self.food_bonus_mana_regen = buff_data["value"]

        # Бонусы от наёмника
        self.merc_bonus_damage = 0
        self.merc_bonus_defense = 0
        self.merc_bonus_crit = 0
        self.merc_bonus_heal = 0
        self.merc_bonus_mana_regen = 0
        if player.mercenary:
            merc = MERCENARIES.get(player.mercenary["id"])
            if merc:
                bonus = merc.get("bonus", {})
                self.merc_bonus_damage = bonus.get("damage", 0)
                self.merc_bonus_defense = bonus.get("defense", 0)
                self.merc_bonus_crit = bonus.get("crit", 0)
                self.merc_bonus_heal = bonus.get("heal_per_turn", 0)
                self.merc_bonus_mana_regen = bonus.get("mana_regen", 0)

        # HP/Мана в бою (с бонусами)
        self.player_hp = player.hp
        self.player_mana = player.mana
        self.player_max_hp = player.get_max_hp() + self.food_bonus_hp

        # Враг
        if is_boss:
            self.enemy_name = self.dungeon["boss"]
            self.enemy_emoji = self.dungeon["boss_emoji"]
            self.enemy_hp = int(self.dungeon["boss_hp"] * (1 + floor * 0.05))
            self.enemy_max_hp = self.enemy_hp
            self.enemy_damage = int(self.dungeon["boss_damage"] * (1 + floor * 0.03))
            self.exp_reward = int(100 * self.dungeon["exp_mult"] * (1 + floor * 0.1))
            self.gold_reward = int(15 * self.dungeon["gold_mult"] * (1 + floor * 0.1))  # Уменьшено в 10 раз
        else:
            enemy_id = random.choice(self.dungeon["enemies"])
            enemy = ENEMIES[enemy_id]
            self.enemy_id = enemy_id
            self.enemy_name = enemy["name"]
            self.enemy_emoji = enemy["emoji"]
            self.enemy_hp = int(enemy["hp"] * (1 + floor * 0.1))
            self.enemy_max_hp = self.enemy_hp
            self.enemy_damage = int(enemy["damage"] * (1 + floor * 0.05))
            self.exp_reward = int(enemy["exp"] * self.dungeon["exp_mult"])
            self.gold_reward = int(enemy["gold"] * self.dungeon["gold_mult"] * 0.1)  # Уменьшено в 10 раз
            self.enemy_special = {k: v for k, v in enemy.items() if k in ["poison", "burn", "lifesteal"]}

        # Состояния боя
        self.cooldowns = {}
        self.player_effects = {}
        self.enemy_effects = {}
        self.block_next = False
        self.dodge_next = False
        self.invisible = 0
        self.invulnerable = 0
        self.barrier = 0
        self.first_attack = True

        # Механика подземелья
        self.mechanic_timer = 0
        self.enemy_resurrected = False

        # Лог боя
        self.fight_log = []

        # Таск атаки врага
        self.enemy_attack_task = None
        self.fight_active = True

        # Время начала
        self.start_time = datetime.now()
