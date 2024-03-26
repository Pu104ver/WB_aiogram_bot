from datetime import datetime
from aiogram.client.session import aiohttp
from sqlalchemy import select
from app.database.database import engine, async_session
from app.database.models import Base, Users, RequestHistory


class DBRequest:
    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def add_new_user(username: str, tg_id: int, chat_id: int) -> None:
        async with async_session() as session:
            if await DBRequest.get_user(tg_id=tg_id):
                return

            new_user = Users(username=username, tg_id=tg_id, chat_id=chat_id)
            session.add(new_user)
            await session.commit()

    @staticmethod
    async def add_request_history(user_id: int, article_number: str, request_time: datetime = None):
        if request_time is None:
            request_time = datetime.now()

        async with async_session() as session:
            new_request = RequestHistory(user_id=user_id, request_time=request_time, article_number=article_number)
            session.add(new_request)
            await session.commit()

    @staticmethod
    async def get_user(tg_id: int) -> Users | None:
        async with async_session() as session:
            user_query = select(Users).where(Users.tg_id == tg_id)
            result = await session.execute(user_query)
            user = result.fetchone()
            if user is not None:
                return user[0]

            return None

    @staticmethod
    async def update_user_subscription(tg_id, is_subscribed):
        async with async_session() as session:
            user: Users = await DBRequest.get_user(tg_id)
            user.is_subscribed = is_subscribed
            session.add(user)
            await session.commit()

    @staticmethod
    async def get_user_id_from_db(session, user_tg_id: int) -> int | None:
        query = select(Users.id).where(Users.tg_id == user_tg_id)
        result = await session.execute(query)
        user_id = result.fetchone()

        if user_id is not None:
            return user_id[0]

        return None

    @staticmethod
    async def get_user_last_requested_article(user_id: int) -> str | None:
        async with async_session() as session:
            query = (
                select(RequestHistory.article_number)
                .where(RequestHistory.user_id == user_id)
                .order_by(RequestHistory.request_time.desc())
                .limit(1)
            )
            result = await session.execute(query)
            row = result.fetchone()

            if row:
                last_requested_article = row[0]
                return last_requested_article
            else:
                return None

    @staticmethod
    async def get_product_info(article: str) -> dict:
        product_data = {}
        try:
            async with (aiohttp.ClientSession() as session):
                async with session.get(
                        f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={article}'
                ) as response:
                    response_data = await response.json()
                    if not response_data['data']['products']:
                        return {}
                    product_data['name'] = response_data['data']['products'][0]['name']
                    product_data['article'] = response_data['data']['products'][0]['id']
                    product_data['cost'] = response_data['data']['products'][0]['salePriceU'] / 100
                    product_data['rating'] = response_data['data']['products'][0]['reviewRating']
                    product_data['quantity'] = sum(
                        stock['qty'] for stock in response_data['data']['products'][0]['sizes'][0]['stocks'])
        except Exception as e:
            print(f"Error fetching product info: {e}")
        return product_data

    @staticmethod
    async def get_subscribed_users():
        async with async_session() as session:
            query = select(Users).where(Users.is_subscribed)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_last_entries_from_request_history(user_id: int, limit: int = 1) -> list[RequestHistory]:
        async with async_session() as session:
            stmt = (
                select(RequestHistory)
                .where(RequestHistory.user_id == user_id)
                .order_by(RequestHistory.request_time.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            entries = result.scalars().all()
            return entries
