"""Keys, URLs, and other constants."""
import os
import typing

import dotenv

dotenv.load_dotenv()

# Set to True to prevent log messages sending to Discord
DEV = False

# Version
VERSION = "1.0.0"
VERSION_NAME = "ArbCom"

# Bot config
DISCORD_KEY = typing.cast(str, os.getenv('DISCORD_BOT'))  # type: ignore
BOT_ID = int(os.getenv('BOT_ID'))  # type: ignore
GUILD = int(os.getenv('GUILD'))  # type: ignore

# Roles
MOD = int(os.getenv('MOD_ROLE'))  # type: ignore

# Channels
ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))  # type: ignore

# Server admin (Ferret)
SERVER_OWNER = int(os.getenv('SERVER_ADMIN'))  # type: ignore

# Misc
BOT_ACTIVITY = typing.cast(str, os.getenv('BOT_ACTIVITY'))  # type: ignore
