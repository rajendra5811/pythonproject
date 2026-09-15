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
        self.key_locks = {}
        self.key_locks_lock = threading.Lock()  # Lock to synchronize access to the cache

    def get_lock_for_key(self, key):
        """Get or create a lock for a specific key."""
        with self.key_locks_lock:
            if key not in self.key_locks:
                self.key_locks[key] = threading.Lock()
            return self.key_locks[key]
        
    def get_user_data(self, user_id):

        key_lock = self.get_lock_for_key(user_id)
        with key_lock:  
            if user_id in self.cache:
                print(f"{threading.current_thread().name} : CACHE HIT for user {user_id}.")
                return self.cache[user_id]
            print(f"{threading.current_thread().name} : CACHE MISS for user {user_id}")
            user = fetch_data_from_database(user_id)
            self.cache[user_id] = user
            return user