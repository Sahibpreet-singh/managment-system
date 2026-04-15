import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database as db

# ── Load data from SQLite at startup ──────────────────────────────────────────
def _reload_all():
    global INSTALLMENT_CASES, CREDIT_CASES, OVERVIEW
    INSTALLMENT_CASES = db.get_all_installment_cases()
    CREDIT_CASES      = db.get_all_credit_cases()
    OVERVIEW          = db.get_overview()

INSTALLMENT_CASES = []
CREDIT_CASES      = []
OVERVIEW          = {}
_reload_all()

# Legacy compat helpers (DUE views now come from DB directly)
DUE_PAYMENTS        = []   # populated dynamically
DUE_PAYMENTS_REPORT = []   # populated dynamically
VILLAGE_SETUP       = []   # populated dynamically

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
def fmt_customer(name, relation=""):
    """Return 'Name (Father)' if relation provided, else just 'Name'."""
    name = str(name or "").strip()
    relation = str(relation or "").strip()
    if relation:
        return f"{name} ({relation})"
    return name


# ── Admin password ────────────────────────────────────────────────────────────
ADMIN_PASSWORD = "admin123"   # ← change this to your preferred password

def admin_confirm(parent, action="delete this record"):
    """Show a password dialog. Returns True only if the correct password is entered."""
    dlg = tk.Toplevel(parent)
    dlg.title("Admin Authorisation")
    dlg.resizable(False, False)
    dlg.configure(bg=BG_PANEL)
    dlg.grab_set()
    apply_dark_titlebar(dlg)

    # Centre over parent
    dlg.update_idletasks()
    pw, ph = parent.winfo_rootx(), parent.winfo_rooty()
    pw += parent.winfo_width()  // 2
    ph += parent.winfo_height() // 2
    dlg.geometry(f"360x210+{pw-180}+{ph-105}")

    tk.Frame(dlg, bg=ACCENT_RED, height=4).pack(fill=tk.X)

    body = tk.Frame(dlg, bg=BG_PANEL, padx=28, pady=18)
    body.pack(fill=tk.BOTH, expand=True)

    tk.Label(body, text="🔒  Admin Required",
             font=(FONT_UI, 12, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(body, text=f"Enter admin password to {action}.",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w", pady=(2, 12))

    pw_var = tk.StringVar()
    pw_entry = tk.Entry(body, textvariable=pw_var, show="●",
                        font=(FONT_UI, 11), fg=TEXT, bg=BG_INPUT,
                        insertbackground=ACCENT, relief="flat",
                        highlightthickness=1, highlightcolor=ACCENT,
                        highlightbackground=BORDER)
    pw_entry.pack(fill=tk.X, ipady=7)
    pw_entry.focus_set()

    result = [False]
    err_lbl = tk.Label(body, text="", font=(FONT_UI, 9), fg=ACCENT_RED, bg=BG_PANEL)
    err_lbl.pack(anchor="w", pady=(4, 0))

    def confirm(e=None):
        if pw_var.get() == ADMIN_PASSWORD:
            result[0] = True
            dlg.destroy()
        else:
            err_lbl.config(text="Incorrect password. Try again.")
            pw_entry.delete(0, tk.END)
            pw_entry.focus_set()

    btn_row = tk.Frame(body, bg=BG_PANEL)
    btn_row.pack(fill=tk.X, pady=(10, 0))
    tk.Button(btn_row, text="✓  Confirm", command=confirm,
              font=(FONT_UI, 10, "bold"), fg=BG, bg=ACCENT_RED,
              relief="flat", bd=0, padx=16, pady=6, cursor="hand2").pack(side=tk.LEFT)
    tk.Button(btn_row, text="Cancel", command=dlg.destroy,
              font=(FONT_UI, 10), fg=TEXT_DIM, bg=BG_PANEL,
              relief="flat", bd=0, padx=16, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=8)

    pw_entry.bind("<Return>", confirm)
    dlg.wait_window()
    return result[0]


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
    village_vals = db.get_villages()
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
    for i in range(4):
     fg2.grid_columnconfigure(i, weight=1)

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
            'amount_financed': get('amount_financed'),
            'no_instalments': get('no_instalments'),
            'instalment_amt': get('instalment_amt'),
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

        new_case_id = db.save_installment_case(record)
        record['id'] = new_case_id
        _reload_all()
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
# CASE DETAIL WINDOW (shared by Installment & Credit)
# ═════════════════════════════════════════════════════════════════════════════
def open_installment_case_detail(data, refresh_callback=None):
    """Opens a styled, editable detail window for an existing case."""
    root = tk.Toplevel()
    root.title("Case Details — Sandhu Enterprises")
    root.state("zoomed")
    root.configure(bg=BG)
    apply_dark_titlebar(root)

    # ── Top bar ───────────────────────────────────────────────────────────
    topbar = tk.Frame(root, bg=BG_PANEL)
    topbar.pack(fill=tk.X)
    tk.Frame(topbar, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
    tb_inner = tk.Frame(topbar, bg=BG_PANEL, padx=18, pady=12)
    tb_inner.pack(side=tk.LEFT)
    tk.Label(tb_inner, text="CASE DETAILS",
             font=(FONT_UI, 15, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(tb_inner, text=f"File No: {data.get('file_no', '')}  ·  {fmt_customer(data.get('customer', ''), data.get('relation', ''))}",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    badge_f = tk.Frame(topbar, bg=BG_PANEL, padx=20)
    badge_f.pack(side=tk.RIGHT)
    tk.Label(badge_f, text="CASE ID", font=(FONT_UI, 8),
             fg=TEXT_DIM, bg=BG_PANEL).pack()
    tk.Label(badge_f, text=str(data.get('id', '')),
             font=(FONT_MONO, 22, "bold"), fg=ACCENT, bg=BG_PANEL).pack()

    tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X)
    make_shortcut_bar(root, [
        ("ESC", "CANCEL",      ACCENT_RED),
        ("F10", "SAVE & EXIT", ACCENT2),
    ])
    tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X)

    # ── Scrollable canvas ─────────────────────────────────────────────────
    canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
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

    def make_card(parent, col, padx=(0, 8)):
        card = tk.Frame(parent, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=14, pady=10)
        card.grid(row=0, column=col, sticky="nsew", padx=padx)
        return card

    def add_row(grid, label, key, row, value="", span=3):
        tk.Label(grid, text=label, font=(FONT_UI, 9), fg=TEXT_DIM,
                 bg=BG_CARD, width=12, anchor="w").grid(
                 row=row, column=0, sticky="w", pady=4, padx=4)
        e = make_entry(grid, width=28)
        e.insert(0, value)
        e.grid(row=row, column=1, columnspan=span, sticky="ew",
               ipady=6, pady=4, padx=(0, 4))
        entries[key] = e

    # ── TOP ROW ───────────────────────────────────────────────────────────
    top_row = tk.Frame(body, bg=BG)
    top_row.pack(fill=tk.X, pady=(0, 8))
    top_row.grid_columnconfigure(0, weight=2)
    top_row.grid_columnconfigure(1, weight=3)

    # Customer card
    cust_card = make_card(top_row, 0)
    section_header(cust_card, "CUSTOMER DETAILS", ACCENT)
    cg = tk.Frame(cust_card, bg=BG_CARD)
    cg.pack(fill=tk.X)
    cg.grid_columnconfigure(1, weight=1)

    cust_fields = [
        ("FILE NO",     "file_no",   data.get("file_no", "")),
        ("DATE",        "date",      data.get("date", "")),
        ("ACCOUNT",     "customer",  data.get("customer", "")),
        ("W/O D/O S/O", "relation",  data.get("relation", "")),
        ("ADDRESS",     "address",   data.get("address", "")),
        ("MOBILE NO",   "mobile_no", data.get("mobile_no", "")),
        ("REMARKS",     "remarks",   data.get("remarks", "")),
    ]
    for i, (lbl, key, val) in enumerate(cust_fields):
        add_row(cg, lbl, key, i, val)

    # Village combobox
    tk.Label(cg, text="VILLAGE", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=len(cust_fields), column=0, sticky="w", pady=3, padx=4)
    village_var = tk.StringVar(value=data.get("village", ""))
    entries['village'] = village_var
    village_vals = db.get_villages()
    ttk.Combobox(cg, textvariable=village_var, values=village_vals,
                 style="Dark.TCombobox", font=(FONT_UI, 10), width=20
                 ).grid(row=len(cust_fields), column=1, sticky="ew", ipady=4, pady=3, padx=(0, 4))

    # Item card
    item_card = make_card(top_row, 1, padx=0)
    section_header(item_card, "ITEM PARTICULARS", ACCENT_PUR)
    ig = tk.Frame(item_card, bg=BG_CARD)
    ig.pack(fill=tk.X)
    ig.grid_columnconfigure(1, weight=1)

    item_fields = [
        ("ITEM",            "item",       data.get("item", "")),
        ("BRAND",           "brand",      data.get("brand", "")),
        ("MODEL",           "model",      data.get("model", "")),
        ("SRNO",            "srno",       data.get("srno", "")),
        ("INVOICE NO",      "invoice_no", data.get("invoice_no", "")),
        ("AMOUNT",          "amount",     data.get("amount", "")),
        ("ADVANCE",         "advance",    data.get("advance", "")),
        ("AMOUNT FINANCED", "amount_financed", data.get("amount_financed", "")),
        ("NO. OF INST",     "no_inst",    data.get("no_instalments", "")),
        ("INST AMOUNT",     "inst_amt",   data.get("instalment_amt", "")),
        ("BALANCE",     "balance",    data.get("balance", "")),
    ]
    for i, (lbl, key, val) in enumerate(item_fields):
        add_row(ig, lbl, key, i, val)

    # ── GUARANTORS ROW ────────────────────────────────────────────────────
    guar_row = tk.Frame(body, bg=BG)
    guar_row.pack(fill=tk.X, pady=(8, 0))
    guar_row.grid_columnconfigure(0, weight=1)
    guar_row.grid_columnconfigure(1, weight=1)

    def build_guar(parent_frame, prefix, title, color, col, data):
        card = tk.Frame(parent_frame, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=14, pady=10)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0, 8) if col == 0 else 0)
        section_header(card, title, color)
        gg = tk.Frame(card, bg=BG_CARD)
        gg.pack(fill=tk.X)
        gg.grid_columnconfigure(1, weight=1)
        fields = [
            ("NAME",        f"{prefix}_name",     data.get(f"{prefix}_name", "")),
            ("W/O D/O S/O", f"{prefix}_relation", data.get(f"{prefix}_relation", "")),
            ("ADDRESS",     f"{prefix}_address",  data.get(f"{prefix}_address", "")),
            ("VILLAGE",     f"{prefix}_village",  data.get(f"{prefix}_village", "")),
            ("MOBILE NO",   f"{prefix}_mobile",   data.get(f"{prefix}_mobile", "")),
            ("REMARKS",     f"{prefix}_remarks",  data.get(f"{prefix}_remarks", "")),
        ]
        for i, (lbl, key, val) in enumerate(fields):
            add_row(gg, lbl, key, i, val)

    build_guar(guar_row, "g1", "FIRST GUARANTOR PARTICULARS",  ACCENT,     0, data)
    build_guar(guar_row, "g2", "SECOND GUARANTOR PARTICULARS", ACCENT_PUR, 1, data)

    # ── Action bar ────────────────────────────────────────────────────────
    tk.Frame(root, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)
    action_bar = tk.Frame(root, bg=BG_PANEL, pady=12, padx=24)
    action_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def get(key):
        v = entries.get(key)
        if v is None: return ""
        if isinstance(v, tk.StringVar): return v.get()
        if isinstance(v, tk.Entry):     return v.get()
        return ""

    def save_changes(e=None):
        data["file_no"]    = get("file_no")
        data["date"]       = get("date")
        data["customer"]   = get("customer")
        data["relation"]   = get("relation")
        data["address"]    = get("address")
        data["village"]    = get("village")
        data["mobile_no"]  = get("mobile_no")
        data["remarks"]    = get("remarks")
        data["item"]       = get("item")
        data["brand"]      = get("brand")
        data["model"]      = get("model")
        data["srno"]       = get("srno")
        data["invoice_no"] = get("invoice_no")
        data["amount"]     = get("amount")
        data["advance"]    = get("advance")
    def save_changes(e=None):
        data["file_no"]        = get("file_no")
        data["date"]           = get("date")
        data["customer"]       = get("customer")
        data["relation"]       = get("relation")
        data["address1"]       = get("address")
        data["village"]        = get("village")
        data["mobile_no"]      = get("mobile_no")
        data["remarks_cust"]   = get("remarks")
        data["item"]           = get("item")
        data["brand"]          = get("brand")
        data["model"]          = get("model")
        data["srno"]           = get("srno")
        data["invoice_no"]     = get("invoice_no")
        data["amount"]         = get("amount")
        data["advance"]        = get("advance")
        data["amount_financed"] = get("amount_financed")
        data["no_instalments"] = get("no_inst")
        data["instalment_amt"] = get("inst_amt")
        data["balance"]        = get("balance")
        data["g1_name"]        = get("g1_name")
        data["g1_relation"]    = get("g1_relation")
        data["g1_address"]     = get("g1_address")
        data["g1_village"]     = get("g1_village")
        data["g1_mobile"]      = get("g1_mobile")
        data["g1_remarks"]     = get("g1_remarks")
        data["g2_name"]        = get("g2_name")
        data["g2_relation"]    = get("g2_relation")
        data["g2_address"]     = get("g2_address")
        data["g2_village"]     = get("g2_village")
        data["g2_mobile"]      = get("g2_mobile")
        data["g2_remarks"]     = get("g2_remarks")

        db.save_installment_case(data)
        _reload_all()
        messagebox.showinfo("Saved ✓", "Changes saved successfully!", parent=root)
        if refresh_callback:
            refresh_callback()
        root.destroy()

    tk.Button(action_bar, text="✕  CANCEL  ESC",
              command=root.destroy,
              font=(FONT_UI, 11, "bold"), fg=ACCENT_RED, bg=BG_CARD,
              activeforeground=ACCENT_RED, activebackground=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
              highlightthickness=1, highlightbackground=ACCENT_RED
              ).pack(side=tk.LEFT, padx=(0, 16))

    tk.Button(action_bar, text="💾  SAVE & EXIT  F10",
              command=save_changes,
              font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT2,
              activeforeground=BG, activebackground="#2ebd68",
              relief="flat", bd=0, cursor="hand2", padx=24, pady=10,
              ).pack(side=tk.LEFT)

    root.bind("<F10>",    save_changes)
    root.bind("<Escape>", lambda e: root.destroy())


# ═════════════════════════════════════════════════════════════════════════════
# INSTALLMENT CHART WINDOW  (top-level, callable from anywhere)
# ═════════════════════════════════════════════════════════════════════════════
def open_installment_chart_window(case_record, parent_win):
    """Open the installment payment chart for a given case record dict."""
    r = case_record
    case_id_str  = str(r.get('id', ''))
    customer     = fmt_customer(r.get('customer', ''), r.get('relation', ''))
    mobile       = r.get('mobile_no', '')
    balance_orig = r.get('balance', '0')
    inst_amt     = r.get('instalment_amt', '0')
    no_inst      = int(r.get('no_instalments') or r.get('no_inst') or 12)

    top = tk.Toplevel(parent_win)
    top.title("Installment Chart")
    top.state("zoomed")
    top.configure(bg=BG)
    apply_dark_titlebar(top)

    # ── Header ────────────────────────────────────────────────────────────
    header = tk.Frame(top, bg=BG_PANEL, pady=10)
    header.pack(fill="x")
    tk.Frame(header, bg=ACCENT, width=4).pack(side="left", fill="y")
    hi = tk.Frame(header, bg=BG_PANEL, padx=16)
    hi.pack(side="left")
    tk.Label(hi, text="INSTALLMENT CHART", font=(FONT_UI, 13, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(hi, text=f"{customer}  ·  Mobile: {mobile}  ·  Case ID: {case_id_str}",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    bal_badge_var = tk.StringVar(value=f"₹ {balance_orig}")
    tk.Label(header, textvariable=bal_badge_var, font=(FONT_MONO, 12, "bold"),
             fg=ACCENT_YEL, bg=BG_PANEL).pack(side="right", padx=20)
    tk.Label(header, text="BALANCE:", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_PANEL).pack(side="right")

    # Show "Amount to be Paid per Instalment" once in header
    tk.Frame(header, bg=BORDER, width=1).pack(side="right", fill="y", padx=4)
    tk.Label(header, text=f"₹ {inst_amt}", font=(FONT_MONO, 12, "bold"),
             fg=ACCENT2, bg=BG_PANEL).pack(side="right", padx=4)
    tk.Label(header, text="AMT TO BE PAID:", font=(FONT_UI, 9), fg=TEXT_DIM,
             bg=BG_PANEL).pack(side="right")

    tk.Frame(top, bg=BORDER, height=1).pack(fill="x")

    make_shortcut_bar(top, [
        ("F10", "SAVE",       ACCENT2),
        ("INS", "ADD ROW",    ACCENT_PUR),
        ("DEL", "DELETE ROW", ACCENT_YEL),
        ("ESC", "CLOSE",      ACCENT_RED),
    ])
    tk.Frame(top, bg=BORDER, height=1).pack(fill="x")

    # ── Table ─────────────────────────────────────────────────────────────
    columns  = ("no", "inst_date", "rec_date", "receipt_no", "amount", "balance")
    headings = ["NO.", "INST. DATE", "RECVD. DATE", "RECEIPT NO.", "AMOUNT PAID", "BALANCE"]
    col_widths = [50, 120, 120, 120, 120, 120]

    tbl_outer = tk.Frame(top, bg=BG, padx=20, pady=8)
    tbl_outer.pack(fill="both", expand=True)

    tbl_border = tk.Frame(tbl_outer, bg=BORDER, bd=1)
    tbl_border.pack(fill="both", expand=True)
    tbl_border.grid_rowconfigure(0, weight=1)
    tbl_border.grid_columnconfigure(0, weight=1)

    tree2 = ttk.Treeview(tbl_border, columns=columns, show="headings",
                          style="T.Treeview")
    tree2.grid(row=0, column=0, sticky="nsew")

    vsb = tk.Scrollbar(tbl_border, orient="vertical", command=tree2.yview)
    tree2.configure(yscrollcommand=vsb.set)
    vsb.grid(row=0, column=1, sticky="ns")

    for col, head, w in zip(columns, headings, col_widths):
        tree2.heading(col, text=head)
        tree2.column(col, anchor="center", width=w, minwidth=50, stretch=True)

    tree2.tag_configure("even",    background=BG_CARD)
    tree2.tag_configure("odd",     background=BG_ROW_ALT)
    tree2.tag_configure("paid",    background="#f0fdf4", foreground="#15803d")
    tree2.tag_configure("unpaid",  background="#fff7ed", foreground="#c2410c")
    tree2.tag_configure("overdue", background="#fff0f0", foreground="#b91c1c")

    attach_selection_bar(tree2, tbl_outer, color=ACCENT2)

    # ── Load saved payments or generate blank rows ─────────────────────────
    saved = []
    try:
        saved = db.get_installment_payments(int(case_id_str))
    except Exception:
        pass

    import datetime as _dt_chart

    def _row_tag(i, recv, inst_date=""):
        """Return 'paid', 'overdue', or 'unpaid' tag for a chart row."""
        if recv and str(recv).strip():
            return "paid"
        # Check if the instalment date has already passed today
        if inst_date and str(inst_date).strip():
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    due = _dt_chart.datetime.strptime(str(inst_date).strip(), fmt).date()
                    if due < _dt_chart.date.today():
                        return "overdue"
                    break
                except ValueError:
                    continue
        return "unpaid"

    if saved:
        for i, p in enumerate(saved):
            recv      = p.get('recv_date', '')
            inst_date = p.get('inst_date', '')
            tree2.insert("", "end", values=(
                p.get('inst_no', i + 1),
                inst_date,
                recv,
                p.get('receipt_no', ''),
                p.get('amount', ''),
                p.get('balance', balance_orig),
            ), tags=(_row_tag(i, recv, inst_date),))
    else:
        for i in range(1, no_inst + 1):
            tree2.insert("", "end", values=(
                i, f"30/{str(i).zfill(2)}/2024", "", "", "", balance_orig
            ), tags=("unpaid",))

    # ── Inline cell editor ────────────────────────────────────────────────
    edit_entry = [None]

    def on_cell_dbl(event):
        item = tree2.identify_row(event.y)
        col  = tree2.identify_column(event.x)
        if not item:
            return
        ci = int(col.replace("#", "")) - 1
        if ci == 0:          # lock NO column only; balance is now editable
            return
        if edit_entry[0]:
            edit_entry[0].destroy(); edit_entry[0] = None
        bbox = tree2.bbox(item, col)
        if not bbox:
            return
        x, y, w, h = bbox
        cur = tree2.item(item, "values")[ci]
        ent = tk.Entry(tree2, font=(FONT_MONO, 10), fg=TEXT, bg=BG_INPUT,
                       insertbackground=ACCENT, relief="flat",
                       highlightthickness=1, highlightcolor=ACCENT,
                       highlightbackground=ACCENT)
        ent.place(x=x, y=y, width=w, height=h)
        ent.insert(0, cur)
        ent.select_range(0, tk.END)
        ent.focus_set()
        edit_entry[0] = ent

        def commit(e=None):
            vals = list(tree2.item(item, "values"))
            vals[ci] = ent.get()
            # update paid/overdue/unpaid colour based on recv_date (index 2) and inst_date (index 1)
            recv      = vals[2] if ci != 2 else ent.get()
            inst_date = vals[1] if ci != 1 else ent.get()
            tree2.item(item, values=vals, tags=(_row_tag(0, recv, inst_date),))
            ent.destroy(); edit_entry[0] = None
            _recalc_balance()

        ent.bind("<Return>",   commit)
        ent.bind("<Tab>",      commit)
        ent.bind("<Escape>",   lambda e: (ent.destroy(), edit_entry.__setitem__(0, None)))
        ent.bind("<FocusOut>", commit)

    tree2.bind("<Double-1>", on_cell_dbl)

    # ── Balance recalc ────────────────────────────────────────────────────
    def _recalc_balance():
        """Recompute running balance for each row and update badge."""
        try:
            fin_amt = float(str(r.get('amount_financed') or r.get('finance_amt') or 0))
        except Exception:
            fin_amt = 0.0
        running = fin_amt
        children = tree2.get_children()
        for child in children:
            vals = list(tree2.item(child, "values"))
            try:
                paid = float(str(vals[4]).replace(',', '') or 0)
            except Exception:
                paid = 0.0
            if vals[2] and str(vals[2]).strip():   # has recv_date → paid
                running -= paid
            vals[5] = f"{running:.2f}"
            recv      = vals[2]
            inst_date = vals[1]
            tree2.item(child, values=vals, tags=(_row_tag(0, recv, inst_date),))
        bal_badge_var.set(f"₹ {running:,.2f}")

    # ── Add / Delete rows ─────────────────────────────────────────────────
    def add_row(e=None):
        n   = len(tree2.get_children())
        no  = n + 1
        tree2.insert("", "end", values=(no, "", "", "", "", balance_orig),
                     tags=("unpaid",))

    def del_row(e=None):
        sel = tree2.selection()
        if not sel:
            return
        if not admin_confirm(top, "delete this instalment row"):
            return
        if messagebox.askyesno("Delete Row", "Delete selected instalment row?", parent=top):
            tree2.delete(sel[0])
            # renumber
            for idx, child in enumerate(tree2.get_children()):
                vals = list(tree2.item(child, "values"))
                vals[0] = idx + 1
                tree2.item(child, values=vals)
            _recalc_balance()

    top.bind("<Insert>", add_row)
    top.bind("<Delete>", del_row)

    # ── Save ──────────────────────────────────────────────────────────────
    def save_chart(e=None):
        rows = []
        for child in tree2.get_children():
            v = tree2.item(child, "values")
            rows.append({
                'inst_no':    v[0],
                'inst_date':  v[1],
                'recv_date':  v[2],
                'receipt_no': v[3],
                'amount':     v[4],
                'balance':    v[5],
            })
        try:
            db.save_installment_payments(int(case_id_str), rows)
            _reload_all()
            messagebox.showinfo("Saved ✓", "Installment chart saved to database.", parent=top)
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=top)

    # ── Button bar ────────────────────────────────────────────────────────
    tk.Frame(top, bg=BORDER, height=1).pack(fill="x")
    btn_bar = tk.Frame(top, bg=BG_PANEL, pady=8, padx=16)
    btn_bar.pack(fill="x")

    tk.Button(btn_bar, text="＋  Add Row  INS", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT_PUR, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=add_row).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="−  Delete Row  DEL", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT_YEL, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=del_row).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="🔄  Recalc Balance", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=_recalc_balance).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="💾  SAVE  F10", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT2, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=save_chart).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="✕  CLOSE  ESC", font=(FONT_UI, 9, "bold"),
              fg=ACCENT_RED, bg=BG_PANEL, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=top.destroy).pack(side=tk.LEFT)

    top.bind("<F10>",    save_chart)
    top.bind("<Escape>", lambda e: top.destroy())


# ═════════════════════════════════════════════════════════════════════════════
# INSTALLMENT CASES WINDOW
# ═════════════════════════════════════════════════════════════════════════════
INST_COLS   = ['file_no', 'date', 'customer_display', 'village', 'mobile_no', 'finance_amt', 'balance', 'id']
INST_HEADS  = ['File No', 'Date', 'Customer (Father)', 'Village', 'Mobile No', 'Finance Amt', 'Balance', 'ID']
INST_WIDTHS = [70, 95, 220, 130, 150, 110, 100, 55]


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

    def _inst_row(r):
        row = []
        for c in INST_COLS:
            if c == 'customer_display':
                row.append(fmt_customer(r.get('customer', ''), r.get('relation', '')))
            else:
                row.append(r.get(c, ''))
        return tuple(row)

    all_data = [_inst_row(r) for r in INSTALLMENT_CASES]

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
        _reload_all()
        all_data.clear()
        all_data.extend(_inst_row(r) for r in INSTALLMENT_CASES)
        do_search()
        pending_lbl.config(text=f"NO OF PENDING CASES  {len(INSTALLMENT_CASES)}")

    def new_case():
        new_case_form(win, on_save_callback=lambda _: win.after(100, refresh))

    def open_detail(e=None):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first", parent=win)
            return
        vals = tree.item(sel[0], "values")
        for r in INSTALLMENT_CASES:
            if str(r.get("id")) == str(vals[-1]):
                open_installment_case_detail(r, refresh)
                break

    def open_installment_chart(tree, win):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first", parent=win)
            return
        vals = tree.item(sel[0], "values")
        case_id = str(vals[-1])
        for r in INSTALLMENT_CASES:
            if str(r.get("id")) == case_id:
                open_installment_chart_window(r, win)
                return

    def delete_case():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("F8", "Select a case to delete.", parent=win); return
        vals = tree.item(sel[0], "values")
        if not admin_confirm(win, "delete this installment case"):
            return
        if messagebox.askyesno("Delete", f"Delete case {vals[0]} — {vals[2]}?", parent=win):
            cid = str(vals[-1])
            db.delete_installment_case(int(cid))
            _reload_all()
            refresh()

    def do_search(*_):
        q = sv.get().lower().strip()
        if q == PH.lower(): q = ""
        populate([r for r in all_data if not q or any(q in str(v).lower() for v in r)])

    def open_chart_from_tree(e=None):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first.", parent=win); return
        vals = tree.item(sel[0], "values")
        case_id = str(vals[-1])
        for r in INSTALLMENT_CASES:
            if str(r.get("id")) == case_id:
                open_installment_chart_window(r, win)
                return
        messagebox.showinfo("Not Found", "Case not found.", parent=win)

    sv.trace_add("write", do_search)
    win.bind("<F1>",     lambda e: new_case())
    win.bind("<F2>",     open_chart_from_tree)
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
    _reload_all()   # refresh stats from DB
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
# CREDIT CASE FORM  (one-time payment — no instalments)
# ═════════════════════════════════════════════════════════════════════════════
def new_credit_case_form(parent, data=None, on_save_callback=None):
    """New / Edit form for Credit Cases.
    Pass data=None for a new case, or a dict to pre-fill for editing.
    """
    editing = data is not None
    win = tk.Toplevel(parent)
    win.title("Credit Case Details — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)

    if editing:
        next_id = data.get('id', '?')
    else:
        try:
            next_id = max(int(r.get('id', 0)) for r in CREDIT_CASES) + 1
        except Exception:
            next_id = 1

    # ── Top bar ───────────────────────────────────────────────────────────
    topbar = tk.Frame(win, bg=BG_PANEL)
    topbar.pack(fill=tk.X)
    tk.Frame(topbar, bg=ACCENT_RED, width=4).pack(side=tk.LEFT, fill=tk.Y)
    tb_inner = tk.Frame(topbar, bg=BG_PANEL, padx=18, pady=12)
    tb_inner.pack(side=tk.LEFT)
    tk.Label(tb_inner,
             text="EDIT CASE DETAILS" if editing else "NEW CASE DETAILS",
             font=(FONT_UI, 15, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(tb_inner, text="Complete all sections · Press F10 to save",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    badge_f = tk.Frame(topbar, bg=BG_PANEL, padx=20)
    badge_f.pack(side=tk.RIGHT)
    tk.Label(badge_f, text="CASE ID", font=(FONT_UI, 8),
             fg=TEXT_DIM, bg=BG_PANEL).pack()
    tk.Label(badge_f, text=str(next_id),
             font=(FONT_MONO, 22, "bold"), fg=ACCENT_RED, bg=BG_PANEL).pack()

    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
    make_shortcut_bar(win, [
        ("ESC", "CANCEL",      ACCENT_RED),
        ("F10", "SAVE & EXIT", ACCENT2),
        ("INS", "ADD ROW",     ACCENT_PUR),
        ("DEL", "DELETE ROW",  ACCENT_YEL),
    ])
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    # ── Main paned layout: no scroll needed at 1920×1080 ─────────────────
    # outer frame fills everything between shortcut bar and action bar
    outer = tk.Frame(win, bg=BG)
    outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

    # Two columns: LEFT ~30%  |  RIGHT ~70%
    outer.grid_columnconfigure(0, weight=3)   # customer + guarantor
    outer.grid_columnconfigure(1, weight=7)   # item + table
    outer.grid_rowconfigure(0, weight=1)

    d = data or {}
    entries = {}

    # ══════════════════════════════════════════════════════════════════════
    # LEFT COLUMN  — Customer + Guarantor stacked
    # ══════════════════════════════════════════════════════════════════════
    left_col = tk.Frame(outer, bg=BG)
    left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    left_col.grid_rowconfigure(0, weight=0)
    left_col.grid_rowconfigure(1, weight=1)
    left_col.grid_columnconfigure(0, weight=1)

    # ── Customer card ─────────────────────────────────────────────────────
    cust_card = tk.Frame(left_col, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=16, pady=12)
    cust_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    section_header(cust_card, "CUSTOMER DETAILS", ACCENT_RED)

    cg = tk.Frame(cust_card, bg=BG_CARD)
    cg.pack(fill=tk.X)
    cg.grid_columnconfigure(1, weight=1)
    cg.grid_columnconfigure(3, weight=1)

    # FILE NO + DATE on same row
    tk.Label(cg, text="FILE NO", font=(FONT_UI, 10), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=0, sticky="w", pady=5, padx=4)
    e_fn = make_entry(cg, width=10)
    e_fn.insert(0, d.get('file_no', ''))
    e_fn.grid(row=0, column=1, sticky="ew", ipady=7, pady=5, padx=(0, 12))
    entries['file_no'] = e_fn

    tk.Label(cg, text="DATE", font=(FONT_UI, 10), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=2, sticky="w", pady=5, padx=4)
    e_dt = make_entry(cg, width=13)
    e_dt.insert(0, d.get('date', 'DD/MM/YYYY'))
    e_dt.config(fg=TEXT if d.get('date') else TEXT_DIM)
    e_dt.grid(row=0, column=3, sticky="ew", ipady=7, pady=5)
    entries['date'] = e_dt
    e_dt.bind("<FocusIn>",
              lambda e: (e_dt.delete(0, tk.END), e_dt.config(fg=TEXT))
                        if e_dt.get() == "DD/MM/YYYY" else None)
    e_dt.bind("<FocusOut>",
              lambda e: (e_dt.insert(0, "DD/MM/YYYY"), e_dt.config(fg=TEXT_DIM))
                        if not e_dt.get() else None)

    for i, (lbl, key) in enumerate([
        ("ACCOUNT",     "customer"),
        ("W/O D/O S/O", "relation"),
        ("ADDRESS",     "address"),
        ("VILLAGE",     "_village_entry"),
        ("MOBILE NO",   "mobile_no"),
        ("REMARKS",     "remarks"),
    ], start=1):
        tk.Label(cg, text=lbl, font=(FONT_UI, 10), fg=TEXT_DIM,
                 bg=BG_CARD, width=12, anchor="w").grid(
                 row=i, column=0, sticky="w", pady=4, padx=4)
        if lbl == "VILLAGE":
            village_var = tk.StringVar(value=d.get('village', ''))
            entries['village'] = village_var
            village_vals = db.get_villages()
            ttk.Combobox(cg, textvariable=village_var, values=village_vals,
                         style="Dark.TCombobox", font=(FONT_UI, 10), width=26
                         ).grid(row=i, column=1, columnspan=3, sticky="ew",
                                ipady=5, pady=4, padx=(0, 4))
        else:
            e = make_entry(cg, width=26)
            e.insert(0, d.get(key, ''))
            e.grid(row=i, column=1, columnspan=3, sticky="ew",
                   ipady=7, pady=4, padx=(0, 4))
            entries[key] = e

    # ── Guarantor card ────────────────────────────────────────────────────
    guar_card = tk.Frame(left_col, bg=BG_CARD,
                          highlightbackground=BORDER, highlightthickness=1,
                          padx=16, pady=12)
    guar_card.grid(row=1, column=0, sticky="nsew")
    section_header(guar_card, "FIRST GUARANTOR PARTICULARS", ACCENT)

    gg = tk.Frame(guar_card, bg=BG_CARD)
    gg.pack(fill=tk.X)
    gg.grid_columnconfigure(1, weight=1)

    for i, (lbl, key) in enumerate([
        ("NAME",        "g1_name"),
        ("W/O D/O S/O", "g1_relation"),
        ("ADDRESS",     "g1_address"),
        ("VILLAGE",     "g1_village"),
        ("MOBILE NO",   "g1_mobile"),
        ("REMARKS",     "g1_remarks"),
    ]):
        tk.Label(gg, text=lbl, font=(FONT_UI, 10), fg=TEXT_DIM,
                 bg=BG_CARD, width=12, anchor="w").grid(
                 row=i, column=0, sticky="w", pady=5, padx=4)
        e = make_entry(gg, width=26)
        e.insert(0, d.get(key, ''))
        e.grid(row=i, column=1, sticky="ew", ipady=7, pady=5, padx=(0, 4))
        entries[key] = e

    # ══════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN — Item Particulars + Photo + Payment Table
    # ══════════════════════════════════════════════════════════════════════
    right_col = tk.Frame(outer, bg=BG)
    right_col.grid(row=0, column=1, sticky="nsew")
    right_col.grid_rowconfigure(1, weight=1)   # table expands
    right_col.grid_columnconfigure(0, weight=1)

    # ── Item Particulars card (top) ───────────────────────────────────────
    item_card = tk.Frame(right_col, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=16, pady=12)
    item_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    section_header(item_card, "ITEM PARTICULARS", ACCENT_PUR)

    # item_card has fields on the left and photo on the right
    item_inner = tk.Frame(item_card, bg=BG_CARD)
    item_inner.pack(fill=tk.X)
    item_inner.grid_columnconfigure(0, weight=1)
    item_inner.grid_columnconfigure(1, weight=0)

    ig = tk.Frame(item_inner, bg=BG_CARD)
    ig.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
    ig.grid_columnconfigure(1, weight=1)

    def money_entry(parent, var, row, label, editable=True, color=ACCENT_RED):
        tk.Label(parent, text=label, font=(FONT_UI, 10), fg=TEXT_DIM,
                 bg=BG_CARD, width=16, anchor="w").grid(
                 row=row, column=0, sticky="w", pady=6, padx=4)
        state = "normal" if editable else "readonly"
        rbg   = BG_INPUT if editable else BG_CARD
        e = tk.Entry(parent, textvariable=var, state=state,
                     font=(FONT_MONO, 11, "bold"), fg=color,
                     bg=rbg, readonlybackground=rbg,
                     insertbackground=ACCENT, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER, width=20)
        e.grid(row=row, column=1, sticky="ew", ipady=8, pady=6, padx=(0, 8))
        return e

    amount_var  = tk.StringVar(value=d.get('amount', ''))
    receipt_var = tk.StringVar(value=d.get('total_receipt', '0.00'))
    balance_var = tk.StringVar(value=d.get('balance', '0.00'))

    money_entry(ig, amount_var,  0, "AMOUNT",         editable=True)
    money_entry(ig, receipt_var, 1, "TOTAL RECEIPT",  editable=False)
    money_entry(ig, balance_var, 2, "BALANCE AMOUNT", editable=False)
    entries['amount'] = amount_var

    # NEXT DUE DATE — highlighted
    tk.Label(ig, text="NEXT DUE DATE", font=(FONT_UI, 10, "bold"), fg=ACCENT_PUR,
             bg=BG_CARD, width=16, anchor="w").grid(row=3, column=0, sticky="w", pady=6, padx=4)
    e_due = make_entry(ig, width=20)
    e_due.insert(0, d.get('next_due_date', ''))
    e_due.grid(row=3, column=1, sticky="ew", ipady=7, pady=6, padx=(0, 8))
    entries['next_due_date'] = e_due

    # Photo placeholder — right side of item card
    photo_frame = tk.Frame(item_inner, bg=BG_CARD,
                           highlightbackground=BORDER, highlightthickness=1,
                           width=160, height=160)
    photo_frame.grid(row=0, column=1, sticky="n", pady=(0, 4))
    photo_frame.grid_propagate(False)
    ph_canvas = tk.Canvas(photo_frame, bg=BG_INPUT, highlightthickness=0)
    ph_canvas.pack(fill=tk.BOTH, expand=True)

    def draw_x(e=None):
        ph_canvas.delete("all")
        w = ph_canvas.winfo_width() or 158
        h = ph_canvas.winfo_height() or 158
        ph_canvas.create_rectangle(2, 2, w-2, h-2, outline=BORDER)
        ph_canvas.create_line(2, 2, w-2, h-2, fill=BORDER)
        ph_canvas.create_line(w-2, 2, 2, h-2, fill=BORDER)
        ph_canvas.create_text(w//2, h//2, text="No Photo",
                              fill=TEXT_DIM, font=(FONT_UI, 10))
    ph_canvas.bind("<Configure>", draw_x)
    ph_canvas.after(150, draw_x)

    # ── PAYMENT TABLE ─────────────────────────────────────────────────────
    tbl_card = tk.Frame(right_col, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=16, pady=12)
    tbl_card.grid(row=1, column=0, sticky="nsew")
    # section_header uses pack — keep it in tbl_card via pack
    section_header(tbl_card, "SALE / RECEIPT ENTRIES", ACCENT2)

    # All grid children go inside tbl_inner (avoids pack/grid conflict)
    tbl_inner = tk.Frame(tbl_card, bg=BG_CARD)
    tbl_inner.pack(fill=tk.BOTH, expand=True)
    tbl_inner.grid_rowconfigure(0, weight=1)
    tbl_inner.grid_columnconfigure(0, weight=1)

    tbl_cols   = ("description", "date", "sale_amt", "receipt")
    tbl_heads  = ("SALE / RECEIPT DESCRIPTION", "DATE", "SALE AMOUNT", "RECEIPT")

    tbl_wrap = tk.Frame(tbl_inner, bg=BORDER, bd=1)
    tbl_wrap.grid(row=0, column=0, sticky="nsew")
    tbl_wrap.grid_rowconfigure(0, weight=1)
    tbl_wrap.grid_columnconfigure(0, weight=1)

    sale_tree = ttk.Treeview(tbl_wrap, columns=tbl_cols, show="headings",
                              style="T.Treeview")
    # Column widths proportional to ~1340px available (70% of 1920 minus padding)
    col_weights = {"description": 5, "date": 2, "sale_amt": 2, "receipt": 2}
    for col, head in zip(tbl_cols, tbl_heads):
        sale_tree.heading(col, text=head)
        sale_tree.column(col,
                         anchor="w" if col == "description" else "center",
                         stretch=True, minwidth=80)
    sale_tree.tag_configure("even", background=BG_CARD)
    sale_tree.tag_configure("odd",  background=BG_ROW_ALT)

    # Pre-fill rows from existing data or auto-create first entry for new case
    import datetime as _dt
    if editing:
        existing_rows = d.get('payment_rows', [("", "", "", "")])
    else:
        today_str = _dt.date.today().strftime("%d/%m/%Y")
        existing_rows = [("Total Amount", today_str, amount_var.get() or "", "")]
    for i, row in enumerate(existing_rows):
        sale_tree.insert("", "end", values=row,
                         tags=("even" if i % 2 == 0 else "odd",))

    vsb2 = tk.Scrollbar(tbl_wrap, orient="vertical", command=sale_tree.yview)
    sale_tree.configure(yscrollcommand=vsb2.set)
    vsb2.grid(row=0, column=1, sticky="ns")
    sale_tree.grid(row=0, column=0, sticky="nsew")

    # Totals footer
    footer = tk.Frame(tbl_inner, bg=BG_CARD)
    footer.grid(row=1, column=0, sticky="ew", pady=(4, 0))
    footer.grid_columnconfigure(0, weight=5)
    footer.grid_columnconfigure(1, weight=2)
    footer.grid_columnconfigure(2, weight=2)
    footer.grid_columnconfigure(3, weight=2)

    tk.Label(footer, text="TOTAL", font=(FONT_UI, 9, "bold"),
             fg=TEXT_DIM, bg=BG_CARD, anchor="e").grid(row=0, column=1, sticky="e", padx=4)
    sale_total_lbl = tk.Label(footer, text="0.00",
                               font=(FONT_MONO, 11, "bold"), fg=ACCENT2,
                               bg=BG_CARD, anchor="center")
    sale_total_lbl.grid(row=0, column=2, sticky="ew", padx=4)
    receipt_total_lbl = tk.Label(footer, text="0.00",
                                  font=(FONT_MONO, 11, "bold"), fg=ACCENT_RED,
                                  bg=BG_CARD, anchor="center")
    receipt_total_lbl.grid(row=0, column=3, sticky="ew", padx=4)

    
    
    
    # ── Inline cell editing ───────────────────────────────────────────────
    
    _edit = [None]
    def update_totals():
        sale_total = 0
        receipt_total = 0

        for item in sale_tree.get_children():
            vals = sale_tree.item(item, "values")

            try:
                sale_total += float(vals[2] or 0)
            except:
                pass

            try:
                receipt_total += float(vals[3] or 0)
            except:
                pass

        sale_total_lbl.config(text=f"{sale_total:.2f}")
        receipt_total_lbl.config(text=f"{receipt_total:.2f}")
    
    def add_row(event=None):
        i = len(sale_tree.get_children())
        sale_tree.insert("", "end", values=("", "", "", ""),
                        tags=("even" if i % 2 == 0 else "odd",))

    win.bind("<Insert>", add_row)

    def delete_row(event=None):
        sel = sale_tree.selection()
        if sel:
            if not admin_confirm(win, "delete this payment row"):
                return
            sale_tree.delete(sel[0])
            update_totals()

    win.bind("<Delete>", delete_row)

    def on_double_click(event):
        item = sale_tree.identify_row(event.y)
        col  = sale_tree.identify_column(event.x)

        if not item:
            return

        col_index = int(col.replace("#", "")) - 1

        if _edit[0]:
            _edit[0].destroy()

        bbox = sale_tree.bbox(item, col)
        if not bbox:
            return

        x, y, width, height = bbox
        value = sale_tree.item(item, "values")[col_index]

        entry = tk.Entry(sale_tree, font=(FONT_UI, 10),
                        justify="center" if col_index != 0 else "left")
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        _edit[0] = entry

        def save_edit(e=None):
            values = list(sale_tree.item(item, "values"))
            values[col_index] = entry.get()
            sale_tree.item(item, values=values)
            entry.destroy()
            _edit[0] = None
            update_totals()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    sale_tree.bind("<Double-1>", on_double_click)



    def on_dbl(event):
        row = sale_tree.identify_row(event.y)
        col = sale_tree.identify_column(event.x)
        if not row: return
        if _edit[0]:
            _edit[0].destroy(); _edit[0] = None
        bbox = sale_tree.bbox(row, col)
        if not bbox: return
        bx, by, bw, bh = bbox
        ci = int(col.replace("#", "")) - 1
        cur = sale_tree.item(row, "values")[ci]
        ent = tk.Entry(sale_tree, font=(FONT_UI, 10), fg=TEXT, bg=BG_INPUT,
                       insertbackground=ACCENT, relief="flat",
                       highlightthickness=1, highlightcolor=ACCENT,
                       highlightbackground=ACCENT)
        ent.place(x=bx, y=by, width=bw, height=bh)
        ent.insert(0, cur)
        ent.select_range(0, tk.END)
        ent.focus_set()
        _edit[0] = ent

        def commit(e=None):
            vals = list(sale_tree.item(row, "values"))
            vals[ci] = ent.get()
            sale_tree.item(row, values=vals)
            ent.destroy(); _edit[0] = None
            recalc_totals()

        ent.bind("<Return>",   commit)
        ent.bind("<Tab>",      commit)
        ent.bind("<Escape>",   lambda e: (ent.destroy(), _edit.__setitem__(0, None)))
        ent.bind("<FocusOut>", commit)

    sale_tree.bind("<Double-1>", on_dbl)

    def recalc_totals():
        sale_tot = 0.0
        rec_tot  = 0.0
        for item in sale_tree.get_children():
            vals = sale_tree.item(item, "values")
            try: sale_tot += float(str(vals[2]).replace(',', '') or 0)
            except: pass
            try: rec_tot  += float(str(vals[3]).replace(',', '') or 0)
            except: pass
        sale_total_lbl.config(text=f"{sale_tot:,.2f}")
        receipt_total_lbl.config(text=f"{rec_tot:,.2f}")
        receipt_var.set(f"{rec_tot:.2f}")
        try:
            amt = float(str(amount_var.get()).replace(',', '') or 0)
            balance_var.set(f"{amt - rec_tot:.2f}")
        except:
            balance_var.set("0.00")

    def _on_amount_change(*_):
        recalc_totals()
        # For new cases, keep the first row's sale amount in sync with AMOUNT field
        if not editing:
            children = sale_tree.get_children()
            if children:
                first = children[0]
                vals = list(sale_tree.item(first, "values"))
                vals[2] = amount_var.get() or ""
                sale_tree.item(first, values=vals)
                recalc_totals()

    amount_var.trace_add("write", _on_amount_change)

    def add_row(e=None):
        n = len(sale_tree.get_children())
        sale_tree.insert("", "end", values=("", "", "", ""),
                         tags=("even" if n % 2 == 0 else "odd",))

    def del_row(e=None):
        sel = sale_tree.selection()
        if sel:
            if not admin_confirm(win, "delete this payment row"):
                return
            sale_tree.delete(sel[0])
            recalc_totals()

    btn_row = tk.Frame(tbl_inner, bg=BG_CARD)
    btn_row.grid(row=2, column=0, sticky="ew", pady=(4, 0))
    tk.Button(btn_row, text="＋  Add Row  INS", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT_PUR, relief="flat", bd=0, padx=12, pady=5,
              cursor="hand2", command=add_row).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_row, text="−  Delete Row  DEL", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT_YEL, relief="flat", bd=0, padx=12, pady=5,
              cursor="hand2", command=del_row).pack(side=tk.LEFT)

    win.bind("<Insert>", add_row)
    win.bind("<Delete>", del_row)

    # initial totals
    recalc_totals()

    # ── Action bar ────────────────────────────────────────────────────────
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

        rows = [sale_tree.item(i, "values") for i in sale_tree.get_children()]

        record = {
            'id':             next_id if editing else None,
            'file_no':        file_no,
            'date':           get('date'),
            'customer':       get('customer'),
            'relation':       get('relation'),
            'address':        get('address'),
            'village':        get('village'),
            'mobile_no':      get('mobile_no'),
            'remarks':        get('remarks'),
            'amount':         get('amount'),
            'finance_amt':    get('amount'),
            'total_receipt':  receipt_var.get(),
            'balance':        balance_var.get(),
            'next_due_date':  get('next_due_date'),
            'g1_name':        get('g1_name'),
            'g1_relation':    get('g1_relation'),
            'g1_address':     get('g1_address'),
            'g1_village':     get('g1_village'),
            'g1_mobile':      get('g1_mobile'),
            'g1_remarks':     get('g1_remarks'),
            'payment_rows':   rows,
        }

        saved_id = db.save_credit_case(record)
        record['id'] = saved_id
        _reload_all()

        if on_save_callback:
            on_save_callback(record)

        messagebox.showinfo("Saved ✓",
                            f"Case '{file_no}' saved!\nCase ID: {next_id}",
                            parent=win)
        win.destroy()

    tk.Button(action_bar, text="✕  CANCEL  ESC",
              command=win.destroy,
              font=(FONT_UI, 11, "bold"), fg=ACCENT_RED, bg=BG_CARD,
              activeforeground=ACCENT_RED, activebackground=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
              highlightthickness=1, highlightbackground=ACCENT_RED
              ).pack(side=tk.LEFT, padx=(0, 16))

    tk.Button(action_bar, text="💾  SAVE & EXIT  F10",
              command=save_and_exit,
              font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT2,
              activeforeground=BG, activebackground="#2ebd68",
              relief="flat", bd=0, cursor="hand2", padx=24, pady=10,
              ).pack(side=tk.LEFT)

    win.bind("<F10>",    save_and_exit)
    win.bind("<Escape>", lambda e: win.destroy())


# ═════════════════════════════════════════════════════════════════════════════
# MODULE WRAPPERS
# ═════════════════════════════════════════════════════════════════════════════
def credit_cases_window(parent):
    win = tk.Toplevel(parent)
    win.title("Credit Cases — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    titlebar = tk.Frame(win, bg=BG_PANEL)
    titlebar.pack(fill=tk.X)
    tk.Frame(titlebar, bg=ACCENT_RED, width=4).pack(side=tk.LEFT, fill=tk.Y)
    ti = tk.Frame(titlebar, bg=BG_PANEL, padx=18, pady=12)
    ti.pack(side=tk.LEFT)
    tk.Label(ti, text="CREDIT CASES", font=(FONT_UI, 15, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(ti, text="Credit Case Management",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    make_shortcut_bar(win, [
        ("F1",  "NEW CASE",          ACCENT2),
        ("F2",  "OPEN CASE DETAILS", ACCENT_PUR),
        ("ESC", "CLOSE",             ACCENT_RED),
        ("F8",  "DELETE CASE",       ACCENT_YEL),
        ("F9",  "SEARCH",            "#36bfd9"),
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

    rec_badge = tk.Label(sf, text=f"  {len(CREDIT_CASES)} records  ",
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

    def _credit_row(r):
        row = []
        for c in INST_COLS:
            if c == 'customer_display':
                row.append(fmt_customer(r.get('customer', ''), r.get('relation', '')))
            else:
                row.append(r.get(c, ''))
        return tuple(row)

    all_data = [_credit_row(r) for r in CREDIT_CASES]

    def populate(rows):
        for item in tree.get_children(): tree.delete(item)
        for i, vals in enumerate(rows):
            tree.insert("", tk.END, values=vals,
                        tags=("even" if i % 2 == 0 else "odd",))
        rec_badge.config(text=f"  {len(rows)} records  ")

    populate(all_data)
    attach_selection_bar(tree, to, color=ACCENT_RED)

    tree.grid(row=0, column=0, sticky="nsew")
    tb.grid_rowconfigure(0, weight=1)
    tb.grid_columnconfigure(0, weight=1)

    # Status bar
    try:
        tf_ = sum(float(str(r.get('finance_amt', 0)).replace(',', '') or 0) for r in CREDIT_CASES)
        tb_ = sum(float(str(r.get('balance', 0)).replace(',', '') or 0)     for r in CREDIT_CASES)
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

    pending_lbl = tk.Label(sbar, text=f"NO OF PENDING CASES  {len(CREDIT_CASES)}",
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
        _reload_all()
        all_data.clear()
        all_data.extend(_credit_row(r) for r in CREDIT_CASES)
        do_search()
        pending_lbl.config(text=f"NO OF PENDING CASES  {len(CREDIT_CASES)}")

    def new_case(e=None):
        new_credit_case_form(win, on_save_callback=lambda _: win.after(100, refresh))

    def delete_case():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("F8", "Select a case to delete.", parent=win); return
        vals = tree.item(sel[0], "values")
        if not admin_confirm(win, "delete this credit case"):
            return
        if messagebox.askyesno("Delete", f"Delete case {vals[0]} — {vals[2]}?", parent=win):
            cid = str(vals[-1])
            db.delete_credit_case(int(cid))
            _reload_all()
            refresh()

    def do_search(*_):
        q = sv.get().lower().strip()
        if q == PH.lower():
            q = ""
        populate([r for r in all_data if not q or any(q in str(v).lower() for v in r)])

    sv.trace_add("write", do_search)

    def open_selected_case(e=None):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first", parent=win)
            return
        vals = tree.item(sel[0], "values")
        for r in CREDIT_CASES:
            if str(r.get("id")) == str(vals[-1]):
                new_credit_case_form(win, data=r, on_save_callback=lambda _: win.after(100, refresh))
                break

    win.bind("<F1>",     lambda e: new_case())
    win.bind("<F2>",     lambda e: open_selected_case())
    win.bind("<F8>",     lambda e: delete_case())
    win.bind("<F9>",     lambda e: se.focus_set())
    win.bind("<Escape>", lambda e: win.destroy())
    tree.bind("<Double-1>", lambda e: open_selected_case())


def due_report_window(parent):
    """Due Report — Credit cases that still have a balance outstanding."""
    win = tk.Toplevel(parent)
    win.title("Due Report — Credit Cases — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    tk.Frame(win, bg=ACCENT_YEL, width=4).pack(side=tk.LEFT, fill=tk.Y)
    right = tk.Frame(win, bg=BG)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    topbar = tk.Frame(right, bg=BG_PANEL, pady=14, padx=20)
    topbar.pack(fill=tk.X)
    tk.Label(topbar, text="DUE REPORT — CREDIT CASES",
             font=(FONT_UI, 16, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Label(topbar, text="  Credit cases with outstanding balance",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 9),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)

    make_shortcut_bar(right, [
        ("ESC", "CLOSE",       ACCENT_RED),
        ("F2",  "OPEN CASE",   ACCENT),
        ("F9",  "SEARCH",      "#36bfd9"),
        ("F5",  "REFRESH",     ACCENT_YEL),
    ])
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    sf = tk.Frame(right, bg=BG, padx=16, pady=8)
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
    se.bind("<FocusIn>",  lambda e: (se.delete(0, tk.END), se.config(fg=TEXT)) if se.get() == PH else None)
    se.bind("<FocusOut>", lambda e: (se.insert(0, PH), se.config(fg=TEXT_DIM)) if not se.get() else None)

    rec_badge = tk.Label(sf, text="  0 records  ", font=(FONT_UI, 9, "bold"),
                         fg=ACCENT, bg="#1b2e4a", padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    COLS   = ['file_no', 'date', 'customer_display', 'village', 'mobile_no', 'finance_amt', 'balance', 'next_due_date', 'id']
    HEADS  = ['File No', 'Date', 'Customer (Father)', 'Village', 'Mobile No', 'Finance Amt', 'Balance', '⚠ Next Due Date', 'ID']
    WIDTHS = [75, 95, 210, 130, 145, 110, 100, 120, 55]

    tf4 = tk.Frame(right, bg=BG, padx=20)
    tf4.pack(fill=tk.BOTH, expand=True)
    border2 = tk.Frame(tf4, bg=BORDER)
    border2.pack(fill=tk.BOTH, expand=True, pady=8)
    border2.grid_rowconfigure(0, weight=1)
    border2.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(border2, columns=COLS, show="headings", style="T.Treeview")
    for col, head, w in zip(COLS, HEADS, WIDTHS):
        tree.heading(col, text=head)
        tree.column(col, width=w, minwidth=40,
                    anchor="center" if col in ('finance_amt','balance') else "w")
    tree.tag_configure("even",    background=BG_CARD)
    tree.tag_configure("odd",     background=BG_ROW_ALT)
    tree.tag_configure("overdue", background="#fff0f0", foreground="#b91c1c")
    tree.grid(row=0, column=0, sticky="nsew")
    attach_selection_bar(tree, tf4, color=ACCENT_YEL)

    all_rows = []

    def load_data():
        all_rows.clear()
        for r in db.get_due_report():
            row = []
            for c in COLS:
                if c == 'customer_display':
                    row.append(fmt_customer(r.get('customer', ''), r.get('relation', '')))
                else:
                    row.append(str(r.get(c, '')))
            all_rows.append(tuple(row))

    def populate(rows):
        for item in tree.get_children(): tree.delete(item)
        for i, vals in enumerate(rows):
            tree.insert("", tk.END, values=vals,
                        tags=("even" if i % 2 == 0 else "odd",))
        rec_badge.config(text=f"  {len(rows)} records  ")

    def do_search(*_):
        q = sv.get().lower().strip()
        if q == PH.lower(): q = ""
        populate([r for r in all_rows if not q or any(q in str(v).lower() for v in r)])

    sv.trace_add("write", do_search)

    def refresh(e=None):
        load_data()
        do_search()
        try:
            tb = sum(float(r[6] or 0) for r in all_rows)
            bal_lbl.config(text=f"₹ {tb:,.2f}")
        except Exception:
            pass

    load_data()
    populate(all_rows)

    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)
    sbar = tk.Frame(right, bg=BG_PANEL, pady=7, padx=16)
    sbar.pack(fill=tk.X)
    tk.Label(sbar, text="Due Report  ·  Credit cases overdue (next due date passed, balance > 0)",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    bf = tk.Frame(sbar, bg=BG_CARD, padx=12, pady=4)
    bf.pack(side=tk.RIGHT, padx=4)
    tk.Label(bf, text="Total Balance Due", font=(FONT_UI, 7, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
    try:
        tb_ = sum(float(r[6] or 0) for r in all_rows)
    except Exception:
        tb_ = 0
    bal_lbl = tk.Label(bf, text=f"₹ {tb_:,.2f}", font=(FONT_MONO, 11, "bold"), fg=ACCENT_RED, bg=BG_CARD)
    bal_lbl.pack(anchor="w")

    # ── Open credit case detail ────────────────────────────────────────────
    def open_case(e=None):
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first.", parent=win)
            return
        vals    = tree.item(sel[0], "values")
        case_id = str(vals[-1])          # last col is id
        _reload_all()
        for cr in CREDIT_CASES:
            if str(cr.get("id")) == case_id:
                new_credit_case_form(win, data=cr,
                                     on_save_callback=lambda _: win.after(100, refresh))
                return
        messagebox.showinfo("Not Found", f"Case ID {case_id} not found.", parent=win)

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<F2>", open_case)
    win.bind("<F5>", refresh)
    win.bind("<F9>", lambda e: se.focus_set())
    tree.bind("<Double-1>", lambda e: open_case())


def due_payments_window(parent):
    """Due Payments — Installment cases with unpaid balance (overdue instalments)."""
    win = tk.Toplevel(parent)
    win.title("Due Payments — Installment Cases — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    tk.Frame(win, bg=ACCENT2, width=4).pack(side=tk.LEFT, fill=tk.Y)
    right = tk.Frame(win, bg=BG)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    topbar = tk.Frame(right, bg=BG_PANEL, pady=14, padx=20)
    topbar.pack(fill=tk.X)
    tk.Label(topbar, text="DUE PAYMENTS — INSTALLMENT CASES",
             font=(FONT_UI, 16, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Label(topbar, text="  Instalments with outstanding dues",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 9),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)

    make_shortcut_bar(right, [
        ("ESC", "CLOSE",       ACCENT_RED),
        ("F2",  "OPEN CASE",   ACCENT),
        ("F3",  "INST. CHART", ACCENT_PUR),
        ("F9",  "SEARCH",      "#36bfd9"),
        ("F5",  "REFRESH",     ACCENT2),
    ])
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    sf = tk.Frame(right, bg=BG, padx=16, pady=8)
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
    se.bind("<FocusIn>",  lambda e: (se.delete(0, tk.END), se.config(fg=TEXT)) if se.get() == PH else None)
    se.bind("<FocusOut>", lambda e: (se.insert(0, PH), se.config(fg=TEXT_DIM)) if not se.get() else None)

    rec_badge = tk.Label(sf, text="  0 records  ", font=(FONT_UI, 9, "bold"),
                         fg=ACCENT2, bg="#1b2e4a", padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    COLS   = ['file_no', 'date', 'customer_display', 'village', 'mobile_no', 'instalment_amt', 'missed_instalments', 'total_overdue', 'balance', 'id']
    HEADS  = ['File No', 'Date', 'Customer (Father)', 'Village', 'Mobile No', 'Inst. Amt', 'Missed', 'Total Overdue', 'Total Balance', 'ID']
    WIDTHS = [70, 90, 210, 120, 140, 100, 65, 110, 110, 50]

    tf4 = tk.Frame(right, bg=BG, padx=20)
    tf4.pack(fill=tk.BOTH, expand=True)
    border2 = tk.Frame(tf4, bg=BORDER)
    border2.pack(fill=tk.BOTH, expand=True, pady=8)
    border2.grid_rowconfigure(0, weight=1)
    border2.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(border2, columns=COLS, show="headings", style="T.Treeview")
    for col, head, w in zip(COLS, HEADS, WIDTHS):
        tree.heading(col, text=head)
        tree.column(col, width=w, minwidth=40,
                    anchor="center" if col in ('missed_instalments','total_overdue','instalment_amt','balance') else "w")
    tree.tag_configure("even", background=BG_CARD)
    tree.tag_configure("odd",  background=BG_ROW_ALT)
    tree.grid(row=0, column=0, sticky="nsew")
    attach_selection_bar(tree, tf4, color=ACCENT2)

    all_rows = []

    def load_data():
        all_rows.clear()
        for r in db.get_due_payments():
            row = []
            for c in COLS:
                if c == 'customer_display':
                    row.append(fmt_customer(r.get('customer', ''), r.get('relation', '')))
                else:
                    row.append(str(r.get(c, '')))
            all_rows.append(tuple(row))

    def populate(rows):
        for item in tree.get_children(): tree.delete(item)
        for i, vals in enumerate(rows):
            tree.insert("", tk.END, values=vals,
                        tags=("even" if i % 2 == 0 else "odd",))
        rec_badge.config(text=f"  {len(rows)} records  ")

    def do_search(*_):
        q = sv.get().lower().strip()
        if q == PH.lower(): q = ""
        populate([r for r in all_rows if not q or any(q in str(v).lower() for v in r)])

    sv.trace_add("write", do_search)

    def refresh(e=None):
        load_data()
        do_search()
        try:
            tb = sum(float(r[7] or 0) for r in all_rows)
            bal_lbl.config(text=f"₹ {tb:,.2f}")
        except Exception:
            pass

    load_data()
    populate(all_rows)

    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)
    sbar = tk.Frame(right, bg=BG_PANEL, pady=7, padx=16)
    sbar.pack(fill=tk.X)
    tk.Label(sbar, text="Due Payments  ·  Instalment cases with overdue / unpaid instalments",
             font=(FONT_UI, 9), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    bf = tk.Frame(sbar, bg=BG_CARD, padx=12, pady=4)
    bf.pack(side=tk.RIGHT, padx=4)
    tk.Label(bf, text="Total Overdue Amount", font=(FONT_UI, 7, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
    try:
        tb_ = sum(float(r[7] or 0) for r in all_rows)
    except Exception:
        tb_ = 0
    bal_lbl = tk.Label(bf, text=f"₹ {tb_:,.2f}", font=(FONT_MONO, 11, "bold"), fg=ACCENT2, bg=BG_CARD)
    bal_lbl.pack(anchor="w")

    # ── Open Case Detail (F2 / double-click) ──────────────────────────────
    def _get_case_record():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a case first.", parent=win)
            return None
        vals  = tree.item(sel[0], "values")
        case_id = str(vals[-1])
        _reload_all()
        for r in INSTALLMENT_CASES:
            if str(r.get("id")) == case_id:
                return r
        messagebox.showinfo("Not Found", f"Case ID {case_id} not found.", parent=win)
        return None

    def open_case(e=None):
        r = _get_case_record()
        if r:
            open_installment_case_detail(r, lambda: refresh())

    def open_chart(e=None):
        r = _get_case_record()
        if r:
            open_installment_chart_window(r, win)

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<F2>", open_case)
    win.bind("<F3>", open_chart)
    win.bind("<F5>", refresh)
    win.bind("<F9>", lambda e: se.focus_set())
    tree.bind("<Double-1>", lambda e: open_case())


def village_setup_window(parent):
    """Village directory with add/delete, backed by SQLite."""
    win = tk.Toplevel(parent)
    win.title("Village Setup — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    tk.Frame(win, bg=ACCENT_PUR, width=4).pack(side=tk.LEFT, fill=tk.Y)
    right = tk.Frame(win, bg=BG)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    topbar = tk.Frame(right, bg=BG_PANEL, pady=14, padx=20)
    topbar.pack(fill=tk.X)
    tk.Label(topbar, text="VILLAGE SETUP",
             font=(FONT_UI, 16, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 9),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    add_bar = tk.Frame(right, bg=BG, padx=20, pady=10)
    add_bar.pack(fill=tk.X)
    tk.Label(add_bar, text="Village Name:", font=(FONT_UI, 10), fg=TEXT_DIM,
             bg=BG).pack(side=tk.LEFT)
    ne = make_entry(add_bar, width=28)
    ne.pack(side=tk.LEFT, ipady=7, padx=(8, 12))

    def add_village(e=None):
        name = ne.get().strip()
        if not name:
            return
        db.save_village(name)
        ne.delete(0, tk.END)
        refresh()

    ne.bind("<Return>", add_village)
    tk.Button(add_bar, text="＋ Add Village", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT_PUR, relief="flat", bd=0, padx=14, pady=7,
              cursor="hand2", command=add_village).pack(side=tk.LEFT)

    tf4 = tk.Frame(right, bg=BG, padx=20)
    tf4.pack(fill=tk.BOTH, expand=True)
    border2 = tk.Frame(tf4, bg=BORDER)
    border2.pack(fill=tk.BOTH, expand=True, pady=8)
    border2.grid_rowconfigure(0, weight=1)
    border2.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(border2, columns=('name',), show="headings", style="T.Treeview")
    tree.heading('name', text='Village Name')
    tree.column('name', width=400, anchor="w")
    tree.tag_configure("even", background=BG_CARD)
    tree.tag_configure("odd",  background=BG_ROW_ALT)
    tree.grid(row=0, column=0, sticky="nsew")

    def refresh():
        for item in tree.get_children(): tree.delete(item)
        for i, v in enumerate(db.get_villages()):
            tree.insert("", tk.END, values=(v,),
                        tags=("even" if i % 2 == 0 else "odd",))

    refresh()

    def delete_village(e=None):
        sel = tree.selection()
        if not sel: return
        name = tree.item(sel[0], "values")[0]
        if not admin_confirm(win, f"delete village '{name}'"):
            return
        if messagebox.askyesno("Delete", f"Delete village '{name}'?", parent=win):
            db.delete_village(name)
            refresh()

    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)
    sbar = tk.Frame(right, bg=BG_PANEL, pady=7, padx=16)
    sbar.pack(fill=tk.X)
    tk.Button(sbar, text="🗑  Delete Selected  Del", font=(FONT_UI, 9, "bold"),
              fg=BG, bg=ACCENT_RED, relief="flat", bd=0, padx=12, pady=5,
              cursor="hand2", command=delete_village).pack(side=tk.LEFT)

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<Delete>", delete_village)


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
