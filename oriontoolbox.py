import discord
from discord.ext import commands
import os
from os_info import get_os_info as os_info
from dotenv import load_dotenv
import exceptions
import sys
import asyncio
from datetime import datetime, UTC
import signal
from cogs.moderation import load_action_counts

os.system("cls" if os.name == "nt" else "clear")


intents = discord.Intents.default()
intents.message_content = True

osinfo: dict = os_info()

HOST_MAINTAINER = "Orion Altair" # Modify only this variable if you are hosting a toolbox instant
VERSION_MAINTAINER = "Orion Altair"
TOOLBOX_CREATOR = "Orion Altair"
TOOLBOX_VERSION = "0.1.2"
TOOLBOX_CHANNEL = "RollingRelease"
VERSION_STATUS = "Live/Supported"
VERSION_CODENAME = "Hammer"
HOST_ID = "1-MAIN-SYS.OWN"
# Change nothing below this!!!
TOOLBOX_LANGUAGE = "Python"
HOST_INITIALS = "".join(letter[0] for letter in HOST_MAINTAINER.split(" "))
HOST_CODENAME = f"{HOST_INITIALS}{("-"+osinfo["id"].upper()) if osinfo['type'] == "Linux" else ""}"
SYSTEM_VERSION = sys.version
if osinfo["type"] == "Linux":
  ostype = str(osinfo["type"])
  osname = str(osinfo["name"]).replace(" ", "_")
  osvers = str(osinfo["version"])
  string = f"{ostype}:{osname}-{osvers}"
elif osinfo["type"] == "Windows":
  ostype = str(osinfo["type"])
  osvers = str(osinfo["version"])
  osrels = str(osinfo["release"])
  string = f"{ostype}_{osrels}@{osvers}"
elif osinfo["type"] == "macOS":
  ostype = str(osinfo["type"])
  osvers = str(osinfo["version"])
  string = f"{ostype}@{osvers}"
else:
  string = f"{osinfo["type"]}@{osinfo["version"]}"

VERSION_NAMEDATA = f"{VERSION_CODENAME}@{TOOLBOX_VERSION}::{string}"


DISCORD_IDs = os.getenv('DISCORD_IDs')
TOKEN = os.getenv('DISCORD_TOKEN')

live_intents = {}

for intent in dir(intents):
  intent_value = getattr(intents, intent)
  live_intents.update({intent: intent_value})

start = None

bot = discord.Bot(intents=intents, max_messages=1000, auto_update_commands=False)

load_dotenv()

start_start = datetime.now(UTC)


# system = discord.commands.SlashCommandGroup(name = "system")
# info = discord.commands.SlashCommandGroup(name = "info", parent=system)

# Load the moderation cog
try:
  module_start = datetime.now(UTC)
  raise exceptions.cogFail
  AIFail = False
  bot.load_extension('cogs.moderation-ai')
  ai_time = (datetime.now(UTC) - module_start).total_seconds()
except exceptions.cogFail:
  ai_time = (datetime.now(UTC) - module_start).total_seconds()
  print("AI Moderation failed to load. Skipping...")
  AIFail = True
finally:
  try:
    module_start = datetime.now(UTC)
    ModFail = False
    bot.load_extension('cogs.moderation')
    mod_time = (datetime.now(UTC) - module_start).total_seconds()
  except exceptions.cogFail:
    mod_time = (datetime.now(UTC) - module_start).total_seconds()
    print("Moderation Failed to load. CRITICAL ERROR. Continuing...")
    ModFail = True

try:
  module_start = datetime.now(UTC)
  sillyFail = False
  bot.load_extension('cogs.stupid.silly')
  silly_time = (datetime.now(UTC) - module_start).total_seconds()
except exceptions.cogFail:
  silly_time = (datetime.now(UTC) - module_start).total_seconds()
  print("Silly module had failed to load. Skipping...")
  sillyFail = True

# System Management Commands: Added in version 0.1.1
@bot.slash_command(name = "system", description = "Perform System tasks on the bot")
async def system_command(ctx: discord.ApplicationContext):
  await ctx.respond("""
# System Main:
  - Info Commands:
    - `info`: Generic system info
    - `version`: Version info
    - `host`: Host version info (including python version)

  - Power Commands:    ***(REQUIRES AUTHENTICATION)***
    - `shutdown <node?:string>`: Shutdown bot instance on target host node (use `host` to get the name)
    - `shutdown all`: Shutdown all running bot instances
    - `kill <node?:string>`: Force Shutdown bot instance on target host node [This exits without saving and leaves an error log]
    - `kill all`: Force Shutdown all running bot instances

  - Management Commands:
    - module <name?:string>/<id?:int> <enabled?:boolean>: Turn modules on or off
    - channel:
      - channel <name?:string>/<id?:int> <mode?:Literal["Whitelist", "Blacklist"]> <Enabled?:boolean>: Change server commands mode to whitelist or blacklist (Whitelist as default)
      - channel <name?:string>/<id?:int> <mode?:Literal["Whitelist", "Blacklist"]> <operation?:Literal["Add", "Remove"]>: Add or remove channels from the server's whitelist or blacklist
""")

@bot.slash_command(name = "info", description = "System information")
async def info_command(ctx: discord.ApplicationContext):
  await ctx.respond(f"""
System Info:
  Version: {TOOLBOX_VERSION}
  Creator: {TOOLBOX_CREATOR}
  Channel: {TOOLBOX_CHANNEL}
  Language: {TOOLBOX_LANGUAGE}
""")

@bot.slash_command(name = "version")
async def version_info(ctx: discord.ApplicationContext):
  await ctx.respond(f"""
Version info:
  Version: {TOOLBOX_VERSION}
  Version Name: {VERSION_CODENAME}
  Maintainer: {VERSION_MAINTAINER}
  Name-Data: {VERSION_NAMEDATA}
  Version Status: {VERSION_STATUS}
  Channel: {TOOLBOX_CHANNEL}
  Language: {TOOLBOX_LANGUAGE}
""")

@bot.slash_command(name = "host")
async def host_info(ctx: discord.ApplicationContext):
  await ctx.respond(f"""
Host info:
  Version: {TOOLBOX_VERSION}
  Host Name: {HOST_CODENAME}
  Host ID: {HOST_ID}
  Host Maintainer: {HOST_MAINTAINER}
  Python Version: {SYSTEM_VERSION}
""")

def _exit(signum, _):
  """Handle the exit signal."""
  print(f'Caught signal {signum}. Shutting down...')
  asyncio.create_task(_shutdown())

async def _shutdown():
  """Perform cleanup before shutdown."""
  end = datetime.now(UTC)
  print(f'{bot.user} has disconnected.')
  channels = []
  all_channels = bot.get_all_channels()
  channel = discord.utils.get(all_channels, guild__id=1297520659718475817, id=1297522814638882847)
  channels.append(channel)
  channel = discord.utils.get(all_channels, guild__id=1297520659718475817, id=1298351962722406421)
  channels.append(channel)
  action_count = load_action_counts()
  for channel in channels:
    await channel.send(f"""
End of use log (Finished):
```
Start time: {start.strftime("%B %d, %Y, %H:%M:%S")}
End time: {end.strftime("%B %d, %Y, %H:%M:%S")}
Warns: {action_count["warns"]}
Kicks: {action_count["kicks"]}
Deletes: {action_count["deletes"]}
Purges: {action_count["purges"]}
```
Bot has been online for: {(end - start)}.
""")
  if os.path.exists("action_counts.json"):
    os.remove("action_counts.json")
  await bot.close()

# Register the signal handler for SIGINT
signal.signal(signal.SIGINT, _exit)
signal.signal(signal.SIGTERM, _exit)

@bot.event
async def on_connect() -> None:
  await bot.sync_commands(delete_existing=True)
  print("Synchronized commands.")

@bot.event
async def on_ready():
  global start
  print(f'{bot.user} has connected')
  await bot.change_presence(status=discord.Status.online)
  channels = []
  all_channels = bot.get_all_channels()
  channel = discord.utils.get(all_channels, guild__id=1297520659718475817, id=1297522814638882847)
  await channel.purge(bulk=False)
  channels.append(channel)
  channel = discord.utils.get(all_channels, guild__id=1297520659718475817, id=1298351962722406421)
  channels.append(channel)
  start_end = datetime.now(UTC)
  for channel in channels:
    await channel.send(f"""
Start-up log (Finished):
```
Start time: {start_start.strftime("%B %d, %Y, %H:%M:%S")}
{"AI Moderation Online" if not AIFail else "AI Moderation failed to load..."} (Took {ai_time:.4f} Seconds.)
{"Standard Moderation Online" if not ModFail else "Standard Moderation failed to load..."} (Took {mod_time:.4f} Seconds.)
{"Silly Module Online" if not sillyFail else "Silly Module failed to load..."} (Took {silly_time:.4f} Seconds.)
```
Bot loaded in: {(start_end - start_start).total_seconds()} seconds.
""")
  start = datetime.now(UTC)

bot.run(TOKEN)
