import argparse
import concurrent.futures
import time
import urllib.error
import urllib.request


def hit(url: str, timeout: float) -> int:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    end = time.time() + args.duration
    counts = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        while time.time() < end:
            futures = [pool.submit(hit, args.url, args.timeout) for _ in range(args.workers)]
            for future in futures:
                status = future.result()
                counts[status] = counts.get(status, 0) + 1
    print(counts)


if __name__ == "__main__":
    main()
