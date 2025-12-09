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


def load_sprite(layer: str, filename: str, scale: float = 2.0, center: bool = True) -> Optional[Image.Image]:
    """Загрузить спрайт с прозрачностью, масштабировать и центрировать"""
    path = get_asset_path(layer, filename)
    if os.path.exists(path):
        try:
            img = Image.open(path).convert("RGBA")

            # Масштабируем спрайт (например 128x128 -> 256x256)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.NEAREST)  # NEAREST для пиксель-арта

            if center:
                # Создаём холст нужного размера и центрируем спрайт
                canvas = Image.new("RGBA", AVATAR_SIZE, (0, 0, 0, 0))
                x = (AVATAR_SIZE[0] - img.width) // 2
                y = (AVATAR_SIZE[1] - img.height) // 2
                canvas.paste(img, (x, y), img)
                return canvas
            else:
                return img
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


def create_gradient_background(size: tuple, color1: tuple, color2: tuple) -> Image.Image:
    """Создать градиентный фон"""
    img = Image.new("RGBA", size, color1)
    draw = ImageDraw.Draw(img)

    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))

    return img


# Цвета фона для классов
CLASS_BACKGROUNDS = {
    "warrior": ((60, 30, 30), (30, 15, 15)),      # Тёмно-красный
    "mage": ((30, 30, 60), (15, 15, 40)),          # Тёмно-синий
    "archer": ((30, 50, 30), (15, 30, 15)),        # Тёмно-зелёный
    "paladin": ((50, 50, 30), (30, 30, 15))        # Тёмно-жёлтый
}


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

    # Создаём градиентный фон
    bg_colors = CLASS_BACKGROUNDS.get(player_class, ((40, 40, 50), (20, 20, 30)))
    final = create_gradient_background(AVATAR_SIZE, bg_colors[0], bg_colors[1])

    # Пытаемся загрузить базовый спрайт класса
    base_sprite_name = CLASS_SPRITES.get(player_class, "warrior.png")
    base = load_sprite("base", base_sprite_name)

    if base is None:
        # Нет спрайтов - используем заглушку
        base = create_placeholder_avatar(player_class, level)

    # Накладываем персонажа на фон
    final = Image.alpha_composite(final, base)

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
