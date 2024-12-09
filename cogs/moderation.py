import json

# Load action counts on startup
def load_action_counts():
    try:
        with open('action_counts.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {"warns": 0, "kicks": 0, "deletes": 0, "purges": 0}

# Save action counts on shutdown
def save_action_counts():
    with open('action_counts.json', 'w') as f:
        json.dump(action_count, f)

import asyncio
import os
import re
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# !! Global Imports
from wordlists import BRAIN_ROT_LIST, SLURS_LIST, trusted_ids, SWEARS, INSULTS
import exceptions

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

action_count = load_action_counts()

TOKEN = os.getenv('DISCORD_TOKEN')

# Configurable warning limit
WARNING_LIMIT = 3

brain_rot_list = set(BRAIN_ROT_LIST)

SPEC_CHARLIST = "~!@#$%^&*()-_=+[]{}\\|;:'\",.<>/?`•¢£€¥©®™§¶°±×÷µ√∞≠≤≥→←↑↓↔↕‘’“”«»‹›¬¿¡°¯˘˙˚˛ˇ‣⁂†‡′″‽§‰ℵ"

async def check_for_substitutions(word, message):
    charlist = "abcdefghijklmnopqrstuvwxyz"
    global SPEC_CHARLIST
    for spec_char in SPEC_CHARLIST:
        if spec_char in word:
            for x in range(len(word)):
                for char in charlist:
                    modified_word = word[:x] + char + word[x+1:]
                    return modified_word

async def clean(word_list: list):
    global SPEC_CHARLIST
    for char in SPEC_CHARLIST:
        x = 0
        for word in word_list:
            word_list[x] = word.replace(char, "")
            x+=1
    return word_list

async def log_brain_rot_action(message, word):
    await message.reply(f"Message would have been deleted, Reason: Brainrot ({word})", mention_author=False)
    # log = await message.channel.send(f'{message.author.nick or message.author.global_name}, no brain rot thank you.')
    # await asyncio.sleep(5)
    # await log.delete()
    # action_count["deletes"] += 1

async def formatting_pass(message, after):
    words = message.content.lower().split()
    global SPEC_CHARLIST
    for word in words:
        formatting = word
        for char in SPEC_CHARLIST:
            # Triple occurrence of the special character
            if re.search(rf"(.*)\{char}{{3}}(\S+)\{char}{{3}}(.*)", word):
                p1 = re.search(rf"(.*)\{char}{{3}}(\S+)\{char}{{3}}(.*)", word).group(1)
                p2 = re.search(rf"(.*)\{char}{{3}}(\S+)\{char}{{3}}(.*)", word).group(2)
                p3 = re.search(rf"(.*)\{char}{{3}}(\S+)\{char}{{3}}(.*)", word).group(3)
                formatting = f"{p1}{p2}{p3}"
                await after(formatting, message)

            # Double occurrence of the special character
            elif re.search(rf"(.*)\{char}{{2}}(\S+)\{char}{{2}}(.*)", formatting):
                p1 = re.search(rf"(.*)\{char}{{2}}(\S+)\{char}{{2}}(.*)", formatting).group(1)
                p2 = re.search(rf"(.*)\{char}{{2}}(\S+)\{char}{{2}}(.*)", formatting).group(2)
                p3 = re.search(rf"(.*)\{char}{{2}}(\S+)\{char}{{2}}(.*)", formatting).group(3)
                formatting = f"{p1}{p2}{p3}"
                await after(formatting, message)

            # Single occurrence of the special character
            elif re.search(rf"(.*)\{char}(\S+)\{char}(.*)", formatting):
                p1 = re.search(rf"(.*)\{char}(\S+)\{char}(.*)", formatting).group(1)
                p2 = re.search(rf"(.*)\{char}(\S+)\{char}(.*)", formatting).group(2)
                p3 = re.search(rf"(.*)\{char}(\S+)\{char}(.*)", formatting).group(3)
                formatting = f"{p1}{p2}{p3}"
                await after(formatting, message)
    await asyncio.sleep(0)

async def check_brainrot(message):
    if message:
        await formatting_pass(message, check_for_substitutions)
        words = await clean(message.content.lower().split())
        found = False
        for word in words:
            if word in brain_rot_list:
                await log_brain_rot_action(message, word)
                found = True
        if not found:
            for word in message.content.lower().split():
                modified_word = await check_for_substitutions(word, message)
                await check_subbed_brainrot(message, modified_word)

async def check_subbed_brainrot(message, modified_word):
    if message:
        if modified_word in brain_rot_list:
            await log_brain_rot_action(message, modified_word)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = self.load_warnings()
        self.restricted_guild_channels = {
            1293936397165658244:1297277584765096007,
        }
        self.restricted_guild_ids = [1293936397165658244]  # Restricted guild ID
        self.allowed_channel_ids = [1297277584765096007]  # Allowed channel ID

    def is_correct_channel(self, ctx):
        """Check if the command is invoked in the correct channel."""
        for gid in self.restricted_guild_ids:
            if ctx.guild.id == gid:
                for cid in self.allowed_channel_ids:
                    return ctx.channel.id == cid
        return True  # Allow commands in all channels for other servers

    def load_warnings(self):
        warnings = {}
        if os.path.exists('warns.txt'):
            with open('warns.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:  # Check if the line is not empty
                        parts = line.split(' ')
                        if len(parts) == 2:  # Ensure there are exactly two parts
                            username, num_warns = parts
                            warnings[username] = int(num_warns)
        return warnings

    async def warn_user(self, user, ctx):
        try:
            if user in self.warnings:
                self.warnings[user] += 1
            else:
                self.warnings[user] = 1

            if self.warnings[user] >= WARNING_LIMIT:
                # Use ctx.guild to get the current guild
                guild = ctx.guild

                # Extract user ID cleanly using regex
                match = re.match(r'<@!?(\d+)>', user)
                if match:
                    user_id = int(match.group(1))
                    member = await guild.fetch_member(user_id)

                    if member:
                        await self.kick_user(member, reason="Exceeded warning limit")
                        await ctx.respond(f"{user}({user_id}) has been kicked")

                    else:
                        await ctx.respond(f'Could not find member {user}({user_id}) to kick.')
                    self.warnings.pop(user)  # Remove user from warnings
                else:
                    await ctx.respond(f'Could not parse user ID from {user}.')

                # Update the warnings file
                with open('warns.txt', 'w') as f:
                    for username, num_warns in self.warnings.items():
                        f.write(f'{username} {num_warns}\n')

            else:
                # Update the warnings file
                with open('warns.txt', 'w') as f:
                    for username, num_warns in self.warnings.items():
                        f.write(f'{username} {num_warns}\n')
                await ctx.respond(f"{user} has been warned.")
                action_count["warns"] += 1
            await ctx.delete()
        except discord.errors.NotFound:
            await ctx.respond(f"Couldn't warn {user}, they aren't here!")
        except Exception as e:
            await ctx.respond(f"Couldn't warn {user}, Reason: {e}")

    async def kick_user(self, member: discord.Member, reason: str = "No reason provided"):
        try:
            await member.kick(reason=reason)
            await member.send(f'You have been kicked from {member.guild.name} for: {reason}')
            action_count["kicks"] += 1
        except discord.Forbidden:
            logging.error(f'Failed to kick. I do not have permission.')
        except discord.HTTPException as e:
            logging.error(f'Failed to kick. HTTP Exception: {e}')

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f'{self.bot.user} has connected')

    # Convert 'toolbox.warn' to slash command
    @commands.slash_command(name="warn", description="Warn a user")
    @commands.has_permissions(kick_members=True)
    async def warn_command(self, ctx, target_user: discord.User):
        try:
            await self.warn_user(target_user.mention, ctx)
        except commands.MissingPermissions:
            await ctx.respond("You do not have permission to warn users.", ephemeral = True)

    @commands.slash_command(name="purge", description="Purge messages from a channel")
    @commands.has_permissions(manage_messages=True)
    async def purge_command(self, ctx, num_messages: int, user: discord.User = None):
        await ctx.defer()  # Ensure this is awaited

        try:
            if 1 <= num_messages < 100:
                await ctx.followup.send(f"Purging {num_messages} messages...")  # Send an initial confirmation message

                def check(msg):
                    return msg.author == user if user else True

                deleted_messages = await ctx.channel.purge(limit=num_messages+1, check=check)
                logging.info(f"Deleted {len(deleted_messages)-1} messages.")
                
                # After purging, send a final message indicating how many were purged
                await ctx.channel.send(f"Purged {len(deleted_messages)-1} messages.")  # Use channel.send instead
                action_count["purges"] += 1
            else:
                await ctx.followup.send("Please specify a number between 1 and 99.")
        except commands.MissingPermissions:
            await ctx.followup.send("You do not have permission to purge messages.", ephemeral=True)
        except Exception as e:
            logging.error(f"Error in purge command: {str(e)}")  # Log the error
            try:
                await ctx.followup.send("An error occurred while trying to purge messages. Please try again later.", ephemeral=True)
            except Exception as followup_error:
                logging.error(f"Follow-up failed: {str(followup_error)}")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        await check_brainrot(message)

        warn = 0

        if message and int(message.author.id) not in trusted_ids:
            # Check for banned slurs
            for word in SLURS_LIST:
                content = await clean(message.content.lower())
                if word in content:
                    await message.reply(f"Message would have been deleted, Reason: Slurs ({word})", mention_author=False)
                    # await message.delete()
                    # log = await message.channel.send(f'{message.author.nick or message.author.global_name}, that is banned.')
                    # await asyncio.sleep(5)
                    # await log.delete()
                    # action_count["deletes"] += 1
                    return
            # Check for swears
            for word in SWEARS:
                content = clean(message.content.lower())
                for test_word in content.split():  # Split message into individual words
                    if test_word == word:
                        warn += 1
                        if warn >= 3:
                            await message.reply(f"Message would have been deleted, Reason: Swears ({word})", mention_author=False)
                            # await message.delete()
                            # log = await message.channel.send(f'{message.author.nick or message.author.global_name}, language!')
                            # await asyncio.sleep(5)
                            # await log.delete()
                            # action_count["deletes"] += 1
                            return
            # Check for insults
            for word in INSULTS:
                for test_word in clean(message.content.lower()).split():  # Split message into individual words
                    if test_word == word:
                        warn += 1
                        if warn >= 5:
                            await message.reply(f"Message would have been deleted, Reason: Insults ({word})", mention_author=False)
                            # await message.delete()
                            # log = await message.channel.send(f'{message.author.nick or message.author.global_name}, be nice.')
                            # await asyncio.sleep(5)
                            # await log.delete()
                            # action_count["deletes"] += 1
                            return

        save_action_counts()

def setup(bot):
    try:
        bot.add_cog(Moderation(bot))
    except Exception:
        logging.critical("CRITICAL ERROR: Moderation Module Failed to load!")
        raise exceptions.cogFail
