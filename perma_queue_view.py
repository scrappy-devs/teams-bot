import discord
import random
from discord.ext import commands
from discord.utils import get
from queue_state import format_queue, format_perma_queue, start_game
from match_start_view import MatchStartView

class PermaQueueView(discord.ui.View):
    def __init__(self, queue_size=0, game="", creator_id=None):
        super().__init__(timeout=None)  # Permanent view (no timeout)
        self.queue = []  # General queue list
        self.queue_size = queue_size
        self.game = game
        self.creator_id = creator_id


    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in self.queue:
            await interaction.response.send_message(
                "You are already in the queue.", ephemeral=True
            )
            return
        
        if len(self.queue) >= self.queue_size:
            await interaction.response.send_message(
                "The queue is already full.", ephemeral=True
            )
            return

        self.queue.append(user)
        
        # Check if queue is now full
        if len(self.queue) >= self.queue_size:
            # Randomize and split into two teams
            shuffled_queue = self.queue.copy()
            random.shuffle(shuffled_queue)
            mid = len(shuffled_queue) // 2
            team1 = shuffled_queue[:mid]
            team2 = shuffled_queue[mid:]
            
            # Send message to general channel with MatchStartView
            general_channel = get(interaction.guild.text_channels, name="general")
            if general_channel:
                await general_channel.send(
                    content=start_game(team1, team2, self.game),
                    view=MatchStartView(team1, team2, self.game, self.creator_id)
                )
            
            # Reset the queue
            self.queue = []
            await interaction.response.edit_message(
                content=format_perma_queue(self.queue, self.queue_size, self.game),
                view=self
            )
        else:
            await interaction.response.edit_message(
                content=format_perma_queue(self.queue, self.queue_size, self.game),
                view=self
            )

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user not in self.queue:
            await interaction.response.send_message(
                "You are not in the queue.", ephemeral=True
            )
            return

        self.queue.remove(user)
        await interaction.response.edit_message(
            content=format_perma_queue(self.queue, self.queue_size, self.game),
            view=self
        )
