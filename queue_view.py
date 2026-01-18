import discord
from discord.ext import commands
from queue_state import format_queue

class QueueView(discord.ui.View):
    def __init__(self, queue_size, game):
        super().__init__(timeout=None)
        self.team1 = []
        self.team2 = []
        self.queue_size = queue_size
        self.game = game

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
            content=format_queue(self.team1, self.team2, self.queue_size),
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
            content=format_queue(self.team1, self.team2, self.queue_size),
            view=self
        )

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
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
            content=format_queue(self.team1, self.team2, self.queue_size),
            view=self
        )