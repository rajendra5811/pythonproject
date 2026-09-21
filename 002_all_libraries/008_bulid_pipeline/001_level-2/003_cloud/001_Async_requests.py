from fastapi import FastAPI
import time
import requests
import asyncio
import os

app = FastAPI()

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

@app.get("/blocking")
def download_images_blocking():
    start_time = time.time()
    response = requests.get("https://picsum.photos/v2/list?limit=5")
    response.raise_for_status()
    images = response.json()
    for i, image in enumerate(images):
        image_url = image["download_url"]
        img_data = requests.get(image_url).content
        with open(f"{IMAGES_DIR}/blocking_image_{i}.jpg", "wb") as f:
            f.write(img_data)
    end_time = time.time()
    return { "method": "blocking", "duration": round(end_time - start_time, 2), "message": "Downloaded 5 images." }

@app.get("/non_blocking")
async def download_images_non_blocking():
    start_time = time.time()
    response = await asyncio.to_thread(requests.get, "https://picsum.photos/v2/list?limit=5")
    response.raise_for_status()
    images = response.json()
    
    async def download_image(i, image_url):
        img_data = await asyncio.to_thread(requests.get, image_url)
        with open(f"{IMAGES_DIR}/non_blocking_image_{i}.jpg", "wb") as f:
            f.write(img_data.content)

    tasks = [download_image(i, image["download_url"]) for i, image in enumerate(images)]
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    return { "method": "non_blocking", "duration": round(end_time - start_time, 2), "message": "Downloaded 5 images." }