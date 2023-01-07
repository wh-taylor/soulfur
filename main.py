import discord
import asyncio
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild = discord.Object(id = 1061147612494954506))
    print("hello!!!!")

# Slash Commands

@tree.command(name = "ping", description = "Ping the bot", guild = discord.Object(id = 1061147612494954506))
async def ping(interaction):
    await interaction.response.send_message("Pong!")

def main():
    with open('TOKEN', 'r') as token:
        client.run(token.read())

if __name__ == '__main__': main()

