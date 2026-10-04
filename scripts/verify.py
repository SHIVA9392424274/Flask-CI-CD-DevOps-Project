"""Deployment verification: poll a URL until it returns HTTP 200 or time runs out.

Usage: python scripts/verify.py http://localhost:5000/health [retries] [delay_seconds]
Exit code 0 = healthy, 1 = failed.
"""
import sys
import time
import urllib.request


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/health"
    retries = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 3

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    print(f"[OK] {url} responded 200 (attempt {attempt})")
                    return 0
        except Exception as exc:
            print(f"[WAIT] attempt {attempt}/{retries}: {exc}")
        time.sleep(delay)

    print(f"[FAIL] {url} did not become healthy")
    return 1


if __name__ == "__main__":
    sys.exit(main())
