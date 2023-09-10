#!/bin/python

import discord
import numpy
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from types import MethodType


client = discord.Bot(auto_sync_commands = True )

@client.event
async def on_ready():
    print(f"{client.user} has connected")


@client.slash_command(name = "ping", description = "pong")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond("pong")


##############
### MARKOV ###
##############

class Probabilities:
    def __init__(self,
        probabilities: Dict[str, Dict[str, float]] = {},
        last_fetched: Optional[datetime] = None
    ):
        self.probabilities = probabilities
        self.last_fetched = last_fetched

MARKOV_PROBABILITIES = Probabilities()


def current_time():
    return int(round(time.time() * 1000))


def increment_or_add_probability(dictionary: Dict[Any, Dict], key1, key2):
    if key1 not in dictionary:
        dictionary[key1] = {}

    if key2 in dictionary[key1]:
        dictionary[key1][key2] += 1
    else:
        dictionary[key1][key2] = 1


def normalise_probabilities(probabilities: Dict[str, Dict[str, float]]):
    for _, v in probabilities.items():
        count = 0.0

        for _, v2 in v.items():
            count += v2

        for k, v2 in v.items():
            v[k] = v2 / count


def get_probabilities(messages: List[List[str]]) -> Dict[str, Dict[str, float]]:
    global MARKOV_PROBABILITIES
    probabilities: Dict[str, Dict[str, float]] = MARKOV_PROBABILITIES.probabilities

    for message in messages:
        if len(message) == 0:
            continue

        message.append("<eof>")

        index = 0
        while index < len(message):
            word = message[index]

            if index < len(message) - 1:
                if index == 0:
                    increment_or_add_probability(probabilities, "<start>", word)

                next = message[index + 1]
                increment_or_add_probability(probabilities, word, next)

            index += 1

    normalise_probabilities(probabilities)
    MARKOV_PROBABILITIES.probabilities = probabilities

    return probabilities


def generate_markov_chain(probabilities: Dict[str, Dict[str, float]]) -> str:
    words: List[str] = []

    word = "<start>"
    while word != "<eof>":
        possible_words = [ k for k in probabilities[word] ]
        possible_probabilities = [ v for _, v in probabilities[word].items() ]

        word = numpy.random.choice(possible_words, p=possible_probabilities)
        words.append(word)
    words.pop()

    return " ".join(words)


def has_method(obj, name):
    return hasattr(obj, name) and type(getattr(obj, name)) == MethodType


@client.slash_command(name = "markov", description = "generate a markov chain")
async def markov(
    ctx: discord.ApplicationContext,
    user: discord.Option(discord.Member, "user") = None,
    limit: discord.Option(int, "limit") = None,
):
    print("Markov Chain")
    global MARKOV_PROBABILITIES
    user = user or ctx.user
    guild = ctx.guild

    print(f"  Generating chain from {limit or 'all'} of {user}'s messages...")
    overall_start = current_time()

    await ctx.respond("this may take a while...")

    print("  Checking if new messages since last run...", end="", flush=True)
    print(" lmao no im not TODO")

    print("  Getting messages...")
    start = current_time()
    allowed_channel_types = [
        discord.ChannelType.text,
        discord.ChannelType.voice,
        discord.ChannelType.private,
        discord.ChannelType.group,
        discord.ChannelType.category,
        discord.ChannelType.news,
        discord.ChannelType.stage_voice,
        discord.ChannelType.news_thread,
        discord.ChannelType.public_thread,
        discord.ChannelType.private_thread,
        discord.ChannelType.directory,
    ]

    messages = []
    total_messages = 0
    total_matches = 0
    most_recent_message: Optional[discord.Message] = None

    for channel in guild.channels:
        print(f"\r  {channel.name:80s}")
        if has_method(channel, "history"):
            async for message in channel.history(
                limit = limit,
                after = MARKOV_PROBABILITIES.last_fetched
            ):
                total_messages += 1
                print(f"\r  {total_messages} messages...", end="", flush=True)

                if not most_recent_message or most_recent_message.created_at < message.created_at:
                    most_recent_message = message

                if message.author == user:
                    total_matches += 1
                    messages.append(message)

        if has_method(channel, "archived_threads"):
            async for thread in channel.archived_threads():
                print(f"\r    {thread.name:80s}")
                async for message in thread.history(
                    limit = limit,
                    after = MARKOV_PROBABILITIES.last_fetched
                ):
                    total_messages += 1
                    print(f"\r  {total_messages} messages...", end="", flush=True)

                    if message.author == user:
                        total_matches += 1
                        messages.append(message)


        if hasattr(channel, "threads"):
            for thread in channel.threads:
                print(f"\r    {thread.name:80s}")
                async for message in thread.history(
                    limit = limit,
                    after = MARKOV_PROBABILITIES.last_fetched
                ):
                    total_messages += 1
                    print(f"\r  {total_messages} messages...", end="", flush=True)

                    if message.author == user:
                        total_matches += 1
                        messages.append(message)

    if most_recent_message is not None:
        MARKOV_PROBABILITIES.last_fetched = most_recent_message.created_at

    print(f"\n  Took {(current_time() - start) / 1000} seconds")
    print("  Sorting messages...")
    messages.sort(key = lambda message: message.created_at or 0)

    if limit is not None and len(messages) >= limit:
        messages = messages[len(messages) - limit:]

    print("  Splitting messages...")
    messages = [ message.content.split() for message in messages ]

    print("  Generating response...", end="", flush=True)
    start = current_time()
    response = generate_markov_chain(get_probabilities(messages))
    print(f" Took {(current_time() - start) / 1000} seconds")

    print("  Sending response...")
    await (await ctx.interaction.original_response()).edit(content = response)
    print(f"  Completed in {(current_time() - overall_start) / 1000} seconds!")


############
### MAIN ###
############

def main():
    with open("TOKEN", 'r') as token:
        client.run(token.read())


if __name__ == "__main__":
    main()
