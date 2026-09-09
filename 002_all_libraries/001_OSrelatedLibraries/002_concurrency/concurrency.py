import asyncio
import httpx
from multiprocessing import Pool, cpu_count
from typing import List, Dict, Any

class ConcurrentDataIngestionEngine:
    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints
        self.max_workers = cpu_count()

    async def _fetch_single_endpoint(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """Asynchronously fetch a single endpoint using httpx (I/O bound)."""
        try:
            print(f"Fetching async: {url}")
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return {"url": url, "status": response.status_code, "data": response.json()}
        except httpx.HTTPError as e:
            print(f"Failed to fetch {url}: {e}")
            return {"url": url, "status": 500, "data": {}}

    async def fetch_all_async(self) -> List[Dict[str, Any]]:
        """Concurrently fire all HTTP requests via asyncio event loop."""
        async with httpx.AsyncClient() as client:
            tasks = [self._fetch_single_endpoint(client, url) for url in self.endpoints]
            # asyncio.gather fires them concurrently
            results = await asyncio.gather(*tasks)
            return results

    @staticmethod
    def _cpu_heavy_transform(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate heavy CPU parsing/transformation for multiprocessing."""
        data = payload.get("data", {})
        # Imagine heavy normalization, regex parsing, or heavy numeric loops here
        payload["processed_records_count"] = len(str(data)) * 2 
        return payload

    def run_pipeline(self) -> List[Dict[str, Any]]:
        """Orchestrate async network extraction followed by multiprocessing CPU transformation."""
        print(f"Starting async extraction across {len(self.endpoints)} endpoints...")
        
        # 1. Run asyncio event loop for I/O bound extraction
        raw_payloads = asyncio.run(self.fetch_all_async())
        
        print(f"Passing payloads to multiprocessing pool (Workers: {self.max_workers})...")
        
        # 2. Run multiprocessing Pool for CPU-bound transformations
        with Pool(processes=self.max_workers) as pool:
            processed_results = pool.map(self._cpu_heavy_transform, raw_payloads)
            
        return processed_results

# Example execution simulation
if __name__ == "__main__":
    sample_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
        "https://httpbin.org/user-agent"
    ]
    engine = ConcurrentDataIngestionEngine(sample_urls)
    results = engine.run_pipeline()
    print(results)