"""
Генерация изображения персонажа с экипировкой
"""

from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from typing import Optional, Dict, Any

# Базовый размер изображения персонажа
AVATAR_SIZE = (256, 256)

# Путь к ассетам
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

# Маппинг классов на базовые спрайты
CLASS_SPRITES = {
    "warrior": "warrior.png",
    "mage": "mage.png",
    "archer": "archer.png",
    "paladin": "paladin.png"
}

# Слои для отрисовки (порядок важен - снизу вверх)
LAYER_ORDER = ["base", "armor", "helmet", "weapon", "accessory", "effects"]


def get_asset_path(layer: str, filename: str) -> str:
    """Получить полный путь к ассету"""
    return os.path.join(ASSETS_PATH, layer, filename)


def asset_exists(layer: str, filename: str) -> bool:
    """Проверить существует ли ассет"""
    return os.path.exists(get_asset_path(layer, filename))


def load_sprite(layer: str, filename: str) -> Optional[Image.Image]:
    """Загрузить спрайт с прозрачностью"""
    path = get_asset_path(layer, filename)
    if os.path.exists(path):
        try:
            img = Image.open(path).convert("RGBA")
            return img.resize(AVATAR_SIZE, Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Ошибка загрузки спрайта {path}: {e}")
    return None


def create_placeholder_avatar(player_class: str, level: int) -> Image.Image:
    """Создать заглушку если нет спрайтов"""
    img = Image.new("RGBA", AVATAR_SIZE, (40, 40, 50, 255))
    draw = ImageDraw.Draw(img)

    # Цвета классов
    class_colors = {
        "warrior": (200, 80, 80),    # Красный
        "mage": (80, 80, 200),       # Синий
        "archer": (80, 200, 80),     # Зелёный
        "paladin": (200, 200, 80)    # Жёлтый
    }

    color = class_colors.get(player_class, (150, 150, 150))

    # Рисуем простую фигуру персонажа
    # Голова
    draw.ellipse([103, 30, 153, 80], fill=color, outline=(255, 255, 255))
    # Тело
    draw.rectangle([108, 85, 148, 160], fill=color, outline=(255, 255, 255))
    # Ноги
    draw.rectangle([108, 165, 123, 220], fill=color, outline=(255, 255, 255))
    draw.rectangle([133, 165, 148, 220], fill=color, outline=(255, 255, 255))
    # Руки
    draw.rectangle([80, 90, 105, 140], fill=color, outline=(255, 255, 255))
    draw.rectangle([151, 90, 176, 140], fill=color, outline=(255, 255, 255))

    # Эмодзи класса
    class_emoji = {
        "warrior": "W",
        "mage": "M",
        "archer": "A",
        "paladin": "P"
    }

    # Уровень внизу
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((118, 235), f"Lv.{level}", fill=(255, 255, 255), font=font, anchor="mm")

    return img


def generate_character_image(
    player_class: str,
    level: int,
    equipment: Dict[str, Optional[str]] = None,
    effects: list = None
) -> BytesIO:
    """
    Генерирует изображение персонажа с экипировкой

    Args:
        player_class: Класс персонажа (warrior, mage, archer, paladin)
        level: Уровень персонажа
        equipment: Словарь {слот: id_предмета} экипированных вещей
        effects: Список активных эффектов для отображения

    Returns:
        BytesIO: Изображение в формате PNG для отправки в Telegram
    """
    equipment = equipment or {}
    effects = effects or []

    # Пытаемся загрузить базовый спрайт класса
    base_sprite_name = CLASS_SPRITES.get(player_class, "warrior.png")
    base = load_sprite("base", base_sprite_name)

    if base is None:
        # Нет спрайтов - используем заглушку
        base = create_placeholder_avatar(player_class, level)

    # Создаём финальное изображение
    final = Image.new("RGBA", AVATAR_SIZE, (0, 0, 0, 0))
    final.paste(base, (0, 0), base)

    # Накладываем слои экипировки
    slot_to_layer = {
        "armor": "armor",
        "helmet": "helmet",
        "weapon": "weapon",
        "accessory": "accessory"
    }

    for slot, layer in slot_to_layer.items():
        item_id = equipment.get(slot)
        if item_id:
            # Имя файла = id предмета + .png
            sprite = load_sprite(layer, f"{item_id}.png")
            if sprite:
                final = Image.alpha_composite(final, sprite)

    # Накладываем эффекты (баффы, дебаффы)
    for effect in effects:
        effect_sprite = load_sprite("effects", f"{effect}.png")
        if effect_sprite:
            final = Image.alpha_composite(final, effect_sprite)

    # Конвертируем в BytesIO для отправки
    output = BytesIO()
    final.save(output, format="PNG")
    output.seek(0)

    return output


def generate_profile_image(player) -> BytesIO:
    """
    Генерирует изображение профиля игрока

    Args:
        player: Объект Player с данными персонажа

    Returns:
        BytesIO: Изображение для отправки в Telegram
    """
    # Собираем экипировку
    equipment = {}
    if hasattr(player, 'equipment') and player.equipment:
        for slot, item_id in player.equipment.items():
            if item_id:
                equipment[slot] = item_id

    # Собираем активные эффекты
    effects = []
    if hasattr(player, 'active_effects') and player.active_effects:
        for effect_name in player.active_effects.keys():
            effects.append(effect_name)

    return generate_character_image(
        player_class=player.player_class,
        level=player.level,
        equipment=equipment,
        effects=effects
    )
