from discord.ext import commands


class ThreadOnly(commands.CheckFailure):
    def __init__(self, *args):
        super().__init__("Command may only be used in channels created using the thread command.", *args)


class NotThreadAuthor(commands.CheckFailure):
    def __init__(self, *args):
        super().__init__("Command may only be used by the author of the thread or a Trustee", *args)


class GuildMissingCategory(commands.CheckFailure):
    pass


class NotTrustee(commands.CheckFailure):
    pass


class CommandFailed(commands.CommandError):
    pass
