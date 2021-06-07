import asyncio
import discord
from discord.ext import commands
import io
from utils import checks


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Quotes a message by link or id.")
    async def quote(self, ctx, message: commands.MessageConverter):
        await ctx.send(
            embed=discord.Embed(
                title="Quoted message",
                description=f"{message.content}\n\n[Jump to message]({message.jump_url})",
                timestamp=message.created_at,
                color=discord.Color(0x007fff)).set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar_url
                    ).set_footer(
                    text=f"Files: {len(message.attachments)}  •  Embeds (not quoted): {len(message.embeds)}"
                    ),
            files=[await attachment.to_file() for attachment in message.attachments]
            )

    @commands.guild_only()
    @checks.trustee_only()
    @commands.command(brief="Purges messages from a channel.")
    async def clear(self, ctx, start_message: commands.MessageConverter, end_message: commands.MessageConverter):
        if not (ctx.channel == start_message.channel == end_message.channel):
            raise commands.BadArgument("start_message and end_message must both be in the current channel.")
        if start_message == end_message:
            raise commands.BadArgument("start_message and end_message must not be the same message.")

        # make sure the messages are in the right order, i.e. message1 is earlier than message2
        if start_message.created_at > end_message.created_at:
            message1, message2 = end_message, start_message
        else:
            message1, message2 = start_message, end_message

        async with ctx.channel.typing():
            num_deleted = len(await ctx.channel.purge(before=message2, after=message1))
            await message1.delete()
            await message2.delete()
            num_deleted += 2

        await ctx.send(
            embed=discord.Embed(
                title="Messages cleared",
                description=f"**{num_deleted}** messages have been deleted from this channel.",
                color=discord.Color(0x007fff)))

    @commands.guild_only()
    @checks.trustee_only()
    @commands.command(brief="Bans all members who joined between the selected members, inclusive.")
    async def massban(self, ctx, member_a: commands.MemberConverter, member_b: commands.MemberConverter, reason):
        if member_a.joined_at is None:
            raise commands.BadArgument("Unable to get join datetime for member_a. Try a different member.")
        if member_b.joined_at is None:
            raise commands.BadArgument("Unable to get join datetime for member_b. Try a different member.")
        if len(reason) > 512:
            raise commands.BadArgument("reason must be a maximum of 512 characters.")

        if member_a.joined_at < member_b.joined_at:
            start_time = member_a.joined_at
            end_time = member_b.joined_at
        else:
            start_time = member_b.joined_at
            end_time = member_a.joined_at

        members = []
        for member in ctx.guild.members:
            if member.joined_at is not None and start_time <= member.joined_at <= end_time:
                members.append(member)
        member_string = "\n".join(f"{member.name}#{member.discriminator} ({member.id})" for member in members)

        message = await ctx.send(
            content=f"<@&{(await ctx.bot.database.get_settings(ctx.guild.id))['trustee_role']}>",
            file=discord.File(io.StringIO(member_string), "banlist.txt"),
            embed=discord.Embed(
                title="Mass ban confirmation",
                description="Another trustee must confirm these values to start the mass ban.",
                color=discord.Color(0x007fff))
            .set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar_url)
            .set_footer(
                text="This message will time out in 15 minutes.")
            .add_field(
                name="Start time",
                value=str(start_time))
            .add_field(
                name="End time",
                value=str(end_time))
            .add_field(
                name="Ban count",
                value=str(len(members)))
            .add_field(
                name="Reason",
                value=reason))
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        trustee_role = ctx.guild.get_role((await ctx.bot.database.get_settings(ctx.guild.id))["trustee_role"])

        def check(reaction, user):
            return (reaction.message == message and (trustee_role in user.roles or user == ctx.guild.owner)
                    and not user.bot and (reaction.emoji == "✅" and user != ctx.author or reaction.emoji == "❌"))

        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=15 * 60, check=check)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            await message.edit(
                content=message.content,
                embed=message.embeds[0].set_footer())
            await ctx.send(embed=discord.Embed(
                title="Timed out!",
                description="The mass ban confirmation has timed out after 15 minutes of inactivity.",
                color=discord.Color(0xff0000)))
        else:
            await message.clear_reactions()
            if reaction.emoji == "✅":
                await message.edit(
                    content=message.content,
                    embed=message.embeds[0].set_footer(text="Banning in progress..."))

                for member in members:
                    await member.ban(reason=reason)

                await message.edit(
                    content=message.content,
                    embed=message.embeds[0].set_footer())
                await ctx.send(embed=discord.Embed(
                    title="Mass ban completed",
                    description=f"{len(members)} users have been banned. The confirmation was approved by {user.mention}.",
                    color=discord.Color(0x007fff)))
            else:
                await message.edit(
                    content=message.content,
                    embed=message.embeds[0].set_footer())
                await ctx.send(embed=discord.Embed(
                    title="Cancelled!",
                    description=f"The mass ban has been cancelled by {user.mention}.",
                    color=discord.Color(0xff0000)))

    @commands.guild_only()
    @checks.trustee_only()
    @commands.command(brief="Ban (multiple) user by its id, they do not need to be part of the guild.")
    async def hackban(self, ctx, *, users):
        individual_ids = users.split()
        for id_ in individual_ids:
            try:
                user_id = int(id_)
            except ValueError:
                return await ctx.send("Argument `users` must be space separated ids.")

            await ctx.guild.chunk()
            member = ctx.guild.get_member(user_id)
            if member and member.top_role >= ctx.author.top_role:
                return await ctx.send("You cannot ban someone who is higher or equal to you in role hierarchy.")

            await ctx.guild.ban(discord.Object(id=user_id))

        await ctx.send(embed=discord.Embed(
            title="Hack ban complete",
            description=f"Banned {len(individual_ids)} users from the guild.",
            color=discord.Color(0x007fff)
        ))


def setup(bot):
    bot.add_cog(Utilities(bot))


def teardown(bot):
    bot.remove_cog("Utilities")
