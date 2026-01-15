import requests


def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    """
    try:
        response = requests.get("https://dummyjson.com/products?limit=100", timeout=10)
        response.raise_for_status()
        products = response.json().get("products", [])
        print(f"✓ Fetched {len(products)} products from API")
        return products
    except Exception as e:
        print("✗ API fetch failed:", e)
        return []


def create_product_mapping(api_products):
    """
    Creates mapping of product ID to product info
    """
    return {
        product["id"]: {
            "category": product.get("category"),
            "brand": product.get("brand"),
            "rating": product.get("rating"),
        }
        for product in api_products
    }


def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transactions with API product data
    """
    enriched_transactions = []

    for tx in transactions:
        tx_copy = tx.copy()
        try:
            numeric_id = int("".join(filter(str.isdigit, tx["ProductID"])))
            if numeric_id in product_mapping:
                api_data = product_mapping[numeric_id]
                tx_copy.update({
                    "API_Category": api_data["category"],
                    "API_Brand": api_data["brand"],
                    "API_Rating": api_data["rating"],
                    "API_Match": True
                })
            else:
                tx_copy.update({
                    "API_Category": None,
                    "API_Brand": None,
                    "API_Rating": None,
                    "API_Match": False
                })
        except Exception:
            tx_copy.update({
                "API_Category": None,
                "API_Brand": None,
                "API_Rating": None,
                "API_Match": False
            })

        enriched_transactions.append(tx_copy)

    save_enriched_data(enriched_transactions)
    return enriched_transactions


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched sales data to file
    """
    if not enriched_transactions:
        print("No enriched data to save.")
        return

    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    with open(filename, "w", encoding="utf-8") as file:
        file.write("|".join(headers) + "\n")
        for tx in enriched_transactions:
            row = [str(tx.get(h, "")) if tx.get(h) is not None else "" for h in headers]
            file.write("|".join(row) + "\n")

    print(f"✓ Enriched data saved to {filename}")
