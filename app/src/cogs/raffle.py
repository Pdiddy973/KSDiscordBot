"""
The cog module for the raffle command.
"""

import asyncio
import io
import random

import discord
from discord.ext import commands
import orjson


class Raffle(commands.Cog):
    """
    The class to handle the raffle command.
    """
    
    raffle = discord.SlashCommandGroup("raffle", description="The raffle commands.")
    
    def __init__(self, client: discord.AutoShardedBot) -> None:
        self.client = client

    @raffle.command(description="Create a raffle.")
    @discord.option(name="prize", description="The prize of the raffle.", required=True)
    @discord.option(name="winners", description="The number of winners.", required=True, min_value=1, max_value=10)
    async def create(self, ctx: discord.ApplicationContext, prize: str, winners: int) -> discord.Message:
        """
        The function to handle the raffle command.
        
        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param prize: The prize of the raffle.
        :type prize: str
        :param winners: The number of winners.
        :type winners: int
        
        :return: The message that was sent.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        raffle = discord.File(io.BytesIO(orjson.dumps({"prize": prize, "winners": winners, "participants": {}})), filename="raffle.json")
        return await ctx.respond("Here is the raffle file.", file=raffle)

    @raffle.command(description="Add a participant to a raffle.")
    @discord.option(name="raffle", description="The raffle file.", required=True)
    @discord.option(name="participant", description="The participant to add.", required=True)
    @discord.option(name="amount", description="The amount of entries.", required=True)
    async def add_participant(self, ctx: discord.ApplicationContext, raffle: discord.Attachment, participant: discord.Member, amount: int) -> discord.Message:
        """
        The function to handle the add_participant command.
        
        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param raffle: The raffle file.
        :type raffle: discord.File
        :param participant: The participant to add.
        :type participant: discord.Member
        :param amount: The amount of entries.
        :type amount: int
        
        :return: The message that was sent.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        try:
            raffle = orjson.loads(await raffle.read())
        except Exception:
            return await ctx.respond(f"The raffle file is invalid. You can create a new one with </raffle create:{self.client.get_command('raffle').id}>.")
        raffle["participants"][str(participant.id)] = amount
        raffle = discord.File(io.BytesIO(orjson.dumps(raffle)), filename="raffle.json")
        return await ctx.respond(f"Here is the updated raffle file. {participant.mention} now have {amount} entries.", file=raffle)
    
    @raffle.command(description="Remove a participant from a raffle.")
    @discord.option(name="raffle", description="The raffle file.", required=True)
    @discord.option(name="participant", description="The participant to remove.", required=True)
    async def remove_participant(self, ctx: discord.ApplicationContext, raffle: discord.Attachment, participant: discord.Member) -> discord.Message:
        """
        The function to handle the remove_participant command.
        
        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param raffle: The raffle file.
        :type raffle: discord.File
        
        :return: The message that was sent.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        try:
            raffle = orjson.loads(await raffle.read())
        except Exception:
            return await ctx.respond(f"The raffle file is invalid. You can create a new one with </raffle create:{self.client.get_command('raffle').id}>.")
        if str(participant.id) not in raffle["participants"]:
            return await ctx.respond(f"{participant.mention} is not a participant in this raffle.")
        del raffle["participants"][str(participant.id)]
        raffle = discord.File(io.BytesIO(orjson.dumps(raffle)), filename="raffle.json")
        return await ctx.respond(f"Here is the updated raffle file. {participant.mention} was removed.", file=raffle)
    
    @raffle.command(description="Draw the winners of a raffle.")
    @discord.option(name="raffle", description="The raffle file.", required=True)
    async def draw(self, ctx: discord.ApplicationContext, raffle: discord.Attachment) -> discord.Message:
        """
        The function to handle the draw command.
        
        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param raffle: The raffle file.
        :type raffle: discord.File
        
        :return: The message that was sent.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        try:
            raffle = orjson.loads(await raffle.read())
        except Exception:
            return await ctx.respond(f"The raffle file is invalid. You can create a new one with </raffle create:{self.client.get_command('raffle').id}>.")
        if not raffle["participants"]:
            return await ctx.respond("There are no participants in this raffle.")
        elif len(raffle["participants"]) < raffle["winners"]:
            return await ctx.respond("There are not enough participants in this raffle.")
        await ctx.respond("Starting the raffle...")
        participants = []
        entries = []
        for k,v in raffle["participants"].items():
            participants.append(int(k))
            entries.append(v)
        winners = '\n'.join([f'<@{i}>' for i in random.choices(participants, entries, k=raffle["winners"])])
        embed0 = discord.Embed(title="Preparing the raffle", color=0x00ff00)
        embed1 = discord.Embed(title="Picking a winner", color=0x00ff00).add_field(name="Prize", value=raffle["prize"], inline=False)
        embed2 = discord.Embed(title="Picking a winner.", color=0x00ff00).add_field(name="Prize", value=raffle["prize"], inline=False)
        embed3 = discord.Embed(title="Picking a winner..", color=0x00ff00).add_field(name="Prize", value=raffle["prize"], inline=False)
        embed4 = discord.Embed(title="Picking a winner...", color=0x00ff00).add_field(name="Prize", value=raffle["prize"], inline=False)
        embed5 = discord.Embed(title="Winner!", color=0x00ff00).add_field(name="Prize", value=raffle["prize"], inline=False).add_field(name="Winners", value=winners, inline=False)
        message = await ctx.channel.send(embed=embed0)
        for i in [embed1, embed2, embed3, embed4, embed5]:
            await asyncio.sleep(1)
            await message.edit(embed=i)


def setup(client: discord.AutoShardedBot) -> None:
    """
    The function to add the cog to the client.
    
    :param client: The client to add the cog to.
    :type client: discord.AutoShardedBot
    """
    client.add_cog(Raffle(client))