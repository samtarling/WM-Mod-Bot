"""Cogs (categories of bot command)"""
import datetime
import utils
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
    async def role(self,
                   ctx: Context,
                   action: str,
                   role: Role,
                   member: Member) -> None:
        "Changes roles for a user. Usage ~role [give|take] [role] [member]"
        if action == "give":
            await member.add_roles(role)
            await ctx.send(f"Giving {role.name} role to {member.mention}")
        elif action == "take":
            await member.remove_roles(role)
            await ctx.send(f"Removing {role.name} role from {member.mention}")
        else:
            await ctx.send(f"Invalid role action {action}")


class EditorInfo(Cog, name='Editor Information'):  # type: ignore
    """Information about one or more editors from an outside tool."""

    _xtools_facets = utils.AliasDict(
        {'full': 'ec',
         ('general', 'generalstats'): 'ec-generalstats',
         ('totals', 'namespacetotals'): 'ec-namespacetotals',
         ('years', 'yearcounts'): 'ec-yearcounts',
         ('months', 'monthcounts'): 'ec-monthcounts',
         ('timecard', 'tc'): 'ec-timecard',
         ('edits', 'topedits'): 'topedits',
         ('rights', 'rightschanges'): 'ec-rightschanges'}
    )

    @commands.command()
    async def xtools(self, ctx: Context, facet: str, *, username: str) -> None:
        """Get XTools info.  Usage info: ~help xtools

        Usage: ~xtools <facet> <username>

        Options for facet are:
          full                     -- the main XTools page
          general / generalstats   -- general stats
          totals / namespacetotals -- namespace totals
          years / yearcounts       -- year counts
          months / monthcounts     -- month counts
          timecard / tc            -- time card
          edits / topedits         -- most-edited pages
          rights / rightschanges   -- rights changes

        ~tc and ~timecard can be used as aliases for ~xtools tc/timecard.
        """
        await ctx.send(utils.get_page(
            base_url=constants.XTOOLS_URL,
            basepage=self._xtools_facets[facet] + "/en.wikipedia.org/",
            subpage=username)
        )

    @commands.command(aliases=['ca'])
    async def centralauth(self, ctx: Context, username: str) -> None:
        """Get CentralAuth link.

        Usage: ~ca <username>
        """
        await ctx.send(utils.get_page(
            base_url=constants.CA_URL,
            subpage=username)
        )


class BotInternal(Cog, name="Bot Internal", command_attrs={'hidden': True}):
    """Commands that relate to the bot itself."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    async def version(self, ctx: Context) -> None:
        "Gets the bots current version number"
        embed = Embed(
            title=f"WM Mod Bot v{constants.VERSION}",
            description=f"I'm currently running version {constants.VERSION}",
            type="rich",
            url="https://github.com/theresnotime/WM-Mod-Bot",
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"Codename: {constants.VERSION_NAME}")
        await ctx.reply(embed=embed)
