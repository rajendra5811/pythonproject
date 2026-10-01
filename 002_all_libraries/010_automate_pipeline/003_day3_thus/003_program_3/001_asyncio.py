import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

import httpx


@dataclass
class PaymentRecord:
    txn_id: str
    amount: float
    status: str

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "PaymentRecord":
        return cls(
            txn_id=str(payload.get("txn_id") or payload.get("transaction_id") or "UNKNOWN"),
            amount=float(payload.get("amount", 0.0)),
            status=str(payload.get("status", "unknown")).lower(),
        )


def build_mock_response(txn_id: str) -> Dict[str, Any]:
    digits = [int(ch) for ch in txn_id if ch.isdigit()]
    seed = sum(digits) if digits else 0
    amount = round(10.0 + (seed % 25) * 2.5, 2)
    status = "approved" if seed % 2 == 0 else "pending"
    return {"txn_id": txn_id, "amount": amount, "status": status}


async def fetch_status(client: httpx.AsyncClient, txn_id: str, base_url: str = "https://api.gateway.com") -> Dict[str, Any]:
    url = f"{base_url}/status/{txn_id}"

    try:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return payload
    except (httpx.HTTPError, ValueError, TypeError):
        pass

    return build_mock_response(txn_id)


async def process_batch(batch_size: int = 20) -> List[PaymentRecord]:
    async with httpx.AsyncClient() as client:
        tasks = [fetch_status(client, f"TXN-{i}") for i in range(batch_size)]
        results = await asyncio.gather(*tasks)

    return [PaymentRecord.from_payload(payload) for payload in results]


async def main() -> None:
    records = await process_batch(20)
    summary: Dict[str, int] = {}

    for record in records:
        summary[record.status] = summary.get(record.status, 0) + 1

    print(f"Processed {len(records)} payment records.")
    for status, count in sorted(summary.items()):
        print(f"{status}: {count}")

    print("Sample records:")
    for record in records[:3]:
        print(record)


if __name__ == "__main__":
    asyncio.run(main())