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

from datetime import datetime

# Accepts any common date format — no more ValueError crashes
_DATE_FORMATS = [
    "%d/%m/%Y",   # DD/MM/YYYY  ← primary UI input format
    "%Y-%m-%d",   # YYYY-MM-DD  ← MySQL native / already-converted
    "%Y/%m/%d",   # YYYY/MM/DD
    "%d-%m-%Y",   # DD-MM-YYYY
    "%m/%d/%Y",   # MM/DD/YYYY
]

def _parse_date(d):
    if not d or str(d).strip() == "":
        return None
    s = str(d).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

# any format → YYYY-MM-DD for MySQL
def to_mysql_date(d):
    dt = _parse_date(d)
    return dt.strftime("%Y-%m-%d") if dt else None

# any format → DD/MM/YYYY for display
def to_display_date(d):
    dt = _parse_date(d)
    return dt.strftime("%d/%m/%Y") if dt else ""



# ── Admin password ────────────────────────────────────────────────────────────
ADMIN_PASSWORD = "9241"   # ← change this to your preferred password

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
             font=(FONT_UI, 15, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(body, text=f"Enter admin password to {action}.",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w", pady=(2, 12))

    pw_var = tk.StringVar()
    pw_entry = tk.Entry(body, textvariable=pw_var, show="●",
                        font=(FONT_UI, 14), fg=TEXT, bg=BG_INPUT,
                        insertbackground=ACCENT, relief="flat",
                        highlightthickness=1, highlightcolor=ACCENT,
                        highlightbackground=BORDER)
    pw_entry.pack(fill=tk.X, ipady=7)
    pw_entry.focus_set()

    result = [False]
    err_lbl = tk.Label(body, text="", font=(FONT_UI, 12), fg=ACCENT_RED, bg=BG_PANEL)
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
              font=(FONT_UI, 13, "bold"), fg=BG, bg=ACCENT_RED,
              relief="flat", bd=0, padx=16, pady=6, cursor="hand2").pack(side=tk.LEFT)
    tk.Button(btn_row, text="Cancel", command=dlg.destroy,
              font=(FONT_UI, 13), fg=TEXT_DIM, bg=BG_PANEL,
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
                fieldbackground=BG_CARD, rowheight=40,
                font=(FONT_UI, 13), borderwidth=0, relief="flat")
    s.configure("T.Treeview.Heading",
                background=BG_PANEL, foreground=ACCENT,
                font=(FONT_UI, 12, "bold"), borderwidth=0,
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


def make_entry(parent, **kw):
    return tk.Entry(parent, font=(FONT_UI, 13), fg=TEXT, bg=BG_INPUT,
                    insertbackground=ACCENT, relief="flat",
                    highlightthickness=1, highlightcolor=ACCENT,
                    highlightbackground=BORDER, **kw)


def section_header(parent, text, color=ACCENT):
    f = tk.Frame(parent, bg=BG_CARD)
    f.pack(fill=tk.X, pady=(12, 10))
    tk.Frame(f, bg=color, width=3).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
    tk.Label(f, text=text, font=(FONT_UI, 13, "bold"),
             fg=color, bg=BG_CARD).pack(side=tk.LEFT)
    tk.Frame(f, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X,
                                           expand=True, padx=(12, 0))


def make_shortcut_bar(parent, shortcuts):
    bar = tk.Frame(parent, bg=BG_PANEL, pady=6, padx=12)
    bar.pack(fill=tk.X)
    for key, desc, color in shortcuts:
        chip = tk.Frame(bar, bg=BG_PANEL)
        chip.pack(side=tk.LEFT, padx=4)
        tk.Label(chip, text=key, font=(FONT_UI, 11, "bold"),
                 fg=BG, bg=color, padx=6, pady=3).pack(side=tk.LEFT)
        tk.Label(chip, text=f" {desc}", font=(FONT_UI, 11),
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
             font=(FONT_UI, 18, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(tb_inner, text="Complete all sections · Press F10 to save",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    # Case ID (top right)
    badge_f = tk.Frame(topbar, bg=BG_PANEL, padx=20)
    badge_f.pack(side=tk.RIGHT)
    tk.Label(badge_f, text="CASE ID", font=(FONT_UI, 11),
             fg=TEXT_DIM, bg=BG_PANEL).pack()
    tk.Label(badge_f, text=str(next_id),
             font=(FONT_MONO, 25, "bold"), fg=ACCENT, bg=BG_PANEL).pack()

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
    body.pack(fill=tk.BOTH, expand=True)
    body_id = canvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>",
              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    def resize_body(event):
        canvas.itemconfig(body_id, width=event.width)

    canvas.bind("<Configure>", resize_body)
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    entries = {}

    # ══════════════════════════════════════════════════════════════════════
    # TOP ROW: 2 columns — Customer LEFT | Item Particulars + Photo RIGHT
    # ══════════════════════════════════════════════════════════════════════
    top_row = tk.Frame(body, bg=BG)
    top_row.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
    top_row.grid_columnconfigure(0, weight=5)   # customer — good width
    top_row.grid_columnconfigure(1, weight=7)   # item + photo — wider

    # ── CUSTOMER DETAILS ──────────────────────────────────────────────────
    cust_card = tk.Frame(top_row, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=16, pady=12)
    cust_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    section_header(cust_card, "CUSTOMER DETAILS", ACCENT)

    cg = tk.Frame(cust_card, bg=BG_CARD)
    cg.pack(fill=tk.X)
    cg.grid_columnconfigure(0, weight=0)
    cg.grid_columnconfigure(1, weight=1)
    cg.grid_columnconfigure(2, weight=0)
    cg.grid_columnconfigure(3, weight=1)

    # FILE NO + DATE on same row
    tk.Label(cg, text="FILE NO", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, width=12, anchor="w").grid(row=0, column=0, sticky="w", pady=5, padx=4)
    e_fn = make_entry(cg, width=10)
    e_fn.grid(row=0, column=1, sticky="ew", ipady=7, pady=5, padx=(0, 14))
    entries['file_no'] = e_fn

    tk.Label(cg, text="DATE", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=2, sticky="w", pady=5, padx=4)
    e_dt = make_entry(cg, width=13)
    e_dt.insert(0, datetime.today().strftime("%d/%m/%Y"))
    e_dt.config(fg=TEXT_DIM)
    e_dt.grid(row=0, column=3, sticky="ew", ipady=7, pady=5)
    entries['date'] = e_dt
    e_dt.bind("<FocusIn>",
              lambda e: (e_dt.delete(0, tk.END), e_dt.config(fg=TEXT))
                        if e_dt.get() == "DD/MM/YYYY" else None)
    e_dt.bind("<FocusOut>",
              lambda e: (e_dt.insert(0, datetime.today().strftime("%d/%m/%Y")), e_dt.config(fg=TEXT_DIM))
                        if not e_dt.get() else None)

    for i, (lbl, key) in enumerate([
        ("ACCOUNT",     "account"),
        ("W/O D/O S/O", "relation"),
        ("ADDRESS",     "address1"),
        ("",            "address2"),
        ("MOBILE NO",   "mobile_no"),
        ("REMARKS",     "remarks_cust"),
    ], start=1):
        tk.Label(cg, text=lbl, font=(FONT_UI, 13), fg=TEXT_DIM,
                 bg=BG_CARD, width=12, anchor="w").grid(
                 row=i, column=0, sticky="w", pady=4, padx=4)
        e = make_entry(cg, width=28)
        e.grid(row=i, column=1, columnspan=3, sticky="ew",
               ipady=7, pady=4, padx=(0, 4))
        entries[key] = e

    # VILLAGE combobox
    tk.Label(cg, text="VILLAGE", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, width=12, anchor="w").grid(row=7, column=0, sticky="w", pady=4, padx=4)
    village_var = tk.StringVar()
    entries['village'] = village_var
    village_vals = db.get_villages()
    village_cb = ttk.Combobox(cg, textvariable=village_var, values=village_vals,
                               style="Dark.TCombobox", font=(FONT_UI, 13), width=24)
    village_cb.grid(row=7, column=1, columnspan=3, sticky="ew",
                    ipady=5, pady=4, padx=(0, 4))

    # ── ITEM PARTICULARS + PHOTO (right column) ───────────────────────────
    item_card = tk.Frame(top_row, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=16, pady=12)
    item_card.grid(row=0, column=1, sticky="nsew")
    section_header(item_card, "ITEM PARTICULARS", ACCENT_PUR)

    # item_card splits into fields (left) and photo (right)
    item_inner = tk.Frame(item_card, bg=BG_CARD)
    item_inner.pack(fill=tk.X)
    item_inner.grid_columnconfigure(0, weight=1)
    item_inner.grid_columnconfigure(1, weight=0)

    ig = tk.Frame(item_inner, bg=BG_CARD)
    ig.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
    ig.grid_columnconfigure(0, weight=0)
    ig.grid_columnconfigure(1, weight=1)
    ig.grid_columnconfigure(2, weight=0)
    ig.grid_columnconfigure(3, weight=1)

    # ITEM (full row)
    tk.Label(ig, text="ITEM", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, width=14, anchor="w").grid(
             row=0, column=0, sticky="w", pady=5, padx=4)
    e_item = make_entry(ig, width=38)
    e_item.grid(row=0, column=1, columnspan=3, sticky="ew",
                ipady=7, pady=5, padx=(0, 4))
    entries['item'] = e_item

    # BRAND + MODEL
    tk.Label(ig, text="BRAND", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, width=14, anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=4)
    e_brand = make_entry(ig, width=16)
    e_brand.grid(row=1, column=1, sticky="ew", ipady=7, pady=5, padx=(0, 12))
    entries['brand'] = e_brand

    tk.Label(ig, text="MODEL", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=1, column=2, sticky="w", pady=5, padx=4)
    e_model = make_entry(ig, width=16)
    e_model.grid(row=1, column=3, sticky="ew", ipady=7, pady=5)
    entries['model'] = e_model

    # SRNO
    tk.Label(ig, text="SRNO", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, width=14, anchor="w").grid(
             row=2, column=0, sticky="w", pady=5, padx=4)
    e_srno = make_entry(ig, width=38)
    e_srno.grid(row=2, column=1, columnspan=3, sticky="ew",
                ipady=7, pady=5, padx=(0, 4))
    entries['srno'] = e_srno

    # INVOICE NO
    tk.Label(ig, text="INVOICE NO", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, width=14, anchor="w").grid(
             row=3, column=0, sticky="w", pady=5, padx=4)
    e_inv = make_entry(ig, width=38)
    e_inv.grid(row=3, column=1, columnspan=3, sticky="ew",
               ipady=7, pady=5, padx=(0, 4))
    entries['invoice_no'] = e_inv

    # ── Photo placeholder — inside item card, right side ──────────────────
    photo_col = tk.Frame(item_inner, bg=BG_CARD, width=180)
    photo_col.grid(row=0, column=1, sticky="ns", pady=(0, 0))
    photo_col.grid_propagate(False)

    tk.Label(photo_col, text="PHOTO", font=(FONT_UI, 11, "bold"),
             fg=TEXT_DIM, bg=BG_CARD).pack(pady=(4, 4))

    ph_frame = tk.Frame(photo_col, bg=BG_INPUT,
                        highlightbackground=BORDER, highlightthickness=1,
                        width=168, height=155)
    ph_frame.pack(fill=tk.BOTH, expand=True, padx=6)
    ph_frame.pack_propagate(False)

    ph_canvas = tk.Canvas(ph_frame, bg=BG_INPUT, highlightthickness=0)
    ph_canvas.pack(fill=tk.BOTH, expand=True)

    def draw_x(e=None):
        ph_canvas.delete("all")
        w = ph_canvas.winfo_width() or 162
        h = ph_canvas.winfo_height() or 148
        ph_canvas.create_rectangle(2, 2, w-2, h-2, outline=BORDER, width=1)
        ph_canvas.create_line(2, 2, w-2, h-2, fill=BORDER, width=1)
        ph_canvas.create_line(w-2, 2, 2, h-2, fill=BORDER, width=1)
        ph_canvas.create_text(w//2, h//2, text="No Photo",
                              fill=TEXT_DIM, font=(FONT_UI, 12))

    ph_canvas.bind("<Configure>", draw_x)
    ph_canvas.after(150, draw_x)

    tk.Button(photo_col, text="📷  Upload",
              font=(FONT_UI, 11), fg=TEXT_DIM, bg=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", pady=4,
              command=lambda: messagebox.showinfo(
                  "Photo", "Photo upload feature coming soon.", parent=win)
              ).pack(fill=tk.X, padx=6, pady=(6, 0))

    # ── Financial section separator ───────────────────────────────────────
    tk.Frame(item_card, bg=BORDER, height=1).pack(fill=tk.X, pady=(10, 8))

    fg2 = tk.Frame(item_card, bg=BG_CARD)
    fg2.pack(fill=tk.BOTH,expand=True)
    fg2.grid_columnconfigure(0, weight=1)  # label
    fg2.grid_columnconfigure(1, weight=3)  # input
    fg2.grid_columnconfigure(2, weight=1)  # label
    fg2.grid_columnconfigure(3, weight=3)  # input

    amount_var   = tk.StringVar()
    advance_var  = tk.StringVar()
    amt_fin_var  = tk.StringVar(value="0.00")
    no_inst_var  = tk.StringVar()
    inst_amt_var = tk.StringVar(value="0.00")
    final_var    = tk.StringVar(value="0.00")
    interest_var = tk.StringVar(value="0.00")   # interest value (amount or %)
    interest_mode = tk.StringVar(value="amount") # "amount" or "percent"

    entries.update({
        'amount':          amount_var,
        'advance':         advance_var,
        'amount_financed': amt_fin_var,
        'no_instalments':  no_inst_var,
        'instalment_amt':  inst_amt_var,
        'final_amount':    final_var,
        'interest':        interest_var,
        'interest_mode':   interest_mode,
    })

    def recalculate(*_):
        try:
            amt  = float(amount_var.get()  or 0)
            adv  = float(advance_var.get() or 0)
            n    = float(no_inst_var.get() or 0)
            iraw = float(interest_var.get() or 0)
            fin  = amt - adv
            if interest_mode.get() == "percent":
                interest_amt = fin * iraw / 100.0
            else:
                interest_amt = iraw
            total = fin + interest_amt
            amt_fin_var.set(f"{fin:.2f}")
            if n > 0:
                inst_amt_var.set(f"{total / n:.2f}")
            else:
                inst_amt_var.set("0.00")
            final_var.set(f"{total:.2f}")
        except ValueError:
            pass

    amount_var.trace_add("write",    recalculate)
    advance_var.trace_add("write",   recalculate)
    no_inst_var.trace_add("write",   recalculate)
    interest_var.trace_add("write",  recalculate)
    interest_mode.trace_add("write", recalculate)

    fin_rows = [
        ("AMOUNT",             amount_var,  0, 0, TEXT,       False),
        ("ADVANCE",            advance_var, 0, 2, TEXT,       False),
        ("AMOUNT FINANCED",    amt_fin_var, 1, 0, ACCENT_YEL, True),
        ("NO. OF INSTALMENTS", no_inst_var, 1, 2, TEXT,       False),
        ("INSTALMENT AMOUNT",  inst_amt_var,2, 0, ACCENT2,    True),
        ("FINAL AMOUNT",       final_var,   2, 2, ACCENT_RED, True),
    ]
    for lbl_t, var, r, c, color, ro in fin_rows:
        tk.Label(fg2, text=lbl_t, font=(FONT_UI, 13), fg=TEXT_DIM,
                 bg=BG_CARD, anchor="w").grid(
                 row=r, column=c*2, sticky="w", pady=5, padx=4)
        state = "readonly" if ro else "normal"
        rbg   = BG_CARD if ro else BG_INPUT
        e = tk.Entry(fg2, textvariable=var, state=state,
                     font=(FONT_MONO, 13, "bold"), fg=color, bg=rbg,
                     readonlybackground=rbg,
                     insertbackground=ACCENT, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER)
        e.grid(row=r, column=c*2+1, sticky="ew", ipady=8, pady=5, padx=(0, 8))

    # ── Interest row ─────────────────────────────────────────────────────────
    tk.Label(fg2, text="INTEREST", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD, anchor="w").grid(row=3, column=0, sticky="w", pady=5, padx=4)
    e_int = tk.Entry(fg2, textvariable=interest_var,
                     font=(FONT_MONO, 13, "bold"), fg=ACCENT_PUR, bg=BG_INPUT,
                     insertbackground=ACCENT, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER)
    e_int.grid(row=3, column=1, sticky="ew", ipady=8, pady=5, padx=(0, 8))

    # Toggle button: ₹ Amount  ↔  % Percent
    def _toggle_mode():
        if interest_mode.get() == "amount":
            interest_mode.set("percent")
            mode_btn.config(text="% Percent", fg=BG, bg=ACCENT_PUR)
        else:
            interest_mode.set("amount")
            mode_btn.config(text="₹ Amount", fg=BG, bg=ACCENT)
        recalculate()

    mode_btn = tk.Button(fg2, text="₹ Amount", command=_toggle_mode,
                         font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT,
                         relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
    mode_btn.grid(row=3, column=2, columnspan=2, sticky="w", padx=4, pady=5)

    # ══════════════════════════════════════════════════════════════════════
    # BOTTOM ROW: Two guarantors side-by-side
    # ══════════════════════════════════════════════════════════════════════
    guar_row = tk.Frame(body, bg=BG)
    guar_row.pack(fill=tk.BOTH,expand=True, pady=(8, 0))
    guar_row.grid_columnconfigure(0, weight=1)
    guar_row.grid_columnconfigure(1, weight=1)

    def build_guarantor(parent_frame, prefix, title, color, col):
        card = tk.Frame(parent_frame, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=16, pady=12)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0, 10) if col == 0 else 0)
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
            tk.Label(gg, text=lbl, font=(FONT_UI, 13), fg=TEXT_DIM,
                     bg=BG_CARD, width=13, anchor="w").grid(
                     row=i, column=0, sticky="w", pady=4, padx=4)
            e = make_entry(gg, width=30)
            e.grid(row=i, column=1, sticky="ew", ipady=7, pady=4, padx=(0, 4))
            entries[key] = e

    build_guarantor(guar_row, "g1", "FIRST GUARANTOR PARTICULARS",  ACCENT,     0)
    build_guarantor(guar_row, "g2", "SECOND GUARANTOR PARTICULARS", ACCENT_PUR, 1)

    # ══════════════════════════════════════════════════════════════════════
    # BOTTOM ACTION BAR (pinned)
    # ══════════════════════════════════════════════════════════════════════
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)
    action_bar = tk.Frame(win, bg=BG_PANEL, pady=12, padx=10)
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
            'date':         to_mysql_date(get('date')),
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
            'interest':      get('interest'),
            'interest_mode': get('interest_mode'),
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

    # Save button (rightmost)
    # tk.Button(action_bar, text="💾  SAVE & EXIT  F10",
    #         command=save_and_exit,
    #         font=(FONT_UI, 14, "bold"), fg=BG, bg=ACCENT2,
    #         relief="flat", bd=0, cursor="hand2", padx=24, pady=10
    #         ).pack(side=tk.RIGHT)

    # # Cancel button (left of save)
    # tk.Button(action_bar, text="✕  CANCEL  ESC",
    #         command=win.destroy,
    #         font=(FONT_UI, 14, "bold"), fg=ACCENT_RED, bg=BG_CARD,
    #         relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
    #         highlightthickness=1, highlightbackground=ACCENT_RED
    #         ).pack(side=tk.RIGHT, padx=(0, 16))

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
             font=(FONT_UI, 18, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(tb_inner, text=f"File No: {data.get('file_no', '')}  ·  {fmt_customer(data.get('customer', ''), data.get('relation', ''))}",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    badge_f = tk.Frame(topbar, bg=BG_PANEL, padx=20)
    badge_f.pack(side=tk.RIGHT)
    tk.Label(badge_f, text="CASE ID", font=(FONT_UI, 11),
             fg=TEXT_DIM, bg=BG_PANEL).pack()
    tk.Label(badge_f, text=str(data.get('id', '')),
             font=(FONT_MONO, 25, "bold"), fg=ACCENT, bg=BG_PANEL).pack()

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
        tk.Label(grid, text=label, font=(FONT_UI, 12), fg=TEXT_DIM,
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
        ("DATE",        "date",      to_display_date(data.get("date", ""))),
        ("ACCOUNT",     "customer",  data.get("customer", "")),
        ("W/O D/O S/O", "relation",  data.get("relation", "")),
        ("ADDRESS",     "address",   data.get("address", "")),
        ("MOBILE NO",   "mobile_no", data.get("mobile_no", "")),
        ("REMARKS",     "remarks",   data.get("remarks", "")),
    ]
    for i, (lbl, key, val) in enumerate(cust_fields):
        add_row(cg, lbl, key, i, val)

    # Village combobox
    tk.Label(cg, text="VILLAGE", font=(FONT_UI, 12), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=len(cust_fields), column=0, sticky="w", pady=3, padx=4)
    village_var = tk.StringVar(value=data.get("village", ""))
    entries['village'] = village_var
    village_vals = db.get_villages()
    ttk.Combobox(cg, textvariable=village_var, values=village_vals,
                 style="Dark.TCombobox", font=(FONT_UI, 13), width=20
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
        data["file_no"]        = get("file_no")
        data["date"]           = to_mysql_date(get("date"))
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
              font=(FONT_UI, 14, "bold"), fg=ACCENT_RED, bg=BG_CARD,
              activeforeground=ACCENT_RED, activebackground=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
              highlightthickness=1, highlightbackground=ACCENT_RED
              ).pack(side=tk.LEFT, padx=(0, 16))

    tk.Button(action_bar, text="💾  SAVE & EXIT  F10",
              command=save_changes,
              font=(FONT_UI, 14, "bold"), fg=BG, bg=ACCENT2,
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
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    bal_badge_var = tk.StringVar(value=f"₹ {balance_orig}")
    tk.Label(header, textvariable=bal_badge_var, font=(FONT_MONO, 15, "bold"),
             fg=ACCENT_YEL, bg=BG_PANEL).pack(side="right", padx=20)
    tk.Label(header, text="BALANCE:", font=(FONT_UI, 12), fg=TEXT_DIM,
             bg=BG_PANEL).pack(side="right")

    # Show "Amount to be Paid per Instalment" once in header
    tk.Frame(header, bg=BORDER, width=1).pack(side="right", fill="y", padx=4)
    tk.Label(header, text=f"₹ {inst_amt}", font=(FONT_MONO, 15, "bold"),
             fg=ACCENT2, bg=BG_PANEL).pack(side="right", padx=4)
    tk.Label(header, text="AMT TO BE PAID:", font=(FONT_UI, 12), fg=TEXT_DIM,
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
    col_widths = [55, 150, 150, 160, 150, 150]

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
    tree2.tag_configure("unpaid",  background="#fffbeb", foreground="#b45309")
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
            dt = _parse_date(str(inst_date).strip())
            if dt and dt.date() < _dt_chart.date.today():
                return "overdue" 
        return "unpaid"

    if saved:
        for i, p in enumerate(saved):
            recv      = p.get('recv_date', '')
            inst_date = p.get('inst_date', '')
            tree2.insert("", "end", values=(
                p.get('inst_no', i + 1),
                to_display_date(inst_date),
                to_display_date(recv),
                p.get('receipt_no', ''),
                p.get('amount', ''),
                p.get('balance', balance_orig),
            ), tags=(_row_tag(i, recv, inst_date),),)
    else:
        # Generate monthly instalment dates starting ONE month after the case date
        import calendar
        raw_case_date = r.get('date', '')
        _sd = _parse_date(str(raw_case_date).strip())
        # Always use the case's own date — never fall back to today
        if not _sd:
            messagebox.showwarning(
                "Missing Date",
                "This case has no date set.\n"
                "Instalment dates could not be generated.\n"
                "Please edit the case and set a valid date first.",
                parent=top)
            start_date = _dt_chart.date.today()
        else:
            start_date = _sd.date()

        for i in range(1, no_inst + 1):
            # Correct month arithmetic: add i months to start_date
            total_months = start_date.month - 1 + i   # 0-based months from Jan
            year  = start_date.year + total_months // 12
            month = total_months % 12 + 1              # back to 1-based
            day   = min(start_date.day, calendar.monthrange(year, month)[1])
            inst_date_obj = _dt_chart.date(year, month, day)
            inst_date_str = inst_date_obj.strftime("%d/%m/%Y")
            tree2.insert("", "end", values=(
                i, inst_date_str, "", "", "", balance_orig
            ), tags=(_row_tag(i, "", inst_date_str),))

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
        ent = tk.Entry(tree2, font=(FONT_MONO, 13), fg=TEXT, bg=BG_INPUT,
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

            recv_raw = vals[2]
            inst_raw = vals[1]

            recv_dt = _parse_date(recv_raw)
            inst_dt = _parse_date(inst_raw)

            recv = recv_dt.strftime("%d/%m/%Y") if recv_dt else ""
            inst_date = inst_dt.strftime("%d/%m/%Y") if inst_dt else ""

            vals[1] = inst_date
            vals[2] = recv

            tree2.item(item, values=vals, tags=(_row_tag(0, recv, inst_date),))

            ent.destroy()
            edit_entry[0] = None

            _recalc_balance()

        ent.bind("<Return>",   commit)
        ent.bind("<Tab>",      commit)
        ent.bind("<Escape>",   lambda e: (ent.destroy(), edit_entry.__setitem__(0, None)))
        ent.bind("<FocusOut>", commit)

    tree2.bind("<Double-1>", on_cell_dbl)

    # ── Balance recalc ────────────────────────────────────────────────────
    def _recalc_balance():
        try:
            running = float(str(balance_orig).replace(',', '') or 0)
        except Exception:
            running = 0.0

        children = tree2.get_children()

        for child in children:
            vals = list(tree2.item(child, "values"))

            recv_dt = _parse_date(vals[2])
            inst_dt = _parse_date(vals[1])

            recv      = recv_dt.strftime("%d/%m/%Y") if recv_dt else ""
            inst_date = inst_dt.strftime("%d/%m/%Y") if inst_dt else ""

            vals[1] = inst_date
            vals[2] = recv

            try:
                paid = float(str(vals[4]).replace(',', '') or 0)
            except Exception:
                paid = 0.0

            if recv:
                running -= paid

            vals[5] = f"{running:.2f}"

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
                'inst_date':  to_mysql_date(v[1]) if v[1] else None,
                'recv_date':  to_mysql_date(v[2]) if v[2] else None,
                'receipt_no': v[3],
                'amount':     v[4],
                'balance':    v[5],
            })
        import time as _time
        last_ex = None
        for attempt in range(3):
            try:
                db.save_installment_payments(int(case_id_str), rows)
                _reload_all()
                messagebox.showinfo("Saved ✓", "Installment chart saved to database.", parent=top)
                return
            except Exception as ex:
                last_ex = ex
                if "1205" in str(ex) or "Lock wait timeout" in str(ex):
                    _time.sleep(1.5)
                    continue
                break
        messagebox.showerror("Error", str(last_ex), parent=top)

    # ── Button bar ────────────────────────────────────────────────────────
    tk.Frame(top, bg=BORDER, height=1).pack(fill="x")
    btn_bar = tk.Frame(top, bg=BG_PANEL, pady=8, padx=16)
    btn_bar.pack(fill="x")

    tk.Button(btn_bar, text="＋  Add Row  INS", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT_PUR, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=add_row).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="−  Delete Row  DEL", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT_YEL, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=del_row).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="🔄  Recalc Balance", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=_recalc_balance).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="💾  SAVE  F10", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT2, relief="flat", bd=0, padx=14, pady=6,
              cursor="hand2", command=save_chart).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_bar, text="✕  CLOSE  ESC", font=(FONT_UI, 12, "bold"),
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
    tk.Label(ti, text="NEW CASES", font=(FONT_UI, 18, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(ti, text="Installment Case Management",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
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
    tk.Label(sf, text="🔍", font=(FONT_UI, 14), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, font=(FONT_UI, 13), fg=TEXT_DIM,
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
                         font=(FONT_UI, 12, "bold"), fg=ACCENT, bg="#1b2e4a",
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
    tk.Label(gf, text="GOTO CASE ID", font=(FONT_UI, 11, "bold"),
             fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    goto_var = tk.StringVar()
    ge = tk.Entry(gf, textvariable=goto_var, font=(FONT_MONO, 13),
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
    tk.Button(gf, text="GO", font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT,
              relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
              command=do_goto).pack(side=tk.LEFT, padx=6)

    pending_lbl = tk.Label(sbar, text=f"NO OF PENDING CASES  {len(INSTALLMENT_CASES)}",
                           font=(FONT_UI, 12, "bold"), fg=ACCENT_YEL, bg=BG_PANEL)
    pending_lbl.pack(side=tk.LEFT, padx=30)

    tots = tk.Frame(sbar, bg=BG_PANEL)
    tots.pack(side=tk.RIGHT)
    for lbl, val, color in [("Finance Total", f"₹ {tf_:,.2f}", ACCENT2),
                             ("Balance Total", f"₹ {tb_:,.2f}", ACCENT_RED)]:
        tf2 = tk.Frame(tots, bg=BG_CARD, padx=12, pady=4)
        tf2.pack(side=tk.LEFT, padx=4)
        tk.Label(tf2, text=lbl, font=(FONT_UI, 10, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        tk.Label(tf2, text=val, font=(FONT_MONO, 14, "bold"), fg=color, bg=BG_CARD).pack(anchor="w")

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
    tk.Label(tb2, text=title, font=(FONT_UI, 19, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    if subtitle:
        tk.Label(tb2, text=subtitle, font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
    badge2 = tk.Label(topbar, text=f"  {len(data)}  ", font=(FONT_UI, 12, "bold"),
                      fg=ACCENT, bg="#1b2e4a", padx=6, pady=4)
    badge2.pack(side=tk.LEFT, padx=16)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 12),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)

    make_shortcut_bar(right, [("ESC", "CLOSE", ACCENT_RED), ("F9", "SEARCH", "#36bfd9")])
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    sf2 = tk.Frame(right, bg=BG, padx=16, pady=8)
    sf2.pack(fill=tk.X)
    tk.Label(sf2, text="🔍", font=(FONT_UI, 14), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv2 = tk.StringVar()
    se2 = tk.Entry(sf2, textvariable=sv2, font=(FONT_UI, 13), fg=TEXT_DIM,
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
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)

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
    tk.Label(topbar, text="Dashboard Overview", font=(FONT_UI, 19, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 12),
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
        tk.Label(inn, text=icon, font=(FONT_UI, 23), fg=color, bg=BG_CARD).pack(anchor="w")
        tk.Label(inn, text=value, font=(FONT_UI, 27, "bold"), fg=TEXT, bg=BG_CARD).pack(anchor="w", pady=(6, 2))
        tk.Label(inn, text=label, font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        tk.Frame(card2, bg=color, height=3).pack(fill=tk.X, side=tk.BOTTOM)

    tk.Label(body, text="System Details", font=(FONT_UI, 15, "bold"),
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
        tk.Label(ic2, text=k, font=(FONT_UI, 12, "bold"), fg=TEXT_DIM,
                 bg=BG_CARD, width=16, anchor="w").grid(row=r, column=0, pady=5, sticky="w")
        tk.Label(ic2, text=v, font=(FONT_UI, 13), fg=TEXT,
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

    # ── Auto-apply fine once after due date passes ────────────────────────
    if editing and data.get('id'):
        was_applied = db.apply_fine_if_due(int(data['id']))
        if was_applied:
            # Reload fresh data so the form shows the updated balance & fine_applied flag
            fresh = db.get_credit_case(int(data['id']))
            if fresh:
                data = fresh
                d    = data   # will be re-set below, but refresh the reference early
    # ─────────────────────────────────────────────────────────────────────
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
             font=(FONT_UI, 18, "bold"), fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(tb_inner, text="Complete all sections · Press F10 to save",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

    badge_f = tk.Frame(topbar, bg=BG_PANEL, padx=20)
    badge_f.pack(side=tk.RIGHT)
    tk.Label(badge_f, text="CASE ID", font=(FONT_UI, 11),
             fg=TEXT_DIM, bg=BG_PANEL).pack()
    tk.Label(badge_f, text=str(next_id),
             font=(FONT_MONO, 25, "bold"), fg=ACCENT_RED, bg=BG_PANEL).pack()

    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
    make_shortcut_bar(win, [
        ("ESC", "CANCEL",      ACCENT_RED),
        ("F10", "SAVE & EXIT", ACCENT2),
        ("INS", "ADD ROW",     ACCENT_PUR),
        ("DEL", "DELETE ROW",  ACCENT_YEL),
    ])
    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    # ── Scrollable canvas wrapper ─────────────────────────────────────────
    scroll_canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    _vsb = tk.Scrollbar(win, orient="vertical", command=scroll_canvas.yview)
    _vsb.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_canvas.configure(yscrollcommand=_vsb.set)

    outer = tk.Frame(scroll_canvas, bg=BG, padx=24, pady=12)
    _outer_id = scroll_canvas.create_window((0, 0), window=outer, anchor="nw")

    def _on_outer_configure(e):
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
    def _on_canvas_resize(e):
        scroll_canvas.itemconfig(_outer_id, width=e.width)
    outer.bind("<Configure>", _on_outer_configure)
    scroll_canvas.bind("<Configure>", _on_canvas_resize)
    scroll_canvas.bind_all("<MouseWheel>",
        lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

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
    left_col.grid_rowconfigure(0, weight=2)
    left_col.grid_rowconfigure(1, weight=3)
    left_col.grid_columnconfigure(0, weight=1)

    # ── Customer card ─────────────────────────────────────────────────────
    cust_card = tk.Frame(left_col, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         padx=16, pady=12)
    cust_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
    section_header(cust_card, "CUSTOMER DETAILS", ACCENT_RED)

    cg = tk.Frame(cust_card, bg=BG_CARD)
    cg.pack(fill=tk.X)
    cg.grid_columnconfigure(1, weight=1)
    cg.grid_columnconfigure(3, weight=1)

    # FILE NO + DATE on same row
    tk.Label(cg, text="FILE NO", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=0, sticky="w", pady=5, padx=4)
    e_fn = make_entry(cg, width=10)
    e_fn.insert(0, d.get('file_no', ''))
    e_fn.grid(row=0, column=1, sticky="ew", ipady=7, pady=5, padx=(0, 12))
    entries['file_no'] = e_fn

    tk.Label(cg, text="DATE", font=(FONT_UI, 13), fg=TEXT_DIM,
             bg=BG_CARD).grid(row=0, column=2, sticky="w", pady=5, padx=4)
    e_dt = make_entry(cg, width=13)
    e_dt.insert(0, to_display_date(d.get('date')) or datetime.today().strftime("%d/%m/%Y"))
    e_dt.config(fg=TEXT if d.get('date') else TEXT_DIM)
    e_dt.grid(row=0, column=3, sticky="ew", ipady=7, pady=5)
    entries['date'] = e_dt
    e_dt.bind("<FocusIn>",
              lambda e: (e_dt.delete(0, tk.END), e_dt.config(fg=TEXT))
                        if e_dt.get() == "DD/MM/YYYY" else None)
    e_dt.bind("<FocusOut>",
              lambda e: (e_dt.insert(0, datetime.today().strftime("%d/%m/%Y")), e_dt.config(fg=TEXT_DIM))
                        if not e_dt.get() else None)

    for i, (lbl, key) in enumerate([
        ("ACCOUNT",     "customer"),
        ("W/O D/O S/O", "relation"),
        ("ADDRESS",     "address"),
        ("VILLAGE",     "_village_entry"),
        ("MOBILE NO",   "mobile_no"),
        ("REMARKS",     "remarks"),
    ], start=1):
        tk.Label(cg, text=lbl, font=(FONT_UI, 13), fg=TEXT_DIM,
                 bg=BG_CARD, width=12, anchor="w").grid(
                 row=i, column=0, sticky="w", pady=4, padx=4)
        if lbl == "VILLAGE":
            village_var = tk.StringVar(value=d.get('village', ''))
            entries['village'] = village_var
            village_vals = db.get_villages()
            ttk.Combobox(cg, textvariable=village_var, values=village_vals,
                         style="Dark.TCombobox", font=(FONT_UI, 13), width=26
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
        tk.Label(gg, text=lbl, font=(FONT_UI, 13), fg=TEXT_DIM,
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
    item_inner.pack(fill=tk.BOTH, expand=True)
    item_inner.grid_columnconfigure(0, weight=1)
    item_inner.grid_columnconfigure(1, weight=0)

    ig = tk.Frame(item_inner, bg=BG_CARD)
    ig.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
    ig.grid_columnconfigure(1, weight=1)

    def money_entry(parent, var, row, label, editable=True, color=ACCENT_RED):
        tk.Label(parent, text=label, font=(FONT_UI, 13), fg=TEXT_DIM,
                 bg=BG_CARD, width=16, anchor="w").grid(
                 row=row, column=0, sticky="w", pady=6, padx=4)
        state = "normal" if editable else "readonly"
        rbg   = BG_INPUT if editable else BG_CARD
        e = tk.Entry(parent, textvariable=var, state=state,
                     font=(FONT_MONO, 14, "bold"), fg=color,
                     bg=rbg, readonlybackground=rbg,
                     insertbackground=ACCENT, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER, width=20)
        e.grid(row=row, column=1, sticky="ew", ipady=8, pady=6, padx=(0, 8))
        return e

    amount_var  = tk.StringVar(value=d.get('amount', ''))
    receipt_var = tk.StringVar(value=d.get('total_receipt', '0.00'))
    balance_var = tk.StringVar(value=d.get('balance', '0.00'))
    fine_var    = tk.StringVar(value=d.get('fine', ''))

    money_entry(ig, amount_var,  0, "AMOUNT",         editable=False, color=ACCENT_YEL)
    money_entry(ig, receipt_var, 1, "TOTAL RECEIPT",  editable=False)
    money_entry(ig, balance_var, 2, "BALANCE AMOUNT", editable=False)
    entries['amount'] = amount_var

    # NEXT DUE DATE — highlighted
    tk.Label(ig, text="NEXT DUE DATE", font=(FONT_UI, 13, "bold"), fg=ACCENT_PUR,
             bg=BG_CARD, width=16, anchor="w").grid(row=3, column=0, sticky="w", pady=6, padx=4)
    e_due = make_entry(ig, width=20)
    e_due.insert(0, to_display_date(d.get('next_due_date')) or datetime.today().strftime("%d/%m/%Y"))
    e_due.grid(row=3, column=1, sticky="ew", ipady=7, pady=6, padx=(0, 8))
    entries['next_due_date'] = e_due

    # FINE — editable, shown in red
    tk.Label(ig, text="FINE  ₹", font=(FONT_UI, 13, "bold"), fg=ACCENT_RED,
             bg=BG_CARD, width=16, anchor="w").grid(row=4, column=0, sticky="w", pady=6, padx=4)
    fine_entry_w = tk.Entry(ig, textvariable=fine_var,
                            font=(FONT_MONO, 14, "bold"), fg=ACCENT_RED, bg=BG_INPUT,
                            insertbackground=ACCENT_RED, relief="flat",
                            highlightthickness=1, highlightcolor=ACCENT_RED,
                            highlightbackground=BORDER, width=20)
    fine_entry_w.grid(row=4, column=1, sticky="ew", ipady=8, pady=6, padx=(0, 8))
    entries['fine'] = fine_var

    # Lock fine field once applied so it can't be changed accidentally
    if int(str(d.get('fine_applied', 0) or 0)) == 1:
        fine_entry_w.config(state="readonly", readonlybackground="#fff0f0",
                            fg=ACCENT_RED, font=(FONT_MONO, 14, "bold"))
        tk.Label(ig, text="✓ Applied", font=(FONT_UI, 11, "bold"),
                 fg=ACCENT_RED, bg=BG_CARD).grid(row=4, column=2, sticky="w", padx=4)

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
                              fill=TEXT_DIM, font=(FONT_UI, 13))
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

    # Pre-fill rows from existing data; new cases start with an empty table
    import datetime as _dt
    if editing:
        existing_rows = d.get('payment_rows', [("", "", "", "")])
    else:
        existing_rows = []
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

    tk.Label(footer, text="TOTAL", font=(FONT_UI, 12, "bold"),
             fg=TEXT_DIM, bg=BG_CARD, anchor="e").grid(row=0, column=1, sticky="e", padx=4)
    sale_total_lbl = tk.Label(footer, text="0.00",
                               font=(FONT_MONO, 14, "bold"), fg=ACCENT2,
                               bg=BG_CARD, anchor="center")
    sale_total_lbl.grid(row=0, column=2, sticky="ew", padx=4)
    receipt_total_lbl = tk.Label(footer, text="0.00",
                                  font=(FONT_MONO, 14, "bold"), fg=ACCENT_RED,
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

        entry = tk.Entry(sale_tree, font=(FONT_UI, 13),
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
        ent = tk.Entry(sale_tree, font=(FONT_UI, 13), fg=TEXT, bg=BG_INPUT,
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
        # AMOUNT is driven by the sum of the SALE AMOUNT column
        amount_var.set(f"{sale_tot:.2f}")
        receipt_var.set(f"{rec_tot:.2f}")
        # Fine is added to balance only if due date has passed and fine > 0
        try:
            fine_val = float(str(fine_var.get()).replace(',', '') or 0)
        except Exception:
            fine_val = 0.0
        due_raw = entries.get('next_due_date')
        due_str = due_raw.get() if isinstance(due_raw, tk.Entry) else ""
        due_dt  = _parse_date(due_str)
        fine_pending = fine_val > 0 and due_dt is not None and due_dt.date() < datetime.today().date()
        balance_var.set(f"{sale_tot - rec_tot + (fine_val if fine_pending else 0):.2f}")

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
    tk.Button(btn_row, text="＋  Add Row  INS", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT_PUR, relief="flat", bd=0, padx=12, pady=5,
              cursor="hand2", command=add_row).pack(side=tk.LEFT, padx=(0, 8))
    tk.Button(btn_row, text="−  Delete Row  DEL", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT_YEL, relief="flat", bd=0, padx=12, pady=5,
              cursor="hand2", command=del_row).pack(side=tk.LEFT)

    win.bind("<Insert>", add_row)
    win.bind("<Delete>", del_row)

    # initial totals
    recalc_totals()
    # Recalc whenever fine amount or due date changes
    fine_var.trace_add("write", lambda *_: recalc_totals())

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
            'date':           to_mysql_date(get('date')),
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
            'next_due_date':  to_mysql_date(get('next_due_date')),
            'fine':           get('fine'),
            # Preserve fine_applied flag from the loaded data so saving never resets it
            'fine_applied':   int(str(d.get('fine_applied', 0) or 0)),
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

    # tk.Button(action_bar, text="✕  CANCEL  ESC",
    #           command=win.destroy,
    #           font=(FONT_UI, 14, "bold"), fg=ACCENT_RED, bg=BG_CARD,
    #           activeforeground=ACCENT_RED, activebackground=BG_PANEL,
    #           relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
    #           highlightthickness=1, highlightbackground=ACCENT_RED
    #           ).pack(side=tk.LEFT, padx=(0, 16))

    # tk.Button(action_bar, text="💾  SAVE & EXIT  F10",
    #           command=save_and_exit,
    #           font=(FONT_UI, 14, "bold"), fg=BG, bg=ACCENT2,
    #           activeforeground=BG, activebackground="#2ebd68",
    #           relief="flat", bd=0, cursor="hand2", padx=24, pady=10,
    #           ).pack(side=tk.LEFT)

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
    tk.Label(ti, text="CREDIT CASES", font=(FONT_UI, 18, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(anchor="w")
    tk.Label(ti, text="Credit Case Management",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")
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
    tk.Label(sf, text="🔍", font=(FONT_UI, 14), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, font=(FONT_UI, 13), fg=TEXT_DIM,
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
                         font=(FONT_UI, 12, "bold"), fg=ACCENT, bg="#1b2e4a",
                         padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    # Credit-specific columns (includes Fine on overdue balance)
    CR_COLS   = ['file_no', 'date', 'customer_display', 'village', 'mobile_no',
                 'finance_amt', 'balance', 'next_due_date', 'id']
    CR_HEADS  = ['File No', 'Date', 'Customer (Father)', 'Village', 'Mobile No',
                 'Finance Amt', 'Balance', '\u26a0 Next Due Date', 'ID']
    CR_WIDTHS = [70, 95, 200, 120, 140, 105, 100, 120, 50]

    # Fine rate: 2% per month on outstanding balance
    FINE_RATE_PER_DAY = 0.02 / 30

    def _calc_fine(r):
        """Return fine string if next_due_date is in the past and balance > 0."""
        try:
            due_raw = r.get('next_due_date') or ''
            if not due_raw:
                return ''
            _due_p = _parse_date(str(due_raw).strip())
            if not _due_p: return ''
            due_dt = _due_p.date()
            today  = datetime.today().date()
            if today <= due_dt:
                return ''
            overdue_days = (today - due_dt).days
            balance = float(str(r.get('balance', 0) or 0).replace(',', ''))
            if balance <= 0:
                return ''
            fine = balance * FINE_RATE_PER_DAY * overdue_days
            return f"\u20b9 {fine:,.2f}  ({overdue_days}d)"
        except Exception:
            return ''

    # Table
    to = tk.Frame(win, bg=BG, padx=20)
    to.pack(fill=tk.BOTH, expand=True)
    tb = tk.Frame(to, bg=BORDER, bd=1)
    tb.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(tb, columns=CR_COLS, show="headings", style="T.Treeview")
    for col, head, width in zip(CR_COLS, CR_HEADS, CR_WIDTHS):
        tree.heading(col, text=head)
        anchor = "center" if col in ('finance_amt', 'balance') else "w"
        tree.column(col, width=width, minwidth=50, anchor=anchor)
    tree.tag_configure("even",    background=BG_CARD)
    tree.tag_configure("odd",     background=BG_ROW_ALT)
    tree.tag_configure("overdue", background="#fff0f0", foreground="#b91c1c")

    def _credit_row(r):
        row = []
        for c in CR_COLS:
            if c == 'customer_display':
                row.append(fmt_customer(r.get('customer', ''), r.get('relation', '')))
            elif c == 'next_due_date':
                row.append(to_display_date(r.get('next_due_date', '')))
            elif c == 'fine_overdue':
                row.append(_calc_fine(r))
            else:
                row.append(r.get(c, ''))
        return tuple(row)

    all_data = [_credit_row(r) for r in CREDIT_CASES]

    def populate(rows):
        for item in tree.get_children(): tree.delete(item)
        for i, vals in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", tk.END, values=vals, tags=(tag,))
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
    tk.Label(gf, text="GOTO CASE ID", font=(FONT_UI, 11, "bold"),
             fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    goto_var = tk.StringVar()
    ge = tk.Entry(gf, textvariable=goto_var, font=(FONT_MONO, 13),
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
    tk.Button(gf, text="GO", font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT,
              relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
              command=do_goto).pack(side=tk.LEFT, padx=6)

    pending_lbl = tk.Label(sbar, text=f"NO OF PENDING CASES  {len(CREDIT_CASES)}",
                           font=(FONT_UI, 12, "bold"), fg=ACCENT_YEL, bg=BG_PANEL)
    pending_lbl.pack(side=tk.LEFT, padx=30)

    tots = tk.Frame(sbar, bg=BG_PANEL)
    tots.pack(side=tk.RIGHT)
    for lbl, val, color in [("Finance Total", f"₹ {tf_:,.2f}", ACCENT2),
                             ("Balance Total", f"₹ {tb_:,.2f}", ACCENT_RED)]:
        tf2 = tk.Frame(tots, bg=BG_CARD, padx=12, pady=4)
        tf2.pack(side=tk.LEFT, padx=4)
        tk.Label(tf2, text=lbl, font=(FONT_UI, 10, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        tk.Label(tf2, text=val, font=(FONT_MONO, 14, "bold"), fg=color, bg=BG_CARD).pack(anchor="w")

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
             font=(FONT_UI, 19, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Label(topbar, text="  Credit cases with outstanding balance",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 12),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)

    make_shortcut_bar(right, [
        ("ESC", "CLOSE",       ACCENT_RED),
        ("F2",  "OPEN CASE",   ACCENT),
        ("F9",  "SEARCH",      "#36bfd9"),
        ("F5",  "REFRESH",     ACCENT_YEL),
        ("F6",  "PREVIEW",     "#0ea5e9"),
        ("F7",  "PRINT",       ACCENT_RED),
    ])
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    sf = tk.Frame(right, bg=BG, padx=16, pady=8)
    sf.pack(fill=tk.X)
    tk.Label(sf, text="🔍", font=(FONT_UI, 14), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, font=(FONT_UI, 13), fg=TEXT_DIM,
                  bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                  highlightthickness=1, highlightcolor=ACCENT,
                  highlightbackground=BORDER, width=38)
    se.pack(side=tk.LEFT, ipady=7, padx=(8, 12))
    PH = "Search by file no, customer, village…"
    se.insert(0, PH)
    se.bind("<FocusIn>",  lambda e: (se.delete(0, tk.END), se.config(fg=TEXT)) if se.get() == PH else None)
    se.bind("<FocusOut>", lambda e: (se.insert(0, PH), se.config(fg=TEXT_DIM)) if not se.get() else None)

    rec_badge = tk.Label(sf, text="  0 records  ", font=(FONT_UI, 12, "bold"),
                         fg=ACCENT, bg="#1b2e4a", padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    # Print / Preview buttons
    tk.Button(sf, text="👁  Preview  F6",
              font=(FONT_UI, 11, "bold"), fg=BG, bg="#0ea5e9",
              relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
              command=lambda: _open_print_preview(
                  win,
                  _build_credit_due_html(_get_credit_visible_rows()),
                  "Due Report — Credit Cases"
              )).pack(side=tk.RIGHT, padx=(6, 0))
    tk.Button(sf, text="🖨  Print  F7",
              font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT_RED,
              relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
              command=lambda: _quick_print_credit_due(win, _get_credit_visible_rows())
              ).pack(side=tk.RIGHT, padx=(6, 0))

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
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    bf = tk.Frame(sbar, bg=BG_CARD, padx=12, pady=4)
    bf.pack(side=tk.RIGHT, padx=4)
    tk.Label(bf, text="Total Balance Due", font=(FONT_UI, 10, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
    try:
        tb_ = sum(float(r[6] or 0) for r in all_rows)
    except Exception:
        tb_ = 0
    bal_lbl = tk.Label(bf, text=f"₹ {tb_:,.2f}", font=(FONT_MONO, 14, "bold"), fg=ACCENT_RED, bg=BG_CARD)
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

    def _get_credit_visible_rows():
        """Return currently visible (filtered) rows from the credit due tree."""
        return [tree.item(item, "values") for item in tree.get_children()]

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<F2>", open_case)
    win.bind("<F5>", refresh)
    win.bind("<F6>", lambda e: _open_print_preview(
        win, _build_credit_due_html(_get_credit_visible_rows()),
        "Due Report — Credit Cases"))
    win.bind("<F7>", lambda e: _quick_print_credit_due(win, _get_credit_visible_rows()))
    win.bind("<F9>", lambda e: se.focus_set())
    tree.bind("<Double-1>", lambda e: open_case())


# ═════════════════════════════════════════════════════════════════════════════
# PRINT / PREVIEW — INSTALLMENT DUE PAYMENTS
# ═════════════════════════════════════════════════════════════════════════════

def _build_installment_due_html(rows, title="DUE PAYMENTS REPORT — INSTALLMENT CASES"):
    """
    Build an HTML string for the installment due-payments report.
    rows: list of tuples matching COLS order:
      [file_no, date, customer_display, village, mobile_no,
       instalment_amt, missed_instalments, total_overdue, balance, id]
    Grouped by village, matching the ledger-style image layout.
    """
    from collections import defaultdict
    from datetime import datetime

    # Group rows by village (col index 3)
    groups = defaultdict(list)
    for r in rows:
        groups[str(r[3]).strip().upper() or "UNKNOWN"].append(r)

    today = datetime.today().strftime("%d/%m/%Y")

    rows_html = ""
    grand_total_due = 0.0
    grand_total_inst = 0.0

    for village in sorted(groups.keys()):
        village_rows = groups[village]
        rows_html += f"""
        <tr class="village-header">
            <td colspan="7"><span class="village-name">{village}</span></td>
        </tr>"""
        for r in village_rows:
            file_no   = r[0]
            date_val  = r[1]
            customer  = r[2]
            mobile    = r[4]
            inst_amt  = r[5]
            missed    = r[6]
            total_due = r[7]
            balance   = r[8]

            try:
                inst_f = float(inst_amt or 0)
            except Exception:
                inst_f = 0.0
            try:
                due_f = float(total_due or 0)
            except Exception:
                due_f = 0.0

            grand_total_inst += inst_f
            grand_total_due  += due_f

            rows_html += f"""
        <tr class="data-row">
            <td class="file-cell">
                <div class="file-no">{file_no}</div>
                <div class="date-sub">{date_val}</div>
            </td>
            <td class="customer-cell">
                <div class="cust-name">{customer}</div>
            </td>
            <td class="mobile-cell">{mobile}</td>
            <td class="num-cell missed">{missed}</td>
            <td class="num-cell inst-amt">₹ {inst_f:,.2f}</td>
            <td class="num-cell total-due highlight">₹ {due_f:,.2f}</td>
            <td class="num-cell balance">₹ {float(balance or 0):,.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    background: #fff;
    color: #1a1a2e;
    padding: 18px 20px;
  }}
  .report-header {{
    border-bottom: 3px solid #1e40af;
    padding-bottom: 10px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .company-name {{
    font-size: 20px;
    font-weight: 700;
    color: #1e40af;
    letter-spacing: 1px;
  }}
  .report-title {{
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    margin-top: 2px;
  }}
  .report-meta {{
    font-size: 11px;
    color: #6b7280;
    text-align: right;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  th {{
    background: #1e3a8a;
    color: #fff;
    font-size: 10.5px;
    font-weight: 600;
    padding: 7px 8px;
    text-align: left;
    letter-spacing: 0.5px;
  }}
  th.num {{ text-align: right; }}
  .village-header td {{
    background: #dbeafe;
    color: #1e3a8a;
    padding: 5px 8px;
    font-weight: 700;
    font-size: 11.5px;
    border-top: 1px solid #bfdbfe;
  }}
  .village-name {{
    display: inline-block;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  .data-row td {{
    padding: 5px 8px;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: top;
  }}
  .data-row:nth-child(even) td {{ background: #f9fafb; }}
  .data-row:nth-child(odd)  td {{ background: #ffffff; }}
  .file-no   {{ font-weight: 600; color: #374151; }}
  .date-sub  {{ font-size: 10px; color: #9ca3af; margin-top: 1px; }}
  .cust-name {{ font-weight: 600; color: #111827; }}
  .mobile-cell {{ color: #4b5563; font-size: 11px; vertical-align: middle; }}
  .num-cell  {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .missed    {{ color: #b45309; font-weight: 700; font-size: 13px; text-align: center; }}
  .inst-amt  {{ color: #1d4ed8; }}
  .total-due {{ color: #b91c1c; font-weight: 700; }}
  .highlight {{ background: #fff7ed !important; }}
  .balance   {{ color: #047857; }}
  .grand-total-row td {{
    background: #1e3a8a;
    color: #fff;
    font-weight: 700;
    font-size: 12px;
    padding: 8px 8px;
    border-top: 2px solid #1e40af;
  }}
  .grand-total-row .num-cell {{ text-align: right; }}
  .footer {{
    margin-top: 16px;
    font-size: 10px;
    color: #9ca3af;
    text-align: center;
    border-top: 1px solid #e5e7eb;
    padding-top: 8px;
  }}
  @media print {{
    body {{ padding: 8px 10px; }}
    .no-print {{ display: none !important; }}
    @page {{ margin: 10mm; size: A4; }}
  }}
</style>
</head>
<body>
<div class="report-header">
  <div>
    <div class="company-name">SANDHU ENTERPRISES</div>
    <div class="report-title">DUE PAYMENTS — INSTALLMENT CASES</div>
  </div>
  <div class="report-meta">
    Printed: {today}<br>
    Total Records: {len(rows)}
  </div>
</div>

<div class="no-print" style="margin-bottom:12px; display:flex; gap:10px;">
  <button onclick="window.print()"
    style="background:#1e40af;color:#fff;border:none;padding:8px 20px;
           font-size:13px;font-weight:600;border-radius:5px;cursor:pointer;">
    🖨 Print
  </button>
  <button onclick="window.close()"
    style="background:#f3f4f6;color:#374151;border:1px solid #d1d5db;
           padding:8px 16px;font-size:13px;border-radius:5px;cursor:pointer;">
    ✕ Close
  </button>
</div>

<table>
  <thead>
    <tr>
      <th>File No / Date</th>
      <th>Customer (Father)</th>
      <th>Mobile No</th>
      <th class="num" style="text-align:center;">Missed</th>
      <th class="num">Inst. Amt</th>
      <th class="num">Total Due</th>
      <th class="num">Balance</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
    <tr class="grand-total-row">
      <td colspan="4">GRAND TOTAL — {len(rows)} CASES</td>
      <td class="num-cell">₹ {grand_total_inst:,.2f}</td>
      <td class="num-cell">₹ {grand_total_due:,.2f}</td>
      <td></td>
    </tr>
  </tbody>
</table>
<div class="footer">Sandhu Enterprises · Financial Tracking System · Generated {today}</div>
</body>
</html>"""
    return html


def _build_credit_due_html(rows, title="DUE REPORT — CREDIT CASES"):
    """
    Build HTML for the credit due report.
    rows: tuples matching COLS order:
      [file_no, date, customer_display, village, mobile_no,
       finance_amt, balance, next_due_date, id]
    """
    from collections import defaultdict
    from datetime import datetime

    groups = defaultdict(list)
    for r in rows:
        groups[str(r[3]).strip().upper() or "UNKNOWN"].append(r)

    today = datetime.today().strftime("%d/%m/%Y")

    rows_html = ""
    grand_finance = 0.0
    grand_balance = 0.0

    for village in sorted(groups.keys()):
        village_rows = groups[village]
        rows_html += f"""
        <tr class="village-header">
            <td colspan="7"><span class="village-name">{village}</span></td>
        </tr>"""
        for r in village_rows:
            file_no     = r[0]
            date_val    = r[1]
            customer    = r[2]
            mobile      = r[4]
            finance_amt = r[5]
            balance     = r[6]
            next_due    = r[7]

            try:
                fin_f = float(str(finance_amt or 0).replace(',', ''))
            except Exception:
                fin_f = 0.0
            try:
                bal_f = float(str(balance or 0).replace(',', ''))
            except Exception:
                bal_f = 0.0

            grand_finance += fin_f
            grand_balance += bal_f

            rows_html += f"""
        <tr class="data-row">
            <td class="file-cell">
                <div class="file-no">{file_no}</div>
                <div class="date-sub">{date_val}</div>
            </td>
            <td class="customer-cell">
                <div class="cust-name">{customer}</div>
            </td>
            <td class="mobile-cell">{mobile}</td>
            <td class="num-cell due-date">{next_due}</td>
            <td class="num-cell fin-amt">₹ {fin_f:,.2f}</td>
            <td class="num-cell balance highlight">₹ {bal_f:,.2f}</td>
            <td class="num-cell total-due">₹ {bal_f:,.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Noto Sans', 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    background: #fff;
    color: #1a1a2e;
    padding: 18px 20px;
  }}
  .report-header {{
    border-bottom: 3px solid #dc2626;
    padding-bottom: 10px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .company-name {{ font-size: 20px; font-weight: 700; color: #dc2626; letter-spacing: 1px; }}
  .report-title  {{ font-size: 13px; font-weight: 600; color: #374151; margin-top: 2px; }}
  .report-meta   {{ font-size: 11px; color: #6b7280; text-align: right; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{
    background: #7f1d1d;
    color: #fff;
    font-size: 10.5px;
    font-weight: 600;
    padding: 7px 8px;
    text-align: left;
    letter-spacing: 0.5px;
  }}
  th.num {{ text-align: right; }}
  .village-header td {{
    background: #fee2e2;
    color: #991b1b;
    padding: 5px 8px;
    font-weight: 700;
    font-size: 11.5px;
    border-top: 1px solid #fecaca;
  }}
  .village-name {{
    display: inline-block;
    border-left: 4px solid #dc2626;
    padding-left: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  .data-row td {{
    padding: 5px 8px;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: top;
  }}
  .data-row:nth-child(even) td {{ background: #f9fafb; }}
  .data-row:nth-child(odd)  td {{ background: #ffffff; }}
  .file-no   {{ font-weight: 600; color: #374151; }}
  .date-sub  {{ font-size: 10px; color: #9ca3af; margin-top: 1px; }}
  .cust-name {{ font-weight: 600; color: #111827; }}
  .mobile-cell {{ color: #4b5563; font-size: 11px; vertical-align: middle; }}
  .num-cell  {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .due-date  {{ color: #b45309; font-weight: 600; text-align: center; }}
  .fin-amt   {{ color: #1d4ed8; }}
  .balance   {{ color: #047857; }}
  .highlight {{ background: #fff7ed !important; }}
  .total-due {{ color: #b91c1c; font-weight: 700; }}
  .grand-total-row td {{
    background: #7f1d1d;
    color: #fff;
    font-weight: 700;
    font-size: 12px;
    padding: 8px 8px;
    border-top: 2px solid #dc2626;
  }}
  .grand-total-row .num-cell {{ text-align: right; }}
  .footer {{
    margin-top: 16px;
    font-size: 10px;
    color: #9ca3af;
    text-align: center;
    border-top: 1px solid #e5e7eb;
    padding-top: 8px;
  }}
  @media print {{
    body {{ padding: 8px 10px; }}
    .no-print {{ display: none !important; }}
    @page {{ margin: 10mm; size: A4; }}
  }}
</style>
</head>
<body>
<div class="report-header">
  <div>
    <div class="company-name">SANDHU ENTERPRISES</div>
    <div class="report-title">DUE REPORT — CREDIT CASES</div>
  </div>
  <div class="report-meta">
    Printed: {today}<br>
    Total Records: {len(rows)}
  </div>
</div>

<div class="no-print" style="margin-bottom:12px; display:flex; gap:10px;">
  <button onclick="window.print()"
    style="background:#dc2626;color:#fff;border:none;padding:8px 20px;
           font-size:13px;font-weight:600;border-radius:5px;cursor:pointer;">
    🖨 Print
  </button>
  <button onclick="window.close()"
    style="background:#f3f4f6;color:#374151;border:1px solid #d1d5db;
           padding:8px 16px;font-size:13px;border-radius:5px;cursor:pointer;">
    ✕ Close
  </button>
</div>

<table>
  <thead>
    <tr>
      <th>File No / Date</th>
      <th>Customer (Father)</th>
      <th>Mobile No</th>
      <th class="num" style="text-align:center;">Next Due Date</th>
      <th class="num">Finance Amt</th>
      <th class="num">Balance</th>
      <th class="num">Total Due</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
    <tr class="grand-total-row">
      <td colspan="4">GRAND TOTAL — {len(rows)} CASES</td>
      <td class="num-cell">₹ {grand_finance:,.2f}</td>
      <td class="num-cell">₹ {grand_balance:,.2f}</td>
      <td class="num-cell">₹ {grand_balance:,.2f}</td>
    </tr>
  </tbody>
</table>
<div class="footer">Sandhu Enterprises · Financial Tracking System · Generated {today}</div>
</body>
</html>"""
    return html


def _open_print_preview(parent, html_content, title="Print Preview"):
    """
    Open a Tkinter Toplevel showing the report in a preview window
    with a 'Print' button that writes the HTML to a temp file and
    opens it in the default browser (which supports Ctrl+P / Print).
    """
    import tempfile, os, webbrowser

    # Write HTML to a temporary file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                      mode="w", encoding="utf-8")
    tmp.write(html_content)
    tmp.close()

    preview_path = tmp.name

    win = tk.Toplevel(parent)
    win.title(f"Preview — {title}")
    win.geometry("820x640")
    win.configure(bg=BG)
    apply_dark_titlebar(win)

    # ── Top bar ───────────────────────────────────────────────────────────
    topbar = tk.Frame(win, bg=BG_PANEL, pady=10, padx=16)
    topbar.pack(fill=tk.X)
    tk.Label(topbar, text=f"📄  {title}", font=(FONT_UI, 14, "bold"),
             fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)

    def do_print():
        webbrowser.open(f"file:///{preview_path.replace(os.sep, '/')}")

    tk.Button(topbar, text="🖨  Open & Print in Browser",
              command=do_print,
              font=(FONT_UI, 12, "bold"), fg=BG, bg=ACCENT,
              relief="flat", bd=0, padx=16, pady=6,
              cursor="hand2").pack(side=tk.RIGHT, padx=(8, 0))
    tk.Button(topbar, text="✕  Close", command=win.destroy,
              font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL,
              relief="flat", bd=0, padx=12, pady=6,
              cursor="hand2").pack(side=tk.RIGHT)

    tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

    # ── Preview panel (scrollable HTML-like text render) ──────────────────
    # We render a simplified plain-text version inside Tkinter
    # and open the real HTML for printing in browser
    info_frame = tk.Frame(win, bg=BG_CARD,
                          highlightbackground=BORDER, highlightthickness=1)
    info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

    txt = tk.Text(info_frame, font=(FONT_MONO, 11), fg=TEXT, bg=BG_CARD,
                  relief="flat", highlightthickness=0,
                  padx=12, pady=10, wrap="none")
    sb_v = tk.Scrollbar(info_frame, orient="vertical", command=txt.yview)
    sb_h = tk.Scrollbar(info_frame, orient="horizontal", command=txt.xview)
    txt.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
    sb_v.pack(side=tk.RIGHT,  fill=tk.Y)
    sb_h.pack(side=tk.BOTTOM, fill=tk.X)
    txt.pack(fill=tk.BOTH, expand=True)

    # Parse a plain-text preview from the HTML for display inside Tkinter
    import re
    text_only = re.sub(r'<[^>]+>', '', html_content)
    text_only = re.sub(r'[ \t]{2,}', '  ', text_only)
    text_only = re.sub(r'\n{3,}', '\n\n', text_only)
    txt.insert("1.0", text_only.strip())
    txt.configure(state="disabled")

    hint = tk.Label(win,
                    text="Click 'Open & Print in Browser' to get a full formatted preview and print  (Ctrl+P in the browser).",
                    font=(FONT_UI, 11), fg=TEXT_DIM, bg=BG, wraplength=780)
    hint.pack(pady=(0, 10))

    win.bind("<Escape>", lambda e: win.destroy())


def _quick_print_installment_due(parent, rows):
    """Write HTML to temp file and open in browser immediately."""
    import tempfile, os, webbrowser
    html = _build_installment_due_html(rows)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                      mode="w", encoding="utf-8")
    tmp.write(html); tmp.close()
    webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")


def _quick_print_credit_due(parent, rows):
    """Write HTML to temp file and open in browser immediately."""
    import tempfile, os, webbrowser
    html = _build_credit_due_html(rows)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                      mode="w", encoding="utf-8")
    tmp.write(html); tmp.close()
    webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")


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
             font=(FONT_UI, 19, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Label(topbar, text="  Instalments with outstanding dues",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 12),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)

    make_shortcut_bar(right, [
        ("ESC", "CLOSE",       ACCENT_RED),
        ("F2",  "INST. CHART", ACCENT_PUR),
        ("F3",  "OPEN CASE",   ACCENT),
        ("F9",  "SEARCH",      "#36bfd9"),
        ("F5",  "REFRESH",     ACCENT2),
        ("F6",  "PREVIEW",     "#0ea5e9"),
        ("F7",  "PRINT",       ACCENT_YEL),
    ])
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    sf = tk.Frame(right, bg=BG, padx=16, pady=8)
    sf.pack(fill=tk.X)
    tk.Label(sf, text="🔍", font=(FONT_UI, 14), fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, font=(FONT_UI, 13), fg=TEXT_DIM,
                  bg=BG_CARD, insertbackground=ACCENT, relief="flat",
                  highlightthickness=1, highlightcolor=ACCENT,
                  highlightbackground=BORDER, width=38)
    se.pack(side=tk.LEFT, ipady=7, padx=(8, 12))
    PH = "Search by file no, customer, village…"
    se.insert(0, PH)
    se.bind("<FocusIn>",  lambda e: (se.delete(0, tk.END), se.config(fg=TEXT)) if se.get() == PH else None)
    se.bind("<FocusOut>", lambda e: (se.insert(0, PH), se.config(fg=TEXT_DIM)) if not se.get() else None)

    rec_badge = tk.Label(sf, text="  0 records  ", font=(FONT_UI, 12, "bold"),
                         fg=ACCENT2, bg="#1b2e4a", padx=6, pady=4)
    rec_badge.pack(side=tk.LEFT)

    # Print / Preview buttons in the search bar
    tk.Button(sf, text="👁  Preview  F6",
              font=(FONT_UI, 11, "bold"), fg=BG, bg="#0ea5e9",
              relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
              command=lambda: _open_print_preview(
                  win,
                  _build_installment_due_html(_get_visible_rows()),
                  "Due Payments — Installment Cases"
              )).pack(side=tk.RIGHT, padx=(6, 0))
    tk.Button(sf, text="🖨  Print  F7",
              font=(FONT_UI, 11, "bold"), fg=BG, bg=ACCENT_YEL,
              relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
              command=lambda: _quick_print_installment_due(win, _get_visible_rows())
              ).pack(side=tk.RIGHT, padx=(6, 0))

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
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    bf = tk.Frame(sbar, bg=BG_CARD, padx=12, pady=4)
    bf.pack(side=tk.RIGHT, padx=4)
    tk.Label(bf, text="Total Overdue Amount", font=(FONT_UI, 10, "bold"), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
    try:
        tb_ = sum(float(r[7] or 0) for r in all_rows)
    except Exception:
        tb_ = 0
    bal_lbl = tk.Label(bf, text=f"₹ {tb_:,.2f}", font=(FONT_MONO, 14, "bold"), fg=ACCENT2, bg=BG_CARD)
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

    def _get_visible_rows():
        """Return currently visible (filtered) rows from the tree."""
        return [tree.item(item, "values") for item in tree.get_children()]

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<F2>", open_chart)
    win.bind("<F3>", open_case)
    win.bind("<F5>", refresh)
    win.bind("<F6>", lambda e: _open_print_preview(
        win, _build_installment_due_html(_get_visible_rows()),
        "Due Payments — Installment Cases"))
    win.bind("<F7>", lambda e: _quick_print_installment_due(win, _get_visible_rows()))
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
             font=(FONT_UI, 19, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy, font=(FONT_UI, 12),
              fg=TEXT_DIM, bg=BG_PANEL, activeforeground=ACCENT_RED,
              activebackground=BG_PANEL, relief="flat", bd=0,
              cursor="hand2", padx=12).pack(side=tk.RIGHT)
    tk.Frame(right, bg=BORDER, height=1).pack(fill=tk.X)

    add_bar = tk.Frame(right, bg=BG, padx=20, pady=10)
    add_bar.pack(fill=tk.X)
    tk.Label(add_bar, text="Village Name:", font=(FONT_UI, 13), fg=TEXT_DIM,
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
    tk.Button(add_bar, text="＋ Add Village", font=(FONT_UI, 12, "bold"),
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
    tk.Button(sbar, text="🗑  Delete Selected  Del", font=(FONT_UI, 12, "bold"),
              fg=BG, bg=ACCENT_RED, relief="flat", bd=0, padx=12, pady=5,
              cursor="hand2", command=delete_village).pack(side=tk.LEFT)

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<Delete>", delete_village)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICATION SYSTEM  —  WhatsApp + SMS  (Due-date reminders)
# ═════════════════════════════════════════════════════════════════════════════
import json, os, threading, time as _time

# ── Default message templates  (edit inside the Settings window) ──────────
_NOTIF_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "notif_config.json")

_DEFAULT_CONFIG = {
    # {name}, {amount}, {date}, {file_no}, {company} are replaced at send-time
    "whatsapp_msg": (
        "Namaskar {name} ji,\n\n"
        "Aapka Sandhu Enterprises me file no *{file_no}* ka due payment "
        "₹*{amount}* ki date *{date}* ko thi jo abhi tak pending hai.\n\n"
        "Kripya jald se jald bhugtan karein.\n\n"
        "Shukriya 🙏\n— {company}"
    ),
    "sms_msg": (
        "Namaskar {name} ji, "
        "Aapka Sandhu Enterprises file {file_no} ka due ₹{amount} "
        "date {date} ko tha. Kripya jald payment karein. "
        "-{company}"
    ),
    "company": "Sandhu Enterprises",
    "send_whatsapp": True,
    "send_sms": True,
    # Fast2SMS API key (free tier — get from fast2sms.com)
    "fast2sms_key": "",
    # Delay between messages in seconds (WhatsApp Web needs a small gap)
    "whatsapp_delay": 15,
}


def _load_notif_config():
    try:
        if os.path.exists(_NOTIF_CONFIG_FILE):
            with open(_NOTIF_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                # Fill missing keys from defaults
                for k, v in _DEFAULT_CONFIG.items():
                    cfg.setdefault(k, v)
                return cfg
    except Exception:
        pass
    return dict(_DEFAULT_CONFIG)


def _save_notif_config(cfg):
    try:
        with open(_NOTIF_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass


def _clean_phone(raw):
    """Strip spaces/dashes, add +91 if not present, return None if invalid."""
    if not raw:
        return None
    digits = ''.join(c for c in str(raw) if c.isdigit() or c == '+')
    digits = digits.lstrip('+')
    if len(digits) == 10:
        digits = '91' + digits
    elif len(digits) == 12 and digits.startswith('91'):
        pass
    else:
        return None   # can't parse
    return '+' + digits


def _format_msg(template, name, amount, date_str, file_no, company):
    return (template
            .replace("{name}",    str(name    or ""))
            .replace("{amount}",  str(amount  or ""))
            .replace("{date}",    str(date_str or ""))
            .replace("{file_no}", str(file_no  or ""))
            .replace("{company}", str(company  or "Sandhu Enterprises")))


def _send_whatsapp_one(phone_e164, message, delay=15):
    """
    Send one WhatsApp message via pywhatkit (opens WhatsApp Web in browser).
    phone_e164  e.g. '+919815565672'
    """
    try:
        import pywhatkit as pwk
        # sendwhatmsg_instantly sends immediately (no scheduling)
        pwk.sendwhatmsg_instantly(
            phone_no      = phone_e164,
            message       = message,
            wait_time     = delay,      # seconds to wait for WhatsApp Web to load
            tab_close     = True,
            close_time    = 3,
        )
        return True, "Sent"
    except ImportError:
        return False, "pywhatkit not installed.\nRun:  pip install pywhatkit"
    except Exception as e:
        return False, str(e)


def _send_sms_fast2sms(phone_10digit, message, api_key):
    """
    Send SMS via Fast2SMS free API (India only).
    phone_10digit  e.g. '9815565672'
    api_key        from fast2sms.com → Developer → API
    """
    try:
        import urllib.request, urllib.parse
        payload = urllib.parse.urlencode({
            "authorization": api_key,
            "message":       message,
            "language":      "english",
            "route":         "q",
            "numbers":       phone_10digit,
        }).encode()
        req = urllib.request.Request(
            "https://www.fast2sms.com/dev/bulkV2",
            data    = payload,
            headers = {"cache-control": "no-cache"},
            method  = "POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("return"):
                return True, "SMS sent"
            return False, result.get("message", "Unknown error")
    except Exception as e:
        return False, str(e)


def _send_sms_phonelink(phone_e164, message):
    """
    Fallback SMS: open sms: URI — works if Windows Phone Link is set up.
    """
    import urllib.parse, webbrowser
    encoded = urllib.parse.quote(message)
    webbrowser.open(f"sms:{phone_e164}?body={encoded}")
    return True, "SMS URI opened (Phone Link)"


# ── Progress / result log window ─────────────────────────────────────────────
def _run_notifications(parent, recipients, cfg, log_widget, done_label):
    """
    Worker function — runs in a background thread.
    recipients: list of dicts with keys: name, phone, amount, date, file_no
    """
    wa_msg_tpl  = cfg.get("whatsapp_msg", _DEFAULT_CONFIG["whatsapp_msg"])
    sms_msg_tpl = cfg.get("sms_msg",      _DEFAULT_CONFIG["sms_msg"])
    company     = cfg.get("company",      "Sandhu Enterprises")
    do_wa       = cfg.get("send_whatsapp", True)
    do_sms      = cfg.get("send_sms",     True)
    api_key     = cfg.get("fast2sms_key", "").strip()
    wa_delay    = int(cfg.get("whatsapp_delay", 15))

    def log(text, tag="info"):
        try:
            log_widget.config(state="normal")
            log_widget.insert("end", text + "\n", tag)
            log_widget.see("end")
            log_widget.config(state="disabled")
        except Exception:
            pass

    total = len(recipients)
    for idx, r in enumerate(recipients, 1):
        name     = r.get("name",    "Customer")
        phone    = r.get("phone",   "")
        amount   = r.get("amount",  "")
        date_str = r.get("date",    "")
        file_no  = r.get("file_no", "")

        phone_e164 = _clean_phone(phone)

        log(f"\n[{idx}/{total}]  {name}  —  {phone}  —  ₹{amount}")

        if not phone_e164:
            log(f"  ⚠  Invalid phone number: '{phone}' — skipped", "warn")
            continue

        wa_msg  = _format_msg(wa_msg_tpl,  name, amount, date_str, file_no, company)
        sms_msg = _format_msg(sms_msg_tpl, name, amount, date_str, file_no, company)

        # ── WhatsApp ────────────────────────────────────────────────────────
        if do_wa:
            log(f"  📲  Sending WhatsApp to {phone_e164}…", "info")
            ok, msg = _send_whatsapp_one(phone_e164, wa_msg, delay=wa_delay)
            if ok:
                log(f"  ✅  WhatsApp OK — {msg}", "ok")
            else:
                log(f"  ❌  WhatsApp FAILED — {msg}", "err")

        # ── SMS ──────────────────────────────────────────────────────────────
        if do_sms:
            phone_10 = phone_e164.lstrip('+')[2:]   # strip +91
            if api_key:
                log(f"  📩  Sending SMS via Fast2SMS…", "info")
                ok, msg = _send_sms_fast2sms(phone_10, sms_msg, api_key)
            else:
                log(f"  📩  Opening SMS via Phone Link…", "info")
                ok, msg = _send_sms_phonelink(phone_e164, sms_msg)
            if ok:
                log(f"  ✅  SMS OK — {msg}", "ok")
            else:
                log(f"  ❌  SMS FAILED — {msg}", "err")

        # Small pause between contacts so WhatsApp Web doesn't rate-limit
        if do_wa and idx < total:
            log(f"  ⏳  Waiting {wa_delay}s before next…", "dim")
            _time.sleep(wa_delay)

    log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log(f"✅  Done — {total} contact(s) processed.", "ok")
    try:
        done_label.config(text="✅  All done!", fg=ACCENT2)
    except Exception:
        pass


# ── Main notification window ──────────────────────────────────────────────────
def notification_window(parent, recipients=None):
    """
    Full notification centre.
    recipients: list of dicts {name, phone, amount, date, file_no}
                If None, auto-loads all overdue cases from DB.
    """
    import datetime as _dt

    cfg = _load_notif_config()

    # ── Auto-load if not passed ───────────────────────────────────────────
    if recipients is None:
        recipients = []
        # Installment overdue
        try:
            for r in db.get_due_payments():
                recipients.append({
                    "name":    fmt_customer(r.get("customer",""), r.get("relation","")),
                    "phone":   r.get("mobile_no",""),
                    "amount":  r.get("total_overdue",""),
                    "date":    to_display_date(r.get("date","")),
                    "file_no": r.get("file_no",""),
                    "type":    "Installment",
                })
        except Exception:
            pass
        # Credit overdue
        try:
            for r in db.get_due_report():
                recipients.append({
                    "name":    fmt_customer(r.get("customer",""), r.get("relation","")),
                    "phone":   r.get("mobile_no",""),
                    "amount":  r.get("balance",""),
                    "date":    to_display_date(r.get("next_due_date","")),
                    "file_no": r.get("file_no",""),
                    "type":    "Credit",
                })
        except Exception:
            pass

    win = tk.Toplevel(parent)
    win.title("Notification Centre — Sandhu Enterprises")
    win.state("zoomed")
    win.configure(bg=BG)
    apply_dark_titlebar(win)
    build_style()

    # ── Sidebar accent ────────────────────────────────────────────────────
    tk.Frame(win, bg="#10b981", width=4).pack(side=tk.LEFT, fill=tk.Y)
    body = tk.Frame(win, bg=BG)
    body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ── Top bar ───────────────────────────────────────────────────────────
    topbar = tk.Frame(body, bg=BG_PANEL, pady=14, padx=20)
    topbar.pack(fill=tk.X)
    tk.Label(topbar, text="🔔  NOTIFICATION CENTRE",
             font=(FONT_UI, 19, "bold"), fg=TEXT, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Label(topbar, text="  WhatsApp & SMS due-date reminders",
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)
    tk.Button(topbar, text="✕  Close", command=win.destroy,
              font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL,
              activeforeground=ACCENT_RED, activebackground=BG_PANEL,
              relief="flat", bd=0, cursor="hand2", padx=12).pack(side=tk.RIGHT)
    tk.Frame(body, bg=BORDER, height=1).pack(fill=tk.X)

    # ── Two-column layout ─────────────────────────────────────────────────
    cols = tk.Frame(body, bg=BG)
    cols.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
    cols.grid_columnconfigure(0, weight=5)
    cols.grid_columnconfigure(1, weight=4)
    cols.grid_rowconfigure(0, weight=1)

    # ════════════════════════════════════════════════════════════════════
    # LEFT — Recipients list
    # ════════════════════════════════════════════════════════════════════
    left = tk.Frame(cols, bg=BG_CARD,
                    highlightbackground=BORDER, highlightthickness=1)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    left.grid_rowconfigure(1, weight=1)
    left.grid_columnconfigure(0, weight=1)

    lhdr = tk.Frame(left, bg=BG_CARD, padx=14, pady=10)
    lhdr.grid(row=0, column=0, sticky="ew")
    tk.Label(lhdr, text="📋  Recipients — Overdue Cases",
             font=(FONT_UI, 13, "bold"), fg=TEXT, bg=BG_CARD).pack(side=tk.LEFT)
    count_lbl = tk.Label(lhdr, text=f"  {len(recipients)}  ",
                         font=(FONT_UI, 11, "bold"), fg=ACCENT2,
                         bg="#1b2e4a", padx=6, pady=2)
    count_lbl.pack(side=tk.LEFT, padx=6)

    # Select All / None
    sel_all_var = tk.BooleanVar(value=True)
    chk_frame = tk.Frame(lhdr, bg=BG_CARD)
    chk_frame.pack(side=tk.RIGHT)

    rec_cols   = ("sel", "name", "phone", "amount", "date", "type", "file_no")
    rec_heads  = ("✓", "Customer", "Mobile", "Due Amt", "Due Date", "Type", "File")
    rec_widths = (30, 200, 120, 100, 95, 90, 75)

    rec_wrap = tk.Frame(left, bg=BORDER, bd=1)
    rec_wrap.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,8))
    rec_wrap.grid_rowconfigure(0, weight=1)
    rec_wrap.grid_columnconfigure(0, weight=1)

    rec_tree = ttk.Treeview(rec_wrap, columns=rec_cols, show="headings",
                             style="T.Treeview")
    for col, head, w in zip(rec_cols, rec_heads, rec_widths):
        rec_tree.heading(col, text=head)
        rec_tree.column(col, width=w, minwidth=30,
                        anchor="center" if col in ("sel","amount","type") else "w")
    rec_tree.tag_configure("even",    background=BG_CARD)
    rec_tree.tag_configure("odd",     background=BG_ROW_ALT)
    rec_tree.tag_configure("nophone", background="#fff0f0", foreground="#9ca3af")

    vsb_r = tk.Scrollbar(rec_wrap, orient="vertical", command=rec_tree.yview)
    rec_tree.configure(yscrollcommand=vsb_r.set)
    vsb_r.grid(row=0, column=1, sticky="ns")
    rec_tree.grid(row=0, column=0, sticky="nsew")

    # Track selection per row
    _selected = {}

    def _populate_recipients():
        for item in rec_tree.get_children():
            rec_tree.delete(item)
        _selected.clear()
        for i, r in enumerate(recipients):
            sel_mark = "☑" if _selected.get(i, True) else "☐"
            phone_ok = bool(_clean_phone(r.get("phone","")))
            tag = ("nophone",) if not phone_ok else (("even" if i%2==0 else "odd"),)
            iid = rec_tree.insert("", "end", iid=str(i), tags=tag, values=(
                sel_mark,
                r.get("name",""),
                r.get("phone",""),
                f"₹ {float(r.get('amount') or 0):,.2f}",
                r.get("date",""),
                r.get("type",""),
                r.get("file_no",""),
            ))
            _selected[i] = phone_ok   # deselect invalid phones by default

        _refresh_sel_marks()
        count_lbl.config(text=f"  {len(recipients)}  ")

    def _refresh_sel_marks():
        for i in range(len(recipients)):
            try:
                mark = "☑" if _selected.get(i, True) else "☐"
                vals = list(rec_tree.item(str(i), "values"))
                if vals:
                    vals[0] = mark
                    rec_tree.item(str(i), values=vals)
            except Exception:
                pass

    def _toggle_row(e):
        item = rec_tree.identify_row(e.y)
        if not item:
            return
        try:
            idx = int(item)
            _selected[idx] = not _selected.get(idx, True)
            _refresh_sel_marks()
        except Exception:
            pass

    rec_tree.bind("<Button-1>", _toggle_row)

    def _select_all():
        for i in range(len(recipients)):
            phone_ok = bool(_clean_phone(recipients[i].get("phone","")))
            _selected[i] = phone_ok
        _refresh_sel_marks()

    def _select_none():
        for i in range(len(recipients)):
            _selected[i] = False
        _refresh_sel_marks()

    btn_row_l = tk.Frame(left, bg=BG_CARD, padx=8, pady=6)
    btn_row_l.grid(row=2, column=0, sticky="ew")
    tk.Button(btn_row_l, text="☑ Select All", font=(FONT_UI,11), fg=TEXT,
              bg=BG_PANEL, relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
              command=_select_all).pack(side=tk.LEFT)
    tk.Button(btn_row_l, text="☐ Select None", font=(FONT_UI,11), fg=TEXT,
              bg=BG_PANEL, relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
              command=_select_none).pack(side=tk.LEFT, padx=4)
    tk.Label(btn_row_l, text="Click any row to toggle selection",
             font=(FONT_UI,10), fg=TEXT_DIM, bg=BG_CARD).pack(side=tk.RIGHT, padx=8)

    _populate_recipients()

    # ════════════════════════════════════════════════════════════════════
    # RIGHT — Settings + Send
    # ════════════════════════════════════════════════════════════════════
    right_col = tk.Frame(cols, bg=BG)
    right_col.grid(row=0, column=1, sticky="nsew")
    right_col.grid_rowconfigure(3, weight=1)
    right_col.grid_columnconfigure(0, weight=1)

    # ── Channel toggles ───────────────────────────────────────────────
    ch_card = tk.Frame(right_col, bg=BG_CARD,
                       highlightbackground=BORDER, highlightthickness=1,
                       padx=14, pady=12)
    ch_card.grid(row=0, column=0, sticky="ew", pady=(0,8))
    tk.Label(ch_card, text="📡  Channels", font=(FONT_UI,13,"bold"),
             fg=TEXT, bg=BG_CARD).pack(anchor="w")
    tk.Frame(ch_card, bg=BORDER, height=1).pack(fill=tk.X, pady=(6,8))

    wa_var  = tk.BooleanVar(value=cfg.get("send_whatsapp", True))
    sms_var = tk.BooleanVar(value=cfg.get("send_sms", True))

    ch_row = tk.Frame(ch_card, bg=BG_CARD)
    ch_row.pack(fill=tk.X)
    tk.Checkbutton(ch_row, text="📲  WhatsApp (pywhatkit)",
                   variable=wa_var, font=(FONT_UI,12),
                   fg=TEXT, bg=BG_CARD, selectcolor=BG_INPUT,
                   activebackground=BG_CARD).pack(side=tk.LEFT)
    tk.Checkbutton(ch_row, text="📩  SMS",
                   variable=sms_var, font=(FONT_UI,12),
                   fg=TEXT, bg=BG_CARD, selectcolor=BG_INPUT,
                   activebackground=BG_CARD).pack(side=tk.LEFT, padx=16)

    # Fast2SMS key
    api_frame = tk.Frame(ch_card, bg=BG_CARD)
    api_frame.pack(fill=tk.X, pady=(8,0))
    tk.Label(api_frame, text="Fast2SMS API Key (optional, for direct SMS):",
             font=(FONT_UI,11), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
    api_var = tk.StringVar(value=cfg.get("fast2sms_key",""))
    api_entry = make_entry(api_frame, width=38)
    api_entry.insert(0, cfg.get("fast2sms_key",""))
    api_entry.pack(fill=tk.X, ipady=5, pady=(4,0))
    tk.Label(api_frame,
             text="Leave blank to use Windows Phone Link for SMS",
             font=(FONT_UI,10), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", pady=(2,0))

    # ── Message templates ─────────────────────────────────────────────
    msg_card = tk.Frame(right_col, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=14, pady=12)
    msg_card.grid(row=1, column=0, sticky="ew", pady=(0,8))
    tk.Label(msg_card, text="✏️  Message Templates",
             font=(FONT_UI,13,"bold"), fg=TEXT, bg=BG_CARD).pack(anchor="w")
    tk.Label(msg_card,
             text="Variables: {name}  {file_no}  {amount}  {date}  {company}",
             font=(FONT_UI,10), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", pady=(2,6))
    tk.Frame(msg_card, bg=BORDER, height=1).pack(fill=tk.X, pady=(0,8))

    tk.Label(msg_card, text="WhatsApp Message:",
             font=(FONT_UI,11,"bold"), fg=TEXT, bg=BG_CARD).pack(anchor="w")
    wa_txt = tk.Text(msg_card, font=(FONT_UI,11), fg=TEXT, bg=BG_INPUT,
                     relief="flat", highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT,
                     height=6, padx=8, pady=6, wrap="word")
    wa_txt.insert("1.0", cfg.get("whatsapp_msg", _DEFAULT_CONFIG["whatsapp_msg"]))
    wa_txt.pack(fill=tk.X, pady=(4,10))

    tk.Label(msg_card, text="SMS Message (keep short):",
             font=(FONT_UI,11,"bold"), fg=TEXT, bg=BG_CARD).pack(anchor="w")
    sms_txt = tk.Text(msg_card, font=(FONT_UI,11), fg=TEXT, bg=BG_INPUT,
                      relief="flat", highlightthickness=1,
                      highlightbackground=BORDER, highlightcolor=ACCENT,
                      height=4, padx=8, pady=6, wrap="word")
    sms_txt.insert("1.0", cfg.get("sms_msg", _DEFAULT_CONFIG["sms_msg"]))
    sms_txt.pack(fill=tk.X, pady=(4,0))

    company_var = tk.StringVar(value=cfg.get("company","Sandhu Enterprises"))
    delay_var   = tk.StringVar(value=str(cfg.get("whatsapp_delay",15)))
    extra_frame = tk.Frame(msg_card, bg=BG_CARD)
    extra_frame.pack(fill=tk.X, pady=(8,0))
    tk.Label(extra_frame, text="Company Name:", font=(FONT_UI,11), fg=TEXT_DIM, bg=BG_CARD,
             width=14, anchor="w").grid(row=0, column=0, sticky="w")
    co_e = make_entry(extra_frame, width=20)
    co_e.insert(0, company_var.get())
    co_e.grid(row=0, column=1, sticky="ew", ipady=5, padx=(4,16))
    tk.Label(extra_frame, text="WA Delay (s):", font=(FONT_UI,11), fg=TEXT_DIM, bg=BG_CARD,
             width=12, anchor="w").grid(row=0, column=2, sticky="w")
    dl_e = make_entry(extra_frame, width=6)
    dl_e.insert(0, delay_var.get())
    dl_e.grid(row=0, column=3, sticky="ew", ipady=5, padx=(4,0))
    extra_frame.grid_columnconfigure(1, weight=1)

    def _save_cfg():
        cfg["send_whatsapp"]   = wa_var.get()
        cfg["send_sms"]        = sms_var.get()
        cfg["fast2sms_key"]    = api_entry.get().strip()
        cfg["whatsapp_msg"]    = wa_txt.get("1.0","end-1c").strip()
        cfg["sms_msg"]         = sms_txt.get("1.0","end-1c").strip()
        cfg["company"]         = co_e.get().strip() or "Sandhu Enterprises"
        try:
            cfg["whatsapp_delay"] = int(dl_e.get().strip() or 15)
        except Exception:
            cfg["whatsapp_delay"] = 15
        _save_notif_config(cfg)
        return cfg

    tk.Button(msg_card, text="💾  Save Settings",
              font=(FONT_UI,11,"bold"), fg=BG, bg=ACCENT,
              relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
              command=lambda: (_save_cfg(),
                               messagebox.showinfo("Saved", "Settings saved!", parent=win))
              ).pack(anchor="e", pady=(8,0))

    # ── Log window ────────────────────────────────────────────────────
    log_card = tk.Frame(right_col, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1,
                        padx=14, pady=12)
    log_card.grid(row=3, column=0, sticky="nsew")
    log_card.grid_rowconfigure(1, weight=1)
    log_card.grid_columnconfigure(0, weight=1)
    tk.Label(log_card, text="📜  Send Log", font=(FONT_UI,13,"bold"),
             fg=TEXT, bg=BG_CARD).grid(row=0, column=0, sticky="w")

    log_txt = tk.Text(log_card, font=(FONT_MONO,10), fg=TEXT, bg="#0f172a",
                      relief="flat", highlightthickness=0,
                      padx=8, pady=6, state="disabled", wrap="word")
    log_txt.tag_config("ok",   foreground="#34d399")
    log_txt.tag_config("err",  foreground="#f87171")
    log_txt.tag_config("warn", foreground="#fbbf24")
    log_txt.tag_config("dim",  foreground="#6b7280")
    log_txt.tag_config("info", foreground="#e2e8f0")
    log_sb = tk.Scrollbar(log_card, orient="vertical", command=log_txt.yview)
    log_txt.configure(yscrollcommand=log_sb.set)
    log_sb.grid(row=1, column=1, sticky="ns")
    log_txt.grid(row=1, column=0, sticky="nsew", pady=(6,0))

    done_lbl = tk.Label(log_card, text="", font=(FONT_UI,12,"bold"),
                        fg=ACCENT2, bg=BG_CARD)
    done_lbl.grid(row=2, column=0, sticky="w", pady=(4,0))

    # ── Send button ───────────────────────────────────────────────────
    send_frame = tk.Frame(right_col, bg=BG, pady=6)
    send_frame.grid(row=2, column=0, sticky="ew")

    def _do_send():
        live_cfg = _save_cfg()
        selected_recipients = [recipients[i]
                                for i in range(len(recipients))
                                if _selected.get(i, True)]
        if not selected_recipients:
            messagebox.showwarning("No Selection",
                                   "No recipients selected.", parent=win)
            return
        if not live_cfg.get("send_whatsapp") and not live_cfg.get("send_sms"):
            messagebox.showwarning("No Channel",
                                   "Enable at least WhatsApp or SMS.", parent=win)
            return

        confirm_msg = (
            f"Send messages to {len(selected_recipients)} recipient(s)?\n\n"
            f"• WhatsApp: {'Yes' if live_cfg['send_whatsapp'] else 'No'}\n"
            f"• SMS: {'Yes' if live_cfg['send_sms'] else 'No'}\n\n"
            "Keep the app open while sending."
        )
        if not messagebox.askyesno("Confirm Send", confirm_msg, parent=win):
            return

        send_btn.config(state="disabled", text="⏳  Sending…")
        done_lbl.config(text="Sending…", fg=ACCENT_YEL)

        # Run in background thread so UI stays responsive
        t = threading.Thread(
            target=_run_notifications,
            args=(win, selected_recipients, live_cfg, log_txt, done_lbl),
            daemon=True,
        )
        t.start()

        def _watch():
            if t.is_alive():
                win.after(500, _watch)
            else:
                try:
                    send_btn.config(state="normal", text="🚀  Send Notifications")
                except Exception:
                    pass
        win.after(500, _watch)

    send_btn = tk.Button(send_frame, text="🚀  Send Notifications",
                         command=_do_send,
                         font=(FONT_UI,14,"bold"), fg=BG, bg="#10b981",
                         activeforeground=BG, activebackground="#059669",
                         relief="flat", bd=0, padx=24, pady=12,
                         cursor="hand2")
    send_btn.pack(fill=tk.X)

    win.bind("<Escape>", lambda e: win.destroy())


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
    tk.Label(hi, text="Financial Tracking System", font=(FONT_UI, 13),
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
        tk.Label(sf3, text=lbl, font=(FONT_UI, 11), fg=TEXT_DIM, bg=BG_CARD).pack()
        tk.Frame(ss, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

    tk.Frame(main_area, bg=BORDER, height=1).pack(fill=tk.X)

    center = tk.Frame(main_area, bg=BG)
    center.pack(fill=tk.BOTH, expand=True)
    nav = tk.Frame(center, bg=BG)
    nav.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(nav, text="Navigation", font=(FONT_UI, 12, "bold"),
             fg=TEXT_DIM, bg=BG).pack(pady=(0, 20))

    for label, func, color in [
        ("📁  Installment Cases",   installment_window,    ACCENT),
        ("💰  Due Payments",        due_payments_window,   ACCENT2),
        ("🔴  Credit Cases",        credit_cases_window,   ACCENT_RED),
        ("📊  Due Report",          due_report_window,     ACCENT_YEL),
        ("🏘️  Village Setup",       village_setup_window,  ACCENT_PUR),
        ("📈  Overview",            overview_window,       "#36bfd9"),
        ("🔔  Notifications",       notification_window,   "#10b981"),
    ]:
        rf2 = tk.Frame(nav, bg=BG)
        rf2.pack(fill=tk.X, pady=5)
        btn2 = tk.Button(rf2, text=label, command=lambda f=func: f(root),
                         font=(FONT_UI, 13, "bold"), fg=TEXT, bg=BG_CARD,
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
             font=(FONT_UI, 12), fg=TEXT_DIM, bg=BG_PANEL).pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    main()