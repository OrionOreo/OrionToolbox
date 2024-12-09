import asyncio
import os
import re
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

# !! Global Imports
import exceptions
from wordlists import compliment_list

# Configure logging
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

class Silly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_id = 1297521744214491166  # Allowed channel ID
        self.restricted_guild_id = 1297520659718475817  # Restricted guild ID
    
    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f'{self.bot.user} has connected')

    async def is_me(self, ctx, user):
        if user == self.bot.user:
            return True
        else:
            return False

    def is_correct_channel(self, ctx):
        """Check if the command is invoked in the correct channel."""
        if ctx.guild.id == self.restricted_guild_id:
            return ctx.channel.id == self.allowed_channel_id
        return True  # Allow commands in all channels for other servers

    @commands.slash_command(name="autism", description="Find out your autism percentage")
    async def autism(self, ctx, user: discord.Member = None):
        if await self.is_me(ctx, user):
            await ctx.respond("I am a computer, I don't have a brain to be autistic. Wait a sec-")
            return
        
        if not self.is_correct_channel(ctx):
            await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
            return

        if user is None:
            user = ctx.author

        author = ctx.author.display_name
        target = user.display_name
        value = random.randint(0, 100)
        
        if user.id == 1217537431046459452:
            await ctx.respond(f"{target} is {random.randint(80, 100)}% autistic" if target != author else f"You are {random.randint(80, 100)}% autistic {author}")
        elif user.id == 515879989187706881:
            await ctx.respond(f"{target} is {random.randint(60, 100)}% autistic" if target != author else f"You are {random.randint(60, 100)}% autistic {author}")
        else:
            await ctx.respond(f"{target} is {value}% autistic" if target != author else f"You are {value}% autistic {author}")

    @commands.slash_command(name="gay", description="Find out your gay percentage")
    async def gay(self, ctx, user: discord.Member = None):
        if await self.is_me(ctx, user):
            await ctx.respond("I am a bot. I have no attraction to others.")
            return
        
        if not self.is_correct_channel(ctx):
            await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
            return

        if user is None:
            user = ctx.author

        author = ctx.author.display_name
        target = user.display_name
        value = random.randint(0, 100)

        await ctx.respond(f"{target} is {value}% gay" if target != author else f"You are {value}% gay {author}")

    @commands.slash_command(name="braincells", description="Find out how many brain cells you have")
    async def brain_cells(self, ctx, user: discord.Member = None):
        if await self.is_me(ctx, user):
            await ctx.respond("I'm a computer, I don't need brain cells. Just don't ask me what 0.1 + 0.2 is...")
            return
        
        if not self.is_correct_channel(ctx):
            await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
            return

        if user is None:
            user = ctx.author

        author = ctx.author.display_name
        target = user.display_name
        value = random.randint(0, 1000)

        await ctx.respond(f"{target} has {value} braincell{'s' if value != 1 else ''}" if target != author else f"You have {value} braincell{'s' if value != 1 else ''} {author}")

    @commands.slash_command(name="furry", description="Find out your furry percentage")
    async def furry(self, ctx, user: discord.Member = None):
        if await self.is_me(ctx, user):
            await ctx.respond("I'm as much a furry as my creator. Wait a sec...")
            return
        
        await ctx.defer()

        if not self.is_correct_channel(ctx):
            await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
            return

        if user is None:
            user = ctx.author

        author = ctx.author.display_name
        target = user.display_name
        value = random.randint(0, 100)

        if user.id == 952542133586366494:
            message = await ctx.send(f"You know the answer to that {author}...")
            await asyncio.sleep(5)
            value = 100
            await message.delete()

        await ctx.followup.send(f"{target} is {value}% furry OwO" if target != author else f"You are {value}% furry {author} OwO")

    @commands.slash_command(name="smelly", description="Find out your smelly percentage")
    async def smelly(self, ctx, user: discord.Member = None):
        if await self.is_me(ctx, user):
            await ctx.respond("I'm not smelly! I shower every reboot.")
            return
        
        if not self.is_correct_channel(ctx):
            await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
            return

        if user is None:
            user = ctx.author

        author = ctx.author.display_name
        target = user.display_name
        value = random.randint(0, 100)

        await ctx.respond(f"{target} is {value}% smelly" if target != author else f"You are {value}% smelly {author}")

    # # Bitches command (Deprecated in release version)
    # # @commands.slash_command(name="bitches", description="Find out how many bitches you get")
    # # async def bitches(self, ctx, user: discord.Member = None):
    # #     if not self.is_correct_channel(ctx):
    # #         await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
    # #         return

    # #     if user is None:
    # #         user = ctx.author

    # #     author = ctx.author.display_name
    # #     target = user.display_name
    # #     value = random.randint(0, 100)

    # #     if value == 100:
    # #         await ctx.respond(f"{target} gets all the bitches {'' if target == author else author}")
    # #     elif value >= 75:
    # #         await ctx.respond(f"{target} gets most of the bitches {'' if target == author else author}")
    # #     elif value >= 50:
    # #         await ctx.respond(f"{target} gets a lot of bitches {'' if target == author else author}")
    # #     elif value >= 25:
    # #         await ctx.respond(f"{target} gets some of the bitches {'' if target == author else author}")
    # #     elif value > 0:
    # #         await ctx.respond(f"{target} gets a few bitches {'' if target == author else author}")
    # #     else:
    # #         await ctx.respond(f"{target} gets no bitches {'' if target == author else author}")

    @commands.slash_command(name="compliment", description="Compliment a user")
    async def compliment(self, ctx, user: discord.Role | discord.Member):
        if await self.is_me(ctx, user):
            await ctx.respond("I'm flattered, but I don't take compliments <3")
            return
        
        if not self.is_correct_channel(ctx):
            await ctx.respond("This command can only be used in the designated channel.", ephemeral=True)
            return

        if isinstance(user, discord.Member):
            if user.display_name == ctx.author.display_name:
                await ctx.respond(f"<@{user.id}>, are you ok bud?")
                return

            if user:
                compliment = random.choice(compliment_list)
                await ctx.respond(f"{user.mention}, {compliment}\n-# (Sent by {ctx.author.display_name})")
        else:
            if user:
                compliment = random.choice(compliment_list)
                await ctx.respond(f"{user.mention}, {compliment}\n-# (Sent by {ctx.author.display_name})")

def setup(bot):
    try:
        bot.add_cog(Silly(bot))
    except Exception:
        logging.error("ERROR: Silly cog failed to load!")
        raise exceptions.cogFail
