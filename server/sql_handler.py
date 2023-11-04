import mysql.connector

config = {
  'user': 'root',
  'password': 'sskkyy3702',
  'host': '35.201.203.232',
  'database': 'rowdata'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Successfully connected to the database.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("Connection closed.")
