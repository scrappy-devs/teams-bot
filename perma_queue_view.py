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
        # Create pre match if queue is full
        if len(self.queue) >= self.queue_size:
            # Randomize and split into two teams
            shuffled_queue = self.queue.copy()
            random.shuffle(shuffled_queue)
            mid = len(shuffled_queue) // 2
            team1 = shuffled_queue[:mid]
            team2 = shuffled_queue[mid:]
            
            # Reset the queue first
            self.queue = []
            
            # Update the message first
            await interaction.response.edit_message(
                content=format_perma_queue(self.queue, self.queue_size, self.game),
                view=self
            )
            
            # Find or create the category with the game name
            game_category = get(interaction.guild.categories, name=self.game)
            if not game_category:
                try:
                    game_category = await interaction.guild.create_category(self.game)
                except Exception as e:
                    await interaction.followup.send(
                        f"Could not create category '{self.game}': {e}", ephemeral=True
                    )
                    return
            
            # Look for the matches channel in the game category
            matches_channel = get(game_category.text_channels, name="matches")
            
            # Create the channel if it doesn't exist
            if not matches_channel:
                try:
                    matches_channel = await interaction.guild.create_text_channel(
                        "matches",
                        category=game_category
                    )
                except Exception as e:
                    await interaction.followup.send(
                        f"Could not create channel 'matches': {e}", ephemeral=True
                    )
                    return
            
            # Send message to matches channel with MatchStartView
            await matches_channel.send(
                content=start_game(team1, team2, self.game),
                view=MatchStartView(team1, team2, self.game, self.creator_id)
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
