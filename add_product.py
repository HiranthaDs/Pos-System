import tkinter as tk
from tkinter import messagebox

class AddProductWindow:
    def __init__(self, root, db):
        self.db = db
        self.window = tk.Toplevel(root)
        self.window.title("Add New Product")
        self.window.geometry("400x300")

        # Variables
        self.barcode_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.price_var = tk.DoubleVar()
        self.quantity_var = tk.IntVar()

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.window, text="Barcode:").pack(anchor="w", padx=20, pady=5)
        tk.Entry(self.window, textvariable=self.barcode_var).pack(fill="x", padx=20)

        tk.Label(self.window, text="Name:").pack(anchor="w", padx=20, pady=5)
        tk.Entry(self.window, textvariable=self.name_var).pack(fill="x", padx=20)

        tk.Label(self.window, text="Price:").pack(anchor="w", padx=20, pady=5)
        tk.Entry(self.window, textvariable=self.price_var).pack(fill="x", padx=20)

        tk.Label(self.window, text="Quantity:").pack(anchor="w", padx=20, pady=5)
        tk.Entry(self.window, textvariable=self.quantity_var).pack(fill="x", padx=20)

        tk.Button(self.window, text="Add Product", command=self.add_product_to_db).pack(pady=20)

    def add_product_to_db(self):
        barcode = self.barcode_var.get()
        name = self.name_var.get()
        price = self.price_var.get()
        quantity = self.quantity_var.get()

        if not barcode or not name or price <= 0 or quantity <= 0:
            messagebox.showerror("Error", "Please enter valid product details.")
            return

        if self.db.add_product(barcode, name, price, quantity):
            messagebox.showinfo("Success", "Product added successfully.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Product with this barcode already exists.")
