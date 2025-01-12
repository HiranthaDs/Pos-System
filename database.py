import sqlite3

class Database:
    def __init__(self, db_name="products.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Create the products table if it doesn't already exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
        """)
        self.connection.commit()

    def add_product(self, barcode, name, price, quantity):
        """Add a new product to the database."""
        try:
            self.cursor.execute("""
            INSERT INTO products (barcode, name, price, quantity)
            VALUES (?, ?, ?, ?)
            """, (barcode, name, price, quantity))
            self.connection.commit()
        except sqlite3.IntegrityError:
            return "Error: Product with this barcode already exists."

    def get_product_by_barcode(self, barcode):
        """Fetch product details by barcode."""
        self.cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        return self.cursor.fetchone()

    def get_products_by_name(self, name):
        """Search for products by name."""
        self.cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + name + '%',))
        return self.cursor.fetchall()

    def update_product_quantity(self, barcode, new_quantity):
        """Update the quantity of a product."""
        self.cursor.execute("""
        UPDATE products
        SET quantity = ?
        WHERE barcode = ?
        """, (new_quantity, barcode))
        self.connection.commit()

    def close_connection(self):
        """Close the database connection."""
        self.connection.close()
