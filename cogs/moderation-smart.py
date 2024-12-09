import asyncio
import os
import re
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

# Configurable warning limit
WARNING_LIMIT = 3

brainrot_words = ['sigma', 'skibidi', 'ohio', 'fanum', 'rizz', 'rizzler', 'rizzlam', 'mog', 'mogging', 'mew', 'mewing', 'gyatt', 'maxxing']
slurs_list = [
    "fag", "faggot",
    "dyke",
    "bitch",
    "cunt",
    "nigger",
    "chink",
    "gook",
    "spic",
    "wetback",
    "sandnigger",
    "kike",
    "raghead",
    "yid",
    "tranny",
    "queer",
    "slut",
    "whore",
    "retard",
    "cripple",
    "paki",
    "nappy",
    "shemale",
    "hermaphrodite"
]

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = self.load_warnings()

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

    async def warn_user(self, user, message):
        if user in self.warnings:
            self.warnings[user] += 1
        else:
            self.warnings[user] = 1

        if self.warnings[user] > WARNING_LIMIT:
            # Use message.guild to get the current guild
            guild = message.guild

            # Extract user ID cleanly using regex
            match = re.match(r'<@!?(\d+)>', user)
            if match:
                user_id = int(match.group(1))
                member = guild.fetch_member(user_id)

                if member:
                    await self.kick_user(member, reason="Exceeded warning limit")
                    confirmation = await message.channel.send(f"{user}({user_id}) has been kicked")
                    await asyncio.sleep(5)
                    await confirmation.delete()
                else:
                    logging.error(f'Could not find member {user}({user_id}) to kick.')
                    confirmation = await message.channel.send(f'Could not find member {user}({user_id}) to kick.')
                    await asyncio.sleep(5)
                    await confirmation.delete()
                self.warnings.pop(user)  # Remove user from warnings
            else:
                await message.channel.send(f'Could not parse user ID from {user}.')

            # Update the warnings file
            with open('warns.txt', 'w') as f:
                for username, num_warns in self.warnings.items():
                    f.write(f'{username} {num_warns}\n')
            
        else:
            # Update the warnings file
            with open('warns.txt', 'w') as f:
                for username, num_warns in self.warnings.items():
                    f.write(f'{username} {num_warns}\n')
            await message.channel.send(f"{user} has been warned.")
            logging.info(f"{user} has been warned.")

    async def kick_user(self, member: discord.Member, reason: str = "No reason provided"):
        try:
            await member.kick(reason=reason)
            logging.info(f'Kicked {member} for reason: {reason}')
            await member.send(f'You have been kicked from {member.guild.name} for: {reason}')
        except discord.Forbidden:
            logging.error(f'Failed to kick {member}. I do not have permission.')
        except discord.HTTPException as e:
            logging.error(f'Failed to kick {member}. HTTP Exception: {e}')

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f'{self.bot.user} has connected')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Check for the purge command in plain text
        if message.content.startswith('toolbox.purge'):
            try:
                # Extract the number of messages to purge
                num_messages = int(message.content.split(' ')[1])
                try:
                    reason = message.content.split(' ')[2]
                except IndexError:
                    reason = None
                if 1 <= num_messages < 100:
                    # Delete the specified number of messages
                    if reason:
                        await message.channel.purge(limit=num_messages + 1, reason=reason)  # +1 to include the purge command itself
                    else:
                        await message.channel.purge(limit=num_messages + 1)  # +1 to include the purge command itself
                    confirmation = await message.channel.send(f"Purged {num_messages} messages.")
                    await asyncio.sleep(5)
                    await confirmation.delete()
                else:
                    await message.channel.send("Please specify a number between 1 and 99.")
            except (IndexError, ValueError):
                await message.channel.send("Invalid format. Use `toolbox.purge x reason`, where `x` is a number between 1 and 99.")

        if 'load_warn' in message.content and message.author.guild_permissions.manage_messages:
            warns = self.load_warnings()
            await message.channel.send(warns)

        elif 'toolbox.warn' in message.content and message.author.guild_permissions.manage_messages:
            target_user = message.content.replace('toolbox.warn ', '').strip()
            await self.warn_user(target_user, message)
            logging.info(f'{message.author} issued a warn to {target_user}')

        for word in brainrot_words:
            if word in message.content:
                await message.delete()
                await message.channel.send(f'{message.author.nick or message.author.global_name}, no brain rot thank you.')
                logging.info(f'{message.author} tried to use a banned word: {word}')
            
        
        for word in slurs_list:
            if word in message.content:
                await message.delete()
                await message.channel.send(f'{message.author.nick or message.author.global_name}, no brain rot thank you.')
                logging.info(f'{message.author} tried to use a banned word: {word}')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == '💀' and reaction.message.author == self.bot.user:
            if reaction.message.content == "Damn Ok.":
                async with reaction.message.channel.typing():
                    await asyncio.sleep(0.5)
                    await reaction.message.channel.send('Why!?')
            elif reaction.message.content == "Why!?":
                pass
            else:
                async with reaction.message.channel.typing():
                    await asyncio.sleep(0.5)
                    await reaction.message.channel.send('Damn Ok.')
        else:
            await reaction.message.channel.send('ok')

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        pass


def setup(bot):
    bot.add_cog(Moderation(bot))
