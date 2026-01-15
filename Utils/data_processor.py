from datetime import datetime


def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions
    """
    return round(sum(tx['Quantity'] * tx['UnitPrice'] for tx in transactions), 2)


def region_wise_sales(transactions):
    """
    Analyzes sales by region
    """
    region_data = {}
    total_sales = calculate_total_revenue(transactions)

    for tx in transactions:
        region = tx['Region']
        amount = tx['Quantity'] * tx['UnitPrice']

        region_data.setdefault(region, {'total_sales': 0, 'transaction_count': 0})
        region_data[region]['total_sales'] += amount
        region_data[region]['transaction_count'] += 1

    for region in region_data:
        region_data[region]['percentage'] = round(
            (region_data[region]['total_sales'] / total_sales) * 100, 2
        )

    return dict(sorted(region_data.items(),
                       key=lambda x: x[1]['total_sales'],
                       reverse=True))


def top_selling_products(transactions, n=5):
    """
    Finds top n products by quantity sold
    """
    products = {}

    for tx in transactions:
        name = tx['ProductName']
        amount = tx['Quantity'] * tx['UnitPrice']

        products.setdefault(name, {'qty': 0, 'rev': 0})
        products[name]['qty'] += tx['Quantity']
        products[name]['rev'] += amount

    result = [(k, v['qty'], round(v['rev'], 2)) for k, v in products.items()]
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:n]


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    """
    customers = {}

    for tx in transactions:
        cid = tx['CustomerID']
        amount = tx['Quantity'] * tx['UnitPrice']

        customers.setdefault(cid, {'total_spent': 0, 'count': 0, 'products': set()})
        customers[cid]['total_spent'] += amount
        customers[cid]['count'] += 1
        customers[cid]['products'].add(tx['ProductName'])

    result = {
        k: {
            'total_spent': round(v['total_spent'], 2),
            'purchase_count': v['count'],
            'avg_order_value': round(v['total_spent'] / v['count'], 2),
            'products_bought': list(v['products'])
        }
        for k, v in customers.items()
    }

    return dict(sorted(result.items(),
                       key=lambda x: x[1]['total_spent'],
                       reverse=True))


def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date
    """
    daily = {}

    for tx in transactions:
        date = tx['Date']
        amount = tx['Quantity'] * tx['UnitPrice']

        daily.setdefault(date, {'revenue': 0, 'transaction_count': 0, 'customers': set()})
        daily[date]['revenue'] += amount
        daily[date]['transaction_count'] += 1
        daily[date]['customers'].add(tx['CustomerID'])

    return {
        d: {
            'revenue': round(v['revenue'], 2),
            'transaction_count': v['transaction_count'],
            'unique_customers': len(v['customers'])
        }
        for d, v in sorted(daily.items())
    }


def find_peak_sales_day(transactions):
    """
    Identifies date with highest revenue
    """
    trend = daily_sales_trend(transactions)
    peak = max(trend.items(), key=lambda x: x[1]['revenue'])
    return peak[0], peak[1]['revenue'], peak[1]['transaction_count']


def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales
    """
    products = {}

    for tx in transactions:
        name = tx['ProductName']
        amount = tx['Quantity'] * tx['UnitPrice']

        products.setdefault(name, {'qty': 0, 'rev': 0})
        products[name]['qty'] += tx['Quantity']
        products[name]['rev'] += amount

    low = [(k, v['qty'], round(v['rev'], 2))
           for k, v in products.items() if v['qty'] < threshold]

    low.sort(key=lambda x: x[1])
    return low


def generate_sales_report(transactions, enriched_transactions,
                          output_file='output/sales_report.txt'):
    """
    Generates formatted sales analytics report
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_rev = calculate_total_revenue(transactions)
    avg_order = round(total_rev / len(transactions), 2)
    dates = [t['Date'] for t in transactions]

    region_stats = region_wise_sales(transactions)
    top_products = top_selling_products(transactions)
    customers = customer_analysis(transactions)
    daily = daily_sales_trend(transactions)
    peak = find_peak_sales_day(transactions)
    low = low_performing_products(transactions)

    enriched_ok = sum(1 for t in enriched_transactions if t.get('API_Match'))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("SALES ANALYTICS REPORT\n")
        f.write(f"Generated: {now}\n")
        f.write(f"Records Processed: {len(transactions)}\n")
        f.write("=" * 50 + "\n\n")

        f.write("OVERALL SUMMARY\n")
        f.write(f"Total Revenue: ₹{total_rev:,.2f}\n")
        f.write(f"Total Transactions: {len(transactions)}\n")
        f.write(f"Average Order Value: ₹{avg_order:,.2f}\n")
        f.write(f"Date Range: {min(dates)} to {max(dates)}\n\n")

        f.write("REGION-WISE PERFORMANCE\n")
        for r, d in region_stats.items():
            f.write(f"{r} | ₹{d['total_sales']:,.2f} | {d['percentage']}% | {d['transaction_count']} txns\n")

        f.write("\nTOP 5 PRODUCTS\n")
        for i, p in enumerate(top_products, 1):
            f.write(f"{i}. {p[0]} | Qty: {p[1]} | Revenue: ₹{p[2]:,.2f}\n")

        f.write("\nTOP 5 CUSTOMERS\n")
        for i, (cid, d) in enumerate(list(customers.items())[:5], 1):
            f.write(f"{i}. {cid} | ₹{d['total_spent']:,.2f} | Orders: {d['purchase_count']}\n")

        f.write("\nDAILY SALES TREND\n")
        for d, v in daily.items():
            f.write(f"{d} | ₹{v['revenue']:,.2f} | Txns: {v['transaction_count']} | Customers: {v['unique_customers']}\n")

        f.write("\nPRODUCT PERFORMANCE\n")
        f.write(f"Best Selling Day: {peak[0]} | ₹{peak[1]:,.2f} | {peak[2]} txns\n")

        if low:
            f.write("Low Performing Products:\n")
            for p in low:
                f.write(f"{p[0]} | Qty: {p[1]} | ₹{p[2]:,.2f}\n")
        else:
            f.write("No low performing products\n")

        f.write("\nAPI ENRICHMENT SUMMARY\n")
        f.write(f"Enriched Transactions: {enriched_ok}/{len(enriched_transactions)}\n")
        f.write(f"Success Rate: {(enriched_ok / len(enriched_transactions)) * 100:.2f}%\n")
