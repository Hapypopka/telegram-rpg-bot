"""
Хранение и загрузка данных игроков
"""

import json
import os
from config import DATA_FILE
from models import Player


# Словарь игроков в памяти
players = {}


def save_data():
    """Сохранить данные всех игроков в файл"""
    data = {str(uid): player.to_dict() for uid, player in players.items()}
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_data():
    """Загрузить данные игроков из файла"""
    global players
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for uid, pdata in data.items():
                players[int(uid)] = Player.from_dict(pdata)
            print(f"Загружено {len(players)} игроков")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            players = {}


def get_player(user_id: int) -> Player:
    """Получить игрока по ID или создать нового"""
    if user_id not in players:
        players[user_id] = Player(user_id)
    return players[user_id]
