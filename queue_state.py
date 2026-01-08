# queue_state.py

queue = []
# When True the queue accepts new users. When False the queue is closed/full.
queue_open = True


def add_user(user, queue_size=None):
    """Attempt to add a user to the queue.

    Returns True if the user was added. Returns False if the queue is closed
    or the user is already in the queue.
    If adding the user fills the queue (len == queue_size) the queue will be
    closed automatically.
    """
    global queue, queue_open

    if not queue_open:
        return False

    # avoid duplicates
    if user in queue:
        return False

    queue.append(user)

    # Close the queue when it reaches the target size (if a size was provided)
    if queue_size is not None and len(queue) >= queue_size:
        queue_open = False

    return True


def remove_user(user):
    """Remove a user from the queue.

    Returns True if the user was removed, False if the user wasn't in the queue.
    """
    global queue
    if user not in queue:
        return False
    queue.remove(user)
    return True


def close_queue():
    """Explicitly close the queue so it stops accepting new users."""
    global queue_open
    queue_open = False


def open_queue():
    """Open the queue to accept new users. This does not clear existing users."""
    global queue_open
    queue_open = True


def is_closed():
    """Return True if the queue is closed (not accepting new users)."""
    return not queue_open


def format_queue(game, queue_size=None):
    """Return a human-friendly representation of the queue.

    `queue_size` is optional; when provided it will be displayed alongside
    the current length and used to show whether the queue is full.
    """
    if not queue:
        return "**Queue is empty**"

    header = f"**Current Queue for `{game}`** ({len(queue)}"
    if queue_size is not None:
        header += f"/{queue_size}"
    header += ")"

    status = "\n**Status:** Closed" if is_closed() else "\n**Status:** Open"

    members = "\n".join(f"{i+1}. {user.mention}" for i, user in enumerate(queue))

    return header + status + "\n" + members
