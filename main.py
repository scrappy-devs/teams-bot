import os
import random
import discord
import logging
import json
from discord.ext import commands
from dotenv import load_dotenv
from discord.utils import get
from queue_view import QueueView
from queue_state import format_queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FOR LOCAL DEVELOPMENT:
# Get token from .env file
load_dotenv()

intents = discord.Intents().all()
client = discord.Client(intents=intents)

token = ""
valid_games = {"mpt", "cod", "rainbow", "rocket"}

token = os.getenv('TOKEN')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

async def handle_team_command(message, command):
    parts = message.content.split()
    if len(parts) < 2:
        await message.channel.send(f"Usage: `{command} <source_channel_name>`")
        return
    return parts[1]

async def get_queue_size(message, command):
    parts = message.content.split()
    if len(parts) < 3:
        await message.channel.send(f"Usage: `{command} <game> <queue_size>`")
        return
    game = parts[1]
    if game.lower() not in valid_games:
        await message.channel.send(f"`{game}` is not a valid game. Please choose from the following games: `{valid_games}`")
        return
    try:
        # Attempt to convert the string input to an integer
        queue_size = int(parts[2])
        if queue_size < 2:
            raise ValueError
    except ValueError:
        # Catch the error if the conversion fails and prompt the user again
        await message.channel.send(f"queue size needs to be greater than 1")
        return
    if queue_size % 2 != 0:
        await message.channel.send(f"queue size needs to be an even number")
        return
    return game, queue_size

async def send_help(message):
    help_message = """
**Available Commands:**

**!queue <game> <queue_size>**
Creates a queue for players to join teams. 
Example: `!queue mpt 8`
Valid games: `mpt`, `cod`, `rainbow`, `rocket`

**!random_teams <channel_name>**
Randomly splits members from a voice channel into two teams and displays them.
Example: `!random_teams Lobby`

**!create_teams <channel_name>**
Randomly splits members from a voice channel into two teams and moves them to separate voice channels.
Example: `!create_teams Lobby`

**!help**
Shows this message.
    """
    await message.channel.send(help_message)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        await send_help(message)
        return

    if message.content.startswith("!queue"):
        game, queue_size = await get_queue_size(message, '!queue')
        if not game and not queue_size:
            return
        await message.channel.send(
            content=format_queue([], [], queue_size, game),
            view=QueueView(queue_size=queue_size, game=game, creator_id=message.author.id)
        )

    # Command to split teams and print members (without creating channels)
    if message.content.startswith('!random_teams'):
        source_channel_name = await handle_team_command(message, '!random_teams')
        if not source_channel_name:
            return
    
        try:
            # Find the source voice channel by name
            source_channel = get(message.guild.voice_channels, name=source_channel_name)
            if not source_channel:
                await message.channel.send(f"Could not find a voice channel named '{source_channel_name}'.")
                return

            # Get members in the source channel
            members = source_channel.members
            if not members:
                await message.channel.send(f"No members found in {source_channel.name}.")
                return

            # Shuffle and split members
            random.shuffle(members)
            mid = len(members) // 2
            team1 = members[:mid]
            team2 = members[mid:]

            # Print teams in the message
            team1_names = ', '.join([m.display_name for m in team1])
            team2_names = ', '.join([m.display_name for m in team2])

            await message.channel.send(
                f"Teams split successfully:\n"
                f"**Team 1**: {team1_names}\n"
                f"**Team 2**: {team2_names}"
            )

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("An error occurred while processing your request.")

    # Command to create teams with new channels
    if message.content.startswith('!create_teams'):
        source_channel_name = await handle_team_command(message, '!create_teams')
        if not source_channel_name:
            return


        try:
            # Find the source voice channel by name
            source_channel = get(message.guild.voice_channels, name=source_channel_name)
            if not source_channel:
                await message.channel.send(f"Could not find a voice channel named '{source_channel_name}'.")
                return
            # Get members in the source channel
            members = source_channel.members
            if not members:
                await message.channel.send(f"No members found in {source_channel.name}.")
                return
            # Shuffle and split members
            random.shuffle(members)
            mid = len(members) // 2
            team1 = members[:mid]
            team2 = members[mid:]
            # Create temporary voice channels
            team1_channel = await message.guild.create_voice_channel("Team 1", category=source_channel.category)
            team2_channel = await message.guild.create_voice_channel("Team 2", category=source_channel.category)
            # Move members to temporary channels
            for member in team1:
                await member.move_to(team1_channel)
            for member in team2:
                await member.move_to(team2_channel)
            await message.channel.send(
                f"Teams split successfully:\n"
                f"({team1_channel.name}): {', '.join([m.display_name for m in team1])}\n"
                f"({team2_channel.name}): {', '.join([m.display_name for m in team2])}"
            )
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("An error occurred while processing your request.")

@client.event
async def on_voice_state_update(member, before, after):
    # Only care about members who were moved between voice channels
    if before.channel.name.startswith("Team"):  
        if len(before.channel.members) == 0:
            print(f"Deleting empty channel: {before.channel.name}")
            await before.channel.delete()

client.run(token)