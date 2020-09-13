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
                trustee_role BIGINT NOT NULL
            );
        """)
        await conn.execute("""CREATE TABLE IF NOT EXISTS thread_categories (
                category_id BIGINT PRIMARY KEY,
                guild_id BIGINT
            );
        """)
        await conn.execute("""CREATE TABLE IF NOT EXISTS archive_categories (
                category_id BIGINT PRIMARY KEY,
                guild_id BIGINT
            );
        """)
        await conn.execute("""CREATE TABLE IF NOT EXISTS autoroles (
                role_id BIGINT PRIMARY KEY,
                guild_id BIGINT
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
            return await conn.fetchval("UPDATE settings SET $1=$2; WHERE guild_id=$2;", setting, value, guild_id)

    async def insert_settings(self, guild_id, welcome_channel, autorole, thread_category, archive_category):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO settings (guild_id, welcome_channel, autorole, thread_category, archive_category) VALUES($1, $2, $3, $4, $5);",
                guild_id, welcome_channel, autorole, thread_category, archive_category)

    async def get_thread_categories(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM thread_categories WHERE guild_id=$1;", guild_id)

    async def insert_thread_category(self, guild_id, category_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO thread_categories (category_id, guild_id) VALUES($1, $2);", category_id, guild_id,
                )

    async def remove_thread_category(self, category_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("DELETE FROM thread_categories WHERE category_id=$1;", category_id)

    async def get_archive_category(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM archive_categories WHERE guild_id=$1;", guild_id)

    async def insert_archive_category(self, guild_id, category_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO archive_categories (category_id, guild_id) VALUES($1, $2);", category_id, guild_id,
                )

    async def remove_archive_category(self, category_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("DELETE FROM archive_categories WHERE category_id=$1;", category_id)

    async def get_autoroles(self, guild_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM autoroles WHERE guild_id=$1;", guild_id)

    async def insert_autorole(self, guild_id, role_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO autoroles (role_id, guild_id) VALUES($1, $2);", role_id, guild_id,
                )

    async def remove_autorole(self, role_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("DELETE FROM autoroles WHERE category_id=$1;", role_id)
