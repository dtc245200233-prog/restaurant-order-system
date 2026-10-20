CREATE TABLE IF NOT EXISTS dishes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    category VARCHAR(100) NOT NULL,
    available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS restaurant_tables (
    id SERIAL PRIMARY KEY,
    table_number VARCHAR(20) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'available'
        CHECK (status IN ('available', 'occupied', 'reserved'))
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES restaurant_tables(id),
    customer_name VARCHAR(150),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'preparing', 'served', 'cancelled')),
    total NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (total >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    dish_id INTEGER NOT NULL REFERENCES dishes(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0)
);

INSERT INTO dishes (name, description, price, category) VALUES
('Phở bò', 'Phở bò truyền thống', 45000, 'Món chính'),
('Cơm gà', 'Cơm gà thơm ngon', 40000, 'Món chính'),
('Trà đào', 'Trà đào mát lạnh', 25000, 'Đồ uống')
ON CONFLICT DO NOTHING;

INSERT INTO restaurant_tables (table_number, capacity) VALUES
('B01', 4),
('B02', 4),
('B03', 6),
('B04', 2)
ON CONFLICT (table_number) DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE
ON dishes, restaurant_tables, orders, order_items
TO restaurant_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO restaurant_app;
