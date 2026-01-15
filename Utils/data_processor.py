from datetime import datetime


def calculate_total_revenue(transactions):
    return round(sum(tx['Quantity'] * tx['UnitPrice'] for tx in transactions), 2)


def region_wise_sales(transactions):
    region_data = {}
    total_sales = calculate_total_revenue(transactions)

    for tx in transactions:
        r = tx['Region']
        amt = tx['Quantity'] * tx['UnitPrice']

        if r not in region_data:
            region_data[r] = {'total_sales': 0, 'transaction_count': 0}

        region_data[r]['total_sales'] += amt
        region_data[r]['transaction_count'] += 1

    for r in region_data:
        region_data[r]['percentage'] = round(
            (region_data[r]['total_sales'] / total_sales) * 100, 2
        )

    return dict(sorted(region_data.items(), key=lambda x: x[1]['total_sales'], reverse=True))


def top_selling_products(transactions, n=5):
    prod = {}

    for tx in transactions:
        p = tx['ProductName']
        prod.setdefault(p, {'qty': 0, 'rev': 0})
        prod[p]['qty'] += tx['Quantity']
        prod[p]['rev'] += tx['Quantity'] * tx['UnitPrice']

    result = [(k, v['qty'], round(v['rev'], 2)) for k, v in prod.items()]
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:n]


def customer_analysis(transactions):
    cust = {}

    for tx in transactions:
        c = tx['CustomerID']
        cust.setdefault(c, {'total_spent': 0, 'count': 0, 'products': set()})
        cust[c]['total_spent'] += tx['Amount']
        cust[c]['count'] += 1
        cust[c]['products'].add(tx['ProductName'])

    result = {}
    for k, v in cust.items():
        result[k] = {
            'total_spent': round(v['total_spent'], 2),
            'purchase_count': v['count'],
            'avg_order_value': round(v['total_spent'] / v['count'], 2),
            'products_bought': list(v['products'])
        }

    return dict(sorted(result.items(), key=lambda x: x[1]['total_spent'], reverse=True))


def daily_sales_trend(transactions):
    daily = {}

    for tx in transactions:
        d = tx['Date']
        daily.setdefault(d, {'revenue': 0, 'transaction_count': 0, 'customers': set()})
        daily[d]['revenue'] += tx['Amount']
        daily[d]['transaction_count'] += 1
        daily[d]['customers'].add(tx['CustomerID'])

    return {
        d: {
            'revenue': round(v['revenue'], 2),
            'transaction_count': v['transaction_count'],
            'unique_customers': len(v['customers'])
        }
        for d, v in sorted(daily.items())
    }


def find_peak_sales_day(transactions):
    trend = daily_sales_trend(transactions)
    peak = max(trend.items(), key=lambda x: x[1]['revenue'])
    return peak[0], peak[1]['revenue'], peak[1]['transaction_count']


def low_performing_products(transactions, threshold=10):
    prod = {}

    for tx in transactions:
        p = tx['ProductName']
        prod.setdefault(p, {'qty': 0, 'rev': 0})
        prod[p]['qty'] += tx['Quantity']
        prod[p]['rev'] += tx['Amount']

    low = [(k, v['qty'], round(v['rev'], 2)) for k, v in prod.items() if v['qty'] < threshold]
    low.sort(key=lambda x: x[1])
    return low


def generate_sales_report(transactions, enriched, output_file='output/sales_report.txt'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_rev = calculate_total_revenue(transactions)
    avg = round(total_rev / len(transactions), 2)
    dates = [t['Date'] for t in transactions]

    region_stats = region_wise_sales(transactions)
    top_products = top_selling_products(transactions)
    customers = customer_analysis(transactions)
    daily = daily_sales_trend(transactions)
    peak = find_peak_sales_day(transactions)
    low = low_performing_products(transactions)

    enriched_ok = sum(1 for t in enriched if t['API_Match'])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\nSALES ANALYTICS REPORT\n")
        f.write(f"Generated: {now}\nRecords: {len(transactions)}\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Total Revenue: ₹{total_rev:,.2f}\n")
        f.write(f"Average Order Value: ₹{avg:,.2f}\n")
        f.write(f"Date Range: {min(dates)} to {max(dates)}\n\n")

        f.write("REGION PERFORMANCE\n")
        for r, d in region_stats.items():
            f.write(f"{r}: ₹{d['total_sales']:,.2f} ({d['percentage']}%)\n")

        f.write("\nTOP PRODUCTS\n")
        for i, p in enumerate(top_products, 1):
            f.write(f"{i}. {p[0]} | Qty: {p[1]} | ₹{p[2]:,.2f}\n")

        f.write("\nPEAK DAY\n")
        f.write(f"{peak[0]} | ₹{peak[1]:,.2f} | {peak[2]} txns\n")

        f.write("\nLOW PERFORMING PRODUCTS\n")
        for p in low:
            f.write(f"{p[0]} | Qty: {p[1]} | ₹{p[2]:,.2f}\n")

        f.write("\nAPI ENRICHMENT\n")
        f.write(f"Enriched: {enriched_ok}/{len(enriched)}\n")

