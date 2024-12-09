import asyncio
import os
import re
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
import openai

# !! Global imports:
import exceptions
from wordlists import SLURS_LIST

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = openai.OpenAI(timeout=5)

# Configurable warning limit
WARNING_LIMIT = 3

class ModerationAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f'{self.bot.user} has connected')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        try:
            response = client.moderations.create(
                model = "omni-moderation-latest",
                input = message.content,
            )
            analysis = response["results"]
        except openai.InternalServerError as e:
            logging.error(f"Unable to connect: {e}")
            analysis = None
            error = True
        
        if analysis:
            logging.info(f'Flagging {message.author}: {message.content}')
            categories = analysis["categories"]
            output = f"Content Violates: {categories[0]}"
            for category in categories[1:]:
                output = f"{output}, {category}"
            for word in SLURS_LIST:
                if word in message.content:
                    await message.delete()
                    warn = await message.channel.send(f'{message.author.nick or message.author.global_name}, that word is banned.')
                    logging.info(f'{message.author} tried to use a banned word: {word}.')
                    await asyncio.sleep(5)
                    await warn.delete()
        elif error:
            logging.warning(f"Error in analysis. See above for details.")
        else:
            # Allow positive/neutral messages through
            logging.info(f'Allowed message from {message.author}: {message.content}.')

def setup(bot):
    try:
        # Attempt to create the moderation AI cog
        response = client.moderations.create(
            model = "omni-moderation-latest",
            input = "test",
        )
        bot.add_cog(ModerationAI(bot))
    except openai.InternalServerError as e:
        logging.critical("CRITICAL COG FAILURE: Stopping due to error: %s", e)
        raise exceptions.cogFail