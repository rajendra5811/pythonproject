import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


# -------------------------
# BATCH
# -------------------------

def load_posts():

    posts = read_json(BASE / "posts.json")

    lookup = {}

    for post in posts:
        lookup[post["post_id"]] = post

    return lookup


# -------------------------
# STREAM
# -------------------------

def stream_events():

    events = read_json(BASE / "events.json")

    for event in events:
        yield event


# -------------------------
# PROCESS
# -------------------------

def process_events(posts):

    analytics = defaultdict(lambda: {
        "likes": 0,
        "comments": 0,
        "shares": 0
    })

    for event in stream_events():

        post_id = event["post_id"]

        # Reject unknown post
        if post_id not in posts:
            continue

        event_type = event["event"]

        if event_type == "like":
            analytics[post_id]["likes"] += 1

        elif event_type == "comment":
            analytics[post_id]["comments"] += 1

        elif event_type == "share":
            analytics[post_id]["shares"] += 1

    return analytics


# -------------------------
# REPORT
# -------------------------

def print_report(posts, analytics):

    for post_id, data in analytics.items():

        post = posts[post_id]

        print(
            post["creator"],
            "|",
            post["category"],
            "|",
            data
        )


# -------------------------
# PIPELINE
# -------------------------

def main():

    posts = load_posts()

    analytics = process_events(posts)

    print_report(posts, analytics)


if __name__ == "__main__":
    main()