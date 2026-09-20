from typing import Any
import time
import requests

BASE_URL = "https://httpbin.org"

def fetch_get() -> Any:
    response = requests.get(f"{BASE_URL}/get")
    return response.json()

def fetch_post() -> Any:
    data_to_post = {"key": "value"}
    response = requests.post(f"{BASE_URL}/post", json = data_to_post)
    return response.json()

def fetch_put() -> Any:
    data_to_put = {"key": "updated_value"}
    response = requests.put(f"{BASE_URL}/put", json = data_to_put)
    return response.json()

def fetch_delete() -> Any:
    response = requests.delete(f"{BASE_URL}/delete")
    return response.json()  

def main() -> None:
    start_time = time.time()
    
    get_result = fetch_get()
    print("GET Result:", get_result)
    
    post_result = fetch_post()
    print("POST Result:", post_result)
    
    put_result = fetch_put()
    print("PUT Result:", put_result)
    
    delete_result = fetch_delete()
    print("DELETE Result:", delete_result)
    
    end_time = time.time()
    print(f"All HTTP requests completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()