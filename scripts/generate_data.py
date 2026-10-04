"""Generate the SellerPulse synthetic dataset (Task 6).

Reproducible: the random seed is fixed, so re-running gives identical files.
Abhijit's original 10 SKUs, their September sales and their 8 reviews are kept exactly.
Output: data/synthetic/*.csv plus one Excel workbook with a sheet per table.
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)
START, END = date(2026, 7, 20), date(2026, 9, 15)   # 8 weeks of history
TODAY = date(2026, 9, 16)                          # "today" for every relative question
OUT = Path("data/synthetic")

# ---------------------------------------------------------------- sellers
SELLERS = [
    ("S001", "Meera Iyer", "Meera Home Studio", "2025-03-10"),
    ("S002", "Anika Rao", "Clay & Loom", "2025-11-02"),
]

# ---------------------------------------------------------------- Abhijit's original data (kept exactly)
ORIGINAL_LISTINGS = [
    ("SKU-1001", "Boho Wall Hanging - Macrame", "Wall Decor", 34.99, 6, "Active",
     "Handmade macrame wall hanging in natural cotton cord. Adds warmth and texture to any room."),
    ("SKU-1002", "Ceramic Table Vase - Ivory", "Vases", 22.50, 0, "Out of Stock",
     "Matte ivory stoneware vase. Height 25 cm, opening 8 cm. Not watertight for fresh flowers."),
    ("SKU-1003", "Rattan Pendant Light Shade", "Lighting", 58.00, 14, "Active",
     "Hand-woven rattan shade for E27 fittings. Diameter 40 cm, height 30 cm. Bulb not included."),
    ("SKU-1004", "Linen Throw Pillow Cover Set (2)", "Textiles", 19.99, 32, "Active",
     "Two stonewashed linen cushion covers, 45 x 45 cm, with hidden zip. Inserts not included."),
    ("SKU-1005", "Wooden Floating Shelf - Walnut", "Shelving", 27.75, 9, "Active",
     "Solid walnut shelf with concealed bracket. 60 x 15 x 4 cm. Holds up to 10 kg."),
    ("SKU-1006", "Handwoven Jute Area Rug 4x6", "Rugs", 89.00, 3, "Low Stock",
     "Natural jute rug, 120 x 180 cm (4 x 6 ft). Hand-braided. Ships from the workshop in 10-14 days."),
    ("SKU-1007", "Terracotta Planter Trio", "Planters", 31.20, 21, "Active",
     "Set of three unglazed terracotta pots, 10, 14 and 18 cm, with drainage holes and saucers."),
    ("SKU-1008", "Brass Wall Sconce - Set of 2", "Lighting", 64.50, 0, "Out of Stock",
     "Pair of brushed brass wall lights, 22 cm arm, hardwired. Requires an electrician to install."),
    ("SKU-1009", "Cotton Woven Table Runner", "Textiles", 14.25, 40, "Active",
     "Handloom cotton runner, 35 x 180 cm, fringed ends. Machine washable at 30 degrees."),
    ("SKU-1010", "Winter Sherpa Throw Blanket", "Textiles", 42.00, 17, "Active",
     "Reversible sherpa and knit throw, 130 x 170 cm. Machine washable."),
]
ORIGINAL_SALES = [  # (date, sku, units, revenue) -> each becomes one delivered order
    ("2026-09-01", "SKU-1001", 3, 104.97), ("2026-09-01", "SKU-1004", 5, 99.95),
    ("2026-09-02", "SKU-1010", 2, 84.00), ("2026-09-03", "SKU-1006", 1, 89.00),
    ("2026-09-04", "SKU-1007", 4, 124.80), ("2026-09-05", "SKU-1001", 2, 69.98),
    ("2026-09-07", "SKU-1009", 6, 85.50), ("2026-09-08", "SKU-1003", 1, 58.00),
    ("2026-09-10", "SKU-1010", 3, 126.00), ("2026-09-12", "SKU-1004", 2, 39.98),
    ("2026-09-13", "SKU-1001", 1, 34.99), ("2026-09-15", "SKU-1005", 2, 55.50),
]
ORIGINAL_REVIEWS = [
    ("REV-501", "SKU-1001", 5, "Beautiful and well made, arrived fast!", "2026-08-20"),
    ("REV-502", "SKU-1006", 2, "Nice rug but delivery took almost 3 weeks.", "2026-08-25"),
    ("REV-503", "SKU-1004", 4, "Good quality linen, color slightly different than photo.", "2026-08-28"),
    ("REV-504", "SKU-1001", 3, "Cute but smaller than expected for the price.", "2026-09-02"),
    ("REV-505", "SKU-1008", 1, "Item shown as available but order got cancelled.", "2026-09-03"),
    ("REV-506", "SKU-1010", 5, "Super soft and warm, buying another for a gift.", "2026-09-06"),
    ("REV-507", "SKU-1007", 4, "Planters are lovely, one had a small chip.", "2026-09-09"),
    ("REV-508", "SKU-1006", 2, "Shipping delay again, love the rug itself though.", "2026-09-11"),
]
# Price changes on original SKUs: the Boho went up before its reviews turned; the rug came down.
PRICE_CHANGES = {"SKU-1001": (29.99, "2026-08-25"), "SKU-1006": (95.00, "2026-08-18")}

# ---------------------------------------------------------------- generated catalogue
PRODUCT_TYPES = [  # (category, product, price range, size text)
    ("Wall Decor", "Woven Wall Basket", (18, 40), "Diameter 30 cm"),
    ("Wall Decor", "Framed Botanical Print", (22, 55), "30 x 40 cm, oak frame"),
    ("Wall Decor", "Macrame Plant Hanger", (12, 24), "Length 90 cm"),
    ("Vases", "Ceramic Bud Vase", (12, 24), "Height 12 cm"),
    ("Vases", "Glass Carafe Vase", (18, 35), "Height 28 cm"),
    ("Lighting", "Paper Lantern Pendant", (25, 48), "Diameter 45 cm"),
    ("Lighting", "Ceramic Table Lamp", (48, 95), "Height 42 cm, E14 fitting"),
    ("Textiles", "Chunky Knit Throw", (38, 70), "120 x 150 cm"),
    ("Textiles", "Boucle Cushion Cover", (16, 28), "45 x 45 cm"),
    ("Textiles", "Linen Tea Towel Set (3)", (14, 24), "50 x 70 cm each"),
    ("Shelving", "Oak Wall Ledge", (24, 45), "80 x 10 cm"),
    ("Rugs", "Wool Runner Rug", (70, 140), "70 x 240 cm"),
    ("Rugs", "Cotton Bath Mat", (18, 32), "50 x 80 cm"),
    ("Planters", "Glazed Ceramic Planter", (20, 45), "Diameter 20 cm"),
    ("Planters", "Hanging Terracotta Pot", (12, 22), "Diameter 14 cm"),
    ("Candles", "Soy Candle in Amber Jar", (14, 26), "200 g, 40 hours"),
    ("Candles", "Beeswax Taper Pair", (9, 16), "Height 25 cm"),
    ("Mirrors", "Round Rattan Mirror", (45, 90), "Diameter 50 cm"),
    ("Kitchen & Dining", "Stoneware Serving Bowl", (22, 40), "Diameter 26 cm"),
    ("Kitchen & Dining", "Mango Wood Board", (18, 34), "40 x 20 cm"),
    ("Baskets & Storage", "Seagrass Storage Basket", (20, 42), "35 x 30 cm"),
    ("Clocks", "Minimal Wall Clock", (28, 55), "Diameter 30 cm"),
]
COLOURS = ["Ivory", "Sage", "Terracotta", "Charcoal", "Sand", "Ochre", "Indigo", "Natural", "Rust", "Olive"]
MATERIALS = {"Vases": "stoneware", "Lighting": "handmade", "Textiles": "cotton", "Rugs": "wool",
             "Candles": "natural wax", "Mirrors": "rattan", "Kitchen & Dining": "hand-finished",
             "Baskets & Storage": "hand-woven", "Clocks": "powder-coated steel", "Shelving": "solid oak",
             "Planters": "hand-thrown", "Wall Decor": "handmade"}


def status_for(stock):
    return "Out of Stock" if stock == 0 else "Low Stock" if stock <= 5 else "Active"


def make_catalogue(seller_id, first_sku, count, types):
    """Unique product-colour combinations with a price, stock level and description."""
    combos = [(t, c) for t in types for c in COLOURS]
    random.shuffle(combos)
    rows = []
    for i, ((cat, product, (lo, hi), size), colour) in enumerate(combos[:count]):
        price = round(random.uniform(lo, hi), 0) - 0.01
        stock = random.choice([0, 2, 4] + list(range(6, 60, 3)))
        desc = f"{MATERIALS[cat].capitalize()} {product.lower()} in {colour.lower()}. {size}."
        rows.append((seller_id, f"SKU-{first_sku + i}", f"{product} - {colour}", cat, price, stock,
                     status_for(stock), desc))
    return rows


def build_listings():
    rows = [("S001",) + r for r in ORIGINAL_LISTINGS]
    rows += make_catalogue("S001", 1011, 140, PRODUCT_TYPES)
    # Deliberate policy risk: an Active listing with zero stock (policy section 3).
    i = next(k for k, r in enumerate(rows) if r[2].startswith("Macrame Plant Hanger"))
    rows[i] = rows[i][:5] + (0, "Active") + rows[i][7:]
    ceramics = [t for t in PRODUCT_TYPES if t[0] in ("Vases", "Planters", "Kitchen & Dining")]
    rows += make_catalogue("S002", 2001, 30, ceramics)
    return pd.DataFrame(rows, columns=["seller_id", "sku", "title", "category", "price_usd",
                                       "stock_qty", "status", "description"])


def build_price_history(listings):
    rows = []
    for r in listings.itertuples():
        if r.sku in PRICE_CHANGES:
            old, changed = PRICE_CHANGES[r.sku]
            prev_end = (date.fromisoformat(changed) - timedelta(days=1)).isoformat()
            rows.append((r.seller_id, r.sku, old, START.isoformat(), prev_end))
            rows.append((r.seller_id, r.sku, r.price_usd, changed, ""))
        else:
            rows.append((r.seller_id, r.sku, r.price_usd, START.isoformat(), ""))
    return pd.DataFrame(rows, columns=["seller_id", "sku", "price_usd", "valid_from", "valid_to"])


def price_on(ph, sku, day):
    p = ph[(ph.sku == sku) & (ph.valid_from <= day) & ((ph.valid_to == "") | (ph.valid_to >= day))]
    return float(p.price_usd.iloc[0])


# ---------------------------------------------------------------- orders
ORIGINAL_RATES = {  # orders per day before 1 September, to tell each original SKU's story
    "SKU-1001": 0.40, "SKU-1002": 0.10, "SKU-1003": 0.06, "SKU-1004": 0.15, "SKU-1005": 0.06,
    "SKU-1006": 0.15, "SKU-1007": 0.08, "SKU-1008": 0.07, "SKU-1009": 0.10, "SKU-1010": 0.03,
}
SOLD_OUT_ON = {"SKU-1002": "2026-08-20", "SKU-1008": "2026-08-25"}  # no sales after these dates
NOTES = {"delayed": "Past promised delivery date; not yet delivered",
         "cancelled": "Cancelled: item could not be fulfilled",
         "returned": "Returned by buyer; refund issued",
         "return_requested": "Buyer requested a return"}


def order_status(sku, day):
    """Status, promised date and delivered date, based on how long ago the order was placed."""
    lead = 14 if sku == "SKU-1006" else 5                 # the rug ships from the workshop
    promised = day + timedelta(days=lead)
    late = sku == "SKU-1006" or random.random() < 0.06
    delivered = promised + timedelta(days=random.randint(3, 8) if late else -random.randint(0, 2))
    if delivered < TODAY:
        roll = random.random()
        if roll < 0.03:
            return "returned", promised, delivered
        if roll < 0.12 and (TODAY - delivered).days <= 7:
            return "return_requested", promised, delivered
        return "delivered", promised, delivered
    return ("delayed" if promised < TODAY else "in_transit"), promised, None


def build_orders(listings, ph):
    rows, day = [], START
    rates = {r.sku: ORIGINAL_RATES.get(r.sku, random.choice([0.0] + [0.02, 0.04, 0.06, 0.09, 0.12] * 3))
             for r in listings.itertuples()}
    sold_out = dict(SOLD_OUT_ON)
    for r in listings.itertuples():                      # generated items at 0 stock sold out in August
        if r.stock_qty == 0 and r.sku not in sold_out and r.status != "Active":
            sold_out[r.sku] = (date(2026, 8, 1) + timedelta(days=random.randint(0, 30))).isoformat()
    while day <= END:
        iso = day.isoformat()
        for r in listings.itertuples():
            is_original = r.sku in ORIGINAL_RATES
            if is_original and iso >= "2026-09-01":
                continue                                  # September comes from Abhijit's sales rows
            if r.sku in sold_out and iso > sold_out[r.sku]:
                continue
            rate = rates[r.sku]
            if r.sku == "SKU-1010":
                rate *= 0.5 + day.month - 7              # winter throw: demand rises into autumn
            if r.sku == "SKU-1001":
                rate = 0.9 if iso < "2026-08-25" else 0.35  # strong seller until the price rise
            if random.random() < rate:
                qty = random.choices([1, 2, 3], [0.75, 0.2, 0.05])[0]
                rows.append([r.seller_id, r.sku, iso, qty] + list(order_status(r.sku, day)))
        day += timedelta(days=1)
    for iso, sku, units, _ in ORIGINAL_SALES:
        status, promised, delivered = order_status(sku, date.fromisoformat(iso))
        if status in ("returned", "return_requested"):
            status = "delivered"                          # keep the original sales intact
        rows.append(["S001", sku, iso, units, status, promised, delivered])
    # Two cancellations: the sconce behind REV-505, and the active-but-empty plant hanger.
    hanger = listings[listings.title.str.startswith("Macrame Plant Hanger") & (listings.stock_qty == 0)].sku.iloc[0]
    for sku, iso in (("SKU-1008", "2026-09-01"), (hanger, "2026-09-12")):
        rows.append(["S001", sku, iso, 1, "cancelled", date.fromisoformat(iso) + timedelta(days=5), None])

    df = pd.DataFrame(rows, columns=["seller_id", "sku", "order_date", "quantity", "status",
                                     "promised_delivery_date", "delivered_date"])
    df = df.sort_values(["order_date", "sku"]).reset_index(drop=True)
    df.insert(0, "order_id", [f"ORD-{100001 + i}" for i in range(len(df))])
    df["unit_price_usd"] = [price_on(ph, s, d) for s, d in zip(df.sku, df.order_date)]
    df["order_total_usd"] = (df.unit_price_usd * df.quantity).round(2)
    df["issue_note"] = df.status.map(NOTES).fillna("")
    for c in ("promised_delivery_date", "delivered_date"):
        df[c] = df[c].map(lambda v: v.isoformat() if v else "")
    return df[["order_id", "seller_id", "sku", "order_date", "quantity", "unit_price_usd",
               "order_total_usd", "status", "promised_delivery_date", "delivered_date", "issue_note"]]


def build_sales(orders):
    """Daily sales per SKU: every order except cancelled ones (returns stay visible in orders)."""
    live = orders[orders.status != "cancelled"]
    s = live.groupby(["order_date", "seller_id", "sku"]).agg(
        units_sold=("quantity", "sum"), revenue_usd=("order_total_usd", "sum"),
        order_count=("order_id", "count")).reset_index().rename(columns={"order_date": "date"})
    s["revenue_usd"] = s.revenue_usd.round(2)
    return s


# ---------------------------------------------------------------- reviews
COMMENTS = {
    5: ["Absolutely love it, looks even better in person.", "Beautiful quality and carefully packed.",
        "Exactly as pictured. Would buy again."],
    4: ["Lovely piece, the colour is a little darker than the photo.", "Good quality, arrived a few days late.",
        "Really nice, though slightly smaller than I imagined."],
    3: ["It's okay, the finish is a bit uneven.", "Decent, but smaller than expected.",
        "Fine product, the packaging was damaged."],
    2: ["Arrived later than promised and the box was crushed.", "The colour is quite different from the listing.",
        "Smaller than described for the price."],
    1: ["Arrived broken.", "Not as described at all.", "Took weeks to arrive and then had to be returned."],
}


def build_reviews(orders):
    rows = [("S001", rid, sku, "", rating, text, d) for rid, sku, rating, text, d in ORIGINAL_REVIEWS]
    quality = {}
    n = 1001
    for o in orders.itertuples():
        if o.status not in ("delivered", "returned") or random.random() > 0.18:
            continue
        if o.sku in ORIGINAL_RATES and o.sku != "SKU-1006" and o.order_date >= "2026-08-10":
            continue                                      # originals' recent reviews are Abhijit's
        q = quality.setdefault(o.sku, random.uniform(3.4, 4.8))
        if o.sku == "SKU-1006":
            rating = random.choice([2, 3])                # the rug's delivery problem is a pattern
        elif o.status == "returned":
            rating = random.choice([1, 2])
        else:
            rating = max(1, min(5, round(random.gauss(q, 0.8))))
        text = ("Lovely rug but it took far longer to arrive than the listing said." if o.sku == "SKU-1006"
                else random.choice(COMMENTS[rating]))
        day = date.fromisoformat(o.delivered_date) + timedelta(days=random.randint(1, 6))
        if day > END:
            continue
        rows.append((o.seller_id, f"REV-{n}", o.sku, o.order_id, rating, text, day.isoformat()))
        n += 1
    df = pd.DataFrame(rows, columns=["seller_id", "review_id", "sku", "order_id", "rating", "comment", "review_date"])
    return df.sort_values(["review_date", "review_id"]).reset_index(drop=True)


# ---------------------------------------------------------------- write
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sellers = pd.DataFrame(SELLERS, columns=["seller_id", "seller_name", "store_name", "joined_date"])
    listings = build_listings()
    ph = build_price_history(listings)
    orders = build_orders(listings, ph)
    sales = build_sales(orders)
    reviews = build_reviews(orders)
    tables = {"sellers": sellers, "listings": listings, "price_history": ph,
              "orders": orders, "sales": sales, "reviews": reviews}
    with pd.ExcelWriter(OUT / "sellerpulse_data.xlsx") as xl:
        for name, df in tables.items():
            df.to_csv(OUT / f"{name}.csv", index=False)
            df.to_excel(xl, sheet_name=name, index=False)
    print(f"Data window {START} to {END}; today = {TODAY}")
    for name, df in tables.items():
        print(f"  {name:14} {len(df):5} rows")
    for sid in sellers.seller_id:
        print(f"  {sid}: {(listings.seller_id == sid).sum()} listings, "
              f"{(orders.seller_id == sid).sum()} orders, {(reviews.seller_id == sid).sum()} reviews")


if __name__ == "__main__":
    main()
