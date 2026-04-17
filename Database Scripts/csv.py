import sqlite3
import csv

# --- Configuration ---
db_file = r"C:\Users\Administrator\Desktop\bothtml\eguls.db"
table_name = 'planets'
csv_file = 'eguls.csv'
# ---------------------

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute the query to select all data from the table
    print(f"Exporting data from table '{table_name}' to '{csv_file}'...")
    cursor.execute(f"SELECT * FROM {table_name}")

    # Open the CSV file in write mode
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write the header row (column names)
        # cursor.description provides column names
        writer.writerow([description[0] for description in cursor.description])

        # Write all the data rows
        writer.writerows(cursor)

    print("Export complete.")

except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    # Close the database connection
    if conn:
        conn.close()
