import discord
from discord.ext import commands
from queue_state import format_queue, start_game

class MatchStartView(discord.ui.View):
    def __init__(self, team1, team2, game, creator_id):
        super().__init__(timeout=None)
        self.team1 = team1
        self.team2 = team2
        self.game = game
        self.creator_id = creator_id

    @discord.ui.button(label="Team 1", style=discord.ButtonStyle.green)
    async def team1_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the queue creator can pick the winner.", ephemeral=True
            )
            return
        await interaction.response.edit_message(content="Team 1 wins!", view=None)
        self.stop()

    @discord.ui.button(label="Team 2", style=discord.ButtonStyle.blurple)
    async def team2_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the queue creator can pick the winner.", ephemeral=True
            )
            return
        await interaction.response.edit_message(content="Team 2 wins!", view=None)
        self.stop()

    @discord.ui.button(label="CANCEL ", style=discord.ButtonStyle.red)
    async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the queue creator can cancel the match.", ephemeral=True
            )
            return
        await interaction.response.edit_message(content="Match cancelled", view=None)
        self.stop()
    # @discord.ui.button(label="Team 2", style=discord.ButtonStyle.blurple)
    # async def team2_win(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     user = interaction.user

    #     if user in self.team2:
    #         await interaction.response.send_message(
    #             "You are already in Team 2.", ephemeral=True
    #         )
    #         return
        
    #     if len(self.team2) >= self.queue_size // 2:
    #         await interaction.response.send_message(
    #             "Team 2 is already full", ephemeral=True
    #         )
    #         return
        
    #     if user in self.team1:
    #         self.team1.remove(user)

    #     self.team2.append(user)
    #     await interaction.response.edit_message(
    #         content=format_queue(self.team1, self.team2, self.queue_size),
    #         view=self
    #     )

    # @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
    # async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     user = interaction.user

    #     if user in self.team1:
    #         self.team1.remove(user)
    #     elif user in self.team2:
    #         self.team2.remove(user)
    #     else:
    #         await interaction.response.send_message(
    #             "You are not in any team.", ephemeral=True
    #         )
    #         return

    #     await interaction.response.edit_message(
    #         content=format_queue(self.team1, self.team2, self.queue_size),
    #         view=self
    #     )

    # @discord.ui.button(label="Start Match", style=discord.ButtonStyle.gray)
    # async def start_match(self, interaction: discord.Interaction, button: discord.ui.Button):     
    #     # if len(self.team1) + len(self.team2) < self.queue_size:
    #     #     await interaction.response.send_message(
    #     #         "Not enough players to start the match.", ephemeral=True
    #     #     )
    #     #     return

    #     await interaction.response.edit_message(
    #         content=start_game(self.team1, self.team2, self.game),
    #         view=self
    #     )

