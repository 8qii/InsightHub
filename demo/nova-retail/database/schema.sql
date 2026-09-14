CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    segment TEXT NOT NULL CHECK (segment IN ('Standard', 'Premium', 'VIP')),
    region TEXT NOT NULL CHECK (region IN ('Northeast', 'Southeast', 'Midwest', 'West')),
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price > 0)
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    amount NUMERIC(14, 2) NOT NULL CHECK (amount > 0),
    order_date DATE NOT NULL
);

CREATE TABLE payments (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(id),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('paid', 'pending', 'refunded')),
    amount NUMERIC(14, 2) NOT NULL CHECK (amount > 0)
);

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    warehouse TEXT NOT NULL CHECK (warehouse IN ('East Hub', 'Central Hub', 'West Hub')),
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE discount_events (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    discount_percent NUMERIC(5, 2) NOT NULL CHECK (discount_percent >= 0 AND discount_percent <= 100),
    approved BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_customers_segment_region ON customers (segment, region);
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
CREATE INDEX idx_orders_product_date ON orders (product_id, order_date);
CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_payments_status ON payments (payment_status);
CREATE INDEX idx_inventory_product ON inventory (product_id);
CREATE INDEX idx_inventory_updated_at ON inventory (updated_at);
CREATE INDEX idx_discount_events_order ON discount_events (order_id);
CREATE INDEX idx_discount_events_compliance ON discount_events (discount_percent, approved);
