import discord
from discord.ext import commands
from queue_state import queue, format_queue

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in queue:
            await interaction.response.send_message(
                "You are already in the queue.", ephemeral=True
            )
            return

        queue.append(user)
        await interaction.response.edit_message(
            content=format_queue(),
            view=self
        )

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user not in queue:
            await interaction.response.send_message(
                "You are not in the queue.", ephemeral=True
            )
            return

        queue.remove(user)
        await interaction.response.edit_message(
            content=format_queue(),
            view=self
        )