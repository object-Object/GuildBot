import discord
from discord.ext import commands


class GuildBotHelp(commands.HelpCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Help",
            description="Listing all top-level commands and groups. Specify a command to see more information.",
            color=discord.Color(0x007fff))

        for cog in mapping.keys():
            if mapping[cog]:
                embed.add_field(
                    name=cog.qualified_name if cog else "Uncategorized",
                    value=f"`{'`, `'.join([command.name for command in mapping[cog]])}`")

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=cog.qualified_name,
            description=cog.description,
            color=discord.Color(0x007fff))

        for command in cog.get_commands():
            embed.add_field(name=command.name, value=command.brief)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=group.name,
            description="`{0}`{1}{2}".format(
                self.get_command_signature(group),
                " - " + group.brief if group.brief is not None else "",
                "\n\n" + group.help if group.help is not None else "",
                ),
            color=discord.Color(0x007fff))

        for command in group.commands:
            embed.add_field(name=command.name, value=command.brief)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        await self.get_destination().send(embed=discord.Embed(
            title=command.name,
            description="`{}`{}{}".format(
                self.get_command_signature(command),
                " - " + command.brief if command.brief is not None else "",
                "\n\n" + command.help if command.help is not None else ""),
            color=discord.Color(0x007fff)))

    async def send_error_message(self, error):
        await self.get_destination().send(embed=discord.Embed(
            title="Command failed!",
            description=error,
            color=discord.Color(0xff0000)))
