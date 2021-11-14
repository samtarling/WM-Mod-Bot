"""Cogs (categories of bot command)"""
import datetime
import discord
from discord import Member, Embed, Role
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context

import constants


class Mod(Cog, name="Moderation"):  # type: ignore
    """Mod-only commands"""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.has_any_role(constants.MOD)
    async def role(self, ctx: Context, action: str, role: Role, member: Member) -> None:
        "Changes roles for a user. Usage ~role [give|take] [role] [member]"
        if action == "give":
            await member.add_roles(role)
            await ctx.send(f"Giving {role.name} role to {member.mention}")
        elif action == "take":
            await member.remove_roles(role)
            await ctx.send(f"Removing {role.name} role from {member.mention}")
        else:
            await ctx.send(f"Invalid role action {action}")


class BotInternal(Cog, name="Bot Internal", command_attrs={'hidden': True}):  # type: ignore
    """Commands that relate to the bot itself."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    async def version(self, ctx: Context) -> None:
        "Gets the bots current version number"
        embed = Embed(
            title=f"TheresNoBot v{constants.VERSION}",
            description=f"I'm currently running version {constants.VERSION}",
            type="rich",
            url="https://github.com/TheresNoGit/TheresNoDiscordBot",
            color=constants.DEBUG_COL,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"Codename: {constants.VERSION_NAME}")
        await ctx.reply(embed=embed)
