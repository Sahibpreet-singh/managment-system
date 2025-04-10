import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from data import *

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = "#f9fafb"
BG_PANEL    = "#ffffff"
BG_CARD     = "#ffffff"
BG_ROW_ALT  = "#f3f4f6"
BG_INPUT    = "#ffffff"

BORDER      = "#e5e7eb"

ACCENT      = "#60a5fa"   # soft blue
ACCENT2     = "#34d399"   # mint green
ACCENT_RED  = "#f87171"
ACCENT_YEL  = "#fbbf24"
ACCENT_PUR  = "#a78bfa"

TEXT        = "#1f2937"
TEXT_DIM    = "#9ca3af"

SEL_BG      = "#1e40af"   # strong blue — clearly selected
SEL_FG      = "#ffffff"   # white text on selected row

FONT_UI     = "Segoe UI"
FONT_MONO   = "Consolas"


# ── Helpers ───────────────────────────────────────────────────────────────────
def apply_dark_titlebar(win):
    try:
        import ctypes
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        if hwnd == 0:
            hwnd = win.winfo_id()
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass


def build_style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("T.Treeview",
                background=BG_CARD, foreground=TEXT,
                fieldbackground=BG_CARD, rowheight=34,
                font=(FONT_UI, 10), borderwidth=0, relief="flat")
    s.configure("T.Treeview.Heading",
                background=BG_PANEL, foreground=ACCENT,
                font=(FONT_UI, 9, "bold"), borderwidth=0,
                relief="flat", padding=(8, 7))
    s.map("T.Treeview",
          background=[("selected", SEL_BG)],
          foreground=[("selected", SEL_FG)])
    s.map("T.Treeview.Heading",
          background=[("active", BORDER)])
    
    s.map("Dark.TCombobox",
          fieldbackground=[("readonly", BG_INPUT)],
          foreground=[("readonly", TEXT)])
    return s


def attach_selection_bar(tree, canvas_parent, color=ACCENT):
    """Draw a colored bar to the left of the selected tree row."""
    bar = tk.Frame(canvas_parent, bg=color, width=4)

    def update_bar(e=None):
        sel = tree.selection()
        if not sel:
            bar.place_forget()
            return
        bbox = tree.bbox(sel[0])
        if not bbox:
            bar.place_forget()
            return
        # Get tree's position relative to canvas_parent
        tx = tree.winfo_x()
        ty = tree.winfo_y()
        _, row_y, _, row_h = bbox
        bar.place(x=tx - 4, y=ty + row_y, width=4, height=row_h)
        bar.lift()

    tree.bind("<<TreeviewSelect>>", update_bar)
    tree.bind("<Configure>",        update_bar)
    return bar


def make_entry(parent, width=18, **kw):
    return tk.Entry(parent, font=(FONT_UI, 10), fg=TEXT, bg=BG_INPUT,
                    insertbackground=ACCENT, relief="flat",
                    highlightthickness=1, highlightcolor=ACCENT,
                    highlightbackground=BORDER, width=width, **kw)


def section_header(parent, text, color=ACCENT):
    f = tk.Frame(parent, bg=BG_CARD)
    f.pack(fill=tk.X, pady=(12, 10))
    tk.Frame(f, bg=color, width=3).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
    tk.Label(f, text=text, font=(FONT_UI, 10, "bold"),
             fg=color, bg=BG_CARD).pack(side=tk.LEFT)
    tk.Frame(f, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X,
                                           expand=True, padx=(12, 0))


def make_shortcut_bar(parent, shortcuts):
    bar = tk.Frame(parent, bg=BG_PANEL, pady=6, padx=12)
    bar.pack(fill=tk.X)
    for key, desc, color in shortcuts:
        chip = tk.Frame(bar, bg=BG_PANEL)
        chip.pack(side=tk.LEFT, padx=4)
        tk.Label(chip, text=key, font=(FONT_UI, 8, "bold"),
                 fg=BG, bg=color, padx=6, pady=3).pack(side=tk.LEFT)
        tk.Label(chip, text=f" {desc}", font=(FONT_UI, 8),
                 fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    return bar


# ═════════════════════════════════════════════════════════════════════════════
# NEW CASE DETAILS FORM
# ═════════════════════════════════════════════════════════════════════════════
def new_case_form(parent, on_save_callback=None):
    win = tk.Toplevel(parent)
    win.title("New Case Details — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)

    try:
        next_id = max(int(r.get('id', 0)) for r in INSTALLMENT_CASES) + 1
    except Exception:
        next_id = 1

    # ── Top bar ───────────────────────────────────────────────────────────
    topbar = tk.Frame(win, bg=BG_PANEL)
    topbar.pack(fill=tk.X)
    tk.Frame(topbar, bg=ACCENT2, width=4).pack(side=tk.LEFT, fill=tk.Y)
    tb_inner = tk.Frame(topbar, bg=BG_PANEL, padx=18, pady=12)
    tb_inner.pack(side=tk.LEFT)
    tk.Label(tb_inner, text="NEW CASE DETAILS",
             font=(FONT_UI, 15, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(tb_inner, text="Complete all sections · Press F10 to save",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    # Case ID (top right)
    badge_f = tk.Frame(topbar, bg=BG_PANEL, padx=20)
    badge_f.pack(side=tk.RIGHT)
    tk.Label(badge_f, text="CASE ID", font=(FONT_UI, 8),
             fg=TEXT_DIM, bg=BG_PANEL).pack()
    tk.Label(badge_f, text=str(next_id),
             font=(FONT_MONO, 22, "bold"), fg=ACCENT, bg=BG_PANEL).pack()

    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
    make_shortcut_bar(win, [
        ("ESC",  "CANCEL",     ACCENT_RED),
        ("F10",  "SAVE & EXIT", ACCENT2),
    ])
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    # ── Scrollable canvas ─────────────────────────────────────────────────
    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
   
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    body = tk.Frame(canvas, bg=BG, padx=20, pady=16)
    body_id = canvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>",
              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
                lambda e: canvas.itemconfig(body_id, width=e.width))
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    entries = {}

    # ══════════════════════════════════════════════════════════════════════
    # TOP ROW: 3 columns — Customer | Item Particulars | Photo
    # ══════════════════════════════════════════════════════════════════════
    top_row = tk.Frame(body, bg=BG)
    top_row.pack(fill=tk.X, pady=(0, 8))
    top_row.grid_columnconfigure(0, weight=3, minsize=320)
    top_row.grid_columnconfigure(1, weight=4, minsize=420)
    top_row.grid_columnconfigure(2, weight=2, minsize=200)

    # ── CUSTOMER DETAILS ──────────────────────────────────────────────────
    cust_card = tk.Frame(top_row, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=14, pady=10)
    cust_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    section_header(cust_card, "CUSTOMER DETAILS", ACCENT)

    cg = tk.Frame(cust_card, bg=BG_CARD)
    cg.pack(fill=tk.X)
    cg.grid_columnconfigure(1, weight=1)
    cg.grid_columnconfigure(3, weight=1)

    # FILE NO + DATE
    tk.Label(cg, text="FILE NO", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=0, sticky="w", pady=4, padx=4)
    e_fn = make_entry(cg, width=9)
    e_fn.grid(row=0, column=1, sticky="ew", ipady=6, pady=4, padx=(0, 10))
    entries['file_no'] = e_fn

    tk.Label(cg, text="DATE", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=2, sticky="w", pady=4, padx=4)
    e_dt = make_entry(cg, width=11)
    e_dt.insert(0, "DD/MM/YYYY")
    e_dt.config(fg=TEXT_DIM)
    e_dt.grid(row=0, column=3, sticky="ew", ipady=6, pady=4)
    entries['date'] = e_dt
    e_dt.bind("<FocusIn>",
              lambda e: (e_dt.delete(0, tk.END), e_dt.config(fg=TEXT))
                        if e_dt.get() == "DD/MM/YYYY" else None)
    e_dt.bind("<FocusOut>",
              lambda e: (e_dt.insert(0, "DD/MM/YYYY"), e_dt.config(fg=TEXT_DIM))
                        if not e_dt.get() else None)

    for i, (lbl, key) in enumerate([
        ("ACCOUNT",     "account"),
        ("W/O D/O S/O", "relation"),
        ("ADDRESS",     "address1"),
        ("",            "address2"),
        ("MOBILE NO",   "mobile_no"),
        ("REMARKS",     "remarks_cust"),
    ], start=1):
        tk.Label(cg, text=lbl, font=(FONT_UI, 9), fg=TEXT_DIM,
                 bg=BG_CARD, width=11, anchor="w").grid(
                 row=i, column=0, sticky="w", pady=3, padx=4)
        e = make_entry(cg, width=22)
        e.grid(row=i, column=1, columnspan=3, sticky="ew",
               ipady=6, pady=3, padx=(0, 4))
        entries[key] = e

    # VILLAGE combobox
    tk.Label(cg, text="VILLAGE", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=7, column=0, sticky="w", pady=3, padx=4)
    village_var = tk.StringVar()
    entries['village'] = village_var
    village_vals = sorted({r.get('village', '') for r in INSTALLMENT_CASES if r.get('village')})
    village_cb = ttk.Combobox(cg, textvariable=village_var, values=village_vals,
                               style="Dark.TCombobox", font=(FONT_UI, 10), width=20)
    village_cb.grid(row=7, column=1, columnspan=3, sticky="ew",
                    ipady=4, pady=3, padx=(0, 4))

    # ── ITEM PARTICULARS ──────────────────────────────────────────────────
    item_card = tk.Frame(top_row, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=14, pady=10)
    item_card.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
    section_header(item_card, "ITEM PARTICULARS", ACCENT_PUR)

    ig = tk.Frame(item_card, bg=BG_CARD)
    ig.pack(fill=tk.X)
    ig.grid_columnconfigure(1, weight=1)
    ig.grid_columnconfigure(3, weight=1)

    # ITEM (full row)
    tk.Label(ig, text="ITEM", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD, width=11, anchor="w").grid(
             row=0, column=0, sticky="w", pady=4, padx=4)
    e_item = make_entry(ig, width=34)
    e_item.grid(row=0, column=1, columnspan=3, sticky="ew",
                ipady=6, pady=4, padx=(0, 4))
    entries['item'] = e_item

    # BRAND + MODEL
    tk.Label(ig, text="BRAND", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=1, column=0, sticky="w", pady=4, padx=4)
    e_brand = make_entry(ig, width=14)
    e_brand.grid(row=1, column=1, sticky="ew", ipady=6, pady=4, padx=(0, 10))
    entries['brand'] = e_brand

    tk.Label(ig, text="MODEL", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=1, column=2, sticky="w", pady=4, padx=4)
    e_model = make_entry(ig, width=14)
    e_model.grid(row=1, column=3, sticky="ew", ipady=6, pady=4)
    entries['model'] = e_model

    # SRNO
    tk.Label(ig, text="SRNO", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD, width=11, anchor="w").grid(
             row=2, column=0, sticky="w", pady=4, padx=4)
    e_srno = make_entry(ig, width=34)
    e_srno.grid(row=2, column=1, columnspan=3, sticky="ew",
                ipady=6, pady=4, padx=(0, 4))
    entries['srno'] = e_srno

    # INVOICE NO
    tk.Label(ig, text="INVOICE NO", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD, width=11, anchor="w").grid(
             row=3, column=0, sticky="w", pady=4, padx=4)
    e_inv = make_entry(ig, width=34)
    e_inv.grid(row=3, column=1, columnspan=3, sticky="ew",
               ipady=6, pady=4, padx=(0, 4))
    entries['invoice_no'] = e_inv

    # ── Financial section separator ───────────────────────────────────────
    tk.Frame(item_card, bg=BORDER, height=1).pack(fill=tk.X, pady=8)

    fg2 = tk.Frame(item_card, bg=BG_CARD)
    fg2.pack(fill=tk.X)
    fg2.grid_columnconfigure(1, weight=1)
    fg2.grid_columnconfigure(3, weight=1)

    amount_var   = tk.StringVar()
    advance_var  = tk.StringVar()
    amt_fin_var  = tk.StringVar(value="0.00")
    no_inst_var  = tk.StringVar()
    inst_amt_var = tk.StringVar(value="0.00")
    final_var    = tk.StringVar(value="0.00")

    entries.update({
        'amount':          amount_var,
        'advance':         advance_var,
        'amount_financed': amt_fin_var,
        'no_instalments':  no_inst_var,
        'instalment_amt':  inst_amt_var,
        'final_amount':    final_var,
    })

    def recalculate(*_):
        try:
            amt = float(amount_var.get()  or 0)
            adv = float(advance_var.get() or 0)
            n   = float(no_inst_var.get() or 0)
            fin = amt - adv
            amt_fin_var.set(f"{fin:.2f}")
            if n > 0:
                inst = fin / n
                inst_amt_var.set(f"{inst:.2f}")
                final_var.set(f"{fin:.2f}")
            else:
                inst_amt_var.set("0.00")
                final_var.set(f"{fin:.2f}")
        except ValueError:
            pass

    amount_var.trace_add("write",  recalculate)
    advance_var.trace_add("write", recalculate)
    no_inst_var.trace_add("write", recalculate)

    fin_rows = [
        ("AMOUNT",             amount_var,  0, 0, TEXT,       False),
        ("ADVANCE",            advance_var, 0, 2, TEXT,       False),
        ("AMOUNT FINANCED",    amt_fin_var, 1, 0, ACCENT_YEL, True),
        ("NO. OF INSTALMENTS", no_inst_var, 1, 2, TEXT,       False),
        ("INSTALMENT AMOUNT",  inst_amt_var,2, 0, ACCENT2,    True),
        ("FINAL AMOUNT",       final_var,   2, 2, ACCENT_RED, True),
    ]
    for lbl_t, var, r, c, color, ro in fin_rows:
        tk.Label(fg2, text=lbl_t, font=(FONT_UI, 9), fg=TEXT_DIM,
                 bg=BG_CARD, anchor="w").grid(
                 row=r, column=c*2, sticky="w", pady=5, padx=4)
        state = "readonly" if ro else "normal"
        rbg   = BG_CARD if ro else BG_INPUT
        e = tk.Entry(fg2, textvariable=var, state=state,
                     font=(FONT_MONO, 10, "bold"), fg=color, bg=rbg,
                     readonlybackground=rbg,
                     insertbackground=ACCENT, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER, width=14)
        e.grid(row=r, column=c*2+1, sticky="ew", ipady=7, pady=5, padx=(0, 8))

    # ── PHOTO PLACEHOLDER ─────────────────────────────────────────────────
    photo_card = tk.Frame(top_row, bg=BG_CARD,
                          highlightbackground=BORDER, highlightthickness=1,
                          padx=10, pady=10)
    photo_card.grid(row=0, column=2, sticky="nsew")

    tk.Label(photo_card, text="PHOTO", font=(FONT_UI, 8, "bold"),
             fg=TEXT_DIM, bg=BG_CARD).pack()

    ph_frame = tk.Frame(photo_card, bg=BG_INPUT,
                        highlightbackground=BORDER, highlightthickness=1)
    ph_frame.pack(fill=tk.BOTH, expand=True, pady=6)

    ph_canvas = tk.Canvas(ph_frame, bg=BG_INPUT, highlightthickness=0)
    ph_canvas.pack(fill=tk.BOTH, expand=True)

    def draw_x(e=None):
        ph_canvas.delete("all")
        w = ph_canvas.winfo_width() or 170
        h = ph_canvas.winfo_height() or 170
        ph_canvas.create_rectangle(2, 2, w-2, h-2, outline=BORDER, width=1)
        ph_canvas.create_line(2, 2, w-2, h-2, fill=BORDER, width=1)
        ph_canvas.create_line(w-2, 2, 2, h-2, fill=BORDER, width=1)
        ph_canvas.create_text(w//2, h//2, text="No Photo",
                              fill=TEXT_DIM, font=(FONT_UI, 9))

    ph_canvas.bind("<Configure>", draw_x)
    ph_canvas.after(150, draw_x)

    tk.Button(photo_card, text="📷  Upload",
              font=(FONT_UI, 8), fg=TEXT_DIM, bg=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", pady=4,
              command=lambda: messagebox.showinfo(
                  "Photo", "Photo upload feature coming soon.", parent=win)
              ).pack(fill=tk.X, pady=(4, 0))

    # ══════════════════════════════════════════════════════════════════════
    # BOTTOM ROW: Two guarantors side-by-side
    # ══════════════════════════════════════════════════════════════════════
    guar_row = tk.Frame(body, bg=BG)
    guar_row.pack(fill=tk.X, pady=(8, 0))
    guar_row.grid_columnconfigure(0, weight=1)
    guar_row.grid_columnconfigure(1, weight=1)

    def build_guarantor(parent_frame, prefix, title, color, col):
        card = tk.Frame(parent_frame, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=14, pady=10)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0, 8) if col == 0 else 0)
        section_header(card, title, color)

        gg = tk.Frame(card, bg=BG_CARD)
        gg.pack(fill=tk.X)
        gg.grid_columnconfigure(1, weight=1)

        for i, (lbl, key) in enumerate([
            ("NAME",        f"{prefix}_name"),
            ("W/O D/O S/O", f"{prefix}_relation"),
            ("ADDRESS",     f"{prefix}_address1"),
            ("",            f"{prefix}_address2"),
            ("VILLAGE",     f"{prefix}_village"),
            ("MOBILE NO",   f"{prefix}_mobile"),
            ("REMARKS",     f"{prefix}_remarks"),
        ]):
            tk.Label(gg, text=lbl, font=(FONT_UI, 9), fg=TEXT_DIM,
                     bg=BG_CARD, width=12, anchor="w").grid(
                     row=i, column=0, sticky="w", pady=4, padx=4)
            e = make_entry(gg, width=28)
            e.grid(row=i, column=1, sticky="ew", ipady=6, pady=4, padx=(0, 4))
            entries[key] = e

    build_guarantor(guar_row, "g1", "FIRST GUARANTOR PARTICULARS",  ACCENT,     0)
    build_guarantor(guar_row, "g2", "SECOND GUARANTOR PARTICULARS", ACCENT_PUR, 1)

    # ══════════════════════════════════════════════════════════════════════
    # BOTTOM ACTION BAR (pinned)
    # ══════════════════════════════════════════════════════════════════════
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)
    action_bar = tk.Frame(win, bg=BG_PANEL, pady=12, padx=24)
    action_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def get(key):
        v = entries.get(key)
        if v is None: return ""
        if isinstance(v, tk.StringVar): return v.get()
        if isinstance(v, tk.Entry):     return v.get()
        return ""

    def save_and_exit(e=None):
        file_no = get('file_no').strip()
        if not file_no:
            messagebox.showwarning("Required", "FILE NO is required.", parent=win)
            return

        record = {
            'id':           str(next_id),
            'file_no':      file_no,
            'date':         get('date'),
            'customer':     get('account'),
            'village':      get('village'),
            'mobile_no':    get('mobile_no'),
            'finance_amt':  get('amount_financed'),
            'balance':      get('final_amount'),
            'relation':     get('relation'),
            'address':      (get('address1') + " " + get('address2')).strip(),
            'remarks':      get('remarks_cust'),
            'item':         get('item'),
            'brand':        get('brand'),
            'model':        get('model'),
            'srno':         get('srno'),
            'invoice_no':   get('invoice_no'),
            'amount':       get('amount'),
            'advance':      get('advance'),
            'no_inst':      get('no_instalments'),
            'inst_amt':     get('instalment_amt'),
            'final_amount': get('final_amount'),
            'g1_name':      get('g1_name'),
            'g1_relation':  get('g1_relation'),
            'g1_address':   (get('g1_address1') + " " + get('g1_address2')).strip(),
            'g1_village':   get('g1_village'),
            'g1_mobile':    get('g1_mobile'),
            'g1_remarks':   get('g1_remarks'),
            'g2_name':      get('g2_name'),
            'g2_relation':  get('g2_relation'),
            'g2_address':   (get('g2_address1') + " " + get('g2_address2')).strip(),
            'g2_village':   get('g2_village'),
            'g2_mobile':    get('g2_mobile'),
            'g2_remarks':   get('g2_remarks'),
        }

        INSTALLMENT_CASES.append(record)
        if on_save_callback:
            on_save_callback(record)

        messagebox.showinfo("Saved ✓",
                            f"Case '{file_no}' saved successfully!\n"
                            f"Case ID: {next_id}",
                            parent=win)
        win.destroy()

    # Cancel button
    tk.Button(action_bar, text="✕  CANCEL  ESC",
              command=win.destroy,
              font=(FONT_UI, 11, "bold"), fg=ACCENT_RED, bg=BG_CARD,
              activeforeground=ACCENT_RED, activebackground=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
              highlightthickness=1, highlightbackground=ACCENT_RED
              ).pack(side=tk.LEFT, padx=(0, 16))

    # Save button
    tk.Button(action_bar, text="💾  SAVE & EXIT  F10",
              command=save_and_exit,
              font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT2,
              activeforeground=BG, activebackground="#2ebd68",
              relief="flat", bd=0, cursor="hand2", padx=24, pady=10,
              ).pack(side=tk.LEFT)

    win.bind("<F10>",    save_and_exit)
    win.bind("<Escape>", lambda e: win.destroy())


# ═════════════════════════════════════════════════════════════════════════════
# INSTALLMENT CASES WINDOW
# ═════════════════════════════════════════════════════════════════════════════
INST_COLS   = ['file_no', 'date', 'customer', 'village', 'mobile_no', 'finance_amt', 'balance', 'id']
INST_HEADS  = ['File No', 'Date', 'Customer (Father)', 'Village', 'Mobile No', 'Finance Amt', 'Balance', 'ID']
INST_WIDTHS = [70, 95, 200, 130, 150, 110, 100, 55]


def installment_window(parent):
    win = tk.Toplevel(parent)
    win.title("Installment Cases — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    titlebar = tk.Frame(win, bg=BG_PANEL)
    titlebar.pack(fill=tk.X)
    tk.Frame(titlebar, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
    ti = tk.Frame(titlebar, bg=BG_PANEL, padx=18, pady=12)
    ti.pack(side=tk.LEFT)
    tk.Label(ti, text="NEW CASES", font=(FONT_UI, 15, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(ti, text="Installment Case Management",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    make_shortcut_bar(win, [
        ("F1",  "NEW CASE",              ACCENT2),
        ("F2",  "OPEN INSTALMENT CHART", ACCENT),
        ("F3",  "OPEN CASE DETAILS",     ACCENT_PUR),
        ("ESC", "CLOSE",                 ACCENT_RED),
        ("F8",  "DELETE CASE",           ACCENT_YEL),
        ("F9",  "SEARCH",                "#36bfd9"),
    ])
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    # Search bar
    sf = tk.Frame(win, bg=BG, padx=16, pady=8)
    sf.pack(fill=tk.X)
    tk.Label(sf, text="🔍", font=(FONT_UI, 11), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, font=(FONT_UI, 10), fg=TEXT_DIM,
                  bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                  highlightthickness=1, highlightcolor=ACCENT,
                  highlightbackground=BORDER, width=38)
    se.pack(side=tk.LEFT, ipady=7, padx=(8, 12))
    PH = "Search by file no, customer, village…"
    se.insert(0, PH)
    se.bind("<FocusIn>",
            lambda e: (se.delete(0, tk.END), se.config(fg=TEXT)) if se.get() == PH else None)
    se.bind("<FocusOut>",
            lambda e: (se.insert(0, PH), se.config(fg=TEXT_DIM)) if not se.get() else None)

    rec_badge = tk.Label(sf, text=f"  {len(INSTALLMENT_CASES)} records  ",
                         font=(FONT_UI, 9, "bold"), fg=ACCENT, bg="#1b2e4a",
                         padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    # Table
    to = tk.Frame(win, bg=BG, padx=20)
    to.pack(fill=tk.BOTH, expand=True)
    tb = tk.Frame(to, bg=BORDER, bd=1)
    tb.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(tb, columns=INST_COLS, show="headings", style="T.Treeview")
    for col, head, width in zip(INST_COLS, INST_HEADS, INST_WIDTHS):
        tree.heading(col, text=head)
        tree.column(col, width=width, minwidth=50, anchor="w")
    tree.tag_configure("even", background=BG_CARD)
    tree.tag_configure("odd",  background=BG_ROW_ALT)

    all_data = [tuple(r.get(c, "") for c in INST_COLS) for r in INSTALLMENT_CASES]

    def populate(rows):
        for item in tree.get_children(): tree.delete(item)
        for i, vals in enumerate(rows):
            tree.insert("", tk.END, values=vals,
                        tags=("even" if i % 2 == 0 else "odd",))
        rec_badge.config(text=f"  {len(rows)} records  ")

    populate(all_data)
    attach_selection_bar(tree, to, color=ACCENT)

    

    tree.grid(row=0, column=0, sticky="nsew")
    
    tb.grid_rowconfigure(0, weight=1)
    tb.grid_columnconfigure(0, weight=1)

    # Status bar
    try:
        tf_ = sum(float(str(r.get('finance_amt', 0)).replace(',', '') or 0) for r in INSTALLMENT_CASES)
        tb_ = sum(float(str(r.get('balance', 0)).replace(',', '') or 0)     for r in INSTALLMENT_CASES)
    except Exception:
        tf_ = tb_ = 0.0

    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
    sbar = tk.Frame(win, bg=BG_PANEL, pady=7, padx=16)
    sbar.pack(fill=tk.X)

    gf = tk.Frame(sbar, bg=BG_PANEL)
    gf.pack(side=tk.LEFT)
    tk.Label(gf, text="GOTO CASE ID", font=(FONT_UI, 8, "bold"),
             fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    goto_var = tk.StringVar()
    ge = tk.Entry(gf, textvariable=goto_var, font=(FONT_MONO, 10),
                  fg=TEXT, bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                  highlightthickness=1, highlightcolor=ACCENT,
                  highlightbackground=BORDER, width=10)
    ge.pack(side=tk.LEFT, padx=(8, 0), ipady=4)

    def do_goto(e=None):
        t = goto_var.get().strip()
        for item in tree.get_children():
            if str(tree.item(item, "values")[-1]) == t:
                tree.selection_set(item); tree.see(item); return
        messagebox.showinfo("Not Found", f"Case ID '{t}' not found.", parent=win)

    ge.bind("<Return>", do_goto)
    tk.Button(gf, text="GO", font=(FONT_UI, 8, "bold"), fg=BG, bg=ACCENT,
              relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
              command=do_goto).pack(side=tk.LEFT, padx=6)

    pending_lbl = tk.Label(sbar, text=f"NO OF PENDING CASES  {len(INSTALLMENT_CASES)}",
                           font=(FONT_UI, 9, "bold"), fg=ACCENT_YEL, bg=BG_PANEL)
    pending_lbl.pack(side=tk.LEFT, padx=30)

    tots = tk.Frame(sbar, bg=BG_PANEL)
    tots.pack(side=tk.RIGHT)
    for lbl, val, color in [("Finance Total", f"₹ {tf_:,.2f}", ACCENT2),
                             ("Balance Total", f"₹ {tb_:,.2f}", ACCENT_RED)]:
        tf2 = tk.Frame(tots, bg=BG_CARD, padx=12, pady=4)
        tf2.pack(side=tk.LEFT, padx=4)
        tk.Label(tf2, text=lbl, font=(FONT_UI, 7, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        tk.Label(tf2, text=val, font=(FONT_MONO, 11, "bold"), fg=color, bg=BG_CARD).pack(anchor="w")

    # ── Actions ───────────────────────────────────────────────────────────
    def refresh():
        all_data.clear()
        all_data.extend(tuple(r.get(c, "") for c in INST_COLS) for r in INSTALLMENT_CASES)
        do_search()
        pending_lbl.config(text=f"NO OF PENDING CASES  {len(INSTALLMENT_CASES)}")

    def new_case():
        new_case_form(win, on_save_callback=lambda _: win.after(100, refresh))

    def open_detail(e=None):
        
        root = tk.Tk()
        root.title("New Case Details")
        root.geometry("1200x650")
        root.configure(bg="#f4f6f8")

        # ---------- MAIN CONTAINERS ----------
        left_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        left_frame.place(x=10, y=10, width=380, height=600)

        right_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        right_frame.place(x=400, y=10, width=780, height=600)

        # ---------- LEFT SIDE (CUSTOMER) ----------
        tk.Label(left_frame, text="NEW CASE DETAILS", font=("Arial", 12, "bold"), bg="white").pack(pady=5)

        def add_field(parent, label):
            frame = tk.Frame(parent, bg="white")
            frame.pack(fill="x", padx=10, pady=3)
            tk.Label(frame, text=label, width=12, anchor="w", bg="white").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        file_no = add_field(left_frame, "FILE NO")
        date = add_field(left_frame, "DATE")
        account = add_field(left_frame, "ACCOUNT")
        father = add_field(left_frame, "W/O D/O S/O")
        address = add_field(left_frame, "ADDRESS")
        village = add_field(left_frame, "VILLAGE")
        mobile = add_field(left_frame, "MOBILE")
        remarks = add_field(left_frame, "REMARKS")

        # ---------- GUARANTOR ----------
        tk.Label(left_frame, text="FIRST GUARANTOR PARTICULARS",
                font=("Arial", 10, "bold"), bg="white").pack(pady=10)

        g_name = add_field(left_frame, "NAME")
        g_father = add_field(left_frame, "W/O D/O S/O")
        g_address = add_field(left_frame, "ADDRESS")
        g_village = add_field(left_frame, "VILLAGE")
        g_mobile = add_field(left_frame, "MOBILE")
        g_remarks = add_field(left_frame, "REMARKS")

        # ---------- RIGHT SIDE (ITEM DETAILS) ----------
        tk.Label(right_frame, text="ITEM PARTICULARS",
                font=("Arial", 12, "bold"), bg="white").pack(pady=5)

        top_frame = tk.Frame(right_frame, bg="white")
        top_frame.pack(fill="x", padx=10)

        def add_small(parent, label):
            frame = tk.Frame(parent, bg="white")
            frame.pack(side="left", padx=10)
            tk.Label(frame, text=label, bg="white").pack()
            e = tk.Entry(frame, width=12)
            e.pack()
            return e

        item_entry = add_small(top_frame, "ITEM")
        amount     = add_small(top_frame, "AMOUNT")
        receipt_t  = add_small(top_frame, "TOTAL RECEIPT")
        balance    = add_small(top_frame, "BALANCE")

        # NEXT DUE DATE
        due_frame = tk.Frame(right_frame, bg="white")
        due_frame.pack(pady=10)

        tk.Label(due_frame, text="NEXT DUE DATE", bg="white").pack(side="left")
        due_entry = tk.Entry(due_frame)
        due_entry.pack(side="left", padx=10)

        # ---------- TABLE ----------
        tbl_cols = ("item", "date", "sale_amt", "receipt")
        sale_tree = ttk.Treeview(right_frame, columns=tbl_cols, show="headings", height=10)

        sale_tree.heading("item",     text="ITEM")
        sale_tree.heading("date",     text="DATE")
        sale_tree.heading("sale_amt", text="SALE AMT")
        sale_tree.heading("receipt",  text="RECEIPT")

        for c in tbl_cols:
            sale_tree.column(c, anchor="center", width=160)

        sale_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # SAMPLE ROW
        sale_tree.insert("", "end", values=("", "30/07/2024", "15200", "200"))

        # --- Inline editing for the sale table ---
        _sale_edit = [None]

        def on_sale_dbl(event):
            row = sale_tree.identify_row(event.y)
            col = sale_tree.identify_column(event.x)
            if not row:
                return
            if _sale_edit[0]:
                _sale_edit[0].destroy()
                _sale_edit[0] = None
            bbox = sale_tree.bbox(row, col)
            if not bbox:
                return
            bx, by, bw, bh = bbox
            ci = int(col.replace("#", "")) - 1
            cur = sale_tree.item(row, "values")[ci]
            ent = tk.Entry(sale_tree, font=("Segoe UI", 10),
                           relief="flat", highlightthickness=1,
                           highlightcolor="#60a5fa", highlightbackground="#60a5fa")
            ent.place(x=bx, y=by, width=bw, height=bh)
            ent.insert(0, cur)
            ent.select_range(0, tk.END)
            ent.focus_set()
            _sale_edit[0] = ent

            def commit(e=None):
                vals = list(sale_tree.item(row, "values"))
                vals[ci] = ent.get()
                sale_tree.item(row, values=vals)
                ent.destroy()
                _sale_edit[0] = None

            ent.bind("<Return>",   commit)
            ent.bind("<Tab>",      commit)
            ent.bind("<Escape>",   lambda e: (ent.destroy(), _sale_edit.__setitem__(0, None)))
            ent.bind("<FocusOut>", commit)

        sale_tree.bind("<Double-1>", on_sale_dbl)

        def add_sale_row():
            sale_tree.insert("", "end", values=("", "", "", ""))

        tk.Button(right_frame, text="＋  Add Row", font=("Segoe UI", 9),
                  fg="white", bg="#60a5fa", relief="flat", bd=0,
                  padx=10, pady=4, cursor="hand2",
                  command=add_sale_row).pack(anchor="w", padx=10, pady=(0, 6))

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(root, bg="#f4f6f8")
        btn_frame.place(x=10, y=620)

        tk.Button(btn_frame, text="CANCEL Esc", width=15, bg="#ddd",
                  command=root.destroy).pack(side="left", padx=10)
        tk.Button(btn_frame, text="SAVE & EXIT F10", width=20,
                  bg="#4CAF50", fg="white",
                  command=lambda: messagebox.showinfo(
                      "Saved", "Case details saved.", parent=root)
                  ).pack(side="left")
        root.bind("<Escape>", lambda e: root.destroy())
        root.bind("<F10>",    lambda e: messagebox.showinfo(
            "Saved", "Case details saved.", parent=root))

    def open_installment_chart(tree, win):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first", parent=win)
            return

        vals = tree.item(sel[0], "values")

        top = tk.Toplevel(win)
        top.title("Installment Chart")
        top.geometry("1100x640")
        top.configure(bg=BG)
        apply_dark_titlebar(top)

        # HEADER
        header = tk.Frame(top, bg=BG_PANEL, pady=10)
        header.pack(fill="x")
        tk.Frame(header, bg=ACCENT, width=4).pack(side="left", fill="y")
        hi = tk.Frame(header, bg=BG_PANEL, padx=16)
        hi.pack(side="left")
        tk.Label(hi, text="INSTALLMENT CHART", font=(FONT_UI, 13, "bold"),
                 fg=TEXT, bg=BG_PANEL).pack(anchor="w")
        tk.Label(hi, text=f"{vals[2]}  ·  Mobile: {vals[4]}  ·  Case: {vals[-1]}",
                 font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
        tk.Label(header, text=f"Due: {vals[6]}", font=(FONT_UI, 11, "bold"),
                 fg=ACCENT_YEL, bg=BG_PANEL).pack(side="right", padx=20)
        tk.Frame(top, bg=BORDER, height=1).pack(fill="x")

        # TABLE
        columns = ("no", "inst_date", "rec_date", "receipt", "amount", "balance")

        tbl_wrap = tk.Frame(top, bg=BG, padx=20, pady=10)
        tbl_wrap.pack(fill="both", expand=True)

        tree2 = ttk.Treeview(tbl_wrap, columns=columns, show="headings",
                              style="T.Treeview", height=20)
        tree2.pack(fill="both", expand=True)

        headings = ["NO.", "INST.DATE", "RECVD.DATE", "RECEIPT NO.", "AMOUNT", "BALANCE"]

        for col, head in zip(columns, headings):
            tree2.heading(col, text=head)
            tree2.column(col, anchor="center", width=150)

        tree2.tag_configure("even", background=BG_CARD)
        tree2.tag_configure("odd",  background=BG_ROW_ALT)

        balance_fixed = vals[6]

        for i in range(1, 13):
            tree2.insert("", "end", values=(
                i,
                f"30/{str(i).zfill(2)}/2024",
                "",
                "",
                "",
                balance_fixed
            ), tags=("even" if i % 2 == 0 else "odd",))

        attach_selection_bar(tree2, tbl_wrap, color=ACCENT2)

        # EDITABLE CELLS
        edit_entry = [None]

        def on_double_click(event):
            item = tree2.identify_row(event.y)
            col  = tree2.identify_column(event.x)

            if not item:
                return

            col_index = int(col.replace("#", "")) - 1

            if col_index in [0, 5]:   # lock NO + BALANCE
                return

            # Destroy any existing editor
            if edit_entry[0]:
                edit_entry[0].destroy()
                edit_entry[0] = None

            bbox = tree2.bbox(item, col)
            if not bbox:
                return
            x, y, width, height = bbox

            current_val = tree2.item(item, "values")[col_index]

            entry = tk.Entry(tree2, font=(FONT_MONO, 10),
                             fg=TEXT, bg=BG_INPUT,
                             insertbackground=ACCENT, relief="flat",
                             highlightthickness=1, highlightcolor=ACCENT,
                             highlightbackground=ACCENT)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, current_val)
            entry.select_range(0, tk.END)
            entry.focus_set()
            edit_entry[0] = entry

            def commit(e=None):
                values = list(tree2.item(item, "values"))
                values[col_index] = entry.get()
                tree2.item(item, values=values)
                entry.destroy()
                edit_entry[0] = None

            def cancel(e=None):
                entry.destroy()
                edit_entry[0] = None

            entry.bind("<Return>",  commit)
            entry.bind("<Tab>",     commit)
            entry.bind("<Escape>",  cancel)
            entry.bind("<FocusOut>", commit)

        tree2.bind("<Double-1>", on_double_click)

        btn_bar = tk.Frame(top, bg="white")
        btn_bar.pack(fill="x", padx=10, pady=6)
        tk.Button(btn_bar, text="💾  SAVE  F10", font=(FONT_UI, 9, "bold"),
                  fg=BG, bg=ACCENT2, relief="flat", bd=0, padx=14, pady=6,
                  cursor="hand2",
                  command=lambda: messagebox.showinfo(
                      "Saved", "Installment chart saved.", parent=top)
                  ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_bar, text="✕  CLOSE", font=(FONT_UI, 9, "bold"),
                  fg=ACCENT_RED, bg="white", relief="flat", bd=0, padx=14, pady=6,
                  cursor="hand2", command=top.destroy).pack(side=tk.LEFT)
        top.bind("<F10>", lambda e: messagebox.showinfo(
            "Saved", "Installment chart saved.", parent=top))
        top.bind("<Escape>", lambda e: top.destroy())

    def delete_case():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("F8", "Select a case to delete.", parent=win); return
        vals = tree.item(sel[0], "values")
        if messagebox.askyesno("Delete", f"Delete case {vals[0]} — {vals[2]}?", parent=win):
            cid = str(vals[-1])
            for i, r in enumerate(INSTALLMENT_CASES):
                if str(r.get('id', '')) == cid:
                    INSTALLMENT_CASES.pop(i); break
            refresh()

    def do_search(*_):
        q = sv.get().lower().strip()
        if q == PH.lower(): q = ""
        populate([r for r in all_data if not q or any(q in str(v).lower() for v in r)])

    sv.trace_add("write", do_search)
    win.bind("<F1>",     lambda e: new_case())
    win.bind("<F2>",     lambda e: open_installment_chart(tree,win))
    win.bind("<F3>",     lambda e: open_detail())
    win.bind("<F8>",     lambda e: delete_case())
    win.bind("<F9>",     lambda e: se.focus_set())
    win.bind("<Escape>", lambda e: win.destroy())
    tree.bind("<Double-1>", open_detail)


# ═════════════════════════════════════════════════════════════════════════════
# GENERIC TABLE
# ═════════════════════════════════════════════════════════════════════════════
COMMON_COLS   = ['file_no', 'date', 'customer', 'village', 'mobile_no', 'finance_amt', 'balance', 'id']
COMMON_HEADS  = ['File No', 'Date', 'Customer', 'Village', 'Mobile No', 'Finance Amt', 'Balance', 'ID']
COMMON_WIDTHS = [80, 100, 180, 130, 140, 115, 105, 65]


def show_table(parent, title, data, subtitle=""):
    win = tk.Toplevel(parent)
    win.title(f"{title} — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    tk.Frame(win, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
    right = tk.Frame(win, bg=BG)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    topbar = tk.Frame(right, bg=BG_PANEL, pady=14, padx=20)
    topbar.pack(fill=tk.X)
    tb2 = tk.Frame(topbar, bg=BG_PANEL)
    tb2.pack(side=tk.LEFT)
    tk.Label(tb2, text=title, font=(FONT_UI, 16, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    if subtitle:
        tk.Label(tb2, text=subtitle, font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
    badge2 = tk.Label(topbar, text=f"  {len(data)}  ", font=(FONT_UI, 9, "bold"),
                      fg=ACCENT, bg="#1b2e4a", padx=6, pady=4)
    badge2.pack(side=tk.LEFT, padx=16)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 9),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)

    make_shortcut_bar(right, [("ESC", "CLOSE", ACCENT_RED), ("F9", "SEARCH", "#36bfd9")])
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    sf2 = tk.Frame(right, bg=BG, padx=16, pady=8)
    sf2.pack(fill=tk.X)
    tk.Label(sf2, text="🔍", font=(FONT_UI, 11), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv2 = tk.StringVar()
    se2 = tk.Entry(sf2, textvariable=sv2, font=(FONT_UI, 10), fg=TEXT_DIM,
                   bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                   highlightthickness=1, highlightcolor=ACCENT,
                   highlightbackground=BORDER, width=36)
    se2.pack(side=tk.LEFT, ipady=6, padx=(8, 0))
    PH3 = "Search records…"
    se2.insert(0, PH3)
    se2.bind("<FocusIn>",
             lambda e: (se2.delete(0, tk.END), se2.config(fg=TEXT)) if se2.get() == PH3 else None)
    se2.bind("<FocusOut>",
             lambda e: (se2.insert(0, PH3), se2.config(fg=TEXT_DIM)) if not se2.get() else None)

    tf4 = tk.Frame(right, bg=BG, padx=20)
    tf4.pack(fill=tk.BOTH, expand=True)
    border2 = tk.Frame(tf4, bg=BORDER)
    border2.pack(fill=tk.BOTH, expand=True, pady=8)

    tree2 = ttk.Treeview(border2, columns=COMMON_COLS, show="headings", style="T.Treeview")
    for col, head, w in zip(COMMON_COLS, COMMON_HEADS, COMMON_WIDTHS):
        tree2.heading(col, text=head)
        tree2.column(col, width=w, minwidth=50, anchor="w")
    tree2.tag_configure("even", background=BG_CARD)
    tree2.tag_configure("odd",  background=BG_ROW_ALT)

    all_rows2 = [tuple(row.get(c, "") for c in COMMON_COLS) for row in data]

    def pop2(rows):
        for item in tree2.get_children(): tree2.delete(item)
        for i, vals in enumerate(rows):
            tree2.insert("", tk.END, values=vals, tags=("even" if i%2==0 else "odd",))
        badge2.config(text=f"  {len(rows)}  ")

    pop2(all_rows2)

    attach_selection_bar(tree2, tf4, color=ACCENT)
    
    tree2.grid(row=0, column=0, sticky="nsew")
  
    border2.grid_rowconfigure(0, weight=1)
    border2.grid_columnconfigure(0, weight=1)

    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)
    sb2 = tk.Frame(right, bg=BG_PANEL, pady=6, padx=16)
    sb2.pack(fill=tk.X)
    tk.Label(sb2, text=f"Sandhu Enterprises  ·  {title}",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)

    def do_s2(*_):
        q = sv2.get().lower().strip()
        if q == PH3.lower(): q = ""
        pop2([r for r in all_rows2 if not q or any(q in str(v).lower() for v in r)])

    sv2.trace_add("write", do_s2)
    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<F9>",     lambda e: se2.focus_set())


# ═════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
def overview_window(parent):
    win = tk.Toplevel(parent)
    win.title("Overview — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)

    tk.Frame(win, bg=ACCENT2, width=4).pack(side=tk.LEFT, fill=tk.Y)
    right = tk.Frame(win, bg=BG)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    topbar = tk.Frame(right, bg=BG_PANEL, pady=14, padx=20)
    topbar.pack(fill=tk.X)
    tk.Label(topbar, text="Dashboard Overview", font=(FONT_UI, 16, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 9),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    body = tk.Frame(right, bg=BG, padx=36, pady=32)
    body.pack(fill=tk.BOTH, expand=True)

    grid2 = tk.Frame(body, bg=BG)
    grid2.pack(fill=tk.X, pady=(0, 32))
    for i, (icon, label, value, color) in enumerate([
        ("📁", "Total Installments",  str(OVERVIEW['total_installments']), ACCENT),
        ("💰", "Total Due Amount",    f"₹ {OVERVIEW['total_due']:,}",       ACCENT_YEL),
        ("🔴", "Active Credit Cases", str(OVERVIEW['credit_active']),       ACCENT_RED),
        ("🏘️", "Configured Villages", str(OVERVIEW['villages']),            ACCENT2),
    ]):
        card2 = tk.Frame(grid2, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        card2.grid(row=0, column=i, padx=10, sticky="nsew")
        grid2.grid_columnconfigure(i, weight=1)
        inn = tk.Frame(card2, bg=BG_CARD, padx=22, pady=20)
        inn.pack(fill=tk.BOTH, expand=True)
        tk.Label(inn, text=icon, font=(FONT_UI, 20), fg=color, bg=BG_CARD).pack(anchor="w")
        tk.Label(inn, text=value, font=(FONT_UI, 24, "bold"), fg=TEXT, bg=BG_CARD).pack(anchor="w", pady=(6, 2))
        tk.Label(inn, text=label, font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        tk.Frame(card2, bg=color, height=3).pack(fill=tk.X, side=tk.BOTTOM)

    tk.Label(body, text="System Details", font=(FONT_UI, 12, "bold"),
             fg=TEXT, bg=BG).pack(anchor="w", pady=(0, 10))
    ic2 = tk.Frame(body, bg=BG_CARD, highlightbackground=BORDER,
                   highlightthickness=1, padx=24, pady=16)
    ic2.pack(fill=tk.X)
    for r, (k, v) in enumerate([
        ("Business",     "Sandhu Enterprises"),
        ("System",       "Financial Tracking System"),
        ("Installments", str(OVERVIEW['total_installments'])),
        ("Total Due",    f"₹ {OVERVIEW['total_due']:,}"),
        ("Credit Cases", str(OVERVIEW['credit_active'])),
        ("Villages",     str(OVERVIEW['villages'])),
    ]):
        tk.Label(ic2, text=k, font=(FONT_UI, 9, "bold"), fg=TEXT_DIM,
                 bg=BG_CARD, width=16, anchor="w").grid(row=r, column=0, pady=5, sticky="w")
        tk.Label(ic2, text=v, font=(FONT_UI, 10), fg=TEXT,
                 bg=BG_CARD, anchor="w").grid(row=r, column=1, padx=20, pady=5, sticky="w")
    win.bind("<Escape>", lambda e: win.destroy())


# ═════════════════════════════════════════════════════════════════════════════
# MODULE WRAPPERS
# ═════════════════════════════════════════════════════════════════════════════
def due_payments_window(parent):
    show_table(parent, "Due Payments", DUE_PAYMENTS, "Overdue payment records")

def credit_cases_window(parent):
    win = tk.Toplevel(parent)
    win.title("Installment Cases — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    titlebar = tk.Frame(win, bg=BG_PANEL)
    titlebar.pack(fill=tk.X)
    tk.Frame(titlebar, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
    ti = tk.Frame(titlebar, bg=BG_PANEL, padx=18, pady=12)
    ti.pack(side=tk.LEFT)
    tk.Label(ti, text="NEW CASES", font=(FONT_UI, 15, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(ti, text="Installment Case Management",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    make_shortcut_bar(win, [
        ("F1",  "NEW CASE",              ACCENT2),
        ("F2",  "OPEN CASE DETAILS",     ACCENT_PUR),
        ("ESC", "CLOSE",                 ACCENT_RED),
        ("F8",  "DELETE CASE",           ACCENT_YEL),
        ("F9",  "SEARCH",                "#36bfd9"),
    ])
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    # Search bar
    sf = tk.Frame(win, bg=BG, padx=16, pady=8)
    sf.pack(fill=tk.X)
    tk.Label(sf, text="🔍", font=(FONT_UI, 11), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, font=(FONT_UI, 10), fg=TEXT_DIM,
                  bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                  highlightthickness=1, highlightcolor=ACCENT,
                  highlightbackground=BORDER, width=38)
    se.pack(side=tk.LEFT, ipady=7, padx=(8, 12))
    PH = "Search by file no, customer, village…"
    se.insert(0, PH)
    se.bind("<FocusIn>",
            lambda e: (se.delete(0, tk.END), se.config(fg=TEXT)) if se.get() == PH else None)
    se.bind("<FocusOut>",
            lambda e: (se.insert(0, PH), se.config(fg=TEXT_DIM)) if not se.get() else None)

    rec_badge = tk.Label(sf, text=f"  {len(INSTALLMENT_CASES)} records  ",
                         font=(FONT_UI, 9, "bold"), fg=ACCENT, bg="#1b2e4a",
                         padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    # Table
    to = tk.Frame(win, bg=BG, padx=20)
    to.pack(fill=tk.BOTH, expand=True)
    tb = tk.Frame(to, bg=BORDER, bd=1)
    tb.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(tb, columns=INST_COLS, show="headings", style="T.Treeview")
    for col, head, width in zip(INST_COLS, INST_HEADS, INST_WIDTHS):
        tree.heading(col, text=head)
        tree.column(col, width=width, minwidth=50, anchor="w")
    tree.tag_configure("even", background=BG_CARD)
    tree.tag_configure("odd",  background=BG_ROW_ALT)

    all_data = [tuple(r.get(c, "") for c in INST_COLS) for r in INSTALLMENT_CASES]

    def populate(rows):
        for item in tree.get_children(): tree.delete(item)
        for i, vals in enumerate(rows):
            tree.insert("", tk.END, values=vals,
                        tags=("even" if i % 2 == 0 else "odd",))
        rec_badge.config(text=f"  {len(rows)} records  ")

    populate(all_data)
    attach_selection_bar(tree, to, color=ACCENT)

    

    tree.grid(row=0, column=0, sticky="nsew")
    
    tb.grid_rowconfigure(0, weight=1)
    tb.grid_columnconfigure(0, weight=1)

    # Status bar
    try:
        tf_ = sum(float(str(r.get('finance_amt', 0)).replace(',', '') or 0) for r in INSTALLMENT_CASES)
        tb_ = sum(float(str(r.get('balance', 0)).replace(',', '') or 0)     for r in INSTALLMENT_CASES)
    except Exception:
        tf_ = tb_ = 0.0

    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
    sbar = tk.Frame(win, bg=BG_PANEL, pady=7, padx=16)
    sbar.pack(fill=tk.X)

    gf = tk.Frame(sbar, bg=BG_PANEL)
    gf.pack(side=tk.LEFT)
    tk.Label(gf, text="GOTO CASE ID", font=(FONT_UI, 8, "bold"),
             fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    goto_var = tk.StringVar()
    ge = tk.Entry(gf, textvariable=goto_var, font=(FONT_MONO, 10),
                  fg=TEXT, bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                  highlightthickness=1, highlightcolor=ACCENT,
                  highlightbackground=BORDER, width=10)
    ge.pack(side=tk.LEFT, padx=(8, 0), ipady=4)

    def do_goto(e=None):
        t = goto_var.get().strip()
        for item in tree.get_children():
            if str(tree.item(item, "values")[-1]) == t:
                tree.selection_set(item); tree.see(item); return
        messagebox.showinfo("Not Found", f"Case ID '{t}' not found.", parent=win)

    ge.bind("<Return>", do_goto)
    tk.Button(gf, text="GO", font=(FONT_UI, 8, "bold"), fg=BG, bg=ACCENT,
              relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
              command=do_goto).pack(side=tk.LEFT, padx=6)

    pending_lbl = tk.Label(sbar, text=f"NO OF PENDING CASES  {len(INSTALLMENT_CASES)}",
                           font=(FONT_UI, 9, "bold"), fg=ACCENT_YEL, bg=BG_PANEL)
    pending_lbl.pack(side=tk.LEFT, padx=30)

    tots = tk.Frame(sbar, bg=BG_PANEL)
    tots.pack(side=tk.RIGHT)
    for lbl, val, color in [("Finance Total", f"₹ {tf_:,.2f}", ACCENT2),
                             ("Balance Total", f"₹ {tb_:,.2f}", ACCENT_RED)]:
        tf2 = tk.Frame(tots, bg=BG_CARD, padx=12, pady=4)
        tf2.pack(side=tk.LEFT, padx=4)
        tk.Label(tf2, text=lbl, font=(FONT_UI, 7, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        tk.Label(tf2, text=val, font=(FONT_MONO, 11, "bold"), fg=color, bg=BG_CARD).pack(anchor="w")

    # ── Actions ───────────────────────────────────────────────────────────
    def refresh():
        all_data.clear()
        all_data.extend(tuple(r.get(c, "") for c in INST_COLS) for r in INSTALLMENT_CASES)
        do_search()
        pending_lbl.config(text=f"NO OF PENDING CASES  {len(INSTALLMENT_CASES)}")

    def new_case(e=None):
        
        root = tk.Tk()
        root.title("New Case Details")
        root.geometry("1200x650")
        root.configure(bg="#f4f6f8")

        # ---------- MAIN CONTAINERS ----------
        left_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        left_frame.place(x=10, y=10, width=380, height=600)

        right_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        right_frame.place(x=400, y=10, width=780, height=600)

        # ---------- LEFT SIDE (CUSTOMER) ----------
        tk.Label(left_frame, text="NEW CASE DETAILS", font=("Arial", 12, "bold"), bg="white").pack(pady=5)

        def add_field(parent, label):
            frame = tk.Frame(parent, bg="white")
            frame.pack(fill="x", padx=10, pady=3)
            tk.Label(frame, text=label, width=12, anchor="w", bg="white").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        file_no = add_field(left_frame, "FILE NO")
        date = add_field(left_frame, "DATE")
        account = add_field(left_frame, "ACCOUNT")
        father = add_field(left_frame, "W/O D/O S/O")
        address = add_field(left_frame, "ADDRESS")
        village = add_field(left_frame, "VILLAGE")
        mobile = add_field(left_frame, "MOBILE")
        remarks = add_field(left_frame, "REMARKS")

        # ---------- GUARANTOR ----------
        tk.Label(left_frame, text="FIRST GUARANTOR PARTICULARS",
                font=("Arial", 10, "bold"), bg="white").pack(pady=10)

        g_name = add_field(left_frame, "NAME")
        g_father = add_field(left_frame, "W/O D/O S/O")
        g_address = add_field(left_frame, "ADDRESS")
        g_village = add_field(left_frame, "VILLAGE")
        g_mobile = add_field(left_frame, "MOBILE")
        g_remarks = add_field(left_frame, "REMARKS")

        # ---------- RIGHT SIDE (ITEM DETAILS) ----------
        tk.Label(right_frame, text="ITEM PARTICULARS",
                font=("Arial", 12, "bold"), bg="white").pack(pady=5)

        top_frame = tk.Frame(right_frame, bg="white")
        top_frame.pack(fill="x", padx=10)

        def add_small(parent, label):
            frame = tk.Frame(parent, bg="white")
            frame.pack(side="left", padx=10)
            tk.Label(frame, text=label, bg="white").pack()
            e = tk.Entry(frame, width=12)
            e.pack()
            return e

        item_entry = add_small(top_frame, "ITEM")
        amount     = add_small(top_frame, "AMOUNT")
        receipt_t  = add_small(top_frame, "TOTAL RECEIPT")
        balance    = add_small(top_frame, "BALANCE")

        # NEXT DUE DATE
        due_frame = tk.Frame(right_frame, bg="white")
        due_frame.pack(pady=10)

        tk.Label(due_frame, text="NEXT DUE DATE", bg="white").pack(side="left")
        due_entry = tk.Entry(due_frame)
        due_entry.pack(side="left", padx=10)

        # ---------- TABLE ----------
        tbl_cols = ("item", "date", "sale_amt", "receipt")
        sale_tree = ttk.Treeview(right_frame, columns=tbl_cols, show="headings", height=10)

        sale_tree.heading("item",     text="ITEM")
        sale_tree.heading("date",     text="DATE")
        sale_tree.heading("sale_amt", text="SALE AMT")
        sale_tree.heading("receipt",  text="RECEIPT")

        for c in tbl_cols:
            sale_tree.column(c, anchor="center", width=160)

        sale_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # SAMPLE ROW
        sale_tree.insert("", "end", values=("", "30/07/2024", "15200", "200"))

        # --- Inline editing for the sale table ---
        _sale_edit = [None]

        def on_sale_dbl(event):
            row = sale_tree.identify_row(event.y)
            col = sale_tree.identify_column(event.x)
            if not row:
                return
            if _sale_edit[0]:
                _sale_edit[0].destroy()
                _sale_edit[0] = None
            bbox = sale_tree.bbox(row, col)
            if not bbox:
                return
            bx, by, bw, bh = bbox
            ci = int(col.replace("#", "")) - 1
            cur = sale_tree.item(row, "values")[ci]
            ent = tk.Entry(sale_tree, font=("Segoe UI", 10),
                           relief="flat", highlightthickness=1,
                           highlightcolor="#60a5fa", highlightbackground="#60a5fa")
            ent.place(x=bx, y=by, width=bw, height=bh)
            ent.insert(0, cur)
            ent.select_range(0, tk.END)
            ent.focus_set()
            _sale_edit[0] = ent

            def commit(e=None):
                vals = list(sale_tree.item(row, "values"))
                vals[ci] = ent.get()
                sale_tree.item(row, values=vals)
                ent.destroy()
                _sale_edit[0] = None

            ent.bind("<Return>",   commit)
            ent.bind("<Tab>",      commit)
            ent.bind("<Escape>",   lambda e: (ent.destroy(), _sale_edit.__setitem__(0, None)))
            ent.bind("<FocusOut>", commit)

        sale_tree.bind("<Double-1>", on_sale_dbl)

        def add_sale_row():
            sale_tree.insert("", "end", values=("", "", "", ""))

        tk.Button(right_frame, text="＋  Add Row", font=("Segoe UI", 9),
                  fg="white", bg="#60a5fa", relief="flat", bd=0,
                  padx=10, pady=4, cursor="hand2",
                  command=add_sale_row).pack(anchor="w", padx=10, pady=(0, 6))

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(root, bg="#f4f6f8")
        btn_frame.place(x=10, y=620)

        tk.Button(btn_frame, text="CANCEL Esc", width=15, bg="#ddd",
                  command=root.destroy).pack(side="left", padx=10)
        tk.Button(btn_frame, text="SAVE & EXIT F10", width=20,
                  bg="#4CAF50", fg="white",
                  command=lambda: messagebox.showinfo(
                      "Saved", "Case details saved.", parent=root)
                  ).pack(side="left")
        root.bind("<Escape>", lambda e: root.destroy())
        root.bind("<F10>",    lambda e: messagebox.showinfo(
            "Saved", "Case details saved.", parent=root))

    def delete_case():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("F8", "Select a case to delete.", parent=win); return
        vals = tree.item(sel[0], "values")
        if messagebox.askyesno("Delete", f"Delete case {vals[0]} — {vals[2]}?", parent=win):
            cid = str(vals[-1])
            for i, r in enumerate(INSTALLMENT_CASES):
                if str(r.get('id', '')) == cid:
                    INSTALLMENT_CASES.pop(i); break
            refresh()
    
    def open_case_detail(data):

        root = tk.Toplevel()
        root.title("Case Details")
        root.geometry("1200x650")
        root.configure(bg="#f4f6f8")

        # ---------- MAIN CONTAINERS ----------
        left_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        left_frame.place(x=10, y=10, width=380, height=600)

        right_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        right_frame.place(x=400, y=10, width=780, height=600)

        # ---------- LEFT SIDE (CUSTOMER) ----------
        tk.Label(left_frame, text="CASE DETAILS", font=("Arial", 12, "bold"), bg="white").pack(pady=5)

        def add_field(parent, label):
            frame = tk.Frame(parent, bg="white")
            frame.pack(fill="x", padx=10, pady=3)
            tk.Label(frame, text=label, width=12, anchor="w", bg="white").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        # CUSTOMER
        file_no = add_field(left_frame, "FILE NO")
        file_no.insert(0, data.get("file_no", ""))

        date = add_field(left_frame, "DATE")
        date.insert(0, data.get("date", ""))

        account = add_field(left_frame, "ACCOUNT")
        account.insert(0, data.get("customer", ""))

        father = add_field(left_frame, "W/O D/O S/O")
        father.insert(0, data.get("relation", ""))

        address = add_field(left_frame, "ADDRESS")
        address.insert(0, data.get("address", ""))

        village = add_field(left_frame, "VILLAGE")
        village.insert(0, data.get("village", ""))

        mobile = add_field(left_frame, "MOBILE")
        mobile.insert(0, data.get("mobile_no", ""))

        remarks = add_field(left_frame, "REMARKS")
        remarks.insert(0, data.get("remarks", ""))

        # ---------- GUARANTOR ----------
        tk.Label(left_frame, text="FIRST GUARANTOR PARTICULARS",
                font=("Arial", 10, "bold"), bg="white").pack(pady=10)

        g_name = add_field(left_frame, "NAME")
        g_name.insert(0, data.get("g1_name", ""))

        g_father = add_field(left_frame, "W/O D/O S/O")
        g_father.insert(0, data.get("g1_relation", ""))

        g_address = add_field(left_frame, "ADDRESS")
        g_address.insert(0, data.get("g1_address", ""))

        g_village = add_field(left_frame, "VILLAGE")
        g_village.insert(0, data.get("g1_village", ""))

        g_mobile = add_field(left_frame, "MOBILE")
        g_mobile.insert(0, data.get("g1_mobile", ""))

        g_remarks = add_field(left_frame, "REMARKS")
        g_remarks.insert(0, data.get("g1_remarks", ""))

        # ---------- RIGHT SIDE (ITEM DETAILS) ----------
        tk.Label(right_frame, text="ITEM PARTICULARS",
                font=("Arial", 12, "bold"), bg="white").pack(pady=5)

        top_frame = tk.Frame(right_frame, bg="white")
        top_frame.pack(fill="x", padx=10)

        def add_small(parent, label, value=""):
            frame = tk.Frame(parent, bg="white")
            frame.pack(side="left", padx=10)
            tk.Label(frame, text=label, bg="white").pack()
            e = tk.Entry(frame, width=12)
            e.pack()
            e.insert(0, value)
            return e

        item_entry = add_small(top_frame, "ITEM", data.get("item", ""))
        amount     = add_small(top_frame, "AMOUNT", data.get("amount", ""))
        receipt_t  = add_small(top_frame, "TOTAL RECEIPT", "")
        balance    = add_small(top_frame, "BALANCE", data.get("balance", ""))

        # NEXT DUE DATE
        due_frame = tk.Frame(right_frame, bg="white")
        due_frame.pack(pady=10)

        tk.Label(due_frame, text="NEXT DUE DATE", bg="white").pack(side="left")
        due_entry = tk.Entry(due_frame)
        due_entry.pack(side="left", padx=10)

        # ---------- TABLE ----------
        tbl_cols = ("item", "date", "sale_amt", "receipt")
        sale_tree = ttk.Treeview(right_frame, columns=tbl_cols, show="headings", height=10)

        sale_tree.heading("item",     text="ITEM")
        sale_tree.heading("date",     text="DATE")
        sale_tree.heading("sale_amt", text="SALE AMT")
        sale_tree.heading("receipt",  text="RECEIPT")

        for c in tbl_cols:
            sale_tree.column(c, anchor="center", width=160)

        sale_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # sample row (can customize later)
        sale_tree.insert("", "end", values=(
            data.get("item", ""),
            data.get("date", ""),
            data.get("amount", ""),
            ""
        ))

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(root, bg="#f4f6f8")
        btn_frame.place(x=10, y=620)

        tk.Button(btn_frame, text="CANCEL Esc", width=15, bg="#ddd",
                command=root.destroy).pack(side="left", padx=10)

        tk.Button(btn_frame, text="SAVE & EXIT F10", width=20,
                bg="#4CAF50", fg="white",
                command=lambda: messagebox.showinfo(
                    "Saved", "Changes saved.", parent=root)
                ).pack(side="left")

        root.bind("<Escape>", lambda e: root.destroy())
        root.bind("<F10>",    lambda e: messagebox.showinfo(
            "Saved", "Changes saved.", parent=root))


    def do_search(*_):
        q = sv.get().lower().strip()
        if q == PH.lower(): q = ""
        populate([r for r in all_data if not q or any(q in str(v).lower() for v in r)])

    sv.trace_add("write", do_search)
    win.bind("<F1>",     lambda e: new_case())
    win.bind("<F2>",     lambda e: open_case_detail())
    win.bind("<F8>",     lambda e: delete_case())
    win.bind("<F9>",     lambda e: se.focus_set())
    win.bind("<Escape>", lambda e: win.destroy())
    tree.bind("<Double-1>", open_case_detail())


def due_report_window(parent):
    show_table(parent, "Due Payments Report", DUE_PAYMENTS_REPORT, "Full due payment report")

def village_setup_window(parent):
    show_table(parent, "Village Setup", VILLAGE_SETUP, "Configured village directory")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    root.title("Sandhu Enterprises")
    root.state("zoomed")
    root.configure(bg=BG)
    apply_dark_titlebar(root)
    build_style()

    tk.Frame(root, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
    main_area = tk.Frame(root, bg=BG)
    main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    hb = tk.Frame(main_area, bg=BG_PANEL)
    hb.pack(fill=tk.X)
    hi = tk.Frame(hb, bg=BG_PANEL, padx=28, pady=18)
    hi.pack(side=tk.LEFT)
    tk.Label(hi, text="SANDHU ENTERPRISES", font=(FONT_UI, 22, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(hi, text="Financial Tracking System", font=(FONT_UI, 10),
             fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    tk.Frame(main_area, bg=BORDER, height=1).pack(fill=tk.X)
    ss = tk.Frame(main_area, bg=BG_CARD)
    ss.pack(fill=tk.X)
    for val, lbl, color in [
        (str(OVERVIEW['total_installments']), "Installments", ACCENT),
        (f"₹{OVERVIEW['total_due']:,}",       "Total Due",    ACCENT_YEL),
        (str(OVERVIEW['credit_active']),       "Credit Cases", ACCENT_RED),
        (str(OVERVIEW['villages']),            "Villages",     ACCENT2),
    ]:
        sf3 = tk.Frame(ss, bg=BG_CARD, padx=24, pady=12)
        sf3.pack(side=tk.LEFT)
        tk.Label(sf3, text=val, font=(FONT_UI, 14, "bold"), fg=color, bg=BG_CARD).pack()
        tk.Label(sf3, text=lbl, font=(FONT_UI, 8), fg=TEXT_DIM, bg=BG_CARD).pack()
        tk.Frame(ss, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

    tk.Frame(main_area, bg=BORDER, height=1).pack(fill=tk.X)

    center = tk.Frame(main_area, bg=BG)
    center.pack(fill=tk.BOTH, expand=True)
    nav = tk.Frame(center, bg=BG)
    nav.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(nav, text="Navigation", font=(FONT_UI, 11, "bold"),
             fg=TEXT_DIM, bg=BG).pack(pady=(0, 20))

    for label, func, color in [
        ("📁  Installment Cases",   installment_window,   ACCENT),
        ("💰  Due Payments",        due_payments_window,  ACCENT2),
        ("🔴  Credit Cases",        credit_cases_window,  ACCENT_RED),
        ("📊  Due Report",          due_report_window,    ACCENT_YEL),
        ("🏘️  Village Setup",       village_setup_window, ACCENT_PUR),
        ("📈  Overview",            overview_window,      "#36bfd9"),
    ]:
        rf2 = tk.Frame(nav, bg=BG)
        rf2.pack(fill=tk.X, pady=5)
        btn2 = tk.Button(rf2, text=label, command=lambda f=func: f(root),
                         font=(FONT_UI, 12, "bold"), fg=TEXT, bg=BG_CARD,
                         activeforeground=TEXT, activebackground=BG_PANEL,
                         relief="flat", bd=0, cursor="hand2",
                         width=28, height=2, anchor="w", padx=20)
        btn2.pack(side=tk.LEFT)
        btn2.bind("<Enter>", lambda e, b=btn2: b.config(bg=BG_PANEL))
        btn2.bind("<Leave>", lambda e, b=btn2: b.config(bg=BG_CARD))
        ind2 = tk.Frame(rf2, bg=color, width=4)
        ind2.place(in_=btn2, relx=0, rely=0, relheight=1, x=0)

    tk.Frame(main_area, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)
    sb3 = tk.Frame(main_area, bg=BG_PANEL, pady=6, padx=16)
    sb3.pack(fill=tk.X, side=tk.BOTTOM)
    tk.Label(sb3, text="Sandhu Enterprises  ·  Financial Tracking System  ·  Ready",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    main()
