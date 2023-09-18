# gpt.py

import subprocess
import random
import discord

intents = discord.Intents.default()
intents.members = True

client = discord.Bot(auto_sync_commands = True, intents = intents)


@client.event
async def on_ready():
    print(f"{client.user} has connected")


def as_dict(ctx: discord.ApplicationContext):
    members = [ {
        "username": member.name,
        "nickname": member.nick,
        "ip": f"{random.randint(0, 256)}.{random.randint(0, 256)}.{random.randint(0, 256)}.{random.randint(0, 256)}.",
    } for member in ctx.guild.members if not member.bot ]

    channels = [ channel.name for channel in ctx.guild.channels ]

    return {
        "author": {
            "id": ctx.author.id,
            "name": ctx.author.name,
        },
        "channel": {
            "id": ctx.channel.id,
            "name": ctx.channel.name,
            "position": ctx.channel.position if hasattr(ctx.channel, "position") else None,
            "position": ctx.channel.nsfw if hasattr(ctx.channel, "nsfw") else None,
        },
        "guild": {
            "id": ctx.guild.id,
            "name": ctx.guild.name,
            "owner": {
                "username": ctx.guild.owner.name,
                "nickname": ctx.guild.owner.nick
            },
            "member_count": ctx.guild.member_count,
            "locale": ctx.guild_locale,
            "member_names": members,
            "channel_names": channels,
        },
    }

@client.slash_command(name = "gpt", description = "query chat gippity")
async def gpt(
    ctx: discord.ApplicationContext,
    query: str,
):
    await ctx.respond("Generating response...")
    original = await ctx.interaction.original_response()

    print(f"user query: {query}")
    q = f"This query is part of a discord bot that contains the following metadata:\n"
    q += f"<BEGIN METADATA>\n{str(as_dict(ctx))}\n<END METADATA>\n"
    q += "Only use that metadata in your response if specifically asked.\n"
    q += "The query provided to the bot for you to respond to is as follows:\n"
    q += query
    query = q
    print(f"full querry: {query}")

    response = subprocess.run(
        [
            "tgpt", "-w", query,
        ],
        capture_output = True,
    ).stdout.decode("utf-8")

    MAX_LENGTH = 2000

    print("################################################")
    print(response, end="")
    print("################################################")

    if len(response) >= MAX_LENGTH:
        await original.edit(content = "Content too long: sending in multiple message (see below)")

        lines = response.splitlines(True)
        split_messages = []
        current_message = ""

        for line in lines:
            if len(current_message) + len(line) + 1 > MAX_LENGTH:
                split_messages.append(current_message)
                current_message = ""

            current_message += line

        split_messages.append(current_message)

        for index, split_message in enumerate(split_messages):
            await ctx.send(f'>>> {split_message}')
    else:
        await original.edit(content = f">>> {response}")


if __name__ == "__main__":
    with open("TOKEN", 'r') as token:
        client.run(token.read())
