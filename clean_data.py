import pandas as pd
import os

# --- CONFIGURATION ---
filename = "prices.csv"

def clean_database():
    if not os.path.exists(filename):
        print("Error: prices.csv not found!")
        return

    # 1. Show current dates
    df = pd.read_csv(filename)
    print("\n--- Current Data Stats ---")
    print(df["Date"].value_counts())
    
    # 2. Ask user what to delete
    print("\nWhich date do you want to DELETE? (YYYY-MM-DD)")
    date_to_remove = input("Enter Date (or press Enter to cancel): ").strip()
    
    if not date_to_remove:
        print("Cancelled.")
        return

    # 3. Filter the data
    initial_count = len(df)
    # We keep rows that are NOT equal to the date_to_remove
    df_clean = df[df["Date"] != date_to_remove]
    final_count = len(df_clean)
    
    deleted_rows = initial_count - final_count
    
    if deleted_rows > 0:
        # 4. Save back to file
        df_clean.to_csv(filename, index=False)
        print(f"\nSUCCESS: Deleted {deleted_rows} rows from {date_to_remove}.")
        print("Your database is now clean.")
    else:
        print(f"\nNo data found for date: {date_to_remove}")

if __name__ == "__main__":
    clean_database()
