# queue_state.py

queue = []

def format_queue():
    if not queue:
        return "**Queue is empty**"
    print(queue)
    return "**Current Queue:**\n" + "\n".join(
        f"{i+1}. {user.mention}" for i, user in enumerate(queue)
    )
