import discord
from discord.ext import commands
from queue_state import format_queue, start_game
from match_start_view import MatchStartView

class QueueView(discord.ui.View):
    def __init__(self, queue_size, game, creator_id):
        super().__init__(timeout=57600) # 16 hours timeout
        self.team1 = []
        self.team2 = []
        self.queue_size = queue_size
        self.game = game
        self.creator_id = creator_id

    @discord.ui.button(label="Team 1", style=discord.ButtonStyle.green)
    async def join1(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in self.team1:
            await interaction.response.send_message(
                "You are already in Team 1.", ephemeral=True
            )
            return
        
        if len(self.team1) >= self.queue_size // 2:
            await interaction.response.send_message(
                "Team 1 is already full", ephemeral=True
            )
            return
        
        if user in self.team2:
            self.team2.remove(user)

        self.team1.append(user)
        await interaction.response.edit_message(
            content=format_queue(self.team1, self.team2, self.queue_size, self.game),
            view=self
        )

    @discord.ui.button(label="Team 2", style=discord.ButtonStyle.blurple)
    async def join2(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in self.team2:
            await interaction.response.send_message(
                "You are already in Team 2.", ephemeral=True
            )
            return
        
        if len(self.team2) >= self.queue_size // 2:
            await interaction.response.send_message(
                "Team 2 is already full", ephemeral=True
            )
            return
        
        if user in self.team1:
            self.team1.remove(user)

        self.team2.append(user)
        await interaction.response.edit_message(
            content=format_queue(self.team1, self.team2, self.queue_size, self.game),
            view=self
        )

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.gray)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in self.team1:
            self.team1.remove(user)
        elif user in self.team2:
            self.team2.remove(user)
        else:
            await interaction.response.send_message(
                "You are not in any team.", ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content=format_queue(self.team1, self.team2, self.queue_size, self.game),
            view=self
        )

    @discord.ui.button(label="Start Match", style=discord.ButtonStyle.gray)
    async def start_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the queue creator can start the match.", ephemeral=True
            )
            return     
        # if len(self.team1) + len(self.team2) < self.queue_size:
        #     await interaction.response.send_message(
        #         "Not enough players to start the match.", ephemeral=True
        #     )
        #     return

        await interaction.response.edit_message(
            content=start_game(self.team1, self.team2, self.game),
            view=MatchStartView(self.team1, self.team2, self.game, self.creator_id)
        )

        self.stop()  # Stop QueueView since match has started
        
    @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.red)
    async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the queue creator can cancel the match.", ephemeral=True
            )
            return
        
        await interaction.response.edit_message(content="Match cancelled", view=None)
        self.stop()

