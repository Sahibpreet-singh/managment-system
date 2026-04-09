import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date
from ui.login_ui import SUPERADMIN_PASSWORD

from ui.customer_item_ui import CustomerItemUI
from models.report_model import get_all_customer_items   # ← READ DATA ONLY


class MainWindow:
    
    def __init__(self, root, user):
        self.root = root
        self.user = user  # admin or superadmin

        # Zoom functionality
        self.zoom_level = 1.2  # Default at 120% zoom
        self.base_font_size = 9
        self.base_header_font_size = 10
        self.base_row_height = 25

        self.root.title("Sandhu Enterprises – EMI Management System")
        
        # Maximize window
        self.root.state("zoomed")   # ← maximized on Windows
        self.root.resizable(True, True)  # allow resizing if needed

        self.create_header()
        self.create_menu()
        self.create_content_area()


    # ================= HEADER =================
    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#34495e")
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="🏢 Sandhu Enterprises",
            font=("Segoe UI", 20, "bold"),
            bg="#34495e",
            fg="white",
            pady=15
        ).pack(side=tk.LEFT, padx=25)

        tk.Label(
            header_frame,
            text="EMI Management System",
            font=("Segoe UI", 16),
            bg="#34495e",
            fg="#bdc3c7",
            pady=15
        ).pack(side=tk.LEFT, padx=15)

        # User info and zoom controls
        zoom_frame = tk.Frame(header_frame, bg="#34495e")
        zoom_frame.pack(side=tk.RIGHT, padx=25)
        
        tk.Label(
            zoom_frame,
            text="🔍 Zoom:",
            font=("Segoe UI", 10),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack(side=tk.LEFT, padx=(0,5))
        
        tk.Button(
            zoom_frame,
            text="➖",
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            width=3,
            command=self.zoom_out
        ).pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = tk.Label(
            zoom_frame,
            text="120%",
            font=("Segoe UI", 10, "bold"),
            bg="#34495e",
            fg="#ecf0f1",
            width=5
        )
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            zoom_frame,
            text="➕",
            font=("Segoe UI", 10, "bold"),
            bg="#27ae60",
            fg="white",
            width=3,
            command=self.zoom_in
        ).pack(side=tk.LEFT, padx=2)

        user_text = f"👤 {self.user.get('username', 'User')}" if self.user else "👤 Guest"
        tk.Label(
            header_frame,
            text=user_text,
            font=("Segoe UI", 12),
            bg="#34495e",
            fg="#ecf0f1",
            pady=15
        ).pack(side=tk.RIGHT, padx=(25,0))

    # ================= LEFT MENU =================
    def create_menu(self):
        menu_frame = tk.Frame(self.root, bg="#34495e", width=220)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Menu title
        tk.Label(
            menu_frame,
            text="📋 Menu",
            font=("Segoe UI", 16, "bold"),
            bg="#34495e",
            fg="white",
            pady=15
        ).pack(fill=tk.X)

        buttons = [
            ("🏠 Home", self.show_home),
            ("👥 Customers", self.open_customers),
            ("📊 Records", self.open_items),   # renamed logically
            ("💰 Payments", self.open_payments),
            ("➕ Record Payment", self.open_record_payment),
            ("🚪 Exit", self.root.quit)
        ]

        for text, command in buttons:
            btn = tk.Button(
                menu_frame,
                text=text,
                font=("Segoe UI", 12, "bold"),
                width=20,
                pady=12,
                bg="#3498db",
                fg="white",
                activebackground="#2980b9",
                activeforeground="white",
                relief="flat",
                borderwidth=0,
                command=command
            )
            btn.pack(pady=8, padx=10)
            # Separator
            sep = tk.Frame(menu_frame, height=1, bg="#7f8c8d")
            sep.pack(fill=tk.X, padx=10)
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))

    # ================= HOME =================
    def show_home(self):
        """Clear content area and show the home/welcome screen."""
        self.content_frame.destroy()
        self.create_content_area()

    # ================= MAIN CONTENT =================
    def create_content_area(self):
        self.content_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Welcome container
        welcome_frame = tk.Frame(self.content_frame, bg="#f8f9fa")
        welcome_frame.pack(expand=True)

        # Main welcome title
        tk.Label(
            welcome_frame,
            text="🏢 Welcome to Sandhu Enterprises",
            font=("Arial", 24, "bold"),
            fg="#2c3e50",
            bg="#f8f9fa"
        ).pack(pady=(20, 5))

        tk.Label(
            welcome_frame,
            text="EMI Management System",
            font=("Arial", 18),
            fg="#34495e",
            bg="#f8f9fa"
        ).pack(pady=(0, 20))

        # Description
        tk.Label(
            welcome_frame,
            text="Manage customers, items, payments, and installments efficiently.\nSelect an option from the menu to get started.",
            font=("Arial", 12),
            fg="#7f8c8d",
            bg="#f8f9fa",
            justify="center"
        ).pack(pady=(0, 10))

        # Current Date
        from datetime import date
        current_date = date.today().strftime("%B %d, %Y")
        tk.Label(
            welcome_frame,
            text=f"Today: {current_date}",
            font=("Arial", 10, "italic"),
            fg="#34495e",
            bg="#f8f9fa"
        ).pack(pady=(0, 20))

        # Quick Actions
        actions_frame = tk.Frame(welcome_frame, bg="#f8f9fa")
        actions_frame.pack(pady=(10, 20))

        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=("Arial", 14, "bold"),
            fg="#2c3e50",
            bg="#f8f9fa"
        ).pack(pady=(0, 10))

        actions = [
            ("➕ Add Customer", self.add_customer),
            ("💰 Record Payment", self.open_record_payment),
            ("📊 View Records", self.open_items),
            ("🔍 Search Payments", self.open_payments)
        ]

        for text, command in actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                font=("Arial", 11, "bold"),
                width=18,
                pady=8,
                bg="#3498db",
                fg="white",
                activebackground="#2980b9",
                activeforeground="white",
                relief="raised",
                borderwidth=2,
                command=command
            )
            btn.pack(side=tk.LEFT, padx=10)
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))

        # Quick Stats Dashboard
        stats_frame = tk.Frame(welcome_frame, bg="#f8f9fa")
        stats_frame.pack(pady=(10, 20))

        # Store stat labels for refresh
        self.stat_labels = []

        # Get stats
        try:
            from models.customer_model import get_total_customers
            from models.item_model import get_total_items
            from models.payment_model import get_total_payments, get_total_due
            total_customers = get_total_customers()
            total_items = get_total_items()
            total_payments = get_total_payments()
            total_due = get_total_due()
        except Exception:
            total_customers = total_items = total_payments = total_due = 0

        stats = [
            ("👥 Total Customers", total_customers, "#3498db"),
            ("📦 Total Items", total_items, "#e74c3c"),
            ("💰 Total Payments", f"₹{total_payments:,.0f}", "#27ae60"),
            ("📊 Total Due", f"₹{total_due:,.0f}", "#f39c12")
        ]

        for i, (label, value, color) in enumerate(stats):
            stat_card = tk.Frame(stats_frame, bg=color, bd=2, relief="raised")
            stat_card.grid(row=0, column=i, padx=10, pady=5, ipadx=20, ipady=10)

            tk.Label(
                stat_card,
                text=label,
                font=("Arial", 10, "bold"),
                fg="white",
                bg=color
            ).pack()

            value_label = tk.Label(
                stat_card,
                text=str(value),
                font=("Arial", 16, "bold"),
                fg="white",
                bg=color
            )
            value_label.pack()
            self.stat_labels.append(value_label)

        # Refresh button
        tk.Button(
            welcome_frame,
            text="🔄 Refresh Stats",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=self.refresh_welcome_stats
        ).pack(pady=(10, 0))

    def refresh_welcome_stats(self):
        """Refresh the stats displayed on the welcome screen."""
        try:
            from models.customer_model import get_total_customers
            from models.item_model import get_total_items
            from models.payment_model import get_total_payments, get_total_due
            total_customers = get_total_customers()
            total_items = get_total_items()
            total_payments = get_total_payments()
            total_due = get_total_due()
        except Exception:
            total_customers = total_items = total_payments = total_due = 0

        stats = [
            total_customers,
            total_items,
            f"₹{total_payments:,.0f}",
            f"₹{total_due:,.0f}"
        ]

        for i, value in enumerate(stats):
            if i < len(self.stat_labels):
                self.stat_labels[i].config(text=str(value))

    def zoom_in(self):
        """Increase zoom level and refresh all grids."""
        if self.zoom_level < 2.0:
            self.zoom_level += 0.1
            self.update_zoom_display()
            self.refresh_all_grids()

    def zoom_out(self):
        """Decrease zoom level and refresh all grids."""
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.1
            self.update_zoom_display()
            self.refresh_all_grids()

    def update_zoom_display(self):
        """Update the zoom percentage display in the header."""
        if hasattr(self, 'zoom_label'):
            percentage = int(self.zoom_level * 100)
            self.zoom_label.config(text=f"{percentage}%")

    def refresh_all_grids(self):
        """Refresh all currently visible grid layouts with new zoom level."""
        # Get current font sizes based on zoom
        current_font_size = int(self.base_font_size * self.zoom_level)
        current_header_font_size = int(self.base_header_font_size * self.zoom_level)
        current_row_height = int(self.base_row_height * self.zoom_level)

        # Update payment search grid cells if they exist
        if hasattr(self, 'grid_cells') and self.grid_cells:
            for cell in self.grid_cells:
                if cell.winfo_exists():
                    cell.config(font=("Segoe UI", current_font_size))

        # Update payment search header cells if they exist
        if hasattr(self, 'header_cells') and self.header_cells:
            for cell in self.header_cells:
                if cell.winfo_exists():
                    cell.config(font=("Segoe UI", current_header_font_size, "bold"))

        # Update installment grid cells if they exist
        if hasattr(self, 'installment_grid_cells') and self.installment_grid_cells:
            for cell in self.installment_grid_cells:
                if cell.winfo_exists():
                    cell.config(font=("Segoe UI", current_font_size))

        # Update installment header cells if they exist
        if hasattr(self, 'installment_header_cells') and self.installment_header_cells:
            for cell in self.installment_header_cells:
                if cell.winfo_exists():
                    cell.config(font=("Segoe UI", current_header_font_size, "bold"))

        # Update payment records grid cells if they exist
        if hasattr(self, 'records_grid_cells') and self.records_grid_cells:
            for cell in self.records_grid_cells:
                if cell.winfo_exists():
                    cell.config(font=("Segoe UI", current_font_size))

        # Update payment records header cells if they exist
        if hasattr(self, 'records_header_cells') and self.records_header_cells:
            for cell in self.records_header_cells:
                if cell.winfo_exists():
                    cell.config(font=("Segoe UI", current_header_font_size, "bold"))

        # Update canvas scroll region if needed
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.config(height=current_row_height * 20)  # Adjust based on visible rows

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def open_record_payment(self):
        """Open a dedicated Record Payment dialog (reusable from menu or Payments view)."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Record Payment")
        dlg.geometry("700x320")

        tk.Label(dlg, text="Select Item (type to search by customer/name/address/item):").pack(pady=6)
        item_cb = ttk.Combobox(dlg, width=120, state="normal")
        item_cb.pack(pady=4)

        # load items (only those with due > 0 by default)
        from models.report_model import search_customer_items as _search_items
        rows = _search_items({"status": "Unpaid"})
        item_full = []
        item_map = {}
        for r in rows:
            # show village and address together so address is always visible
            loc_parts = [p for p in (r.get('village_name'), r.get('customer_address')) if p]
            location = " / ".join(loc_parts)
            display = f"{r.get('item_id')} - {r.get('customer_name','')} - {location} - {r.get('brand') or ''} {r.get('model') or ''} - Due: {r.get('due_amount') or 0}"
            item_full.append(display)
            item_map[display] = r
        item_cb['values'] = item_full

        def _filter_items(event=None):
            val = item_cb.get().strip().lower()
            if not val:
                item_cb['values'] = item_full
                return
            matches = [s for s in item_full if val in s.lower()]
            item_cb['values'] = matches
            if matches:
                try:
                    item_cb.event_generate('<Down>')
                except Exception:
                    pass

        item_cb.bind('<KeyRelease>', _filter_items)

        from decimal import Decimal
        due_var = tk.StringVar(value="Due: -")
        tk.Label(dlg, textvariable=due_var).pack(pady=6)

        def update_due(event=None):
            sel = item_cb.get()
            r = item_map.get(sel)
            if r:
                due_var.set(f"Due: {r.get('due_amount') or 0}")
        item_cb.bind('<<ComboboxSelected>>', update_due)

        tk.Label(dlg, text="Amount Paid (₹):").pack()
        amount_entry = tk.Entry(dlg)
        amount_entry.pack()

        tk.Label(dlg, text="Payment Date (DD-MM-YYYY):").pack()
        date_entry = tk.Entry(dlg)
        date_entry.insert(0, date.today().strftime('%d-%m-%Y'))
        date_entry.pack()

        def save_payment():
            sel = item_cb.get()
            r = item_map.get(sel)
            if not r:
                messagebox.showerror("Error", "Please select a valid item.")
                return
            try:
                amt = Decimal(str(amount_entry.get()))
            except Exception:
                messagebox.showerror("Error", "Invalid amount.")
                return
            due = r.get('due_amount') or 0
            due_d = Decimal(str(due))
            if amt <= 0 or amt > due_d:
                messagebox.showerror("Error", f"Amount must be >0 and <= due ({due_d})")
                return
            payment_date = date_entry.get().strip()
            try:
                # basic date format check - accept DD-MM-YYYY or YYYY-MM-DD
                if payment_date:
                    from datetime import datetime as _dt
                    try:
                        # Try DD-MM-YYYY first
                        parsed_date = _dt.strptime(payment_date, '%d-%m-%Y')
                        payment_date = parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        # Try YYYY-MM-DD
                        _dt.strptime(payment_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Payment date must be DD-MM-YYYY or YYYY-MM-DD")
                return
            from models.payment_model import add_payment
            remaining = add_payment(r.get('item_id'), payment_date, amt, r.get('item_amount'))
            messagebox.showinfo("Success", f"Payment recorded. Remaining: {remaining}")
            dlg.destroy()
            # Refresh payments view if visible
            try:
                self.open_payments()
            except Exception:
                pass

        tk.Button(dlg, text="Save Payment", bg="#27ae60", fg="white", command=save_payment).pack(pady=10)

    # ================= CUSTOMERS =================
    def open_customers(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="Customer Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)

        tk.Button(
            self.content_frame,
            text="➕ Add Customer (with Item)",
            font=("Arial", 12),
            width=24,
            bg="#27ae60",
            fg="white",
            command=self.add_customer
        ).pack(pady=10)

    def add_customer(self):
        CustomerItemUI(self.root)   # correct usage

    def export_records(self, detail_map):
        # Simple export of currently loaded records to CSV
        import csv
        rows = list(detail_map.values())  # Get all row data from the detail map
        if not rows:
            messagebox.showinfo('Export', 'No records to export')
            return
        path = 'records_export.csv'
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['customer_id','name','address','village','brand'])
            for r in rows:
                w.writerow([r.get('customer_id'), r.get('customer_name'), r.get('customer_address'), r.get('village_name'), r.get('brand')])
        messagebox.showinfo('Export', f'Exported {len(rows)} records to {path}')

    # ================= RECORDS (OLD ITEMS) =================
    def open_items(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="Customer & Item Report",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)

        # Sorting function (works for string and numeric columns)
        def sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            try:
                l.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
            except Exception:
                l.sort(key=lambda t: (t[0] or "").lower(), reverse=reverse)
            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)
            tv.heading(col, command=lambda: sort_column(tv, col, not reverse))

        # Toolbar and table container
        toolbar = tk.Frame(self.content_frame, bg="#ffffff")
        toolbar.pack(fill=tk.X, padx=10, pady=(5, 0))
        tk.Button(toolbar, text="🔄 Refresh", command=lambda: populate(get_all_customer_items()), bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="📤 Export CSV", command=lambda: self.export_records(self.items_detail_map), bg="#3498db", fg="white").pack(side=tk.LEFT)

        # ========== Table Frame ==========
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create scrollable canvas for the grid
        canvas = tk.Canvas(table_frame, bg="#ffffff")
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(self.content_frame, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # Column headers
        columns = ["Customer ID", "Name", "Address", "Village", "Brand"]
        column_widths = [100, 200, 300, 140, 140]
        
        # Create header row
        for col_idx, col_name in enumerate(columns):
            header_label = tk.Label(
                scrollable_frame, 
                text=col_name, 
                font=("Segoe UI", 10, "bold"),
                bg="#e1f5fe",
                fg="#000000",
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=5,
                width=column_widths[col_idx]//8 if col_idx < len(column_widths) else 10
            )
            header_label.grid(row=0, column=col_idx, sticky="nsew", padx=0, pady=0)

        # Function to create grid cell
        def create_grid_cell(parent, text, row, col, bg_color="#ffffff", fg_color="#000000"):
            cell_label = tk.Label(
                parent,
                text=text,
                font=("Segoe UI", 9),
                bg=bg_color,
                fg=fg_color,
                borderwidth=1,
                relief="solid",
                padx=3,
                pady=3,
                anchor="w",
                width=column_widths[col]//8 if col < len(column_widths) else 10
            )
            cell_label.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            return cell_label

        # Store references for data rows
        self.items_grid_labels = []
        self.items_detail_map = {}

        def populate(rows):
            # Clear existing data rows
            for row_labels in self.items_grid_labels:
                for label in row_labels:
                    label.destroy()
            self.items_grid_labels.clear()
            self.items_detail_map.clear()

            for row_idx, row in enumerate(rows):
                grid_row = row_idx + 1  # +1 because row 0 is header
                
                # Alternate row colors for better readability
                bg_color = '#ffffff' if row_idx % 2 == 0 else '#f6f6f6'
                fg_color = '#000000'

                # Create cells for this row
                values = [
                    row.get("customer_id") or "",
                    row.get("customer_name") or "",
                    row.get("customer_address") or "",
                    row.get("village_name") or "",
                    row.get("brand") or ""
                ]

                row_labels = []
                for col_idx, value in enumerate(values):
                    cell_label = create_grid_cell(scrollable_frame, str(value), grid_row, col_idx, bg_color, fg_color)
                    # Bind double-click to open details
                    cell_label.bind("<Double-1>", lambda e, r=row: self.show_customer_details(r, self.content_frame))
                    row_labels.append(cell_label)

                self.items_grid_labels.append(row_labels)
                self.items_detail_map[grid_row] = row

        # Make columns expandable
        for col_idx in range(len(columns)):
            scrollable_frame.grid_columnconfigure(col_idx, weight=1)

        # Fetch data and populate
        rows = get_all_customer_items()
        populate(rows)

    def show_customer_details(self, data, parent=None):
        """Show the customer/item detail dialog (used by Records and Payments)."""
        dlg = tk.Toplevel(parent or self.root)
        dlg.title(f"Customer {data.get('customer_id')} Details")
        dlg.geometry("1000x700")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(True, True)

        # Header
        header = tk.Frame(dlg, bg="#f5f7fa")
        header.pack(fill=tk.X)
        tk.Label(header, text=str(data.get("customer_name") or ""), font=("Segoe UI", 14, "bold"), bg="#f5f7fa").pack(anchor="w", padx=12, pady=(8, 0))
        tk.Label(header, text=f"ID: {data.get('customer_id') or ''}    •    Entry Date: {data.get('entry_date') or ''}", font=("Segoe UI", 9), bg="#f5f7fa").pack(anchor="w", padx=12, pady=(0, 8))

        # Scrollable area with vertical and horizontal support
        container = tk.Frame(dlg)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0, bg="#ffffff")
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        inner = tk.Frame(canvas, bg="#ffffff")
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_canvas_config(event):
            canvas.itemconfig(canvas_window, width=max(event.width, inner.winfo_reqwidth()))
        canvas.bind('<Configure>', _on_canvas_config)

        def _on_frame_config(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind('<Configure>', _on_frame_config)

        # Mouse-wheel scrolling for the canvas
        def _on_mousewheel(e):
            if hasattr(e, 'delta') and e.delta:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
            else:
                if getattr(e, 'num', None) == 4:
                    canvas.yview_scroll(-1, 'units')
                elif getattr(e, 'num', None) == 5:
                    canvas.yview_scroll(1, 'units')

        def _bind_canvas_scroll(ev):
            canvas.bind_all('<MouseWheel>', _on_mousewheel)
            canvas.bind_all('<Button-4>', _on_mousewheel)
            canvas.bind_all('<Button-5>', _on_mousewheel)

        def _unbind_canvas_scroll(ev):
            canvas.unbind_all('<MouseWheel>')
            canvas.unbind_all('<Button-4>')
            canvas.unbind_all('<Button-5>')

        inner.bind('<Enter>', _bind_canvas_scroll)
        inner.bind('<Leave>', _unbind_canvas_scroll)

        fields = [
            ("Customer ID", data.get("customer_id")),
            ("Name", data.get("customer_name")),
            ("Phone", data.get("customer_phone")),
            ("Address", data.get("customer_address")),
            ("Village", data.get("village_name")),
            ("Remarks", data.get("customer_remarks")),
            ("Entry Date", data.get("entry_date")),
            ("Brand", data.get("brand")),
            ("Model", data.get("model")),
            ("Item Amount", data.get("item_amount")),
            ("Advance", data.get("advance_amount")),
            ("Finance", data.get("finance_amount")),
            ("Interest (%)", (f"{data.get('interest_rate')}%" if ((data.get('interest_type','PERCENT') or '').upper().startswith('P')) else f"{data.get('interest_rate')} (amt)")),
            ("Interest Type", (data.get('interest_type') or '').upper()),

            ("Installment Amount", data.get("installment_amount")),
            ("Installment Mode", data.get("installment_mode")),
            ("Total Installments", data.get("total_installments")),
            ("Guarantor Name", data.get("guarantor_name")),
            ("Guarantor Phone", data.get("guarantor_phone")),
            ("Guarantor Address", data.get("guarantor_address"))
        ]

        # Render fields in a side-by-side two-column layout with separators to mimic cells
        # Split fields roughly in half so they display left/right to reduce vertical scrolling
        half = (len(fields) + 1) // 2
        left_fields = fields[:half]
        right_fields = fields[half:]

        # Make columns 1 and 3 expandable
        inner.grid_columnconfigure(1, weight=1)
        inner.grid_columnconfigure(3, weight=1)

        # Prepare interest values: show either percent or amount in separate fields
        interest_val = data.get('interest_rate')
        interest_type = (data.get('interest_type') or '').upper()
        interest_percent = f"{interest_val}%" if interest_val is not None and interest_type.startswith('P') else ""
        interest_amount = f"{interest_val}" if interest_val is not None and not interest_type.startswith('P') else ""

        # Sections: Customer, Item/Financial, Guarantor
        sections = [
            ("Customer Details", [
                ("Customer ID", data.get("customer_id")),
                ("Name", data.get("customer_name")),
                ("Phone", data.get("customer_phone")),
                ("Address", data.get("customer_address")),
                ("Village", data.get("village_name")),
                ("Remarks", data.get("customer_remarks")),
                ("Entry Date", data.get("entry_date")),
            ]),
            ("Item / Financial", [
                ("Brand", data.get("brand")),
                ("Model", data.get("model")),
                ("Item Amount", data.get("item_amount")),
                ("Advance", data.get("advance_amount")),
                ("Finance", data.get("finance_amount")),
                ("Interest (Percent)", interest_percent),
                ("Interest (Amount)", interest_amount),
                ("Interest Type", (data.get('interest_type') or '').upper()),
                ("Installment Amount", data.get("installment_amount")),
                ("Installment Mode", data.get("installment_mode")),
                ("Total Installments", data.get("total_installments")),
            ]),
            ("Guarantor", [
                ("Guarantor Name", data.get("guarantor_name")),
                ("Guarantor Phone", data.get("guarantor_phone")),
                ("Guarantor Address", data.get("guarantor_address")),
            ]),
        ]

        labels_map = {}
        current_row = 0

        for sec_title, sec_fields in sections:
                # Section header
                tk.Label(inner, text=sec_title, font=("Segoe UI", 15, "bold"), bg="#ffffff").grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(12,6))
                current_row += 1

                # split fields for two-column layout inside this section
                half = (len(sec_fields) + 1) // 2
                left_fields = sec_fields[:half]
                right_fields = sec_fields[half:]

                rows_sec = max(len(left_fields), len(right_fields))
                for i in range(rows_sec):
                    # Left column
                    if i < len(left_fields):
                        label_l, val_l = left_fields[i]
                        tk.Label(inner, text=f"{label_l}:", anchor="e", width=18, font=("Segoe UI", 14, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="e", padx=12, pady=(8,2))
                        val_lbl_l = tk.Label(inner, text=str(val_l) if val_l is not None else "", anchor="w", justify="left", wraplength=320, font=("Segoe UI", 14, "bold"), bg="#ffffff", bd=1, relief="groove")
                        val_lbl_l.grid(row=current_row, column=1, sticky="we", padx=6, pady=(8,2))
                        labels_map[label_l] = val_lbl_l
                    else:
                        tk.Label(inner, text="", bg="#ffffff").grid(row=current_row, column=0)
                        tk.Label(inner, text="", bg="#ffffff").grid(row=current_row, column=1)

                    # Right column
                    if i < len(right_fields):
                        label_r, val_r = right_fields[i]
                        tk.Label(inner, text=f"{label_r}:", anchor="e", width=18, font=("Segoe UI", 14, "bold"), bg="#ffffff").grid(row=current_row, column=2, sticky="e", padx=12, pady=(8,2))
                        val_lbl_r = tk.Label(inner, text=str(val_r) if val_r is not None else "", anchor="w", justify="left", wraplength=320, font=("Segoe UI", 14, "bold"), bg="#ffffff", bd=1, relief="groove")
                        val_lbl_r.grid(row=current_row, column=3, sticky="we", padx=6, pady=(8,2))
                        labels_map[label_r] = val_lbl_r
                    else:
                        tk.Label(inner, text="", bg="#ffffff").grid(row=current_row, column=2)
                        tk.Label(inner, text="", bg="#ffffff").grid(row=current_row, column=3)

                    current_row += 1

                # solid separator line for the section
                sep = tk.Frame(inner, height=2, bg="#2c3e50")
                sep.grid(row=current_row, column=0, columnspan=4, sticky="we", padx=8, pady=(8,0))
                current_row += 1

        # Payment history section
        tk.Label(inner, text="Payment History", font=("Segoe UI", 16, "bold"), bg="#ffffff").grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(12,4))
        current_row += 1

        payments = []
        item_id = data.get('item_id')
        if item_id:
            try:
                from models.payment_model import get_payments_by_item
                payments = get_payments_by_item(item_id)
            except Exception:
                payments = []

        if payments:
            ph_cols = ["Date", "Amount Paid", "Remaining"]
            ph_tree = ttk.Treeview(inner, columns=ph_cols, show="headings", height=6, style="Custom.Treeview")
            for pc in ph_cols:
                ph_tree.heading(pc, text=pc)
                ph_tree.column(pc, width=140, anchor="center")
            ph_tree.grid(row=current_row, column=0, columnspan=4, sticky="we", padx=12, pady=(4,12))
            for p in payments:
                ph_tree.insert("", "end", values=[p.get('payment_date'), p.get('amount_paid'), p.get('remaining_amount')])
            current_row += 1
        else:
            tk.Label(inner, text="No payment history.", fg="#666", bg="#ffffff", font=("Segoe UI", 14)).grid(row=current_row, column=0, columnspan=4, sticky="w", padx=12, pady=(4,12))
            current_row += 1

        # -- Edit flow: open modal to edit basic customer fields
        def open_edit_dialog():
            from models.customer_model import get_customer_by_id, update_customer
            from models.address_model import get_all_addresses, add_address
            from models.village_model import get_all_villages, add_village

            customer_id = data.get('customer_id')
            if not customer_id:
                messagebox.showerror("Error", "Cannot edit: missing customer id")
                return

            edit = tk.Toplevel(dlg)
            edit.title(f"Edit Customer {customer_id}")
            edit.transient(dlg)
            edit.grab_set()
            edit.resizable(False, False)

            # Form
            tk.Label(edit, text="Name:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
            name_e = tk.Entry(edit, width=40)
            name_e.grid(row=0, column=1, padx=8, pady=6)
            name_e.insert(0, data.get('customer_name') or "")

            tk.Label(edit, text="Phone:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
            phone_e = tk.Entry(edit, width=40)
            phone_e.grid(row=1, column=1, padx=8, pady=6)
            phone_e.insert(0, data.get('customer_phone') or "")

            tk.Label(edit, text="Address:").grid(row=2, column=0, padx=8, pady=6, sticky="e")
            addresses = get_all_addresses()
            address_list = [f"{a['address_id']} - {a['address']}" for a in addresses]
            address_cb = ttk.Combobox(edit, values=address_list, width=38, state="normal")
            address_cb.grid(row=2, column=1, padx=8, pady=6)
            # set current value (prefer address_id if available)
            if data.get('address_id'):
                current_addr = next((f"{a['address_id']} - {a['address']}" for a in addresses if a['address_id'] == data.get('address_id')), None)
                if current_addr:
                    address_cb.set(current_addr)
            else:
                address_cb.set(data.get('customer_address') or "")

            tk.Label(edit, text="Village:").grid(row=3, column=0, padx=8, pady=6, sticky="e")
            villages = get_all_villages()
            village_list = [f"{v['village_id']} - {v['name']}" for v in villages]
            village_cb = ttk.Combobox(edit, values=village_list, width=38, state="normal")
            village_cb.grid(row=3, column=1, padx=8, pady=6)
            if data.get('village_id'):
                current_vill = next((f"{v['village_id']} - {v['name']}" for v in villages if v['village_id'] == data.get('village_id')), None)
                if current_vill:
                    village_cb.set(current_vill)
            else:
                village_cb.set(data.get('village_name') or "")

            tk.Label(edit, text="Remarks:").grid(row=4, column=0, padx=8, pady=6, sticky="e")
            remarks_e = tk.Entry(edit, width=40)
            remarks_e.grid(row=4, column=1, padx=8, pady=6)
            remarks_e.insert(0, data.get('customer_remarks') or "")

            tk.Label(edit, text="Entry Date (DD-MM-YYYY):").grid(row=5, column=0, padx=8, pady=6, sticky="e")
            entry_date_e = tk.Entry(edit, width=40)
            entry_date_e.grid(row=5, column=1, padx=8, pady=6)
            entry_date_e.insert(0, data.get('entry_date') or "")

            # Buttons
            btn_frame = tk.Frame(edit)
            btn_frame.grid(row=6, column=0, columnspan=2, pady=(6,8))

            def on_save():
                name = name_e.get().strip()
                if not name:
                    messagebox.showerror("Error", "Name is required")
                    return
                phone = phone_e.get().strip()

                # Address handling: if the user selected or typed an id - text pair, parse id
                address_val = address_cb.get().strip()
                address_id = None
                address_text = None
                if address_val:
                    if " - " in address_val:
                        try:
                            address_id = int(address_val.split(" - ", 1)[0])
                            address_text = address_val.split(" - ", 1)[1]
                        except Exception:
                            address_id = None
                            address_text = address_val
                    else:
                        # create new address
                        try:
                            address_id = add_address(address_val)
                            address_text = address_val
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to add address: {e}")
                            return

                # Village handling similarly
                village_val = village_cb.get().strip()
                village_id = None
                if village_val:
                    if " - " in village_val:
                        try:
                            village_id = int(village_val.split(" - ", 1)[0])
                        except Exception:
                            village_id = None
                    else:
                        try:
                            village_id = add_village(village_val)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to add village: {e}")
                            return

                remarks = remarks_e.get().strip() or None
                entry_date_str = entry_date_e.get().strip() or None
                
                # Validate and convert entry date
                if entry_date_str:
                    try:
                        from datetime import datetime as _dt
                        try:
                            # Try DD-MM-YYYY first
                            parsed_date = _dt.strptime(entry_date_str, '%d-%m-%Y')
                            entry_date_str = parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            # Try YYYY-MM-DD
                            _dt.strptime(entry_date_str, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("Error", "Entry Date must be DD-MM-YYYY or YYYY-MM-DD")
                        return

                try:
                    update_customer(customer_id, name, phone, address_text, remarks, address_id, village_id, entry_date_str)
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    return

                # Refresh local data and UI
                new_data = get_customer_by_id(customer_id)
                if new_data:
                    data.update(new_data)

                # Update displayed labels for changed fields
                labels_map.get('Name').config(text=str(data.get('customer_name') or ""))
                labels_map.get('Phone').config(text=str(data.get('customer_phone') or ""))
                labels_map.get('Address').config(text=str(data.get('customer_address') or ""))
                labels_map.get('Village').config(text=str(data.get('village_name') or ""))
                labels_map.get('Remarks').config(text=str(data.get('customer_remarks') or ""))
                labels_map.get('Entry Date').config(text=str(data.get('entry_date') or ""))

                # Refresh the main table
                rows = get_all_customer_items()
                populate(rows)

                edit.destroy()
                messagebox.showinfo("Success", "Customer updated successfully")

            tk.Button(btn_frame, text="Save", command=on_save, bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=6)
            tk.Button(btn_frame, text="Cancel", command=edit.destroy).pack(side=tk.LEFT, padx=6)

        # Bottom action bar with Close
        action_bar = tk.Frame(dlg, bg="#ffffff")
        action_bar.pack(fill=tk.X)
        tk.Button(action_bar, text="Close", command=dlg.destroy, bg="#e74c3c", fg="white").pack(side=tk.RIGHT, padx=12, pady=8)
        tk.Button(action_bar, text="Edit", command=open_edit_dialog, bg="#3498db", fg="white").pack(side=tk.RIGHT, padx=12, pady=8)
        tk.Button(action_bar, text="Installment Details", command=lambda: self.show_installment_details(data.get('item_id'), dlg), bg="#8e44ad", fg="white").pack(side=tk.RIGHT, padx=12, pady=8)

        # Permanent delete (superadmin only)
        customer_id = data.get('customer_id')
        def on_permanent_delete():
            # Prompt for superadmin password (hidden)
            pwd = simpledialog.askstring("Superadmin Password", "Enter superadmin password to permanently delete customer:", show="*")
            if pwd is None:
                return
            if pwd != SUPERADMIN_PASSWORD:
                messagebox.showerror("Error", "Incorrect superadmin password")
                return

            if not messagebox.askyesno("Confirm Deletion", "Permanently delete this customer and all related records? This action cannot be undone."):
                return

            try:
                from models.customer_model import delete_customer
                delete_customer(customer_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {e}")
                return

            # Refresh main table and close dialog
            rows = get_all_customer_items()
            populate(rows)
            dlg.destroy()
            messagebox.showinfo("Success", "Customer permanently deleted")

        if self.user and (self.user.get('role') or '').lower() == 'superadmin':
            tk.Button(action_bar, text="Delete (Permanent)", command=on_permanent_delete, bg="#c0392b", fg="white").pack(side=tk.RIGHT, padx=12, pady=8)

        # Close on Escape
        dlg.bind('<Escape>', lambda e: dlg.destroy())

    def show_installment_details(self, item_id, parent=None):
        """Show installment schedule and allocation dialog for an item_id."""
        from models.item_model import get_item_by_id
        from models.payment_model import get_payments_by_item
        from services.emi_calculate import generate_due_dates
        from datetime import datetime, date as _date
        from tkinter import messagebox

        if not item_id:
            messagebox.showinfo("Info", "No item associated with this selection")
            return

        item = get_item_by_id(item_id)
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        # Parse start_date (DB may return date or string)
        start = item.get('start_date')
        if isinstance(start, str):
            try:
                start = datetime.strptime(start, '%Y-%m-%d').date()
            except Exception:
                start = _date.today()
        if not start:
            start = _date.today()

        total = int(item.get('total_installments') or 0)
        inst_amt = float(item.get('installment_amount') or 0)
        mode = item.get('installment_mode') or 'MONTHLY'

        due_dates = generate_due_dates(start, total, mode)

        payments = get_payments_by_item(item_id) or []

        # Prepare installments data
        installments = []
        for idx, dd in enumerate(due_dates, start=1):
            installments.append({
                'no': idx,
                'due_date': dd,
                'expected': inst_amt,
                'received': 0.0,
                'balance': inst_amt,
                'receipts': [],
                'remarks': ''
            })

        # Allocate payments to installments in chronological order
        for p in payments:
            amt = float(p.get('amount_paid') or 0)
            p_date = p.get('payment_date')
            p_id = p.get('payment_id') or p.get('id') or None

            # normalize payment date
            if isinstance(p_date, str):
                try:
                    p_date = datetime.strptime(p_date, '%Y-%m-%d').date()
                except Exception:
                    p_date = _date.today()

            i = 0
            while amt > 0 and i < len(installments):
                inst = installments[i]
                if inst['balance'] > 0:
                    apply_amt = min(amt, inst['balance'])
                    inst['received'] += apply_amt
                    inst['balance'] -= apply_amt
                    inst['receipts'].append({'payment_id': p_id, 'amount': apply_amt, 'payment_date': p_date})
                    amt = round(amt - apply_amt, 2)
                else:
                    i += 1

        # Compute derived fields for display
        today = _date.today()
        for inst in installments:
            # receipt ids
            r_ids = [str(r['payment_id']) for r in inst['receipts'] if r['payment_id']]
            inst['receipt_no'] = ','.join(r_ids)

            # received dates - collect all payment dates
            recv_dates = [r['payment_date'].strftime('%d-%m-%Y') if hasattr(r['payment_date'], 'strftime') else str(r['payment_date']) for r in inst['receipts'] if r['payment_date']]
            inst['received_dates'] = ', '.join(recv_dates) if recv_dates else ''

            # overdues received (payments that occurred after due date)
            overdue_received = sum(r['amount'] for r in inst['receipts'] if r['payment_date'] and r['payment_date'] > inst['due_date'])
            inst['overdue_received'] = round(overdue_received, 2)

            # determine overdays
            if inst['received'] >= inst['expected'] and inst['receipts']:
                # find date when installment was fully paid
                cum = 0
                full_date = None
                for r in inst['receipts']:
                    cum += r['amount']
                    if cum >= inst['expected']:
                        full_date = r['payment_date']
                        break
                if full_date:
                    inst['overdays'] = max(0, (full_date - inst['due_date']).days)
                else:
                    inst['overdays'] = 0
            else:
                # not fully paid
                inst['overdays'] = max(0, (today - inst['due_date']).days) if today > inst['due_date'] else 0

            # remarks
            if inst['received'] >= inst['expected']:
                inst['remarks'] = 'Paid'
                if inst['overdays'] > 0:
                    inst['remarks'] += f" (Late by {inst['overdays']}d)"
            elif inst['received'] > 0:
                inst['remarks'] = f"Partial ({inst['received']}/{inst['expected']})"
                if inst['overdays'] > 0:
                    inst['remarks'] += f" - Overdue {inst['overdays']}d"
            else:
                inst['remarks'] = 'Unpaid' + (f" - Overdue {inst['overdays']}d" if inst['overdays'] > 0 else '')

        # Build dialog
        dlg2 = tk.Toplevel(parent or self.root)
        dlg2.title(f"Installment Details for Item {item_id}")
        dlg2.geometry('1200x700')

        # Create scrollable canvas for the grid
        canvas = tk.Canvas(dlg2, bg="#ffffff")
        scrollbar_y = ttk.Scrollbar(dlg2, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(dlg2, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # Column headers
        columns = ["Sr No", "Installment Date", "Recv Date", "Receipt No", "Balance", "Remarks"]
        column_widths = [60, 120, 120, 150, 100, 200]
        
        # Create header row
        self.installment_header_cells = []
        for col_idx, col_name in enumerate(columns):
            header_label = tk.Label(
                scrollable_frame, 
                text=col_name, 
                font=("Segoe UI", int(self.base_header_font_size * self.zoom_level), "bold"),
                bg="#e1f5fe",
                fg="#000000",
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=5,
                width=column_widths[col_idx]//8 if col_idx < len(column_widths) else 10
            )
            header_label.grid(row=0, column=col_idx, sticky="nsew", padx=0, pady=0)
            self.installment_header_cells.append(header_label)

        # Function to create grid cell
        def create_grid_cell(parent, text, row, col, bg_color="#ffffff", fg_color="#000000"):
            cell_label = tk.Label(
                parent,
                text=text,
                font=("Segoe UI", int(self.base_font_size * self.zoom_level)),
                bg=bg_color,
                fg=fg_color,
                borderwidth=1,
                relief="solid",
                padx=3,
                pady=3,
                anchor="w",
                width=column_widths[col]//8 if col < len(column_widths) else 10
            )
            cell_label.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            return cell_label

        # Populate grid with installment data
        self.installment_grid_cells = []  # Store installment grid cells for zoom updates
        for row_idx, inst in enumerate(installments):
            grid_row = row_idx + 1  # +1 because row 0 is header
            
            # Determine row colors based on payment status
            if inst['received'] >= inst['expected']:
                bg_color = '#d4edda'  # Green for paid
                fg_color = '#155724'
            elif inst['received'] > 0:
                bg_color = '#fff3cd'  # Yellow for partial
                fg_color = '#856404'
            else:
                bg_color = '#f8d7da'  # Red for unpaid
                fg_color = '#721c24'

            # Create cells for this row
            values = [
                inst['no'],  # Sr No
                inst['due_date'].strftime('%d-%m-%Y') if hasattr(inst['due_date'], 'strftime') else str(inst['due_date']),  # Installment Date
                inst.get('received_dates', ''),  # Recv Date
                inst.get('receipt_no', ''),  # Receipt No
                f"₹{inst.get('balance', 0):.0f}",  # Balance
                inst.get('remarks', '')  # Remarks
            ]

            for col_idx, value in enumerate(values):
                cell_label = create_grid_cell(scrollable_frame, str(value), grid_row, col_idx, bg_color, fg_color)
                self.installment_grid_cells.append(cell_label)  # Store for zoom updates
                # Make cells clickable for potential future functionality
                cell_label.bind("<Double-1>", lambda e: None)

        # Make columns expandable
        for col_idx in range(len(columns)):
            scrollable_frame.grid_columnconfigure(col_idx, weight=1)

        # Close on escape
        dlg2.bind('<Escape>', lambda e: dlg2.destroy())

    # ================= PAYMENTS =================
    def open_payments(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="Payment Search & Filter",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)

        # ========== Filter Panel ==========
        filter_frame = tk.Frame(self.content_frame, bg="white")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Name:", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(filter_frame)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Phone:", bg="white").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        phone_entry = tk.Entry(filter_frame)
        phone_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="Village:", bg="white").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        # make combobox editable so typing filters suggestions
        village_cb = ttk.Combobox(filter_frame, width=30, state="normal")
        village_cb.grid(row=0, column=5, padx=5, pady=5)

        # store full lists so we can filter locally
        village_full = []

        def load_address_village():
            from models.village_model import get_all_villages
            villages = get_all_villages()
            village_full[:] = [f"{v['village_id']} - {v['name']}" for v in villages]
            village_cb["values"] = village_full

        def _filter_combobox(cb, full_list, event=None):
            val = cb.get()
            if not val:
                cb['values'] = full_list
                return
            val_l = val.strip().lower()
            matches = [s for s in full_list if val_l in s.lower()]
            cb['values'] = matches
            if matches:
                try:
                    # open dropdown to show suggestions
                    cb.event_generate('<Down>')
                except Exception:
                    pass

        # bind typing events to filter suggestions
        village_cb.bind('<KeyRelease>', lambda e: _filter_combobox(village_cb, village_full, e))

        load_address_village()

        tk.Label(filter_frame, text="Item:", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        item_entry = tk.Entry(filter_frame)
        item_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Paid Status:", bg="white").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        status_cb = ttk.Combobox(filter_frame, values=["All", "Paid", "Unpaid"], state="readonly", width=10)
        status_cb.grid(row=1, column=3, padx=5, pady=5)
        status_cb.set("All")

        tk.Label(filter_frame, text="Due Min:", bg="white").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        due_min_entry = tk.Entry(filter_frame, width=10)
        due_min_entry.grid(row=1, column=5, padx=5, pady=5)

        tk.Label(filter_frame, text="Due Max:", bg="white").grid(row=1, column=6, padx=5, pady=5, sticky="e")
        due_max_entry = tk.Entry(filter_frame, width=10)
        due_max_entry.grid(row=1, column=7, padx=5, pady=5)

        tk.Label(filter_frame, text="From Date (DD-MM-YYYY):", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        from_date_entry = tk.Entry(filter_frame)
        from_date_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="To Date (DD-MM-YYYY):", bg="white").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        to_date_entry = tk.Entry(filter_frame)
        to_date_entry.grid(row=2, column=3, padx=5, pady=5)

        # ========== Table Frame ==========
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create scrollable canvas for the grid
        canvas = tk.Canvas(table_frame, bg="#ffffff")
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(self.content_frame, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # Column headers
        columns = [
            "Customer ID", "Name", "Phone", "Village", "Item",
            "Total Amount", "Paid Amount", "Due Amount", "Installment Mode", "Total Installments", "Paid Status"
        ]
        
        column_widths = [80, 120, 100, 100, 150, 100, 100, 100, 120, 120, 80]
        
        # Create header row
        self.header_cells = []
        for col_idx, col_name in enumerate(columns):
            header_label = tk.Label(
                scrollable_frame, 
                text=col_name, 
                font=("Segoe UI", int(self.base_header_font_size * self.zoom_level), "bold"),
                bg="#e1f5fe",
                fg="#000000",
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=5,
                width=column_widths[col_idx]//10 if col_idx < len(column_widths) else 10
            )
            header_label.grid(row=0, column=col_idx, sticky="nsew", padx=0, pady=0)
            self.header_cells.append(header_label)

        # Store references for data rows
        self.grid_labels = []
        self.detail_map = {}

        # Function to create grid cell
        def create_grid_cell(parent, text, row, col, bg_color="#ffffff", fg_color="#000000"):
            cell_label = tk.Label(
                parent,
                text=text,
                font=("Segoe UI", int(self.base_font_size * self.zoom_level)),
                bg=bg_color,
                fg=fg_color,
                borderwidth=1,
                relief="solid",
                padx=3,
                pady=3,
                anchor="w",
                width=column_widths[col]//8 if col < len(column_widths) else 10
            )
            cell_label.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            return cell_label

        # Function to populate grid
        def populate_grid(rows):
            # Clear existing data rows
            for row_labels in self.grid_labels:
                for label in row_labels:
                    label.destroy()
            self.grid_labels.clear()
            self.detail_map.clear()
            self.grid_cells = []  # Store all grid cells for zoom updates

            for row_idx, row in enumerate(rows):
                row_labels = []
                grid_row = row_idx + 1  # +1 because row 0 is header
                
                paid_status = row.get("paid_status", "Unpaid")
                due_amount = row.get("due_amount") or 0

                # Determine row colors based on payment status
                if paid_status == "Paid":
                    bg_color = '#d4edda' if row_idx % 2 == 0 else '#c3e6cb'
                    fg_color = '#155724'
                elif paid_status == "Unpaid" and due_amount > 0:
                    bg_color = '#f8d7da' if row_idx % 2 == 0 else '#f5c6cb'
                    fg_color = '#721c24'
                else:
                    bg_color = '#fff3cd' if row_idx % 2 == 0 else '#ffeaa7'
                    fg_color = '#856404'

                # Create cells for this row
                values = [
                    row.get("customer_id") or "",
                    row.get("customer_name") or "",
                    row.get("customer_phone") or "",
                    row.get("village_name") or "",
                    f"{row.get('brand') or ''} {row.get('model') or ''}".strip(),
                    f"₹{row.get('item_amount') or 0:,.0f}",
                    f"₹{row.get('total_paid') or 0:,.0f}",
                    f"₹{row.get('due_amount') or 0:,.0f}",
                    row.get("installment_mode") or "",
                    row.get("total_installments") or "",
                    paid_status
                ]

                for col_idx, value in enumerate(values):
                    cell_label = create_grid_cell(scrollable_frame, str(value), grid_row, col_idx, bg_color, fg_color)
                    row_labels.append(cell_label)
                    self.grid_cells.append(cell_label)  # Store for zoom updates
                    
                    # Bind double-click to open details
                    cell_label.bind("<Double-1>", lambda e, r=row: self.show_customer_details(r, parent=self.content_frame))

                self.grid_labels.append(row_labels)
                self.detail_map[grid_row] = row

        # Make columns expandable
        for col_idx in range(len(columns)):
            scrollable_frame.grid_columnconfigure(col_idx, weight=1)

        # ========== Search Logic ==========
        from models.report_model import get_all_customer_items  # You can modify this to include payment info

        # Store search results for printing
        self.current_search_results = []

        def show_print_preview(content, auto_print=False):
            """Show print preview in a text window for manual printing."""
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Print Preview - Sandhu Enterprises Report")
            preview_window.geometry("900x700")
            
            # Status label
            status_label = tk.Label(preview_window, text="Preparing report...", fg="blue", font=("Arial", 10))
            status_label.pack(pady=5)
            
            # Create text widget with scrollbar
            text_frame = tk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Courier New", 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            # Insert content
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
            
            # Buttons
            button_frame = tk.Frame(preview_window)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Print button
            print_btn = tk.Button(
                button_frame,
                text="🖨️ Print Now",
                command=lambda: print_text_widget(text_widget, status_label),
                bg="#3498db",
                fg="white",
                font=("Arial", 10, "bold")
            )
            print_btn.pack(side=tk.LEFT, padx=5)
            
            # Save button
            tk.Button(
                button_frame,
                text="💾 Save to File",
                command=lambda: save_report_to_file(content),
                bg="#27ae60",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=5)
            
            # Copy button
            tk.Button(
                button_frame,
                text="📋 Copy to Clipboard",
                command=lambda: copy_to_clipboard(content, status_label),
                bg="#f39c12",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame,
                text="❌ Close",
                command=preview_window.destroy,
                bg="#95a5a6",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack(side=tk.RIGHT, padx=5)
            
            # Bind Ctrl+P for printing
            preview_window.bind('<Control-p>', lambda e: print_text_widget(text_widget, status_label))
            preview_window.focus_set()
            
            # Auto-print if requested
            if auto_print:
                status_label.config(text="Attempting to print automatically...", fg="orange")
                preview_window.after(1000, lambda: print_text_widget(text_widget, status_label, show_messages=False))

        def print_text_widget(text_widget, status_label=None, show_messages=True):
            """Print the content of a text widget."""
            if status_label:
                status_label.config(text="Printing...", fg="orange")
            
            try:
                # Get the content
                content = text_widget.get("1.0", tk.END).strip()
                
                # Method 1: Try Windows print command
                import tempfile
                import subprocess
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(content)
                    temp_file = f.name
                
                try:
                    # Try print command first
                    result = subprocess.run(['print', temp_file], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        if status_label:
                            status_label.config(text="✅ Printed successfully to default printer!", fg="green")
                        if show_messages:
                            messagebox.showinfo("Print Success", "Report sent to your default printer!\n\nCheck your printer output.")
                        return
                    
                except subprocess.TimeoutExpired:
                    pass
                except Exception as e:
                    print(f"Print command failed: {e}")
                
                # Method 2: Try notepad /p
                try:
                    result = subprocess.run(['notepad.exe', '/p', temp_file], capture_output=True, text=True, timeout=15)
                    
                    if result.returncode == 0:
                        if status_label:
                            status_label.config(text="✅ Printed successfully via Notepad!", fg="green")
                        if show_messages:
                            messagebox.showinfo("Print Success", "Report sent to printer via Notepad!\n\nCheck your printer output.")
                        return
                    
                except subprocess.TimeoutExpired:
                    pass
                except Exception as e:
                    print(f"Notepad print failed: {e}")
                
                # Method 3: Show instructions for manual printing
                if status_label:
                    status_label.config(text="❌ Auto-print failed. Use manual options below.", fg="red")
                
                if show_messages:
                    manual_msg = (
                        "Automatic printing failed.\n\n"
                        "To print manually:\n"
                        "1. Click 'Save to File' to save the report\n"
                        "2. Open the saved file in Notepad or Word\n"
                        "3. Use File → Print\n\n"
                        "Or click 'Copy to Clipboard' and paste into any document."
                    )
                    messagebox.showwarning("Print Failed", manual_msg)
                    
            except Exception as e:
                error_msg = f"Printing error: {str(e)}"
                print(error_msg)
                if status_label:
                    status_label.config(text=f"❌ Error: {str(e)}", fg="red")
                if show_messages:
                    messagebox.showerror("Print Error", f"Could not print:\n{error_msg}\n\nTry saving to file instead.")
                    
            finally:
                # Clean up temp file
                try:
                    if 'temp_file' in locals():
                        os.unlink(temp_file)
                except:
                    pass

        def copy_to_clipboard(content, status_label=None):
            """Copy content to clipboard."""
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                if status_label:
                    status_label.config(text="✅ Report copied to clipboard!", fg="green")
                messagebox.showinfo("Copied", "Report copied to clipboard!\n\nYou can now paste it into Word, Excel, or any text editor.")
            except Exception as e:
                if status_label:
                    status_label.config(text=f"❌ Copy failed: {str(e)}", fg="red")
                messagebox.showerror("Copy Error", f"Could not copy to clipboard:\n{str(e)}")

        def save_report_to_file(content):
            """Save the report content to a file."""
            from tkinter import filedialog
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Report As",
                initialfile=f"sandhu_report_{date.today().strftime('%d%m%Y')}.txt"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Save Success", f"Report saved to:\n{file_path}\n\nYou can now open this file and print it from any text editor.")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Could not save file:\n{str(e)}")

        def search_records():
            # Build filter dict from UI inputs
            # extract village name/address from combobox value 'id - name'
            village_val = village_cb.get().strip()
            if village_val:
                parts = village_val.split(" - ", 1)
                village_filter = parts[1] if len(parts) > 1 else parts[0]
            else:
                village_filter = None

            filters = {
                "name": name_entry.get().strip() or None,
                "phone": phone_entry.get().strip() or None,
                "village": village_filter,
                "item": item_entry.get().strip() or None,
                "status": status_cb.get() if status_cb.get() != "All" else None,
            }

            # parse due min/max as floats if provided
            try:
                due_min = due_min_entry.get().strip()
                filters["due_min"] = float(due_min) if due_min else None
            except ValueError:
                filters["due_min"] = None

            try:
                due_max = due_max_entry.get().strip()
                filters["due_max"] = float(due_max) if due_max else None
            except ValueError:
                filters["due_max"] = None

            # date filters - convert DD-MM-YYYY to YYYY-MM-DD for DB
            payment_from = from_date_entry.get().strip()
            payment_to = to_date_entry.get().strip()
            
            def convert_date_format(date_str):
                if not date_str:
                    return None
                try:
                    from datetime import datetime as _dt
                    # Try DD-MM-YYYY first
                    try:
                        parsed = _dt.strptime(date_str, '%d-%m-%Y')
                        return parsed.strftime('%Y-%m-%d')
                    except ValueError:
                        # Try YYYY-MM-DD
                        _dt.strptime(date_str, '%Y-%m-%d')
                        return date_str
                except ValueError:
                    return None
            
            payment_from = convert_date_format(payment_from)
            payment_to = convert_date_format(payment_to)
            
            if payment_from:
                filters["payment_from"] = payment_from
            if payment_to:
                filters["payment_to"] = payment_to

            # Call model search that performs SQL-level filtering (efficient)
            from models.report_model import search_customer_items
            rows = search_customer_items(filters)
            
            # Store results for printing
            self.current_search_results = rows

            # Populate the grid with data
            populate_grid(rows)

            # Calculate and display summary statistics
            total_records = len(rows)
            total_amount = sum(row.get("item_amount") or 0 for row in rows)
            total_paid = sum(row.get("total_paid") or 0 for row in rows)
            total_due = sum(row.get("due_amount") or 0 for row in rows)
            paid_records = sum(1 for row in rows if row.get("paid_status") == "Paid")
            unpaid_records = sum(1 for row in rows if row.get("paid_status") == "Unpaid")

            # Update summary labels
            self.summary_labels["Total Records"].config(text=f"{total_records}")
            self.summary_labels["Total Amount"].config(text=f"₹{total_amount:,.0f}")
            self.summary_labels["Total Paid"].config(text=f"₹{total_paid:,.0f}")
            self.summary_labels["Total Due"].config(text=f"₹{total_due:,.0f}")
            self.summary_labels["Paid Records"].config(text=f"{paid_records}")
            self.summary_labels["Unpaid Records"].config(text=f"{unpaid_records}")

        def print_search_results(search_rows):
            """Print the current search results to A4 page."""
            if not search_rows:
                messagebox.showinfo("Print Results", "No records to print. Please search first.")
                return
            
            # Calculate summary
            total_records = len(search_rows)
            total_amount = sum(row.get("item_amount") or 0 for row in search_rows)
            total_paid = sum(row.get("total_paid") or 0 for row in search_rows)
            total_due = sum(row.get("due_amount") or 0 for row in search_rows)
            paid_records = sum(1 for row in search_rows if row.get("paid_status") == "Paid")
            unpaid_records = sum(1 for row in search_rows if row.get("paid_status") == "Unpaid")
            
            # Create print content
            print_content = []
            print_content.append("SANDHU ENTERPRISES")
            print_content.append("CUSTOMER ITEMS REPORT")
            print_content.append("=" * 50)
            print_content.append(f"Generated on: {date.today().strftime('%d-%m-%Y')}")
            print_content.append("")
            print_content.append("SUMMARY:")
            print_content.append(f"Total Records: {total_records}")
            print_content.append(f"Total Amount: ₹{total_amount:,.0f}")
            print_content.append(f"Total Paid: ₹{total_paid:,.0f}")
            print_content.append(f"Total Due: ₹{total_due:,.0f}")
            print_content.append(f"Paid Records: {paid_records}")
            print_content.append(f"Unpaid Records: {unpaid_records}")
            print_content.append("")
            print_content.append("DETAILED RECORDS:")
            print_content.append("=" * 50)
            
            # Header (compact for A4)
            header = f"{'Customer':<18} {'Phone':<10} {'Village':<12} {'Brand':<12} {'Model':<12} {'Amount':>8} {'Paid':>8} {'Due':>8} {'Status':<6}"
            print_content.append(header)
            print_content.append("-" * 50)
            
            # Records
            for row in search_rows:
                customer_name = str(row.get("customer_name", ""))[:18]
                phone = str(row.get("customer_phone", ""))[:10]
                village = str(row.get("village_name", ""))[:12]
                brand = str(row.get("brand", ""))[:12]
                model = str(row.get("model", ""))[:12]
                item_amount = float(row.get("item_amount") or 0)
                total_paid = float(row.get("total_paid") or 0)
                due_amount = float(row.get("due_amount") or 0)
                paid_status = str(row.get("paid_status", ""))[:6]
                
                record_line = f"{customer_name:<18} {phone:<10} {village:<12} {brand:<12} {model:<12} {item_amount:>8,.0f} {total_paid:>8,.0f} {due_amount:>8,.0f} {paid_status:<6}"
                print_content.append(record_line)
            
            print_content.append("=" * 50)
            
            # Create a temporary text file for printing
            import tempfile
            import os
            
            content_text = '\n'.join(print_content)
            
            # Always show preview first, then try to print
            show_print_preview(content_text, auto_print=True)

        # Search button
        tk.Button(
            filter_frame,
            text="🔍 Search",
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            command=search_records
        ).grid(row=0, column=8, padx=10)

        tk.Button(
            filter_frame,
            text="🖨️ Print Results",
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            command=lambda: print_search_results(self.current_search_results)
        ).grid(row=0, column=9, padx=10)

        tk.Button(
            filter_frame,
            text="💰 Payment Records",
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            command=lambda: self.open_payment_records()
        ).grid(row=0, column=10, padx=10)

        # ========== Summary Statistics ==========
        summary_frame = tk.Frame(self.content_frame, bg="#f8f9fa", relief="groove", bd=2)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.summary_labels = {}
        summary_items = [
            ("Total Records", "0"),
            ("Total Amount", "₹0"),
            ("Total Paid", "₹0"),
            ("Total Due", "₹0"),
            ("Paid Records", "0"),
            ("Unpaid Records", "0")
        ]

        for i, (label_text, default_value) in enumerate(summary_items):
            tk.Label(summary_frame, text=f"{label_text}:", bg="#f8f9fa", font=("Arial", 10, "bold")).grid(row=0, column=i*2, padx=10, pady=5, sticky="e")
            label = tk.Label(summary_frame, text=default_value, bg="#f8f9fa", font=("Arial", 10), fg="#2c3e50")
            label.grid(row=0, column=i*2+1, padx=10, pady=5, sticky="w")
            self.summary_labels[label_text] = label

        # Initial load
        search_records()

    def open_payment_records(self):
        """Open a dialog listing all individual payment records with customer details."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Payment Records")
        dlg.geometry("1200x700")

        top = tk.Frame(dlg)
        top.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(top, text="From (DD-MM-YYYY):").pack(side=tk.LEFT)
        from_e = tk.Entry(top, width=12)
        from_e.pack(side=tk.LEFT, padx=6)
        tk.Label(top, text="To (DD-MM-YYYY):").pack(side=tk.LEFT, padx=(10,0))
        to_e = tk.Entry(top, width=12)
        to_e.pack(side=tk.LEFT, padx=6)
        tk.Label(top, text="Name:").pack(side=tk.LEFT, padx=(10,0))
        name_e = tk.Entry(top, width=20)
        name_e.pack(side=tk.LEFT, padx=6)

        # Create scrollable canvas for the grid
        canvas = tk.Canvas(dlg, bg="#ffffff")
        scrollbar_y = ttk.Scrollbar(dlg, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(dlg, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # Column headers
        columns = ["Payment ID", "Date", "Customer ID", "Name", "Phone", "Item ID", "Brand", "Amount Paid", "Remaining"]
        column_widths = [100, 100, 100, 150, 100, 80, 120, 100, 100]
        
        # Create header row
        self.records_header_cells = []
        for col_idx, col_name in enumerate(columns):
            header_label = tk.Label(
                scrollable_frame, 
                text=col_name, 
                font=("Segoe UI", int(self.base_header_font_size * self.zoom_level), "bold"),
                bg="#e1f5fe",
                fg="#000000",
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=5,
                width=column_widths[col_idx]//8 if col_idx < len(column_widths) else 10
            )
            header_label.grid(row=0, column=col_idx, sticky="nsew", padx=0, pady=0)
            self.records_header_cells.append(header_label)

        # Function to create grid cell
        def create_grid_cell(parent, text, row, col, bg_color="#ffffff", fg_color="#000000"):
            cell_label = tk.Label(
                parent,
                text=text,
                font=("Segoe UI", int(self.base_font_size * self.zoom_level)),
                bg=bg_color,
                fg=fg_color,
                borderwidth=1,
                relief="solid",
                padx=3,
                pady=3,
                anchor="w",
                width=column_widths[col]//8 if col < len(column_widths) else 10
            )
            cell_label.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            return cell_label

        # Store references for data rows
        self.records_grid_labels = []

        def load_records():
            from models.payment_model import get_all_payments
            filters = {}
            
            def convert_date_format(date_str):
                if not date_str:
                    return None
                try:
                    from datetime import datetime as _dt
                    # Try DD-MM-YYYY first
                    try:
                        parsed = _dt.strptime(date_str, '%d-%m-%Y')
                        return parsed.strftime('%Y-%m-%d')
                    except ValueError:
                        # Try YYYY-MM-DD
                        _dt.strptime(date_str, '%Y-%m-%d')
                        return date_str
                except ValueError:
                    return None
            
            if from_e.get().strip():
                filters["payment_from"] = convert_date_format(from_e.get().strip())
            if to_e.get().strip():
                filters["payment_to"] = convert_date_format(to_e.get().strip())
            if name_e.get().strip():
                filters["customer_name"] = name_e.get().strip()
            
            rows = get_all_payments(filters)
            
            # Clear existing data rows
            for row_labels in self.records_grid_labels:
                for label in row_labels:
                    label.destroy()
            self.records_grid_labels.clear()
            self.records_grid_cells = []  # Store records grid cells for zoom updates

            # Populate grid with payment data
            for row_idx, r in enumerate(rows):
                grid_row = row_idx + 1  # +1 because row 0 is header
                
                # All payment records are successful payments, so use green color
                bg_color = '#d4edda'
                fg_color = '#155724'

                # Create cells for this row
                values = [
                    r.get('payment_id') or r.get('id') or '',
                    r.get('payment_date') or '',
                    r.get('customer_id') or '',
                    r.get('customer_name') or '',
                    r.get('customer_phone') or '',
                    r.get('item_id') or '',
                    f"{r.get('brand') or ''} {r.get('model') or ''}".strip(),
                    f"₹{r.get('amount_paid') or 0:.0f}",
                    f"₹{r.get('remaining_amount') or 0:.0f}"
                ]

                row_labels = []
                for col_idx, value in enumerate(values):
                    cell_label = create_grid_cell(scrollable_frame, str(value), grid_row, col_idx, bg_color, fg_color)
                    row_labels.append(cell_label)
                    self.records_grid_cells.append(cell_label)  # Store for zoom updates

                self.records_grid_labels.append(row_labels)

        tk.Button(top, text="🔄 Reload", command=load_records, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=8)
        tk.Button(top, text="Close", command=dlg.destroy, bg="#e74c3c", fg="white").pack(side=tk.RIGHT, padx=8)

        # Make columns expandable
        for col_idx in range(len(columns)):
            scrollable_frame.grid_columnconfigure(col_idx, weight=1)

        load_records()
