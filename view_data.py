
# view_data.py
from utils.db import get_connection
import pandas as pd

def view_table_structure(table_name):
    """Display table structure (columns, types, constraints)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    structure = cursor.fetchall()
    conn.close()

    if structure:
        df_structure = pd.DataFrame(structure, columns=["cid", "name", "type", "notnull", "dflt_value", "pk"])
        print(f"\n🧱 STRUCTURE OF TABLE: {table_name.upper()}")
        print("-" * (len(table_name) + 30))
        print(df_structure.to_string(index=False))
    else:
        print(f"\nNo structure found for table '{table_name}'.")

def view_table_data(table_name):
    """Display actual data in the table."""
    conn = get_connection()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"\n📊 DATA OF TABLE: {table_name.upper()}")
    print("-" * (len(table_name) + 25))

    if df.empty:
        print(f"No records found in '{table_name}'")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    tables = ["users", "chats", "documents", "rag_history", "chat_sessions"]

    for table in tables:
        view_table_structure(table)
        view_table_data(table)
        print("\n" + "=" * 100 + "\n")
