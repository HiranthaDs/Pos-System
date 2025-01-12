import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from add_product import AddProductWindow  # Assumes add_product.py is present
from database import Database  # Assumes database.py is present
from datetime import datetime
import os


class POSMainPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Supermarket POS System")
        self.root.geometry("900x650")

        # Database
        self.db = Database()

        # Variables
        self.total_var = tk.DoubleVar(value=0.0)
        self.purchase_list = []
        self.search_var = tk.StringVar()
        self.search_name_var = tk.StringVar()  # Variable for name search
        self.discount_var = tk.DoubleVar(value=0.0)  # Variable for discount

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        # Search Entry Fields
        tk.Label(self.root, text="Search Product by Barcode:").place(x=50, y=20)
        search_entry = tk.Entry(self.root, textvariable=self.search_var)
        search_entry.place(x=180, y=20, width=300)
        search_entry.bind('<Return>', self.add_product_by_barcode)  # Trigger event on "Enter" key press

        tk.Label(self.root, text="Search Product by Name:").place(x=50, y=60)

        # Combobox for product name search with suggestions
        self.search_name_combobox = ttk.Combobox(self.root, textvariable=self.search_name_var, state="normal")
        self.search_name_combobox.place(x=180, y=60, width=300)

        # Bind the event to update suggestions on typing
        self.search_name_combobox.bind("<KeyRelease>", self.update_suggestions)
        self.search_name_combobox.bind('<Return>', self.add_product_by_name)

        # Add Manually Button
        tk.Button(self.root, text="Add Manually", command=self.add_product_manually, bg="#6d899c", fg="white").place(
            x=500, y=18)

        # Purchase List Table
        self.tree = ttk.Treeview(self.root, columns=("Name", "Quantity", "Price", "Total"), show="headings")
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Total", text="Total")
        self.tree.column("Name", width=200)
        self.tree.column("Quantity", width=100)
        self.tree.column("Price", width=100)
        self.tree.column("Total", width=100)
        self.tree.place(x=50, y=100, width=800, height=350)

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.place(x=50, y=550, width=800, height=50)

        # Print Receipt Button
        tk.Button(btn_frame, text="Print Receipt", command=self.print_receipt, width=15, bg="#3cb371", fg="white").grid(
            row=0, column=0, padx=10)

        # Add New Product Button
        tk.Button(btn_frame, text="Add New Product", command=self.add_new_product, width=15, bg="#2e7bff",
                  fg="white").grid(row=0, column=1, padx=10)

        # Delete Button
        delete_btn = tk.Button(
            btn_frame,
            text="Delete Selected",
            command=self.delete_selected,
            width=15,
            bg="#ff4b5b",
            fg="white"
        )
        delete_btn.grid(row=0, column=2, padx=10)

        # Modify Button
        modify_btn = tk.Button(
            btn_frame,
            text="Modify Product",
            command=self.modify_selected_product,
            width=15,
            bg="#2e7bff",
            fg="white"
        )
        modify_btn.grid(row=0, column=3, padx=10)

        # Discount Button
        tk.Button(
            self.root,
            text="Apply Discount",
            command=self.apply_discount,
            width=15,
            bg="#2e7bff",
            fg="white"
        ).place(x=750, y=620)

        # Total Label
        tk.Label(self.root, text="Total:").place(x=750, y=520)
        tk.Label(self.root, textvariable=self.total_var, font=("Arial", 14)).place(x=800, y=520)

        # Before Total, Discount and Final Total Labels
        self.before_total_var = tk.DoubleVar(value=0.0)
        self.discount_var_display = tk.DoubleVar(value=0.0)
        tk.Label(self.root, text="Before Total:").place(x=750, y=550)
        tk.Label(self.root, textvariable=self.before_total_var, font=("Arial", 10)).place(x=830, y=550)

        tk.Label(self.root, text="Discount:").place(x=750, y=580)
        tk.Label(self.root, textvariable=self.discount_var_display, font=("Arial", 10)).place(x=830, y=580)

    def update_suggestions(self, event):
        """Update suggestions in the Combobox as the user types"""
        query = self.search_name_var.get().strip()
        if query:
            matching_products = self.db.search_products_by_name(query)  # Modify this method in your Database class
            suggestions = [product[1] for product in matching_products]  # Assuming product[1] is the product name
            self.search_name_combobox['values'] = suggestions
            self.search_name_combobox.set(query)  # Keep the current query in the box
        else:
            self.search_name_combobox['values'] = []

    def add_product_by_barcode(self, event=None):
        """Fetch product by barcode and add details to the table."""
        barcode = self.search_var.get().strip()
        if not barcode:
            messagebox.showerror("Error", "Please enter a barcode.")
            return

        product = self.db.get_product_by_barcode(barcode)
        if not product:
            messagebox.showerror("Error", f"Product with barcode '{barcode}' not found.")
            return

        name, price = product[1], product[2]

        # Ask for the quantity of the product
        quantity = simpledialog.askinteger(
            "Select Quantity",
            f"Enter quantity to add for '{name}':",
            minvalue=1
        )
        if not quantity:
            return

        total_price = price * quantity
        self.purchase_list.append({
            "name": name,
            "quantity": quantity,
            "price": price,
            "total": total_price
        })
        self.update_table()
        self.search_var.set("")  # Clear the barcode search field

    def add_product_by_name(self, event=None):
        """Fetch product by name and add details to the table."""
        product_name = self.search_name_var.get().strip()
        if not product_name:
            messagebox.showerror("Error", "Please enter a product name.")
            return

        products = self.db.get_products_by_name(product_name)
        if not products:
            messagebox.showerror("Error", f"No products found for '{product_name}'.")
            return

        product = products[0]  # Get the first matching product
        name, price = product[1], product[2]

        # Ask for the quantity of the product
        quantity = simpledialog.askinteger(
            "Select Quantity",
            f"Enter quantity to add for '{name}':",
            minvalue=1
        )
        if not quantity:
            return

        total_price = price * quantity
        self.purchase_list.append({
            "name": name,
            "quantity": quantity,
            "price": price,
            "total": total_price
        })
        self.update_table()
        self.search_name_var.set("")  # Clear the name search field

    def update_table(self):
        """Update the Treeview table."""
        self.tree.delete(*self.tree.get_children())
        total_amount = 0.0
        for item in self.purchase_list:
            self.tree.insert("", "end", values=(item["name"], item["quantity"], item["price"], item["total"]))
            total_amount += item["total"]

        # Update before total, discount and final total
        self.before_total_var.set(total_amount)
        total_amount_after_discount = total_amount * (1 - self.discount_var.get() / 100)
        self.discount_var_display.set(self.discount_var.get())
        self.total_var.set(total_amount_after_discount)

    def delete_selected(self):
        """Delete selected item from the table."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        for item in selected_item:
            values = self.tree.item(item, "values")
            product_name = values[0]

            # Find the product in the purchase list and remove it
            self.purchase_list = [p for p in self.purchase_list if p["name"] != product_name]
            self.tree.delete(item)

        self.update_table()

    def modify_selected_product(self):
        """Modify the price of the selected product by barcode or name."""
        # Ask the user to choose whether they want to modify by barcode or name
        modify_choice = simpledialog.askstring(
            "Modify Product",
            "Choose method to modify product (Enter 'barcode' or 'name'):"
        )
        if modify_choice is None:
            messagebox.showerror("Error", "Please enter a valid choice (either 'barcode' or 'name').")
            return

        modify_choice = modify_choice.strip().lower()

        if modify_choice not in ['barcode', 'name']:
            messagebox.showerror("Error", "Please enter a valid choice (either 'barcode' or 'name').")
            return

        if modify_choice == 'barcode':
            barcode = simpledialog.askstring("Enter Barcode", "Enter the barcode of the product to modify:")
            if not barcode:
                return

            # Search for the product by barcode
            product = self.db.get_product_by_barcode(barcode)
            if not product:
                messagebox.showerror("Error", f"Product with barcode '{barcode}' not found.")
                return
            name, old_price = product[1], product[2]  # Get name and price from the database

        else:
            name = simpledialog.askstring("Enter Name", "Enter the name of the product to modify:")
            if not name:
                return

            # Search for the product by name
            products = self.db.get_products_by_name(name)
            if not products:
                messagebox.showerror("Error", f"Product with name '{name}' not found.")
                return
            product = products[0]
            old_price = product[2]

        new_price = simpledialog.askfloat("New Price", f"Enter the new price for '{name}':", minvalue=0.0)
        if new_price is None:
            return

        # Modify the price in the purchase list
        for item in self.purchase_list:
            if item["name"] == name:
                item["price"] = new_price
                item["total"] = item["quantity"] * new_price
                break

        self.update_table()

        messagebox.showinfo("Success", f"Price for '{name}' updated successfully.")

    def print_receipt(self):
        """Save and print receipt."""
        if not self.purchase_list:
            messagebox.showerror("Error", "No items to print.")
            return

        # Generate receipt content
        receipt_content = "Receipt\n"
        receipt_content += "----------------------------------\n"
        for item in self.purchase_list:
            receipt_content += f"{item['name']} - {item['quantity']} x {item['price']} = {item['total']}\n"
        receipt_content += "----------------------------------\n"
        receipt_content += f"Total: {self.total_var.get()}\n"
        receipt_content += f"Discount: {self.discount_var.get()}%\n"
        receipt_content += f"Total after Discount: {self.total_var.get()}\n"
        receipt_content += f"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Save receipt to file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Receipt"
        )
        if file_path:
            with open(file_path, "w") as file:
                file.write(receipt_content)
            messagebox.showinfo("Saved", f"Receipt saved to {file_path}")

            # Print the receipt
            try:
                os.startfile(file_path, "print")
            except Exception as e:
                messagebox.showerror("Print Error", f"Failed to print receipt: {e}")

    def apply_discount(self):
        """Prompt the user to apply a discount."""
        discount = simpledialog.askfloat("Apply Discount", "Enter discount percentage (0-100):", minvalue=0.0,
                                         maxvalue=100.0)
        if discount is not None:
            self.discount_var.set(discount)
            self.update_table()

    def add_product_manually(self):
        """Open Add Product window to add a product manually."""
        AddProductWindow(self.root, self.db)

    def add_new_product(self):
        """Open Add Product window to register a new product."""
        AddProductWindow(self.root, self.db)


if __name__ == "__main__":
    root = tk.Tk()
    app = POSMainPage(root)
    root.mainloop()
