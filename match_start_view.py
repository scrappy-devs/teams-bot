import discord
from discord.ext import commands
from queue_state import format_queue, start_game, dolphin

class MatchStartView(discord.ui.View):
    def __init__(self, team1, team2, game, creator_id):
        super().__init__(timeout=None)  # Permanent view (no timeout)
        self.team1 = team1
        self.team2 = team2
        self.game = game
        self.creator_id = creator_id
        self.team1_voted = False
        self.team2_voted = False
        self.team1_vote = None  # "Team 1" or "Team 2"
        self.team2_vote = None  # "Team 1" or "Team 2"

    async def declare_winner(self, interaction: discord.Interaction, winning_team: int):
        """Declare the winner and display the winning team members"""
        if winning_team == 1:
            team_mentions = ', '.join(user.mention for user in self.team1)
            content = f"**Team 1 wins!**\n\n**Winners:** {team_mentions}"
        else:
            team_mentions = ', '.join(user.mention for user in self.team2)
            content = f"**Team 2 wins!**\n\n**Winners:** {team_mentions}"
        
        await interaction.response.edit_message(
            content=content,
            view=None
        )
        self.stop()

    @discord.ui.button(label="Team 1", style=discord.ButtonStyle.green)
    async def team1_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # Check if user is in team1
        if user in self.team1:
            if self.team1_voted:
                await interaction.response.send_message(
                    "Your team has already voted.", ephemeral=True
                )
                return
            self.team1_voted = True
            self.team1_vote = "Team 1"
        # Check if user is in team2
        elif user in self.team2:
            if self.team2_voted:
                await interaction.response.send_message(
                    "Your team has already voted.", ephemeral=True
                )
                return
            self.team2_voted = True
            self.team2_vote = "Team 1"
        else:
            await interaction.response.send_message(
                "You are not in either team.", ephemeral=True
            )
            return
        
        # If dolphin voted, immediately declare winner
        if user.id == dolphin:
            await self.declare_winner(interaction, 1)
            return
        
        # Check if both teams have voted
        if self.team1_voted and self.team2_voted:
            # Determine winner
            team1_votes = (1 if self.team1_vote == "Team 1" else 0) + (1 if self.team2_vote == "Team 1" else 0)
            team2_votes = (1 if self.team1_vote == "Team 2" else 0) + (1 if self.team2_vote == "Team 2" else 0)
            
            if team1_votes > team2_votes:
                await self.declare_winner(interaction, 1)
            elif team2_votes > team1_votes:
                await self.declare_winner(interaction, 2)
            else:
                await interaction.response.defer()
                dolphin_member = interaction.guild.get_member(dolphin)
                dolphin_mention = dolphin_member.mention if dolphin_member else f"<@{dolphin}>"
                await interaction.channel.send(dolphin_mention + " **Disputed match, review required**")
        else:
            await interaction.response.send_message(
                "Vote recorded. Waiting for the other team to vote.", ephemeral=True
            )

    @discord.ui.button(label="Team 2", style=discord.ButtonStyle.blurple)
    async def team2_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # Check if user is in team1
        if user in self.team1:
            if self.team1_voted:
                await interaction.response.send_message(
                    "Your team has already voted.", ephemeral=True
                )
                return
            self.team1_voted = True
            self.team1_vote = "Team 2"
        # Check if user is in team2
        elif user in self.team2:
            if self.team2_voted:
                await interaction.response.send_message(
                    "Your team has already voted.", ephemeral=True
                )
                return
            self.team2_voted = True
            self.team2_vote = "Team 2"
        else:
            await interaction.response.send_message(
                "You are not in either team.", ephemeral=True
            )
            return
        
        # If dolphin voted, immediately declare winner
        if user.id == dolphin:
            await self.declare_winner(interaction, 2)
            return
        
        # Check if both teams have voted
        if self.team1_voted and self.team2_voted:
            # Determine winner
            team1_votes = (1 if self.team1_vote == "Team 1" else 0) + (1 if self.team2_vote == "Team 1" else 0)
            team2_votes = (1 if self.team1_vote == "Team 2" else 0) + (1 if self.team2_vote == "Team 2" else 0)
            
            if team1_votes > team2_votes:
                await self.declare_winner(interaction, 1)
            elif team2_votes > team1_votes:
                await self.declare_winner(interaction, 2)
            else:
                await interaction.response.defer()
                dolphin_member = interaction.guild.get_member(dolphin)
                dolphin_mention = dolphin_member.mention if dolphin_member else f"<@{dolphin}>"
                await interaction.channel.send(dolphin_mention + " **Disputed match, review required**")
        else:
            await interaction.response.send_message(
                "Vote recorded. Waiting for the other team to vote.", ephemeral=True
            )

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
        
