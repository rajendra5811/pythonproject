import json
import logging
from collections import Counter, defaultdict
from pathlib import Path


# -----------------------------
# CONFIG
# -----------------------------

BASE_DIR = Path(__file__).parent

SOURCE = BASE_DIR / "data" / "events.json"
OUTPUT = BASE_DIR / "output" / "summary.json"


# -----------------------------
# LOGGING
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------
# READ
# -----------------------------

def read_events():

    with SOURCE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# -----------------------------
# VALIDATE + CLEAN
# -----------------------------

def process_events(events):

    clean_events = []

    for event in events:

        if event["views"] < 0:

            logger.warning(
                "Invalid views: %s",
                event["video"]
            )

            continue

        event["user"] = (
            event["user"]
            .strip()
            .title()
        )

        event["hashtags"] = [
            tag.lower().replace("#", "")
            for tag in event["hashtags"]
        ]

        clean_events.append(event)

    return clean_events


# -----------------------------
# ANALYTICS
# -----------------------------

def summarize(events):

    users = defaultdict(int)
    hashtags = Counter()

    total_views = 0

    for event in events:

        users[event["user"]] += event["views"]

        total_views += event["views"]

        hashtags.update(
            event["hashtags"]
        )

    return {
        "total_views": total_views,
        "views_by_user": dict(users),
        "top_hashtags": dict(hashtags)
    }


# -----------------------------
# WRITE
# -----------------------------

def write_output(data):

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# -----------------------------
# PIPELINE
# -----------------------------

def run_pipeline():

    logger.info(
        "TikTok pipeline started"
    )

    events = read_events()

    clean_events = process_events(
        events
    )

    summary = summarize(
        clean_events
    )

    write_output(
        summary
    )

    logger.info(
        "TikTok pipeline completed"
    )


if __name__ == "__main__":

    run_pipeline()