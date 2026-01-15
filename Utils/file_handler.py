def read_sales_data(filename):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    lines = []

    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as file:
                all_lines = file.readlines()

            for line in all_lines[1:]:  # Skip header
                line = line.strip()
                if line:
                    lines.append(line)

            print(f"File read using encoding: {enc}")
            return lines

        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print("Error: sales data file not found.")
            return []

    print("Error: Unable to read file with supported encodings.")
    return []


def parse_transactions(raw_lines):
    transactions = []

    for line in raw_lines:
        parts = line.split('|')
        if len(parts) != 8:
            continue

        tid, date, pid, pname, qty, price, cid, region = parts

        try:
            transaction = {
                'TransactionID': tid.strip(),
                'Date': date.strip(),
                'ProductID': pid.strip(),
                'ProductName': pname.replace(',', '').strip(),
                'Quantity': int(qty.replace(',', '')),
                'UnitPrice': float(price.replace(',', '')),
                'CustomerID': cid.strip(),
                'Region': region.strip()
            }
            transactions.append(transaction)
        except ValueError:
            continue

    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    valid = []
    invalid = 0
    regions = set()
    amounts = []

    for tx in transactions:
        try:
            if (
                not tx['TransactionID'].startswith('T') or
                not tx['ProductID'].startswith('P') or
                not tx['CustomerID'].startswith('C') or
                tx['Quantity'] <= 0 or
                tx['UnitPrice'] <= 0 or
                not tx['Region']
            ):
                invalid += 1
                continue

            amount = tx['Quantity'] * tx['UnitPrice']
            tx['Amount'] = amount
            regions.add(tx['Region'])
            amounts.append(amount)
            valid.append(tx)

        except KeyError:
            invalid += 1

    print("Available Regions:", sorted(regions))
    if amounts:
        print(f"Amount Range: ₹{int(min(amounts)):,} - ₹{int(max(amounts)):,}")

    filtered_by_region = 0
    filtered_by_amount = 0

    if region:
        before = len(valid)
        valid = [tx for tx in valid if tx['Region'] == region]
        filtered_by_region = before - len(valid)

    if min_amount is not None:
        before = len(valid)
        valid = [tx for tx in valid if tx['Amount'] >= min_amount]
        filtered_by_amount += before - len(valid)

    if max_amount is not None:
        before = len(valid)
        valid = [tx for tx in valid if tx['Amount'] <= max_amount]
        filtered_by_amount += before - len(valid)

    summary = {
        'total_input': len(transactions),
        'invalid': invalid,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid)
    }

    return valid, invalid, summary
