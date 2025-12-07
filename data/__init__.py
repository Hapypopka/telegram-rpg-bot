"""
Игровые данные - константы
"""

from .classes import CLASSES
from .dungeons import DUNGEONS, ENEMIES
from .items import ITEMS, LEGENDARY_SETS
from .quests import QUESTS, ACHIEVEMENTS, DAILY_REWARDS
from .tavern import TAVERN_FOOD, MERCENARIES, BLACKSMITH_UPGRADES, ALCHEMY_RECIPES

__all__ = [
    'CLASSES',
    'DUNGEONS', 'ENEMIES',
    'ITEMS', 'LEGENDARY_SETS',
    'QUESTS', 'ACHIEVEMENTS', 'DAILY_REWARDS',
    'TAVERN_FOOD', 'MERCENARIES', 'BLACKSMITH_UPGRADES', 'ALCHEMY_RECIPES'
]
