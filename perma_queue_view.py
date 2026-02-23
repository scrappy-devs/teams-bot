import discord
from discord.ext import commands
from discord.utils import get
from queue_state import format_queue, format_perma_queue, start_game
from match_start_view import MatchStartView
from database import get_users_stats_for_matchmaking

class PermaQueueView(discord.ui.View):
    def __init__(self, queue_size=0, game="", creator_id=None):
        super().__init__(timeout=None)  # Permanent view (no timeout)
        self.queue = []  # General queue list
        self.queue_size = queue_size
        self.game = game
        self.creator_id = creator_id

    async def balance_teams(self, users):
        """Balance teams based on wins/losses using a simple matchmaking algorithm.
        
        Args:
            users: List of Discord user objects
        
        Returns:
            Tuple of (team1, team2) lists
        """
        # Get stats for all users
        user_stats = await get_users_stats_for_matchmaking(users, self.game)
        
        # Calculate skill rating (win rate) for each user
        # Win rate = wins / (wins + losses), default to 0.5 if no games played
        players_with_rating = []
        for user, wins, losses in user_stats:
            total_games = wins + losses
            if total_games > 0:
                win_rate = wins / total_games
            else:
                win_rate = 0.5  # Default to 50% for new players
            players_with_rating.append((user, win_rate, wins, losses))
        
        # Sort by skill rating (highest first)
        players_with_rating.sort(key=lambda x: x[1], reverse=True)
        
        # Greedy algorithm: ensure equal team sizes first, then balance skill
        team1 = []
        team2 = []
        team1_total_skill = 0.0
        team2_total_skill = 0.0
        target_team_size = len(players_with_rating) // 2
        
        for user, win_rate, wins, losses in players_with_rating:
            # First priority: ensure teams are equal in size
            if len(team1) < len(team2):
                team1.append(user)
                team1_total_skill += win_rate
            elif len(team2) < len(team1):
                team2.append(user)
                team2_total_skill += win_rate
            # If teams are equal in size, assign to team with lower total skill
            elif team1_total_skill <= team2_total_skill:
                team1.append(user)
                team1_total_skill += win_rate
            else:
                team2.append(user)
                team2_total_skill += win_rate
        
        return team1, team2


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
            # Balance teams using matchmaking algorithm
            team1, team2 = await self.balance_teams(self.queue.copy())
            
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
