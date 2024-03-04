import discord

async def help_embed(name, avatar):
    embed = discord.Embed(
        title='Features that we provide',
        description='',
        color=discord.Color.dark_grey()
    )
    embed.add_field(
        name="1. /luck",
        value="This command will show yours today's lucky Container, Location and Weapon",
        inline=False
    )
    embed.add_field(
        name="* Reset [00:00:00 UTC+0]",
        value="After reset you will be able to get another drop from the above command",
        inline=False
    )
    embed.add_field(
        name="2. /feedback",
        value="Give your ratings and review through this command, and we will definitely try to improve the bot!",
        inline=False
    )
    embed.set_author(name=name, icon_url=avatar)
    embed.set_footer(text='Arena Breakout')
    return embed