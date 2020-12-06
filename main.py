import discord
from bot import Bot
from utils.help import GuildBotHelp

intents = discord.Intents.default()
intents.members = True

allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)

bot = Bot(command_prefix=config.prefix, help_command=GuildBotHelp(), intents=intents, allowed_mentions=allowed_mentions)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
