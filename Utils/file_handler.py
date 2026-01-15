def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)
    """

    encodings = ['utf-8', 'latin-1', 'cp1252']
    lines = []

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                all_lines = file.readlines()

                # Skip header and clean empty lines
                for line in all_lines[1:]:
                    line = line.strip()
                    if line:
                        lines.append(line)

            print(f"File successfully read using encoding: {encoding}")
            return lines

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

        except UnicodeDecodeError:
            continue

    print("Error: Unable to read file with supported encodings.")
    return []
