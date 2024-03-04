import os
import discord

from datetime import datetime
from typing import Literal

from dotenv import load_dotenv
from discord import app_commands
from discord.ext import tasks

from add_test import creating_test, get_question_ready, ask_question

load_dotenv()

MAIN_GUILD_ID = int(os.getenv("MAIN_SERVER_ID"))
# TEST_GUILD_ID = int(os.getenv("TEST_SERVER_ID"))


class MyClient(discord.Client):
    def __init__(self, *, intents:discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Set up command tree for the first guild
        first_guild = discord.Object(id=MAIN_GUILD_ID)
        self.tree.copy_global_to(guild=first_guild)
        await self.tree.sync(guild=first_guild)

        # Set up command tree for the second guild
        # second_guild = discord.Object(id=TEST_GUILD_ID)
        # if second_guild.id != MAIN_GUILD_ID:
        #     self.tree.copy_global_to(guild=second_guild)
        #     await self.tree.sync(guild=second_guild)


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Your Arena Breakout bot in succesfully started as {client.user} (ID: {client.user.id})')
    print('-----')
    await my_loop.start()


@tasks.loop(minutes=1)
async def my_loop():
    questions = []
    question = await get_question_ready()
    if question:
        questions = list(question.keys())

    # Get the current UTC time
    current_time_utc = datetime.utcnow().replace(second=0, microsecond=0)
    print(f"current_time_utc: {current_time_utc}", questions)

    if current_time_utc in questions:
        channel = client.get_channel(1199253624350576692)
        await ask_question(question[current_time_utc], current_time_utc, channel)



@client.event
async def on_message(message):
    # Checks if the message is recieved in DM
    if message.channel.type == discord.ChannelType.private:
        print(f'DM --> [{message.author}] : {message.content}')

    # Check if the message author is not client itself
    if message.author == client.user:
        pass

    # Message in server channels
    else:
        username = str(message.author).split('#')[0]
        user_message = str(message.content)
        channel = str(message.channel.name)
        guild_name = message.guild.name
        # print(f'[channel: {channel}] --> {username}: {user_message}')

        if channel == 'fandom':
            print('success')

            if message.content == 'update_database_only_once' and message.author.mention == '<@568179896459722753>':
                print('AYOOOOOOOOOO!')
                await create_updated_db()

@client.tree.command(name='create', description="create your question!")
async def quest(interaction: discord.Interaction):
    if interaction.guild.id == MAIN_GUILD_ID:
        await creating_test(client, interaction, 'title', 'description')

    else:
        await interaction.response.send_message(embed=discord.Embed(title='',
                                                                    description="This command is not available in this server.",
                                                                    color=discord.Color.red()), ephemeral=True)


async def get_avatar_url(interaction):
    try:
        user_avatar_url = interaction.user.avatar.url
        return user_avatar_url
    except:
        default_avatar_url = 'https://cdn.discordapp.com/attachments/1171092440233541632/1176439824622833764/Untitled.png?ex=656edff7&is=655c6af7&hm=3e2cd8767c426187fbfc3171749ccf0158152f94a9b64f5acb3ae0a868a907c5&'
        return default_avatar_url


# Last Optimization [19-01-2024] --> Need Relocation
async def send_error(file, function_name, error, server='Anonymous'):
    embed = discord.Embed(title=f'{server} Server',
        description=file,
        color=discord.Color.red()
    )
    embed.add_field(
        name=function_name,
        value=error,
        inline=False
    )
    user = await client.fetch_user(568179896459722753)
    await user.send(embed=embed)


# @client.event
# async def on_error(event, *args, **kwargs):
#     error = str(sys.exc_info())
#     error = error.replace(',', '\n')
#     await send_error(__file__, event, error, server='Arena Breakout')

client.run(os.getenv("TOKEN"))

