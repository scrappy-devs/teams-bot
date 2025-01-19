import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Get token from .env file
load_dotenv()
token = os.getenv('TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run(token)