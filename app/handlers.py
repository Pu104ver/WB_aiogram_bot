import time

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from app.database.database import async_session
from app.database.db_requests import DBRequest
from app.database.models import Users, RequestHistory
from config import bot
import app.keybords as kb

router = Router()


class ArticleNumber(StatesGroup):
    article = State()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    async with async_session() as session:
        await DBRequest.add_new_user(username=message.from_user.username, tg_id=message.from_user.id,
                                     chat_id=message.chat.id)
        await DBRequest.create_tables()

        await message.answer(f"Здравствуйте, {message.from_user.full_name}!\n"
                             f"Подписаться на уведомления вы можете по кнопке ниже👇",
                             reply_markup=kb.subscribe)


@router.message(Command('help'))
async def command_help_handler(message: Message) -> None:
    subscribed_users = await DBRequest.get_subscribed_users()

    await DBRequest.add_new_user(username=message.from_user.username, tg_id=message.from_user.id,
                                 chat_id=message.chat.id)
    await message.answer(f"Будем знакомы, {message.from_user.full_name}!\n"
                         f"Данный бот представляет собой помощника с быстрым получением информации о "
                         f"товаре по его артикулу с торговой площадки Wildberries.\n"
                         f"Также, бот обладает функционалом рассылок уведомлений.",
                         reply_markup=kb.main)
    for user in subscribed_users:
        await message.answer(f'{user.id=}')


@router.message(F.text == "Получить информацию о товаре")
async def get_product_information_state_one(message: Message, state: FSMContext) -> None:
    await state.set_state(ArticleNumber.article)
    await message.answer('Введите артикул товара')


@router.message(ArticleNumber.article)
async def get_product_information_state_two(message: Message, state: FSMContext) -> None:
    try:
        if not message.text.isdigit():
            raise ValueError('Некорректный артикул')

        await state.update_data(article=message.text)
        data = await state.get_data()
        article = data['article']
        await state.clear()

        product_data: dict = await DBRequest.get_product_info(article)
        if product_data:
            await message.answer(f'Название товара: {product_data['name']}\n'
                                 f'Артикул товара: {product_data['article']}\n'
                                 f'Цена товара: {product_data['cost']:.2f}\n'
                                 f'Рейтинг товара: {product_data['rating']}\n'
                                 f'Количество товара: {product_data['quantity']}\n', reply_markup=kb.subscribe)
        else:
            raise ValueError('Ошибка при получении данных. Возможно, введен некорректный артикул товара🤔')
        async with async_session() as session:
            user_id = await DBRequest.get_user_id_from_db(session=session, user_tg_id=message.from_user.id)
            if user_id:
                await DBRequest.add_request_history(user_id=user_id, article_number=article)
            else:
                raise ValueError('Ошибка при обновлении бд. Кажется, мы еще не успели познакомиться.\n'
                                 'Воспользуйтесь командой /start')

    except ValueError as e:
        await state.clear()
        await message.answer(f'{e}')


@router.callback_query(F.data == 'subscribe')
async def subscribe_user(query: CallbackQuery):
    try:
        user_id = query.from_user.id
        chat_id = query.message.chat.id
        user: Users = await DBRequest.get_user(user_id)

        if not user:
            await bot.send_message(chat_id, "Кажется, мы еще не успели познакомиться.\n"
                                            "Воспользуйтесь командой /start")
        else:
            await DBRequest.update_user_subscription(user_id, is_subscribed=True)
            await bot.send_message(chat_id, "Вы успешно подписались на уведомления!")
    except Exception as e:
        await query.message.answer(f'{e}')


@router.message(F.text == "Остановить уведомления")
async def unsubscribe_user(message: Message):
    user_id = message.from_user.id

    user: Users = await DBRequest.get_user(user_id)

    if user:
        await DBRequest.update_user_subscription(user_id, is_subscribed=False)
        await bot.send_message(message.chat.id, "Вы успешно отписались от уведомлений!")
    else:
        await bot.send_message(message.chat.id, "Кажется, мы еще не успели познакомиться.\n"
                                                "Воспользуйтесь командой /start")


@router.message(F.text == "Получить информацию из бд")
async def get_entry_from_db(message: types.Message) -> None:
    user_id = message.from_user.id
    user: Users = await DBRequest.get_user(user_id)

    if not user:
        return await bot.send_message(message.chat.id, "Кажется мы еще не успели познакомиться.\n"
                                                       "Воспользуйтесь командой /start")

    entries: list[RequestHistory] = await DBRequest.get_last_entries_from_request_history(user.id, limit=5)

    if not entries:
        await message.answer("Ваша история поиска пуста")
    else:
        response_message = "Последние 5 записей из вашей истории поиска:\n\n"
        for index, entry in enumerate(entries, start=1):
            response_message += f"Запись {index}:\n"
            response_message += f"Отправлен: {entry.request_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            response_message += f"Артикул товара: `{entry.article_number}`\n\n"
        await bot.send_message(message.chat.id, response_message, parse_mode="MARKDOWN")


@router.message()
async def unknown_message(message: Message) -> None:
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgIAAxkBAAJLpGYDDtYawdlo4YG906DEZfxi0SpRAALLHgACznXoSYcdHS7Sv5ErNAQ')


@router.message(F.text == "❤️")
async def love_forever(message: Message) -> None:
    chat_id = message.chat.id
    time.sleep(2)

    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJLs2YDESKA4nFAH0XFC6X1Xq9d2LLLAAJMGgAC06JQSCg_2bTHGe2rNAQ')
    time.sleep(2)

    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJLsGYDEK7H0Ryoager_p3UOtC9IOVKAAKePwACVJXRSlUXKnfxWfroNAQ')
    time.sleep(2)

    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJLp2YDD5HGZrL2gNWcTNQ8rUtMr1e0AAL_QgACREPQSoVASDeKw3UENAQ')
    time.sleep(0.5)

    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJGFGXsrpz-VynHXUJebcuLGgFVREcSAALFRQACH2zZSvOiWj0k8AGTNAQ')
    time.sleep(3)

    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJLqmYDD5c7eE86c2QBid0wliOcik1fAAIrPAACo-LRSup6uIGmro4BNAQ')
    time.sleep(1)

    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJLrWYDEKdhIRdS93I_yBGHPNez2GrmAAJuQgACFd7QSrCVYcHKNDhZNAQ')
    time.sleep(1)

    await bot.send_message(chat_id=chat_id, text='Just kidding😉\nLove 4 ever❤')
    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAJLtmYDEmRIP0rGxuHVBYN5_02eeSjFAAIBSAACFiTYSk2MX883v9C5NAQ')
