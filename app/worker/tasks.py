from datetime import timedelta
from app.worker.celery import app
from app.database.db_requests import DBRequest
from config import bot


@app.task
async def send_notifications():  # FIXME: задачу видит, выполняет, запускается, но почему-то внутри функции ничего не срабатывает
    print('Сработала задача\n\n\n')
    subscribed_users = await DBRequest.get_subscribed_users()
    for user in subscribed_users:
        message: str = ''
        chat_id = user.chat_id
        article = await DBRequest.get_user_last_requested_article(user_id=user.id)

        if not article:
            await bot.send_message(chat_id, 'Кажется, ваша история поиска пуста')
            continue

        product_info = await DBRequest.get_product_info(article)
        if product_info:
            message = f"Название товара: {product_info['name']}\n" \
                      f"Артикул товара: {product_info['article']}\n" \
                      f"Цена товара: {product_info['cost']:.2f}\n" \
                      f"Рейтинг товара: {product_info['rating']}\n" \
                      f"Количество товара: {product_info['quantity']}\n"
        else:
            message = f"Товар с артикулом {article} не найден"
        await bot.send_message(chat_id, message)


app.conf.beat_schedule = {
    'send-product-info': {
        'task': 'app.worker.tasks.send_notifications',
        'schedule': timedelta(seconds=10),
    },
}
