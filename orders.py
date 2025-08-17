import sqlite3
from Database import get_connection

def validate_and_place_order(user_id: int, item_id: int, quantity: int):
    """validate stock and place an order atomically."""
    if quantity <= 0:
        return {"ok": False, "message": "quantity must be positive."}
    
    conn = get_connection()
    c = conn.cursor()
    try:

        c.execute("begin immediate")

        c.execute("select quantity, name from menu_items where id = ?", (item_id,))
        row = c.fetchone()
        if not row:
            conn.rollback()
            return {"ok": False, "message": "item not found."}
        
        available_qty, item_name = int(row[0]), row[1]
        if available_qty < quantity:
            conn.rollback()
            return {
                "ok": False,
                "message": f"not enough stock for '{item_name}'. Available: {available_qty}"
            }
        c.execute(
            "update menu_items set quantity = quantity - ? where id = ?",
            (quantity, item_id)
        )

        conn.commit()
        return{
            "ok": True,
            "message": f"order placed: {quantity} x {item_name}",
            "order_id": c.lastrowid
        }
    except Exception as e:
        conn.rollback()
        return {"ok": False, "message": f"order failed: {e}"}
    finally:
        conn.close()

def list_menu():
    conn = get_connection()
    c = conn.cursor()
    c.execute("select id, name, price, quantity from menu_items order by id")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "price": float(r[2]), "quantity": int(r[3])}
        for r in rows
    ]

def list_user_orders(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        select o.id, m.name, o.quantity, o.timestamp
        from orders o
        join menu_items m ON m.id = o.item_id
        where o.user_id = ?
        order by o.id desc
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return [
        {"order_id": r[0], "item": r[1], "quantity": int(r[2]), "timestamp": r[3]}
        for r in rows
    ]