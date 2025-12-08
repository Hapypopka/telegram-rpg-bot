"""
Класс PvP боя
"""

import random
from datetime import datetime


class PvPFight:
    """Класс для управления PvP боем между двумя игроками"""

    def __init__(self, player1, player2):
        self.player1 = player1  # Инициатор
        self.player2 = player2  # Соперник

        # ID игроков
        self.player1_id = player1.user_id
        self.player2_id = player2.user_id

        # HP в бою
        self.p1_hp = player1.get_max_hp()
        self.p1_max_hp = self.p1_hp
        self.p1_mana = player1.mana

        self.p2_hp = player2.get_max_hp()
        self.p2_max_hp = self.p2_hp
        self.p2_mana = player2.mana

        # Статы
        self.p1_damage = player1.get_total_damage()
        self.p1_defense = player1.get_total_defense()
        self.p1_crit = player1.get_total_crit()

        self.p2_damage = player2.get_total_damage()
        self.p2_defense = player2.get_total_defense()
        self.p2_crit = player2.get_total_crit()

        # Чей ход (1 или 2)
        self.current_turn = 1

        # Состояния
        self.cooldowns_p1 = {}
        self.cooldowns_p2 = {}
        self.effects_p1 = {}  # Эффекты на игроке 1
        self.effects_p2 = {}  # Эффекты на игроке 2

        # Блок/уклонение
        self.p1_block = False
        self.p2_block = False

        # Время хода (для таймаута)
        self.turn_start = datetime.now()
        self.turn_timeout = 30  # секунд на ход

        # Лог боя
        self.fight_log = []

        # Статус боя
        self.is_active = True
        self.winner = None

        # Message IDs для обновления
        self.message_id_p1 = None
        self.message_id_p2 = None

    def get_player_stats(self, player_num: int) -> dict:
        """Получить статы игрока"""
        if player_num == 1:
            return {
                "hp": self.p1_hp,
                "max_hp": self.p1_max_hp,
                "mana": self.p1_mana,
                "damage": self.p1_damage,
                "defense": self.p1_defense,
                "crit": self.p1_crit,
                "name": self.player1.name,
                "class": self.player1.player_class,
                "level": self.player1.level
            }
        else:
            return {
                "hp": self.p2_hp,
                "max_hp": self.p2_max_hp,
                "mana": self.p2_mana,
                "damage": self.p2_damage,
                "defense": self.p2_defense,
                "crit": self.p2_crit,
                "name": self.player2.name,
                "class": self.player2.player_class,
                "level": self.player2.level
            }

    def attack(self, attacker: int) -> dict:
        """Атака"""
        if attacker == 1:
            damage = self.p1_damage
            crit = self.p1_crit
            defense = self.p2_defense
            blocked = self.p2_block
            attacker_name = self.player1.name
            defender_name = self.player2.name
        else:
            damage = self.p2_damage
            crit = self.p2_crit
            defense = self.p1_defense
            blocked = self.p1_block
            attacker_name = self.player2.name
            defender_name = self.player1.name

        result = {"type": "attack", "attacker": attacker_name, "defender": defender_name}

        # Блок
        if blocked:
            result["blocked"] = True
            result["damage"] = 0
            if attacker == 1:
                self.p2_block = False
            else:
                self.p1_block = False
            self.fight_log.append(f"🛡️ {defender_name} заблокировал атаку!")
            return result

        # Расчёт урона
        is_crit = random.randint(1, 100) <= crit
        final_damage = max(1, damage - defense // 2)
        if is_crit:
            final_damage = int(final_damage * 1.5)
            result["crit"] = True

        # Нанести урон
        if attacker == 1:
            self.p2_hp = max(0, self.p2_hp - final_damage)
            result["target_hp"] = self.p2_hp
        else:
            self.p1_hp = max(0, self.p1_hp - final_damage)
            result["target_hp"] = self.p1_hp

        result["damage"] = final_damage

        crit_text = " 💥КРИТ!" if is_crit else ""
        self.fight_log.append(f"⚔️ {attacker_name} → {defender_name}: {final_damage} урона{crit_text}")

        # Проверка победы
        self._check_victory()

        return result

    def block(self, player: int) -> dict:
        """Блок"""
        if player == 1:
            self.p1_block = True
            name = self.player1.name
        else:
            self.p2_block = True
            name = self.player2.name

        self.fight_log.append(f"🛡️ {name} готовится к защите")
        return {"type": "block", "player": name}

    def use_skill(self, player: int, skill_id: str) -> dict:
        """Использовать скилл"""
        from data import CLASSES

        if player == 1:
            player_obj = self.player1
            cooldowns = self.cooldowns_p1
            mana = self.p1_mana
            damage = self.p1_damage
            target_hp = self.p2_hp
            target_defense = self.p2_defense
            attacker_name = self.player1.name
            defender_name = self.player2.name
        else:
            player_obj = self.player2
            cooldowns = self.cooldowns_p2
            mana = self.p2_mana
            damage = self.p2_damage
            target_hp = self.p1_hp
            target_defense = self.p1_defense
            attacker_name = self.player2.name
            defender_name = self.player1.name

        # Получить скилл
        player_class = player_obj.player_class
        skills = CLASSES.get(player_class, {}).get("skills", {})
        skill = skills.get(skill_id)

        if not skill:
            return {"error": "Скилл не найден"}

        # Проверить кулдаун
        if cooldowns.get(skill_id, 0) > 0:
            return {"error": f"Скилл на кулдауне: {cooldowns[skill_id]} ходов"}

        # Проверить ману
        mana_cost = skill.get("mana", 0)
        if mana < mana_cost:
            return {"error": "Недостаточно маны"}

        # Потратить ману
        if player == 1:
            self.p1_mana -= mana_cost
        else:
            self.p2_mana -= mana_cost

        # Установить кулдаун
        cooldowns[skill_id] = skill.get("cooldown", 0)

        result = {"type": "skill", "skill": skill["name"], "attacker": attacker_name}

        # Обработать эффекты скилла
        if "damage_mult" in skill:
            mult = skill["damage_mult"]
            hits = skill.get("hits", 1)
            total_damage = 0

            for _ in range(hits):
                hit_damage = max(1, int(damage * mult) - target_defense // 2)
                total_damage += hit_damage

            if player == 1:
                self.p2_hp = max(0, self.p2_hp - total_damage)
            else:
                self.p1_hp = max(0, self.p1_hp - total_damage)

            result["damage"] = total_damage
            self.fight_log.append(f"⚡ {attacker_name} использует {skill['name']}: {total_damage} урона!")

        if skill.get("block"):
            if player == 1:
                self.p1_block = True
            else:
                self.p2_block = True
            self.fight_log.append(f"🛡️ {attacker_name} активировал щит!")

        # Проверка победы
        self._check_victory()

        return result

    def _check_victory(self):
        """Проверить победителя"""
        if self.p1_hp <= 0:
            self.is_active = False
            self.winner = 2
        elif self.p2_hp <= 0:
            self.is_active = False
            self.winner = 1

    def next_turn(self):
        """Переключить ход"""
        # Уменьшить кулдауны
        for skill_id in self.cooldowns_p1:
            if self.cooldowns_p1[skill_id] > 0:
                self.cooldowns_p1[skill_id] -= 1
        for skill_id in self.cooldowns_p2:
            if self.cooldowns_p2[skill_id] > 0:
                self.cooldowns_p2[skill_id] -= 1

        # Переключить ход
        self.current_turn = 2 if self.current_turn == 1 else 1
        self.turn_start = datetime.now()

    def get_current_player_id(self) -> int:
        """Получить ID текущего игрока"""
        return self.player1_id if self.current_turn == 1 else self.player2_id

    def is_turn_timeout(self) -> bool:
        """Проверить таймаут хода"""
        elapsed = (datetime.now() - self.turn_start).seconds
        return elapsed >= self.turn_timeout

    def forfeit(self, player: int):
        """Сдаться"""
        self.is_active = False
        self.winner = 2 if player == 1 else 1
        loser_name = self.player1.name if player == 1 else self.player2.name
        self.fight_log.append(f"🏳️ {loser_name} сдался!")
