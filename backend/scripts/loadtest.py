"""
Concurrency & Load Testing Benchmark Suite
Simulates concurrent mobile label scans against the FastAPI server.
Measures throughput (requests/sec), p50, and p95 latency percentiles across concurrency tiers.
Ported and adapted from Smart-Ingredient-Analyzer.
"""

import sys
import time
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

def percentile(values: List[float], fraction: float) -> Optional[float]:
    if not values:
        return None
    sorted_vals = sorted(values)
    idx = min(len(sorted_vals) - 1, int(len(sorted_vals) * fraction))
    return sorted_vals[idx]

def send_request(url: str, payload: dict) -> Dict[str, Any]:
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"}
    )
    start = time.time()
    status = 500
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read()
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as ex:
        status = 0
    duration_ms = (time.time() - start) * 1000
    return {"status": status, "latency_ms": duration_ms}

def run_load_test(
    url: str = "http://127.0.0.1:8000/analyze",
    concurrency_levels: List[int] = [1, 2, 4],
    requests_per_level: int = 4
):
    print("=" * 75)
    print("      LABELX MULTI-USER CONCURRENCY & LATENCY BENCHMARK SUITE")
    print("=" * 75)
    print(f"Target URL: {url}")
    print(f"Concurrency tiers: {concurrency_levels} | Requests per level: {requests_per_level}")

    # Check server availability first
    try:
        health_req = urllib.request.Request("http://127.0.0.1:8000/health")
        with urllib.request.urlopen(health_req, timeout=2) as resp:
            if resp.status != 200:
                print("Notice: Health check returned non-200. Is the server running?")
    except Exception:
        print("Note: Local server is not currently running on :8000. Running in simulated benchmark mode.")

    print("\n" + "-" * 75)
    print(f"{'Concurrency':<12} | {'Reqs':<6} | {'Throughput':<14} | {'p50 Latency':<14} | {'p95 Latency':<12} | {'Success Rate'}")
    print("-" * 75)

    sample_ingredients = [
        ["Aqua", "Glycerin", "Niacinamide"],
        ["Salicylic Acid", "Ceramide NP", "Centella Asiatica"],
        ["Retinol", "Tocopherol", "Hyaluronic Acid"],
        ["Titanium Dioxide", "Zinc Oxide", "Phenoxyethanol"]
    ]

    for concurrency in concurrency_levels:
        latencies = []
        success_count = 0
        total_requests = requests_per_level * concurrency
        t_start = time.time()

        tasks = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            for i in range(total_requests):
                payload = {
                    "message": f"Benchmark Scan {i}",
                    "ingredients": sample_ingredients[i % len(sample_ingredients)],
                    "skin_type": "sensitive",
                    "expertise_level": "intermediate"
                }
                tasks.append(executor.submit(send_request, url, payload))

            for future in as_completed(tasks):
                res = future.result()
                latencies.append(res["latency_ms"])
                if res["status"] in (200, 201):
                    success_count += 1

        elapsed = time.time() - t_start
        throughput = round(total_requests / elapsed, 2) if elapsed > 0 else 0
        p50 = round(percentile(latencies, 0.50), 1) if latencies else 0
        p95 = round(percentile(latencies, 0.95), 1) if latencies else 0
        success_pct = round((success_count / total_requests) * 100, 1) if total_requests else 0

        print(f"{concurrency:<12} | {total_requests:<6} | {throughput} req/s{'':<6} | {p50} ms{'':<8} | {p95} ms{'':<6} | {success_pct}%")

    print("=" * 75)

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/analyze"
    run_load_test(url=url_arg)
