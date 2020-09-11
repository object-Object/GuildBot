import asyncio

import asyncpg

import config


async def create_pool():
    pool = await asyncpg.create_pool(
        user=config.db_user, password=config.db_pass,
        host=config.db_host, database=config.db_name,
        )
    async with pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS threads (
                channel_id BIGINT PRIMARY KEY,
                author_id BIGINT NOT NULL,
                category_id BIGINT NOT NULL
            );
        """)
        await conn.execute("""CREATE TABLE IF NOT EXISTS settings (
                guild_id BIGINT PRIMARY KEY,
                welcome_channel BIGINT,
                autorole BIGINT,
                thread_category BIGINT NOT NULL,
                archive_category BIGINT NOT NULL
            );
        """)
    return pool


class Database():
    def __init__(self):
        self.pool = asyncio.get_event_loop().run_until_complete(create_pool())

    async def get_thread(self, channel_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT channel_id FROM threads WHERE channel_id = $1;", channel_id)

    async def get_author_of_thread(self, channel_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT author_id FROM threads WHERE channel_id = $1;", channel_id)

    async def get_category_of_thread(self, channel_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT category_id FROM threads WHERE channel_id = $1;", channel_id)

    async def create_thread(self, channel_id, author_id, category_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO threads (channel_id, author_id, category_id) VALUES($1, $2, $3)",
                channel_id, author_id, category_id,
                )

    async def get_settings(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM settings WHERE guild_id=$1;", guild_id)

    async def set_setting(self, guild_id, setting, value):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(f"UPDATE settings SET {setting}=$1; WHERE guild_id=$2;", value, guild_id)
    
    async def insert_settings(self, guild_id, welcome_channel, autorole, thread_category, archive_category):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO settings (guild_id, welcome_channel, autorole, thread_category, archive_category) VALUES($1, $2, $3, $4, $5)",
                guild_id, welcome_channel, autorole, thread_category, archive_category)
