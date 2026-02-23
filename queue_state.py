# queue_state.py
dolphin = 135206021852299264

# game_channel_ids = {
#     "rocket": 1460835372824268945,
#     "mpt": 1458647024206614731
# }

# Game display name mapping (shortened code -> full name)
GAME_DISPLAY_NAMES = {
    "mpt": "Mario Power Tennis",
    "cod": "Call of Duty",
    "rainbow": "Rainbow Six Siege",
    "rocket": "Rocket League"
}

def get_display_name(game_code: str) -> str:
    """Convert game code to display name.
    
    Args:
        game_code: Shortened game code (e.g., "mpt", "cod")
    
    Returns:
        Full display name if mapping exists, otherwise uppercase code
    """
    return GAME_DISPLAY_NAMES.get(game_code.lower(), game_code.upper())

def format_queue(team1, team2, queue_size=0, game=""):
    # Format team1 (left side)
    team1_str = "**Team 1:**\n" + "\n".join(
        f"{i+1}. {user.mention}" for i, user in enumerate(team1)
    ) if team1 else "**Team 1:**"
    
    # Format team2 (right side)
    team2_str = "**Team 2:**\n" + "\n".join(
        f"{i+1}. {user.mention}" for i, user in enumerate(team2)
    ) if team2 else "**Team 2:**"
    
    return f"**Current Queue for** `{game.upper()}` **({len(team1) + len(team2)}/{queue_size}):**\n\n{team1_str}\n\n{team2_str}"

def format_perma_queue(queue, queue_size=0, game=""):
    """Format the permanent queue display"""
    queue_str = "\n".join(
        f"{i+1}. {user.mention}" for i, user in enumerate(queue)
    )
    
    separator = "─" * 40
    
    return f"{separator}\n**Queue for** `{game.upper()}` **({len(queue)}/{queue_size}):**\n\n{queue_str}\n{separator}"

def start_game(team1, team2, game):
    team1_mentions = ', '.join(user.mention for user in team1)
    team2_mentions = ', '.join(user.mention for user in team2)
    
    return (
        f"**Starting {game.upper()}!**\n\n"
        f"**Team 1:** {team1_mentions}\n"
        f"**Team 2:** {team2_mentions}\n\n"
    )
