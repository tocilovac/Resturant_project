import sqlite3
from Database import get_db_connection

ADMIN_username = "arian"
ADMIN_password = "arian123"

def admin_login(username: str, password: str):
    if username == ADMIN_username and password == ADMIN_password:
        return {"message": "admin login successful"}
    return {"error": "invalid admin credentials"}


def add_menu_item(name: str, price: float, quantity: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("insert into menu_items (name, price, quantity) values (?, ?, ?)",
                        (name, price, quantity))
        conn.commit()
        return {"message": f"item '{name}' added successfully."}
    except sqlite3.IntegrityError:
        return {"error": "item already exists in menu."}
    finally: 
        conn.close()

def update_menu_item(item_id: int, price: float = None, quantity: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("select id from menu_items where id = ?", (item_id))
    if cursor.fetchone() is None:
        return {"error": "item not found"}
    
    if price is not None:
        cursor.execute("update menu_items set price=? where id = ?", (price, item_id))
    if quantity is not None:
        cursor.execute("update menu_items set quantity=? where id=?", (quantity, item_id))

    conn.commit()
    conn.close()
    return {"message": f"item {item_id} updated successfully."}

def delete_menu_item(item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("delete from menu_items where id = ?", (item_id,))
    if cursor.rowcount == 0:
        return {"error": "item not found"}
    
    conn.commit()
    conn.close()
    return {"message": f"item {item_id} deleted successfully."}

def list_menu_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("select id, name, price, quantity from menu_items")
    items = cursor.fetchall()
    conn.close()

    return {"menu": [{"id": row[0], "name": row[1], "price": row[2], "quantity": row[3]} for row in items]}
