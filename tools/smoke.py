"""Read-only deployment smoke checks using only the Python standard library."""
import argparse
import json
from urllib.error import HTTPError
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8735")
    args = parser.parse_args()
    origin = args.url.rstrip("/")
    for path in ("/", "/tracks/dsa.html", "/js/dsa-page.js", "/css/dsa.css", "/api/health", "/api/dsa/catalog"):
        with urlopen(origin + path, timeout=10) as response:
            assert response.status == 200, path
            body = response.read()
            assert body, path
            if path == "/api/health":
                health = json.loads(body)
                assert health["ok"], health
                print("Health:", json.dumps(health, sort_keys=True))
        print("OK", path)
    for path in ("/app.py", "/backend/app.py", "/.env", "/1991_academy.db", "/tools/database.py"):
        try:
            urlopen(origin + path, timeout=10).close()
        except HTTPError as error:
            assert error.code == 404, (path, error.code)
        else:
            raise AssertionError(f"Private file exposed: {path}")
    print("Deployment smoke checks passed")


if __name__ == "__main__":
    main()
