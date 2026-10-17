# Builds data\prices.txt, the price list compiled into Lootline.dll (the DLL itself never goes online).
#
# 1. Open these two pages in your browser and save each one as a file (Ctrl+S):
#      https://csfloat.com/api/v1/listings/price-list          -> csfloat.json
#      https://market.csgo.com/api/v2/prices/USD.json          -> marketcsgo.json   (optional)
# 2. python tools\make_prices.py csfloat.json marketcsgo.json
# 3. Rebuild (BUILD.bat).
#
# CSFloat (lowest listing) wins where both lists have the item; market.csgo.com fills the gaps.
# Names are stored lowercase (ASCII letters only, like the DLL's lookup), prices in cents.

import datetime
import json
import os
import sys


def lower_ascii(name):
    return bytes(b + 32 if 65 <= b <= 90 else b for b in name.encode("utf-8")).decode("utf-8")


def read_csfloat(path):
    # [{"market_hash_name": "...", "quantity": 36, "min_price": 65}, ...]   (cents)
    with open(path, encoding="utf-8") as f:
        root = json.load(f)
    out = {}
    for item in root:
        name, cents = item.get("market_hash_name"), item.get("min_price")
        if isinstance(name, str) and isinstance(cents, (int, float)) and cents > 0:
            out[lower_ascii(name)] = int(round(cents))
    return out


def read_marketcsgo(path):
    # {"success": true, "items": [{"market_hash_name": "...", "price": "12.840"}, ...]}   (dollars)
    with open(path, encoding="utf-8") as f:
        root = json.load(f)
    out = {}
    for item in root.get("items", []):
        name = item.get("market_hash_name")
        try:
            dollars = float(item.get("price"))
        except (TypeError, ValueError):
            continue
        if isinstance(name, str) and dollars > 0:
            out[lower_ascii(name)] = max(1, int(round(dollars * 100)))
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: python tools\\make_prices.py csfloat.json [marketcsgo.json]")
        return 1

    prices = read_marketcsgo(sys.argv[2]) if len(sys.argv) > 2 else {}
    csfloat = read_csfloat(sys.argv[1])
    prices.update(csfloat)

    if len(csfloat) < 1000:
        print("csfloat.json has only %d prices - not the price list?" % len(csfloat))
        return 1

    now = datetime.datetime.now(datetime.timezone.utc)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "prices.txt")
    lines = ["LOOTLINE-PRICES 1 %d %s" % (int(now.timestamp()), now.strftime("%Y-%m-%d"))]
    lines += ["%s\t%d" % (name, cents) for name, cents in sorted(prices.items()) if "\t" not in name and "\n" not in name]

    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print("data\\prices.txt: %d prices (%d from CSFloat), %s" % (len(lines) - 1, len(csfloat), now.strftime("%Y-%m-%d")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
