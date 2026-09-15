import threading
import time


def fetch_data_from_database(user_id):
    """Simulate fetching data from a database."""
    print(f"Fetching data for user {user_id}...")
    time.sleep(2)  # Simulate a delay in fetching data
    print(f"Data fetched for user {user_id}.")
    return f"Data for user {user_id}"


class UserCache:
    """A simple cache to store user data."""

    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()  # Lock to synchronize access to the cache

    def get_user_data(self, user_id):
        with self.lock:  # Ensure only one thread accesses the cache at a time
            if user_id in self.cache:
                print(f"Cache hit for user {user_id}.")
                return self.cache[user_id]
            else:
                print(f"Cache miss for user {user_id}. Fetching from database...")
                # Release lock before DB call to avoid blocking other readers
                # (optional design choice; shown here as an alternative pattern)
        
        # If cache miss, fetch outside the lock so other threads aren't blocked
        if user_id not in self.cache:
            # Re-check after possibly waiting; another thread may have populated it
            with self.lock:
                if user_id in self.cache:
                    print(f"Cache hit for user {user_id} (after wait).")
                    return self.cache[user_id]

        user = fetch_data_from_database(user_id)
        with self.lock:
            self.cache[user_id] = user
        return user