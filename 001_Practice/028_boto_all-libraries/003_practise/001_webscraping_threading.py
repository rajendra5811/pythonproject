import threading
import requests
import time

def fetch_url(url):
    response = requests.get(url)
    print(f"Fetched{url}: {len(response.content)} bytes")

def run_fetch_url():
    urls = ["https://bostondynamics.com", "https://www.python.org", "https://www.github.com"]
    start_time = time.time()
    threads = []
    for url in urls:
        thread = threading.Thread(target=fetch_url, args=(url,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    run_fetch_url()
    