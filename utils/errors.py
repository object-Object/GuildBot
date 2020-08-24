from discord.ext import commands

class ThreadOnly(commands.CheckFailure):
    pass

class NotThreadAuthor(commands.CheckFailure):
    pass

class GuildMissingCategory(commands.CheckFailure):
    pass

class NotTrustee(commands.CheckFailure):
    pass