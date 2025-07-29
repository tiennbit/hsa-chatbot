import os
import sqlite3

# Path to the correct database file
db_path = os.path.join('backend', 'instance', 'hsa_chatbot.db')

def check_unanswered_questions():
    """
    Connects to the SQLite database and prints the contents
    of the 'unanswered_questions' table.
    """
    print(f"Connecting to database at: {db_path}")

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'.")
        print("Please make sure you have run the application at least once to create the database.")
        return

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unanswered_questions';")
        if cursor.fetchone() is None:
            print("Error: The table 'unanswered_questions' does not exist in this database.")
            print("This table should be in the main application database, not ChromaDB.")
            conn.close()
            return

        # Fetch all records from the table
        print("\n--- Contents of 'unanswered_questions' table ---")
        cursor.execute("SELECT * FROM unanswered_questions;")
        rows = cursor.fetchall()

        if not rows:
            print("The 'unanswered_questions' table is currently empty.")
            print("This could be because no questions have met the criteria for being 'unanswered' yet.")
        else:
            # Get column names
            column_names = [description[0] for description in cursor.description]
            print(f"Found {len(rows)} record(s).")
            print(" | ".join(column_names))
            print("-" * 50)
            for row in rows:
                print(" | ".join(map(str, row)))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    check_unanswered_questions()
