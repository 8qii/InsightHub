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
    price NUMERIC(12, 2) NOT NULL CHECK (price > 0),
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0 AND unit_cost < price)
);

CREATE TABLE warehouses (
    id SMALLINT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    region TEXT NOT NULL CHECK (region IN ('Northeast', 'Southeast', 'Midwest', 'West'))
);

-- product_id, quantity, and amount are retained for the original single-line API contract.
-- New analytics use order_items as the authoritative line-item grain.
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    amount NUMERIC(14, 2) NOT NULL CHECK (amount > 0),
    order_date DATE NOT NULL,
    region TEXT NOT NULL CHECK (region IN ('Northeast', 'Southeast', 'Midwest', 'West')),
    sales_channel TEXT NOT NULL CHECK (sales_channel IN ('Web', 'Mobile', 'Marketplace'))
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price > 0),
    discount_amount NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    cost_basis NUMERIC(14, 2) NOT NULL CHECK (cost_basis >= 0),
    UNIQUE (id, order_id),
    CHECK (discount_amount <= quantity * unit_price)
);

CREATE TABLE returns (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    order_item_id BIGINT NOT NULL,
    returned_quantity INTEGER NOT NULL CHECK (returned_quantity > 0),
    return_date DATE NOT NULL,
    reason TEXT NOT NULL CHECK (reason IN ('Damaged', 'Changed mind', 'Incorrect item', 'Quality concern')),
    refund_amount NUMERIC(14, 2) NOT NULL CHECK (refund_amount > 0),
    FOREIGN KEY (order_item_id, order_id) REFERENCES order_items(id, order_id)
);

CREATE TABLE payments (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(id),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('paid', 'pending', 'refunded')),
    amount NUMERIC(14, 2) NOT NULL CHECK (amount > 0)
);

-- Compatibility projection for the original inventory API. This is the latest
-- aggregate position per product; temporal and warehouse analysis uses snapshots.
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE REFERENCES products(id),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    warehouse TEXT NOT NULL CHECK (warehouse IN ('East Hub', 'Central Hub', 'West Hub')),
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE inventory_snapshots (
    id BIGINT PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    warehouse_id SMALLINT NOT NULL REFERENCES warehouses(id),
    snapshot_date DATE NOT NULL,
    on_hand_quantity INTEGER NOT NULL CHECK (on_hand_quantity >= 0),
    reserved_quantity INTEGER NOT NULL CHECK (reserved_quantity >= 0),
    received_at DATE NOT NULL,
    UNIQUE (product_id, warehouse_id, snapshot_date),
    CHECK (reserved_quantity <= on_hand_quantity),
    CHECK (received_at <= snapshot_date)
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
CREATE INDEX idx_orders_region_channel_date ON orders (region, sales_channel, order_date);
CREATE INDEX idx_order_items_order ON order_items (order_id);
CREATE INDEX idx_order_items_product ON order_items (product_id);
CREATE INDEX idx_returns_item_date ON returns (order_item_id, return_date);
CREATE INDEX idx_returns_date ON returns (return_date);
CREATE INDEX idx_inventory_snapshots_product_date ON inventory_snapshots (product_id, snapshot_date);
CREATE INDEX idx_inventory_snapshots_warehouse_date ON inventory_snapshots (warehouse_id, snapshot_date);
CREATE INDEX idx_discount_events_order ON discount_events (order_id);
CREATE INDEX idx_discount_events_compliance ON discount_events (discount_percent, approved);
