from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import generate_sales_report
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data


def main():
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)

        raw = read_sales_data("data/sales_data.txt")
        parsed = parse_transactions(raw)

        valid, invalid, _ = validate_and_filter(parsed)

        products = fetch_all_products()
        mapping = create_product_mapping(products)
        enriched = enrich_sales_data(valid, mapping)

        generate_sales_report(valid, enriched)

        print("Process completed successfully.")
        print("Output files generated:")
        print("- data/enriched_sales_data.txt")
        print("- output/sales_report.txt")

    except Exception as e:
        print("Error occurred:", e)


if __name__ == "__main__":
    main()
