# queue_state.py

def format_queue(queue):
    if not queue:
        return "**Queue is empty**"
    print(queue)
    return f"**Current Queue ({len(queue)}/4):**\n" + "\n".join(
        f"{i+1}. {user.mention}" for i, user in enumerate(queue)
    )
