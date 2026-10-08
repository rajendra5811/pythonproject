import asyncio
import json
import logging
import math
import os
import re
import sys

from collections import Counter, defaultdict
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import Any

import httpx


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

SOURCE_DIR = BASE_DIR / "stream_data"
OUTPUT_DIR = BASE_DIR / "output"

EVENT_OUTPUT = OUTPUT_DIR / "clean_events.json"
CREATOR_OUTPUT = OUTPUT_DIR / "creator_summary.json"
HASHTAG_OUTPUT = OUTPUT_DIR / "hashtag_summary.json"
QUALITY_OUTPUT = OUTPUT_DIR / "quality_report.json"
LOG_FILE = OUTPUT_DIR / "pipeline.log"


# ============================================================
# LOGGING
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# VALIDATION
# ============================================================

def validate_event(
    event: dict[str, Any]
) -> bool:

    required_fields = [
        "event_id",
        "video_id",
        "creator",
        "event_type",
        "views",
        "likes",
        "shares",
        "hashtags",
        "country",
        "timestamp"
    ]

    for field in required_fields:

        if field not in event:
            return False

        if event[field] is None:
            return False

    numeric_fields = [
        "views",
        "likes",
        "shares"
    ]

    for field in numeric_fields:

        if not isinstance(
            event[field],
            (int, float)
        ):
            return False

        if event[field] < 0:
            return False

    valid_events = {
        "view",
        "like",
        "share",
        "comment"
    }

    if event["event_type"].lower() not in valid_events:
        return False

    timestamp_pattern = (
        r"^\d{4}-\d{2}-\d{2} "
        r"\d{2}:\d{2}:\d{2}$"
    )

    if not re.match(
        timestamp_pattern,
        event["timestamp"]
    ):
        return False

    if not isinstance(
        event["hashtags"],
        list
    ):
        return False

    return True


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_event(
    event: dict[str, Any]
) -> dict[str, Any]:

    event["creator"] = re.sub(
        r"\s+",
        " ",
        event["creator"].strip()
    ).title()

    event["country"] = (
        event["country"]
        .strip()
        .upper()
    )

    event["event_type"] = (
        event["event_type"]
        .strip()
        .lower()
    )

    cleaned_hashtags = []

    for tag in event["hashtags"]:

        tag = tag.strip().lower()

        tag = tag.lstrip("#")

        if tag:
            cleaned_hashtags.append(tag)

    event["hashtags"] = cleaned_hashtags

    timestamp = datetime.strptime(
        event["timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

    event["timestamp"] = timestamp.isoformat()

    # Engagement score
    event["engagement_score"] = round(
        (
            event["likes"] * 1
            + event["shares"] * 3
            + event["views"] * 0.1
        ),
        2
    )

    # Log-scaled popularity
    event["popularity_score"] = round(
        math.log1p(
            event["views"]
        ),
        2
    )

    return event


# ============================================================
# DISCOVER STREAM FILES
# ============================================================

def discover_files(
    source_dir: Path
) -> list[Path]:

    files = list(
        source_dir.glob("*.json")
    )

    logger.info(
        "Discovered %s stream files",
        len(files)
    )

    return files


# ============================================================
# READ EVENT FILE
# ============================================================

def read_events(
    file_path: Path
) -> list[dict[str, Any]]:

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# PROCESS STREAM
# ============================================================

def process_stream(
    files: list[Path]
) -> tuple[
    list[dict[str, Any]],
    int
]:

    clean_events = []

    rejected_events = 0

    for file_path in files:

        try:

            events = read_events(
                file_path
            )

            for event in events:

                if not validate_event(event):

                    rejected_events += 1

                    logger.warning(
                        "Rejected event from %s",
                        file_path.name
                    )

                    continue

                event = transform_event(
                    event
                )

                clean_events.append(
                    event
                )

        except Exception as error:

            logger.exception(
                "Failed stream file %s: %s",
                file_path.name,
                error
            )

    return (
        clean_events,
        rejected_events
    )


# ============================================================
# EXTERNAL COUNTRY ENRICHMENT
# ============================================================

async def fetch_country(
    client: httpx.AsyncClient,
    country: str
) -> dict[str, Any]:

    url = (
        "https://restcountries.com/v3.1/alpha/"
        f"{country}"
    )

    try:

        response = await client.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        country_data = data[0]

        return {
            "country_name":
                country_data
                .get("name", {})
                .get(
                    "common",
                    "Unknown"
                ),

            "region":
                country_data.get(
                    "region",
                    "Unknown"
                )
        }

    except Exception as error:

        logger.warning(
            "Country enrichment failed: %s",
            error
        )

        return {
            "country_name": "Unknown",
            "region": "Unknown"
        }


# ============================================================
# ASYNC ENRICHMENT
# ============================================================

async def enrich_events(
    events: list[dict[str, Any]]
) -> list[dict[str, Any]]:

    countries = {
        event["country"]
        for event in events
    }

    async with httpx.AsyncClient() as client:

        tasks = [
            fetch_country(
                client,
                country
            )
            for country in countries
        ]

        results = await asyncio.gather(
            *tasks
        )

    country_lookup = dict(
        zip(
            countries,
            results
        )
    )

    for event in events:

        event.update(
            country_lookup[
                event["country"]
            ]
        )

    return events


# ============================================================
# CREATOR ANALYTICS
# ============================================================

def creator_summary(
    events: list[dict[str, Any]]
) -> dict[str, Any]:

    creators = defaultdict(list)

    for event in events:

        creators[
            event["creator"]
        ].append(event)

    summary = {}

    for creator, items in creators.items():

        total_views = reduce(
            lambda x, y: x + y,
            (
                item["views"]
                for item in items
            ),
            0
        )

        total_likes = sum(
            item["likes"]
            for item in items
        )

        total_shares = sum(
            item["shares"]
            for item in items
        )

        summary[creator] = {
            "events": len(items),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_shares": total_shares
        }

    return summary


# ============================================================
# HASHTAG ANALYTICS
# ============================================================

def hashtag_summary(
    events: list[dict[str, Any]]
) -> dict[str, int]:

    counter = Counter()

    for event in events:

        for hashtag in event["hashtags"]:

            counter[hashtag] += 1

    return dict(counter)


# ============================================================
# EVENT TYPE ANALYTICS
# ============================================================

def event_type_summary(
    events: list[dict[str, Any]]
) -> dict[str, int]:

    counter = Counter()

    for event in events:

        counter[
            event["event_type"]
        ] += 1

    return dict(counter)


# ============================================================
# QUALITY REPORT
# ============================================================

def quality_report(
    total_input: int,
    clean_count: int,
    rejected_count: int
) -> dict[str, Any]:

    rejection_rate = 0

    if total_input:

        rejection_rate = (
            rejected_count
            / total_input
        ) * 100

    return {
        "total_input_events": total_input,
        "clean_events": clean_count,
        "rejected_events": rejected_count,
        "rejection_rate": round(
            rejection_rate,
            2
        )
    }


# ============================================================
# WRITE JSON
# ============================================================

def write_json(
    data: Any,
    output_file: Path
) -> None:

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline() -> None:

    logger.info(
        "TIKTOK STREAMING PIPELINE STARTED"
    )

    logger.info(
        "Operating system: %s",
        os.name
    )

    logger.info(
        "Python version: %s",
        sys.version
    )

    try:

        # ----------------------------------------------------
        # 1. DISCOVER
        # ----------------------------------------------------

        files = discover_files(
            SOURCE_DIR
        )

        # ----------------------------------------------------
        # 2. COUNT INPUT
        # ----------------------------------------------------

        total_input = 0

        for file_path in files:

            events = read_events(
                file_path
            )

            total_input += len(events)

        # ----------------------------------------------------
        # 3. VALIDATE + TRANSFORM
        # ----------------------------------------------------

        clean_events, rejected_events = (
            process_stream(files)
        )

        # ----------------------------------------------------
        # 4. EXTERNAL ENRICHMENT
        # ----------------------------------------------------

        clean_events = asyncio.run(
            enrich_events(
                clean_events
            )
        )

        # ----------------------------------------------------
        # 5. ANALYTICS
        # ----------------------------------------------------

        creators = creator_summary(
            clean_events
        )

        hashtags = hashtag_summary(
            clean_events
        )

        event_types = event_type_summary(
            clean_events
        )

        quality = quality_report(
            total_input,
            len(clean_events),
            rejected_events
        )

        # ----------------------------------------------------
        # 6. SINK
        # ----------------------------------------------------

        write_json(
            clean_events,
            EVENT_OUTPUT
        )

        write_json(
            creators,
            CREATOR_OUTPUT
        )

        write_json(
            {
                "hashtags": hashtags,
                "event_types": event_types
            },
            HASHTAG_OUTPUT
        )

        write_json(
            quality,
            QUALITY_OUTPUT
        )

        # ----------------------------------------------------
        # 7. MONITORING
        # ----------------------------------------------------

        logger.info(
            "Input events: %s",
            total_input
        )

        logger.info(
            "Clean events: %s",
            len(clean_events)
        )

        logger.info(
            "Rejected events: %s",
            rejected_events
        )

        logger.info(
            "TIKTOK STREAMING PIPELINE COMPLETED"
        )

    except Exception as error:

        logger.exception(
            "TIKTOK PIPELINE FAILED: %s",
            error
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_pipeline()