from fastapi import FastAPI
import time
import requests
import asyncio
import os
import httpx

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
    return {
        "method": "blocking",
        "duration": round(end_time - start_time, 2),
        "message": "Downloaded 5 images.",
    }


@app.get("/non_blocking")
async def download_images_non_blocking():
    start_time = time.time()

    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Get list of images (async)
        resp = await client.get("https://picsum.photos/v2/list?limit=5")
        resp.raise_for_status()
        images = resp.json()

        async def download_image(i: int, image_url: str):
            img_resp = await client.get(image_url)
            img_resp.raise_for_status()
            with open(f"{IMAGES_DIR}/non_blocking_image_{i}.jpg", "wb") as f:
                f.write(img_resp.content)

        tasks = [
            download_image(i, image["download_url"])
            for i, image in enumerate(images)
        ]
        await asyncio.gather(*tasks)

    end_time = time.time()
    return {
        "method": "non_blocking",
        "duration": round(end_time - start_time, 2),
        "message": "Downloaded 5 images.",
    }