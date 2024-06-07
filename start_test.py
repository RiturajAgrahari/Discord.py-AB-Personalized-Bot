import discord
from discord import ui
from discord.ui import View
from database import Query
from datetime import datetime


query = Query()


async def ask_question(dataset, cur_time, channel):
    answered = {}

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
            async def answer(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id in answered.keys():
                    await interaction.response.send_message('You already responded on this question.', ephemeral=True)
                else:
                    await descriptive_answer(interaction, dataset['title'], dataset['id'])

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
                if interaction.user.id in answered.keys():
                    await interaction.response.send_message('You already responded to this question.', ephemeral=True)
                else:
                    answered[interaction.user.id] = str(self.values[0])
                    await query.add_answer(interaction, dataset["id"], self.values[0])
                    await interaction.response.send_message("Thankyou so much for your response!", ephemeral=True)

        class Select(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(SelectMenu())

        await channel.send(content="", embed=embed, view=Select())


async def descriptive_answer(interaction, title, question_id):
    ANSWERED = {}

    class MyModal(discord.ui.Modal, title=title):
        DESCRIPTION = ui.TextInput(label='Your answer', placeholder='Enter your answer here!', max_length=200,
                                   style=discord.TextStyle.long)

        async def on_submit(self, interaction: discord.Interaction):
            ANSWERED[interaction.user.id] = str(self.DESCRIPTION)
            print(self.DESCRIPTION)
            await query.add_answer(interaction, question_id, self.DESCRIPTION)
            await interaction.response.send_message("thankyou so much for your response!", ephemeral=True)

    await interaction.response.send_modal(MyModal())


async def get_question_ready():
    QUESTIONS = {}
    date = str(datetime.today().date())
    dataset = await query.select_query(column='*', table='personalized_test_question', condition_column='time',
                                       condition_value=date, conditional_operation='>')
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

