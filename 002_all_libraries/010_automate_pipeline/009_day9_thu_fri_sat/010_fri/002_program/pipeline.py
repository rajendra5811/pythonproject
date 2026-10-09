import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


def load_movies():
    movies = read_json(BASE / "movies.json")

    movie_lookup = {}

    for movie in movies:
        movie_lookup[movie["movie_id"]] = movie

    return movie_lookup


def stream_events():
    events = read_json(BASE / "events.json")

    for event in events:
        yield event


def process_events(movies):

    summary = defaultdict(int)

    for event in stream_events():

        movie_id = event["movie_id"]

        if movie_id not in movies:
            continue

        summary[movie_id] += event["watch_minutes"]

    return summary


def main():

    # BATCH
    movies = load_movies()

    # STREAM
    summary = process_events(movies)

    # OUTPUT
    for movie_id, minutes in summary.items():

        movie = movies[movie_id]

        print(
            movie["title"],
            "→",
            movie["genre"],
            "→",
            minutes,
            "minutes"
        )


if __name__ == "__main__":
    main()