# queue_state.py

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
