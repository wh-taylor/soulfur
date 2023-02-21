#!/bin/python

import discord
from discord.ext import commands


_intents = discord.Intents.default()
_intents.message_content = True
BOT = commands.Bot(intents = _intents,
                   command_prefix = "please ")


@BOT.event
async def on_ready():
    print(f"{BOT.user.name} has connected")


@BOT.command(name = "ping", description = "pong")
async def ping(ctx):
    await ctx.send("pong!")


@BOT.command(name = "echo", description = "repeats what you say")
async def echo(ctx, msg = None):
    if(msg):
        await ctx.send(msg)
    else:
        await ctx.send("** **")


def get_text_channels(guild):
    return [ c for c in guild.channels if c.type == discord.ChannelType.text ]


# gets all messages in the channel
async def get_messages_by_user_in_channel(user, channel):
    return [ m async for m in channel.history(limit=None) if m.author == user ]


# gets all messages in the guild
async def get_messages_by_user_in_guild(user, guild):
    msgs = [ ]
    for channel in get_text_channels(guild):
        for msg in await get_messages_by_user_in_channel(user, channel):
            msgs.append(msg)

    return msgs


async def todgraph_current_user(ctx):
    if not ctx.guild:
        await ctx.send("please run this in a guild")
        return

    await ctx.send("this may take a while...")
    messages = await get_messages_by_user_in_guild(ctx.author, ctx.guild)
    print("done")

    # TODO: generate a graph in which the Y axis is the number of messages,
    # and the X axis is the time of day the messages were sent
    # the specific graphing method doesn't matter to me so long as it looks nice
    # and is actually informative


@BOT.command(name = "test", description = "graph user activity by time of day")
async def todgraph(ctx, user = None):
    if user:
        # TODO: allow users to specify a different user to graph
        pass
    else:
        await todgraph_current_user(ctx)


def main():
    with open("TOKEN", 'r') as token:
        BOT.run(token.read())

if __name__ == "__main__":
    main()
