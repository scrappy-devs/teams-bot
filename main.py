import os
import random
import discord
import boto3
import logging
import json
from discord.ext import commands
from dotenv import load_dotenv
from discord.utils import get
from secret_wrapper import GetSecretWrapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_token(secret_name):
    """
    Retrieve a secret from AWS Secrets Manager.

    :param secret_name: Name of the secret to retrieve.
    :type secret_name: str
    """
    try:
        # Validate secret_name
        if not secret_name:
            raise ValueError("Secret name must be provided.")
        # Retrieve the secret by name
        client = boto3.client("secretsmanager")
        wrapper = GetSecretWrapper(client)
        secret = wrapper.get_secret(secret_name)
        secret_dict = json.loads(secret)
        return secret_dict['discord_bot_token']
    except Exception as e:
        logging.error(f"Error retrieving secret: {e}")
        raise

# FOR LOCAL DEVELOPMENT:
# # Get token from .env file
# load_dotenv()
# token = os.getenv('TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
token = get_token("app/discord_bot")


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!customs'):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: `!customs <source_channel_name>`")
            return

        # Parse channel name (not ID)
        source_channel_name = parts[1]

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
async def on_message(message):
    if message.author == client.user:
        return

    # Command to split teams and print members (without creating channels)
    if message.content.startswith('!teams'):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: `!teams <source_channel_name>`")
            return

        # Parse channel name (not ID)
        source_channel_name = parts[1]

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

@client.event
async def on_voice_state_update(member, before, after):
    # Only care about members who were moved between voice channels
    
    if before.channel.name.startswith("Team"):  
        if len(before.channel.members) == 0:
            print(f"Deleting empty channel: {before.channel.name}")
            await before.channel.delete()

def run_scenario(secret_name):
    """
    Retrieve a secret from AWS Secrets Manager.

    :param secret_name: Name of the secret to retrieve.
    :type secret_name: str
    """
    try:
        # Validate secret_name
        if not secret_name:
            raise ValueError("Secret name must be provided.")
        # Retrieve the secret by name
        client = boto3.client("secretsmanager")
        wrapper = GetSecretWrapper(client)
        secret = wrapper.get_secret(secret_name)
        # Note: Secrets should not be logged.
        return secret
    except Exception as e:
        logging.error(f"Error retrieving secret: {e}")
        raise

client.run(token)