import sqlite3
from datetime import datetime

class POSSystem:
    def __init__(self, db_name):
        self.db_name = db_name
        self.cart = {}

    def setup_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Create tables for inventory and transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
                )
            """)
            conn.commit()

    def add_product(self):
        name = input("Enter product name: ").strip()
        try:
            price = float(input("Enter product price: ").strip())
            stock = int(input("Enter stock quantity: ").strip())
        except ValueError:
            print("Invalid input. Price and stock must be numbers.")
            return

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO inventory (name, price, stock)
                    VALUES (?, ?, ?)
                """, (name, price, stock))
                conn.commit()
                print(f"Product '{name}' added successfully.")
            except sqlite3.IntegrityError:
                print(f"Product '{name}' already exists.")

    def view_inventory(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, stock FROM inventory")
            products = cursor.fetchall()

        if not products:
            print("No products in inventory.")
            return

        print("\n=== Inventory ===")
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: ${product[2]:.2f}, Stock: {product[3]}")

    def add_item_to_cart(self):
        product_id = input("Enter product ID: ").strip()
        try:
            quantity = int(input("Enter quantity: ").strip())
        except ValueError:
            print("Invalid input. Quantity must be a number.")
            return

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, price, stock FROM inventory WHERE id = ?", (product_id,))
            product = cursor.fetchone()

        if not product:
            print("Product not found.")
            return

        name, price, stock = product
        if quantity > stock:
            print(f"Insufficient stock. Only {stock} available.")
            return

        if name in self.cart:
            self.cart[name]['quantity'] += quantity
        else:
            self.cart[name] = {'price': price, 'quantity': quantity}

        print(f"Added {quantity} {name}(s) to the cart.")

    def view_cart(self):
        if not self.cart:
            print("Your cart is empty.")
            return

        print("\n=== Cart Items ===")
        total = 0
        for item, details in self.cart.items():
            subtotal = details['price'] * details['quantity']
            total += subtotal
            print(f"{item} - {details['quantity']} x ${details['price']:.2f} = ${subtotal:.2f}")
        print(f"Total: ${total:.2f}")

    def checkout(self):
        if not self.cart:
            print("Your cart is empty. Add items before checking out.")
            return

        self.view_cart()
        confirm = input("Do you want to proceed to checkout? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Checkout cancelled.")
            return

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Record the transaction
            total = sum(details['price'] * details['quantity'] for details in self.cart.values())
            cursor.execute("INSERT INTO transactions (timestamp, total) VALUES (?, ?)",
                           (datetime.now(), total))
            transaction_id = cursor.lastrowid

            # Record transaction details and update inventory
            for item, details in self.cart.items():
                cursor.execute("""
                    INSERT INTO transaction_details (transaction_id, product_name, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, (transaction_id, item, details['quantity'], details['price']))
                cursor.execute("""
                    UPDATE inventory
                    SET stock = stock - ?
                    WHERE name = ?
                """, (details['quantity'], item))
            conn.commit()

        print("Checkout successful. Thank you for your purchase!")
        self.cart.clear()
