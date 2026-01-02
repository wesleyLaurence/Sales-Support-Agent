from __future__ import annotations

import json
from pathlib import Path

from shared.qdrant_tools import seed_products

DATA_PATH = Path(__file__).resolve().parents[1] / "shared" / "data" / "products.json"


def main() -> None:
    products = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    result = seed_products(products)
    print(result)


if __name__ == "__main__":
    main()
