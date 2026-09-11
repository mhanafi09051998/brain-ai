---
name: python-high-throughput
description: High-precision engineering reference for high-throughput, low-latency Python systems. Covers asyncio event loop optimization with uvloop, zero-copy buffers (memoryview), multiprocessing shared memory, Cython/PyO3 acceleration, and production memory profiling.
---

# Python High-Throughput & Low-Latency Systems Engineering

High-precision reference for building high-concurrency, low-latency applications in modern Python (3.12+). Covers event loop acceleration, memory-efficient data pipelines, zero-copy socket processing, and C/Rust extension boundaries.

---

## 1. Asyncio Event Loop & Concurrency Invariants

### A. Event Loop Acceleration with `uvloop`
Replace the standard Python asyncio event loop with libuv-based `uvloop` for 2–4x throughput improvements:

```python
import asyncio
import sys

def enable_uvloop():
    if sys.platform != "win32":
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

### B. Structured Concurrency with `asyncio.TaskGroup` (Python 3.11+)
```python
async def fetch_all_feeds(endpoints: list[str]) -> list[dict]:
    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_single(ep)) for ep in endpoints]
    # All tasks are guaranteed complete or cleanly cancelled if one fails
    return [t.result() for t in tasks]
```

---

## 2. Zero-Copy & Memory Footprint Optimization

### A. Memory Savings with `__slots__`
Eliminate `__dict__` overhead in high-frequency objects (reduces memory consumption by ~60%):

```python
class MarketTick:
    __slots__ = ("symbol", "price", "volume", "timestamp_ns")
    def __init__(self, symbol: str, price: float, volume: float, timestamp_ns: int):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.timestamp_ns = timestamp_ns
```

### B. Buffer Protocol & `memoryview` for Zero-Copy Slicing
```python
def process_binary_payload(raw_bytes: bytes):
    # Zero-copy slicing: creates a view without memory duplication
    view = memoryview(raw_bytes)
    header = view[:16]
    payload = view[16:]
    return header, payload
```

---

## 3. High-Performance Data Engines

* **Columnar Processing**: Prefer Polars over Pandas for multi-threaded, memory-mapped query execution written in Rust.
* **C/Rust Extension Bridge**: Offload CPU-bound tight loops to PyO3 (Rust) or Cython rather than pure Python loops.
