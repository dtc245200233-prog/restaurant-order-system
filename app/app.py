import os
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
DATABASE_URL = os.environ["DATABASE_URL"]


def get_db():
    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dishes (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                description TEXT,
                price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
                category VARCHAR(100) NOT NULL,
                available BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS restaurant_tables (
                id SERIAL PRIMARY KEY,
                table_number VARCHAR(20) NOT NULL UNIQUE,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                status VARCHAR(20) NOT NULL DEFAULT 'available'
                    CHECK (status IN ('available', 'occupied', 'reserved'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                table_id INTEGER REFERENCES restaurant_tables(id),
                customer_name VARCHAR(150),
                status VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'preparing', 'served', 'cancelled')),
                total NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (total >= 0),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                dish_id INTEGER NOT NULL REFERENCES dishes(id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0)
            )
        """)
        conn.execute("""
            INSERT INTO dishes (name, description, price, category)
            VALUES
                ('Phở bò', 'Phở bò truyền thống', 45000, 'Món chính'),
                ('Cơm gà', 'Cơm gà thơm ngon', 40000, 'Món chính'),
                ('Trà đào', 'Trà đào mát lạnh', 25000, 'Đồ uống')
            ON CONFLICT DO NOTHING
        """)
        conn.execute("""
            INSERT INTO restaurant_tables (table_number, capacity)
            VALUES ('B01', 4), ('B02', 4), ('B03', 6), ('B04', 2)
            ON CONFLICT (table_number) DO NOTHING
        """)


@app.route("/")
def index():
    with get_db() as conn:
        dishes = conn.execute(
            "SELECT id, name, description, price, category "
            "FROM dishes WHERE available = TRUE ORDER BY id"
        ).fetchall()
        tables = conn.execute(
            "SELECT id, table_number, capacity, status "
            "FROM restaurant_tables ORDER BY table_number"
        ).fetchall()
        orders = conn.execute("""
            SELECT o.id, o.customer_name, o.status, o.total,
                   o.created_at, t.table_number
            FROM orders o
            LEFT JOIN restaurant_tables t ON t.id = o.table_id
            ORDER BY o.created_at DESC LIMIT 10
        """).fetchall()

    return render_template(
        "index.html", dishes=dishes, tables=tables, orders=orders
    )


@app.route("/orders", methods=["POST"])
def create_order():
    table_id = request.form.get("table_id", type=int)
    customer_name = request.form.get("customer_name", "").strip()
    dish_id = request.form.get("dish_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if not table_id or not dish_id or not quantity or quantity < 1:
        flash("Vui lòng chọn bàn, món ăn và số lượng hợp lệ.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        table = conn.execute(
            "SELECT status FROM restaurant_tables WHERE id = %s",
            (table_id,)
        ).fetchone()
        dish = conn.execute(
            "SELECT price FROM dishes WHERE id = %s AND available = TRUE",
            (dish_id,)
        ).fetchone()

        if not table or table[0] != "available":
            flash("Bàn không tồn tại hoặc hiện không trống.", "error")
            return redirect(url_for("index"))

        if not dish:
            flash("Món ăn không tồn tại hoặc đã ngừng phục vụ.", "error")
            return redirect(url_for("index"))

        price = dish[0]
        total = price * quantity
        order = conn.execute("""
            INSERT INTO orders (table_id, customer_name, total)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (table_id, customer_name or None, total)).fetchone()

        conn.execute("""
            INSERT INTO order_items (order_id, dish_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (order[0], dish_id, quantity, price))

        conn.execute("""
            UPDATE restaurant_tables SET status = 'occupied'
            WHERE id = %s
        """, (table_id,))

    flash("Đã tạo đơn hàng thành công.", "success")
    return redirect(url_for("index"))


@app.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    status = request.form.get("status")
    allowed = {"pending", "preparing", "served", "cancelled"}

    if status not in allowed:
        flash("Trạng thái đơn hàng không hợp lệ.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        order = conn.execute(
            "SELECT table_id, status FROM orders WHERE id = %s",
            (order_id,)
        ).fetchone()

        if not order:
            flash("Không tìm thấy đơn hàng.", "error")
            return redirect(url_for("index"))

        conn.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (status, order_id)
        )

        if status in {"served", "cancelled"} and order[0]:
            conn.execute("""
                UPDATE restaurant_tables SET status = 'available'
                WHERE id = %s
            """, (order[0],))

    flash("Đã cập nhật trạng thái đơn hàng.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}, 200
    except Exception:
        app.logger.exception("Health check failed")
        return {"status": "error", "database": "disconnected"}, 503
