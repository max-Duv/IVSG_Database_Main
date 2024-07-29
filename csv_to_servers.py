"""
This script connects to a PostgreSQL server using psycopg2.

It uses the PostgreSQL COPY FROM command for fast ingestion directly from a buffer to the specified table.

Polars is used to read CSV files efficiently.
"""

# Import necessary libraries
import polars as pl  # Faster for reading and processing large datasets
import psycopg2  # For handling database operations
from io import StringIO  # For handling in-memory file-like objects

# Function to create a database connection
def create_db_connection(host, port, dbname, user, password):
    """
    Establishes a PostgreSQL database connection.

    Args:
    host (str): Host address of the PostgreSQL server
    port (str): Port number
    dbname (str): Database name
    user (str): Username
    password (str): Password

    Returns:
    psycopg2.connection: a psycopg2 connection object
    """
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    return conn

# Function to upload CSV to PostgreSQL
def upload_csv_to_postgresql(csv_path, table_name, conn):
    """
    Loads a CSV file into a Polars DataFrame and uploads it to a PostgreSQL database.

    Args:
    csv_path (str): Path to the CSV file
    table_name (str): Target table name in the database
    conn: Active database connection object
    """
    # Load data from CSV file into a Polars DataFrame
    df = pl.read_csv(csv_path)

    # Convert Polars DataFrame to CSV string for COPY FROM compatibility
    csv_buffer = StringIO()
    df.write_csv(csv_buffer)
    csv_buffer.seek(0)  # Rewind buffer to the beginning for reading

    # Get cursor from connection
    cursor = conn.cursor()

    # Use copy_expert to upload CSV directly into the table
    cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", csv_buffer)  # Adjust parameters as necessary

    # Commit changes and close the cursor
    conn.commit()
    cursor.close()

# Main function to execute the process
def main():
    # Database credentials and details
    host = 'your_host'
    port = '5432'
    dbname = 'your_dbname'
    user = 'your_username'
    password = 'your_password'
    csv_path = 'path_to_your_csv.csv'
    table_name = 'your_table_name'
    
    # Create database connection
    conn = create_db_connection(host, port, dbname, user, password)
    
    # Upload CSV to PostgreSQL
    upload_csv_to_postgresql(csv_path, table_name, conn)
    
    # Close the database connection
    conn.close()

# Execute the main function
if __name__ == "__main__":
    main()