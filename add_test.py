import discord
import asyncio
from discord import ui
from discord._types import ClientT
from discord.ui import View, Button
from database import Query
from datetime import datetime

ANSWERED = {}

async def creating_test(client, interaction, title, description, response=True, image=None, embed_type=None, send_time=[]):
    if title == 'title' or description == 'description' or not send_time or not embed_type:
        save_status = True
    else:
        save_status = False

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )
    embed.set_image(url=image)
    embed.set_footer(text=embed_type)

    class MyView(View):
        def __init__(self):
            super().__init__()


        @discord.ui.button(label='Embed', style=discord.ButtonStyle.blurple)
        async def add_title(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.stop()
            await create_embed(client, interaction, image, send_time, embed_type)

        @discord.ui.button(label="Upload Image", style=discord.ButtonStyle.blurple)
        async def upload_image(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Send a message prompting the user to upload an image
            await interaction.response.edit_message(content="Please upload an image file.", embed=None, view=None)
            try:
                message = await client.wait_for('message', timeout=60.0)
                if message.attachments:
                    await interaction.message.delete()
                    image = message.attachments[0].url
                await creating_test(client, interaction, title, description, response=False, image=image, embed_type=embed_type, send_time=send_time)

            except asyncio.TimeoutError:
                await creating_test(client, interaction, title, description, response=False, image=image, embed_type=embed_type, send_time=send_time)

        async def interaction_check(self, interaction: discord.Interaction):
            # Check if the interaction is from the original user
            return interaction.user == self.viewing_user

        async def on_timeout(self) -> None:
            try:
                await interaction.delete_original_response()
            except:
                try:
                    await interaction.message.delete()
                except:
                    pass


        @discord.ui.button(label='Type', style=discord.ButtonStyle.gray)
        async def question_type(self, interaction: discord.Interaction, button: discord.Button):
            await select_type(client, interaction, title, description, image, embed_type, send_time)

        @discord.ui.button(label='Set time', style=discord.ButtonStyle.gray)
        async def set_time(self, interaction: discord.Interaction, button: discord.Button):
            await set_post_time(client, interaction, title, description, image, embed_type, send_time)


        @discord.ui.button(label='Save', style=discord.ButtonStyle.green, disabled=save_status)
        async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.stop()
            print('1 unit stored!')
            query =Query()
            await query.add_test(str(title), str(description), str(image), str(embed_type), send_time)


    view = MyView()
    view.viewing_user = interaction.user

    if response:
        view.response = await interaction.response.send_message(content='', embed=embed, view=view)

    else:
        try:
            view.response = await interaction.response.edit_message(content='', embed=embed, view=view)
        except:
            view.response = await interaction.followup.send(content='', embed=embed, view=view)


async def create_embed(client, interaction, image, send_time, embed_type):
    class MyModal(discord.ui.Modal, title='Add Title'):
        change_title = ui.TextInput(label='Title', placeholder='Enter title', style=discord.TextStyle.short)
        change_description = ui.TextInput(label='Description', placeholder='Enter description', style=discord.TextStyle.long)

        async def on_submit(self, interaction: discord.Interaction):
            await creating_test(client, interaction, self.change_title, self.change_description, response=False, image=image, embed_type=embed_type, send_time=send_time)


    await interaction.response.send_modal(MyModal())


async def select_type(client, interaction, title, description, image, embed_type, send_time):
    mcq_style = discord.ButtonStyle.gray
    descriptive_style = discord.ButtonStyle.gray
    if embed_type:
        if type(embed_type) is list:
            mcq_style = discord.ButtonStyle.green
        else:
            descriptive_style = discord.ButtonStyle.green


    class MyView(View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label='MCQ', style=mcq_style)
        async def mcq(self, interaction: discord.Interaction, button: discord.Button):
            await type_mcq(client, interaction, title, description, image, embed_type, send_time)


        @discord.ui.button(label='Descriptive', style=descriptive_style)
        async def descriptive(self, interaction: discord.Interaction, button: discord.Button):
            await creating_test(client, interaction, title, description, response=False, image=image, embed_type='descriptive', send_time=send_time)

    view2 = MyView()
    view2.response = await interaction.response.edit_message(
        content='',
        embed=discord.Embed(
            title='Question Type',
            description='',
            color=discord.Color.green()
        ).add_field(
            name='MCQ',
            value='In this embed_type the user will get options to select there answer',
            inline=False
        ).add_field(
            name='Descriptive',
            value='In this embed_type the user will get a form to fill a descriptive answer in it',
            inline=False
        ),
        view=view2
    )
    

async def type_mcq(client, interaction, title, description, image, embed_type, send_time):
    print(embed_type)
    if type(embed_type) is list:
        new_type = embed_type
    else:
        new_type = []

    embed2 = discord.Embed(title='Options', description='', color=discord.Color.gold())
    for element in new_type:
        embed2.add_field(name=element, value='', inline=False)

    class MyView(View):
        def __init__(self):
            super().__init__()
            
        @discord.ui.button(label='Add Options', style=discord.ButtonStyle.green)
        async def add_option(self, interaction: discord.Interaction, button: discord.Button):
            await add_option(client, interaction, title, description, image, new_type, send_time)

        if embed_type:
            @discord.ui.button(label='Remove Options', style=discord.ButtonStyle.red, disabled=False)
            async def remove_option(self, interaction: discord.Interaction, button: discord.Button):
                await remove_option(client, interaction, title, description, image, new_type, embed2, send_time)

        else:
            @discord.ui.button(label='Remove Options', style=discord.ButtonStyle.red, disabled=True)
            async def remove_option(self, interaction: discord.Interaction, button: discord.Button):
                pass

        @discord.ui.button(label='save', style=discord.ButtonStyle.gray)
        async def save(self, interaction: discord.Interaction, button: discord.Button):
            await creating_test(client, interaction, title, description, response=False, image=image, embed_type=new_type, send_time=send_time)

    view = MyView()
    view.response = await interaction.response.edit_message(
        content='',
        embed=embed2,
        view=view
    )




async def add_option(client, interaction, title, description, image, embed_type, send_time):
    class MyModal(discord.ui.Modal, title='Add options'):
        option = ui.TextInput(label='Option', placeholder='Enter option', style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            embed_type.append(str(self.option))
            await type_mcq(client, interaction, title, description, image, embed_type, send_time)

    await interaction.response.send_modal(MyModal())
    

async def remove_option(client, interaction, title, description, image, embed_type, embed2, send_time):
    print(embed_type)
    class SelectMenu(discord.ui.Select):
        def __init__(self):
            options = []
            for element in embed_type:
                options.append(discord.SelectOption(label=element))

            # options = [discord.SelectOption(label=embed_type_element) for embed_type_element in embed_type]
            super().__init__(placeholder='Remove Option:', options=options, min_values=0, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            embed_type.remove(self.values[0])
            await type_mcq(client, interaction, title, description, image, embed_type, send_time)

    class Select(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(SelectMenu())

    await interaction.response.edit_message(content="", embed=embed2, view=Select())


async def set_post_time(client, interaction, title, description, image, embed_type, send_time):
    class MyModal(discord.ui.Modal, title='Set Posting Time'):
        TIME = ui.TextInput(label='Time (in utc)', placeholder='Enter time (12:00)', style=discord.TextStyle.short)
        DATE = ui.TextInput(label='Date', placeholder='Enter date (5)', style=discord.TextStyle.short)
        MONTH = ui.TextInput(label='Month', placeholder='Enter month index (9)', style=discord.TextStyle.short)
        YEAR = ui.TextInput(label='Year', placeholder='Enter Year (2024)', style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(self.TIME, self.DATE, self.MONTH, self.YEAR)
            send_time = [str(self.TIME), str(self.DATE), str(self.MONTH), str(self.YEAR)]
            await creating_test(client, interaction, title, description, response=False, image=image, embed_type=embed_type, send_time=send_time)

    await interaction.response.send_modal(MyModal())



async def ask_question(dataset, cur_time, channel):
    embed = discord.Embed(
        title=dataset['title'],
        description=dataset['description'],
        color=discord.Color.random()
    )
    if dataset['image']:
        embed.set_image(url=dataset['image'])

    embed.set_footer(text=cur_time)

    if dataset['type'] == 'descriptive':
        class MyView(View):
            def __init__(self):
                super().__init__()

            @discord.ui.button(label='answer', style=discord.ButtonStyle.green)
            async def answer(self, interaction: discord.Interaction, button: discord.Button):
                if interaction.user.id in ANSWERED.keys():
                    await interaction.response.send_message('You already responded on this question.', ephemeral=True)
                else:
                    await descriptive_answer(interaction, dataset['title'])


        view = MyView()
        view.response = await channel.send(content="", embed=embed, view=view)

    else:
        trim = str(dataset['type']).removeprefix('[').removesuffix(']')
        get_list = trim.split(',')
        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = []
                for element in get_list:
                    options.append(discord.SelectOption(label=element))

                # options = [discord.SelectOption(label=embed_type_element) for embed_type_element in embed_type]
                super().__init__(placeholder='Choose 1 Option:', options=options, min_values=0, max_values=1)

            async def callback(self, interaction: discord.Interaction):
                print(self.values[0])


        class Select(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(SelectMenu())

        await channel.send(content="", embed=embed, view=Select())


async def descriptive_answer(interaction, title):
    class MyModal(discord.ui.Modal, title=title):
        DESCRIPTION = ui.TextInput(label='Your answer', placeholder='Enter your answer here!',
                                   style=discord.TextStyle.long)

        async def on_submit(self, interaction: discord.Interaction):
            ANSWERED[interaction.user.id] = str(self.DESCRIPTION)
            print(self.DESCRIPTION)

    await interaction.response.send_modal(MyModal())

async def get_question_ready():
    QUESTIONS = {}
    query = Query()
    dataset = await query.select_query(column='*', table='personalized_test')
    for data in dataset:
        mysql_datetime_str = str(data[5])
        mysql_datetime = datetime.strptime(mysql_datetime_str[:-3], '%Y-%m-%d %H:%M')

        QUESTIONS[mysql_datetime] = {
            'id': data[0],
            'title': data[1],
            'description': data[2],
            'image': data[3],
            'type': data[4],
        }

    return QUESTIONS

