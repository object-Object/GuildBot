import asyncio
import asyncpg

async def create_pool():
    pool = await asyncpg.create_pool(dsn='postgresql://guildbot:gu1ldb0t@localhost/guildbot')
    async with pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS threads (
                channel_id BIGINT PRIMARY KEY,
                author_id BIGINT NOT NULL
            );
        """)

class Database():
    def __init__(self):
        self.pool = asyncio.get_event_loop().run_until_complete(create_pool())
    
    async def get_thread(self, channel_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT channel_id FROM threads WHERE channel_id = $1;", channel_id)
    
    async def get_author_of_thread(self, channel_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT author_id FROM threads WHERE channel_id = $1;", channel_id)
    
    async def create_thread(self, channel_id, author_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("INSERT INTO threads (channel_id, author_id) VALUES($1, $2)", channel_id, author_id)
