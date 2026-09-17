-- schema.sql
-- Relational schema for the e-commerce dataset.
-- Mirrors the structure of the Power BI data model (GymBeam portfolio dashboard).

PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    CategoryID   TEXT PRIMARY KEY,
    CategoryName TEXT NOT NULL
);

CREATE TABLE customers (
    CustomerID   TEXT PRIMARY KEY,
    CustomerName TEXT NOT NULL,
    Segment      TEXT,
    Country      TEXT
);

CREATE TABLE products (
    ProductID     TEXT PRIMARY KEY,
    ProductName   TEXT NOT NULL,
    CategoryID    TEXT NOT NULL,
    RegularPrice  REAL NOT NULL,
    Cost          REAL NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES categories (CategoryID)
);

CREATE TABLE date_dim (
    Date      TEXT PRIMARY KEY,
    Year      INTEGER NOT NULL,
    Month     INTEGER NOT NULL,
    MonthName TEXT NOT NULL,
    Quarter   TEXT NOT NULL,
    Week      INTEGER NOT NULL
);

CREATE TABLE orders (
    OrderID     TEXT PRIMARY KEY,
    OrderDate   TEXT NOT NULL,
    CustomerID  TEXT NOT NULL,
    Status      TEXT NOT NULL,
    TotalAmount REAL NOT NULL,
    TotalMargin REAL NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES customers (CustomerID)
);

CREATE TABLE order_details (
    OrderDetailID TEXT PRIMARY KEY,
    OrderID       TEXT NOT NULL,
    ProductID     TEXT NOT NULL,
    Quantity      INTEGER NOT NULL,
    OriginalPrice REAL NOT NULL,
    DiscountPct   REAL NOT NULL,
    SalePrice     REAL NOT NULL,
    Cost          REAL NOT NULL,
    LineTotal     REAL NOT NULL,
    MarginEUR     REAL NOT NULL,
    MarginPct     REAL NOT NULL,
    ReturnReason  TEXT,
    FOREIGN KEY (OrderID) REFERENCES orders (OrderID),
    FOREIGN KEY (ProductID) REFERENCES products (ProductID)
);

-- Helpful indexes for join-heavy analytical queries
CREATE INDEX idx_orderdetails_orderid ON order_details (OrderID);
CREATE INDEX idx_orderdetails_productid ON order_details (ProductID);
CREATE INDEX idx_orders_customerid ON orders (CustomerID);
CREATE INDEX idx_products_categoryid ON products (CategoryID);
