"""
Тени Подземелий - Telegram RPG Bot
Главный файл запуска
"""

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from config import BOT_TOKEN
from utils.storage import load_data, save_data

# Импорт обработчиков
from handlers.menu import (
    start, main_menu, show_class_selection, select_class,
    show_profile, show_stats, show_skills, set_player_name, WAITING_NAME
)
from handlers.combat import (
    fight_attack, fight_block, fight_skill, fight_potion, fight_flee
)
from handlers.dungeon import (
    show_dungeons, select_dungeon, enter_dungeon, next_floor, fight_boss
)
from handlers.tavern import (
    show_tavern, show_food_menu, buy_food,
    show_mercenaries, hire_mercenary,
    show_blacksmith, show_smith_upgrades, show_craft_menu,
    show_craft_category, craft_rare_item, blacksmith_upgrade,
    show_legendary_craft, craft_legendary,
    show_alchemist, craft_potion,
    show_quests, claim_quest_reward,
    show_socket_menu, show_socket_choice, insert_socket, remove_socket
)
from handlers.inventory import (
    show_inventory, show_equipment, show_slot_items, equip_item, unequip_item,
    show_shop, show_shop_category, buy_item, sell_item,
    show_potion_slots, show_potion_choice, select_potion_for_slot
)
from handlers.misc import (
    show_achievements, show_daily, claim_daily,
    rest, show_titles, select_title
)


def main():
    """Запуск бота"""
    print("🏰 Запуск бота 'Тени Подземелий'...")

    # Загрузить данные
    load_data()

    # Создать приложение
    app = Application.builder().token(BOT_TOKEN).build()

    # === ConversationHandler для регистрации ===
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_player_name)]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )
    app.add_handler(registration_handler)

    # === Callback handlers ===

    # Меню
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(show_class_selection, pattern="^select_class$"))
    app.add_handler(CallbackQueryHandler(select_class, pattern="^select_class_"))
    app.add_handler(CallbackQueryHandler(show_profile, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(show_stats, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(show_skills, pattern="^skills$"))

    # Подземелья
    app.add_handler(CallbackQueryHandler(show_dungeons, pattern="^dungeons$"))
    app.add_handler(CallbackQueryHandler(select_dungeon, pattern="^dungeon_"))
    app.add_handler(CallbackQueryHandler(enter_dungeon, pattern="^enter_"))
    app.add_handler(CallbackQueryHandler(next_floor, pattern="^next_floor$"))
    app.add_handler(CallbackQueryHandler(fight_boss, pattern="^fight_boss$"))

    # Бой
    app.add_handler(CallbackQueryHandler(fight_attack, pattern="^fight_attack$"))
    app.add_handler(CallbackQueryHandler(fight_block, pattern="^fight_block$"))
    app.add_handler(CallbackQueryHandler(fight_skill, pattern="^fight_skill_"))
    app.add_handler(CallbackQueryHandler(fight_potion, pattern="^fight_potion_"))
    app.add_handler(CallbackQueryHandler(fight_flee, pattern="^fight_flee$"))

    # Таверна
    app.add_handler(CallbackQueryHandler(show_tavern, pattern="^tavern$"))
    app.add_handler(CallbackQueryHandler(show_food_menu, pattern="^tavern_food$"))
    app.add_handler(CallbackQueryHandler(buy_food, pattern="^buy_food_"))
    app.add_handler(CallbackQueryHandler(show_mercenaries, pattern="^tavern_mercs$"))
    app.add_handler(CallbackQueryHandler(hire_mercenary, pattern="^hire_merc_"))

    # Кузнец
    app.add_handler(CallbackQueryHandler(show_blacksmith, pattern="^tavern_smith$"))
    app.add_handler(CallbackQueryHandler(show_smith_upgrades, pattern="^smith_upgrades$"))
    app.add_handler(CallbackQueryHandler(show_craft_menu, pattern="^smith_craft$"))
    app.add_handler(CallbackQueryHandler(show_legendary_craft, pattern="^smith_legendary$"))
    app.add_handler(CallbackQueryHandler(show_craft_category, pattern="^craft_cat_"))
    app.add_handler(CallbackQueryHandler(craft_rare_item, pattern="^craft_item_"))
    app.add_handler(CallbackQueryHandler(craft_legendary, pattern="^craft_legend_"))
    # Сокеты (до общего smith_ паттерна!)
    app.add_handler(CallbackQueryHandler(show_socket_menu, pattern="^smith_sockets$"))
    app.add_handler(CallbackQueryHandler(show_socket_choice, pattern="^socket_slot_"))
    app.add_handler(CallbackQueryHandler(insert_socket, pattern="^insert_socket_"))
    app.add_handler(CallbackQueryHandler(remove_socket, pattern="^remove_socket_"))
    # Общий обработчик улучшений (должен быть последним из smith_)
    app.add_handler(CallbackQueryHandler(blacksmith_upgrade, pattern="^smith_"))

    # Алхимик
    app.add_handler(CallbackQueryHandler(show_alchemist, pattern="^tavern_alchemy$"))
    app.add_handler(CallbackQueryHandler(craft_potion, pattern="^craft_potion_"))

    # Квесты
    app.add_handler(CallbackQueryHandler(show_quests, pattern="^quests$"))
    app.add_handler(CallbackQueryHandler(claim_quest_reward, pattern="^claim_quest_"))

    # Инвентарь
    app.add_handler(CallbackQueryHandler(show_inventory, pattern="^inventory$"))
    app.add_handler(CallbackQueryHandler(show_equipment, pattern="^equipment$"))
    app.add_handler(CallbackQueryHandler(show_slot_items, pattern="^slot_"))
    app.add_handler(CallbackQueryHandler(equip_item, pattern="^equip_"))
    app.add_handler(CallbackQueryHandler(unequip_item, pattern="^unequip_"))

    # Слоты зелий
    app.add_handler(CallbackQueryHandler(show_potion_slots, pattern="^potion_slots$"))
    app.add_handler(CallbackQueryHandler(show_potion_choice, pattern="^set_potion_"))
    app.add_handler(CallbackQueryHandler(select_potion_for_slot, pattern="^select_potion_"))

    # Магазин
    app.add_handler(CallbackQueryHandler(show_shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(show_shop_category, pattern="^shop_"))
    app.add_handler(CallbackQueryHandler(buy_item, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(sell_item, pattern="^sell_"))

    # Прочее
    app.add_handler(CallbackQueryHandler(show_achievements, pattern="^achievements$"))
    app.add_handler(CallbackQueryHandler(show_daily, pattern="^daily$"))
    app.add_handler(CallbackQueryHandler(claim_daily, pattern="^claim_daily$"))
    app.add_handler(CallbackQueryHandler(rest, pattern="^rest$"))
    app.add_handler(CallbackQueryHandler(show_titles, pattern="^titles$"))
    app.add_handler(CallbackQueryHandler(select_title, pattern="^select_title_"))

    print("✅ Бот запущен! Нажми Ctrl+C для остановки.")

    # Запустить
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
