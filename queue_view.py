import discord
from discord.ext import commands
from queue_state import format_queue

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.queue = []

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in self.queue:
            await interaction.response.send_message(
                "You are already in the queue.", ephemeral=True
            )
            return

        self.queue.append(user)
        await interaction.response.edit_message(
            content=format_queue(self.queue),
            view=self
        )

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user not in self.queue:
            await interaction.response.send_message(
                "You are not in the queue.", ephemeral=True
            )
            return

        self.queue.remove(user)
        await interaction.response.edit_message(
            content=format_queue(self.queue),
            view=self
        )