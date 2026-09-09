import logging
import itertools
from functools import lru_cache
from collections import defaultdict, Counter
from typing import List, Dict, Any, Generator, TypedDict

# Configure structured production logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class PipelineRecord(TypedDict):
    category: str
    value: float
    status: str

class StreamingPipelineAuditor:
    def __init__(self, raw_stream: List[Dict[str, Any]], batch_size: int = 1000):
        self.raw_stream = raw_stream
        self.batch_size = batch_size
        self.status_counter = Counter()

    @lru_cache(maxsize=128)
    def _fetch_reference_multiplier(self, category: str) -> float:
        """Simulate an expensive dimension table lookup cached via functools."""
        logger.info(f"Cache miss: Fetching lookup weight for category '{category}'")
        weights = {"A": 1.2, "B": 1.5, "C": 2.0}
        return weights.get(category, 1.0)

    def _stream_batches(self) -> Generator[List[Dict[str, Any]], None, None]:
        """Memory-efficient generator using itertools.islice to stream batches."""
        iterator = iter(self.raw_stream)
        while True:
            # islice slices the iterator without loading all records into RAM arrays
            batch = list(itertools.islice(iterator, self.batch_size))
            if not batch:
                break
            yield batch

    def process_and_aggregate(self) -> Dict[str, float]:
        """Process streaming batches with collections.defaultdict and track metrics."""
        logger.info("Starting streaming batch aggregation pipeline...")
        
        # defaultdict eliminates KeyError when initializing new category sums
        category_totals = defaultdict(float)

        try:
            for batch_idx, batch in enumerate(self._stream_batches()):
                logger.info(f"Processing batch #{batch_idx + 1} (Size: {len(batch)})")
                
                for record in batch:
                    cat = record.get("category", "UNKNOWN")
                    val = record.get("value", 0.0)
                    status = record.get("status", "SUCCESS")
                    
                    # Track status frequencies using collections.Counter
                    self.status_counter[status] += 1
                    
                    # Apply cached reference multiplier
                    multiplier = self._fetch_reference_multiplier(cat)
                    category_totals[cat] += val * multiplier

            logger.info(f"Aggregation complete. Status breakdown: {dict(self.status_counter)}")
            return dict(category_totals)

        except Exception as e:
            # Capture full traceback using logging.exception
            logger.exception("Pipeline failed during batch aggregation stream!")
            raise e

# Example execution simulation
if __name__ == "__main__":
    sample_data: List[PipelineRecord] = [
        {"category": "A", "value": 10.0, "status": "SUCCESS"},
        {"category": "B", "value": 25.5, "status": "SUCCESS"},
        {"category": "A", "value": 5.0, "status": "FAILED"},
        {"category": "C", "value": 40.0, "status": "SUCCESS"},
    ]
    
    auditor = StreamingPipelineAuditor(sample_data, batch_size=2)
    results = auditor.process_and_aggregate()
    print("Aggregated Totals:", results)