import httpx


def fetch_data(url):

    try:

        response = httpx.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPError as error:

        print(f"Request failed: {url}")
        print(f"Error: {error}")

        return None