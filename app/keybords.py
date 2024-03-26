from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Получить информацию о товаре")
        ],
        [
            KeyboardButton(text="Остановить уведомления"),
            KeyboardButton(text="Получить информацию из бд")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню")

subscribe = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подписаться",
                callback_data='subscribe'
            ),
            InlineKeyboardButton(
                text="Мой GitHub",
                url='https://github.com/Pu104ver'
            )
        ]

    ])
