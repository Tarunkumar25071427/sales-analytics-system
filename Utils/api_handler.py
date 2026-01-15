import requests


def fetch_all_products():
    try:
        r = requests.get("https://dummyjson.com/products?limit=100", timeout=10)
        r.raise_for_status()
        data = r.json().get('products', [])
        print(f"Fetched {len(data)} products from API")
        return data
    except Exception as e:
        print("API error:", e)
        return []


def create_product_mapping(products):
    return {
        p['id']: {
            'category': p.get('category'),
            'brand': p.get('brand'),
            'rating': p.get('rating')
        }
        for p in products
    }


def enrich_sales_data(transactions, mapping):
    enriched = []

    for tx in transactions:
        tx_copy = tx.copy()
        try:
            pid = int(''.join(filter(str.isdigit, tx['ProductID'])))
            if pid in mapping:
                tx_copy.update({
                    'API_Category': mapping[pid]['category'],
                    'API_Brand': mapping[pid]['brand'],
                    'API_Rating': mapping[pid]['rating'],
                    'API_Match': True
                })
            else:
                tx_copy.update({'API_Category': None, 'API_Brand': None, 'API_Rating': None, 'API_Match': False})
        except:
            tx_copy.update({'API_Category': None, 'API_Brand': None, 'API_Rating': None, 'API_Match': False})

        enriched.append(tx_copy)

    with open('data/enriched_sales_data.txt', 'w', encoding='utf-8') as f:
        header = list(enriched[0].keys())
        f.write('|'.join(header) + '\n')
        for tx in enriched:
            f.write('|'.join(str(tx.get(h, '')) for h in header) + '\n')

    return enriched

