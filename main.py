import discord
import asyncio
from discord.ext import commands

bot = commands.Bot(command_prefix = 'pls ', intents = discord.Intents.all())

class Client(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("hello")

def main():
    asyncio.run(bot.add_cog(Client(bot)))
    with open('TOKEN', 'r') as token:
        bot.run(token.read())

if __name__ == '__main__': main()

