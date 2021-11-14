"""Helper functions for the commands.

Functions/classes here should return text to be sent, rather than
sending directly, unless they handle Discord exceptions.
"""
import io
from typing import Optional, Set, Tuple, Union
import time
import datetime

from discord import File, HTTPException, Message, Embed
from discord.ext.commands import Context


async def isDM(message: Message) -> bool:
    """Helper function to see if this message was a DM"""
    return not message.guild


async def isEmbed(message: Message) -> bool:
    """Helper function to see if this message was an Embed"""
    return bool(message.embeds)


async def getUTC() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
