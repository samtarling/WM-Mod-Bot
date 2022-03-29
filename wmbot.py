"""Wikimedia Community Server Discord bot"""
import random
import typing
import datetime

import discord
from discord import Guild, Message, Embed, Member
from discord.ext.commands import (Bot, Context, CommandError, CommandNotFound,
                                  UserInputError, MissingAnyRole)

import cogs
import constants
import utils

__version__ = constants.VERSION

bot = Bot(command_prefix='~',
          description=("Wikimedia Community Server Discord bot"),
          intents=discord.Intents.all(),
          case_insensitive=True)


async def checkMessage(message: Message) -> bool:
    """Check a message against the regexes"""
    if await utils.isDM(message):
        # Message is a DM
        await message.channel.send("Not yet implemented, sorry...")
        # TODO: Probably another function to deal with any DM commands
        return True
    else:
        # Message is not a DM nor an embed
        return False


@bot.event
async def on_ready() -> None:
    """Things to do when the bot readies."""
    now_utc = await utils.getUTC()
    print(f"{now_utc}\n" + "-" * 18)
    if constants.DEV:
        print("In development mode...\n" + "-" * 18)
    print(f"Logged in as\n{bot.user.name}\n{bot.user.id}\nv{constants.VERSION} ({constants.VERSION_NAME})\n"
          + "-" * 18)
    bot.admin_channel = bot.get_channel(constants.ADMIN_CHANNEL)
    bot.server_owner = bot.get_user(constants.SERVER_OWNER)
    bot.custom_activity = constants.BOT_ACTIVITY
    bot.guild = bot.get_guild(constants.GUILD)
    await bot.change_presence(
        activity=discord.Game(
            name=f"{bot.custom_activity}"
        )
    )


@bot.event
async def on_message(message: Message) -> None:
    """Run on every message."""
    if message.author.discriminator != "0000":  # Ignore webhooks.
        if message.author.id != constants.BOT_ID:  # Ignore self.
            if await checkMessage(message) is False:
                await bot.process_commands(message)


@bot.event
async def on_command_error(ctx: Context,
                           error: CommandError) -> None:
    """Notify a user that they have not provided an argument."""
    if ctx.message.content.startswith("~~"):
        return
    print(error)
    replies = {
        UserInputError: ("*You need to use the correct syntax...* "
                         f"Type `~help {ctx.command}` for more information."),
        CommandNotFound: ("*You need to use a valid command...* "
                          "Type `~help` for a list of commands."),
        MissingAnyRole: ("You don't appear to have the correct role "
                         "for this command.")
    }
    for k, v in replies.items():
        if isinstance(error, k):
            await ctx.send(v)
            break
    else:
        await ctx.send("Unknown error.")


for cog in (cogs.BotInternal, cogs.Mod, cogs.EditorInfo):
    bot.add_cog(cog(bot))


bot.run(constants.DISCORD_KEY)
