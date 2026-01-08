import discord
from discord.ext import commands
from queue_state import queue, format_queue, add_user, remove_user, is_closed

class QueueView(discord.ui.View):
    def __init__(self, game: str = "Queue", queue_size: int | None = None):
        super().__init__(timeout=None)
        self.game = game
        self.queue_size = queue_size

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if is_closed():
            await interaction.response.send_message(
                "The queue is currently closed and not accepting new users.",
                ephemeral=True,
            )
            return

        if user in queue:
            await interaction.response.send_message(
                "You are already in the queue.", ephemeral=True
            )
            return

        added = add_user(user, self.queue_size)
        if not added:
            # Fallback message for unexpected failure
            await interaction.response.send_message(
                "Could not join the queue.", ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content=format_queue(self.game, self.queue_size),
            view=self,
        )

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user not in queue:
            await interaction.response.send_message(
                "You are not in the queue.", ephemeral=True
            )
            return

        removed = remove_user(user)
        if not removed:
            await interaction.response.send_message(
                "Could not leave the queue.", ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content=format_queue(self.game, self.queue_size),
            view=self,
        )