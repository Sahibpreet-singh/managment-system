"""
database.py  —  MySQL backend for Sandhu Enterprises Financial Tracking System

Connection config: edit DB_CONFIG below to match your MySQL setup.

Tables (auto-created in sandhu_db):
  installment_cases     — instalment-based finance cases
  installment_payments  — per-instalment chart rows for each case
  credit_cases          — one-time credit / lump-sum cases
  credit_payment_rows   — sale/receipt entry rows inside a credit case
  villages              — village directory
"""

import mysql.connector
from mysql.connector import Error

# ── Connection config — edit these if needed ──────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'root',
    'password': '1234',
    'database': 'sandhu_db',
    'autocommit': False,
}


def get_conn():
    """Return a fresh MySQL connection with sandhu_db selected."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create the database and all tables if they don't exist yet."""
    cfg_no_db = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
    cfg_no_db['autocommit'] = True
    conn = mysql.connector.connect(**cfg_no_db)
    c = conn.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS sandhu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    c.execute("USE sandhu_db")

    # ✅ Installment Cases
    c.execute("""
        CREATE TABLE IF NOT EXISTS installment_cases (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            file_no         VARCHAR(50),
            date            DATE,
            customer        VARCHAR(200),
            relation        VARCHAR(200),
            address1        VARCHAR(300),
            address2        VARCHAR(300),
            mobile_no       VARCHAR(30),
            remarks_cust    TEXT,
            village         VARCHAR(100),
            item            VARCHAR(200),
            brand           VARCHAR(100),
            model           VARCHAR(100),
            srno            VARCHAR(100),
            invoice_no      VARCHAR(100),
            amount          DECIMAL(15,2) DEFAULT 0,
            advance         DECIMAL(15,2) DEFAULT 0,
            amount_financed DECIMAL(15,2) DEFAULT 0,
            no_instalments  INT DEFAULT 0,
            instalment_amt  DECIMAL(15,2) DEFAULT 0,
            final_amount    DECIMAL(15,2) DEFAULT 0,
            finance_amt     DECIMAL(15,2) DEFAULT 0,
            balance         DECIMAL(15,2) DEFAULT 0,
            g1_name         VARCHAR(200),
            g1_relation     VARCHAR(200),
            g1_address      VARCHAR(300),
            g1_village      VARCHAR(100),
            g1_mobile       VARCHAR(30),
            g1_remarks      TEXT,
            g2_name         VARCHAR(200),
            g2_relation     VARCHAR(200),
            g2_address      VARCHAR(300),
            g2_village      VARCHAR(100),
            g2_mobile       VARCHAR(30),
            g2_remarks      TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # ✅ Installment Payments (MOST IMPORTANT)
    c.execute("""
        CREATE TABLE IF NOT EXISTS installment_payments (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            case_id     INT NOT NULL,
            inst_no     INT,
            inst_date   DATE,
            recv_date   DATE,
            receipt_no  VARCHAR(100),
            amount      DECIMAL(15,2) DEFAULT 0,
            balance     DECIMAL(15,2) DEFAULT 0,
            FOREIGN KEY (case_id) REFERENCES installment_cases(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # ✅ Credit Cases
    c.execute("""
        CREATE TABLE IF NOT EXISTS credit_cases (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            file_no         VARCHAR(50),
            date            DATE,
            customer        VARCHAR(200),
            relation        VARCHAR(200),
            address         VARCHAR(300),
            village         VARCHAR(100),
            mobile_no       VARCHAR(30),
            remarks         TEXT,
            amount          DECIMAL(15,2) DEFAULT 0,
            finance_amt     DECIMAL(15,2) DEFAULT 0,
            total_receipt   DECIMAL(15,2) DEFAULT 0,
            balance         DECIMAL(15,2) DEFAULT 0,
            next_due_date   DATE,
            g1_name         VARCHAR(200),
            g1_relation     VARCHAR(200),
            g1_address      VARCHAR(300),
            g1_village      VARCHAR(100),
            g1_mobile       VARCHAR(30),
            g1_remarks      TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # ✅ Credit Payment Rows
    c.execute("""
        CREATE TABLE IF NOT EXISTS credit_payment_rows (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            case_id     INT NOT NULL,
            description TEXT,
            date        DATE,
            sale_amt    DECIMAL(15,2) DEFAULT 0,
            receipt     DECIMAL(15,2) DEFAULT 0,
            FOREIGN KEY (case_id) REFERENCES credit_cases(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # ✅ Villages
    c.execute("""
        CREATE TABLE IF NOT EXISTS villages (
            id      INT AUTO_INCREMENT PRIMARY KEY,
            name    VARCHAR(100) UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    c.close()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# INSTALLMENT CASES
# ═══════════════════════════════════════════════════════════════════════════════

def get_all_installment_cases():
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM installment_cases ORDER BY id")
    rows = c.fetchall()
    c.close(); conn.close()
    result = []
    for r in rows:
        d = _stringify(r)
        # provide unified keys so detail form always finds 'address' and 'remarks'
        d['address'] = (d.get('address1', '') + ' ' + d.get('address2', '')).strip()
        d['remarks'] = d.get('remarks_cust', '')
        result.append(d)
    return result


def get_installment_case(case_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM installment_cases WHERE id=%s", (case_id,))
    row = c.fetchone()
    c.close(); conn.close()
    return _stringify(row) if row else None


def save_installment_case(data):
    conn = get_conn()
    c = conn.cursor()

    text_fields = [
        'file_no','date','customer','relation','address1','address2',
        'mobile_no','remarks_cust','village','item','brand','model',
        'srno','invoice_no',
        'g1_name','g1_relation','g1_address','g1_village','g1_mobile','g1_remarks',
        'g2_name','g2_relation','g2_address','g2_village','g2_mobile','g2_remarks',
    ]
    num_fields = [
        'amount','advance','amount_financed','instalment_amt',
        'final_amount','finance_amt','balance',
    ]
    int_fields = ['no_instalments']

    all_fields = (text_fields + num_fields + int_fields)

    def val(f):
        if f in num_fields:  return _flt(data.get(f, 0))
        if f in int_fields:
            try: return int(str(data.get(f, 0) or 0))
            except: return 0
        if f == 'date':      return _date(data, 'date')
        # map unified 'address' → address1, 'remarks' → remarks_cust
        if f == 'address1':
            return _v(data, 'address1') or _v(data, 'address')
        if f == 'remarks_cust':
            return _v(data, 'remarks_cust') or _v(data, 'remarks')
        # ✅ FIX — keep finance_amt and amount_financed in sync
        if f == 'finance_amt':
            return _flt(data.get('finance_amt') or data.get('amount_financed') or 0)
        if f == 'amount_financed':
            return _flt(data.get('amount_financed') or data.get('finance_amt') or 0)
        return _v(data, f)

    case_id = data.get('id')
    if case_id:
        sets = ", ".join(f"{f}=%s" for f in all_fields)
        vals = [val(f) for f in all_fields] + [case_id]
        c.execute(f"UPDATE installment_cases SET {sets} WHERE id=%s", vals)
    else:
        cols = ", ".join(all_fields)
        phs  = ", ".join("%s" for _ in all_fields)
        vals = [val(f) for f in all_fields]
        c.execute(f"INSERT INTO installment_cases ({cols}) VALUES ({phs})", vals)
        case_id = c.lastrowid

    conn.commit()
    c.close(); conn.close()
    return case_id


def delete_installment_case(case_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM installment_cases WHERE id=%s", (case_id,))
    conn.commit()
    c.close(); conn.close()


def get_installment_payments(case_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM installment_payments WHERE case_id=%s ORDER BY inst_no", (case_id,))
    rows = c.fetchall()
    c.close(); conn.close()
    return [_stringify(r) for r in rows]

from datetime import datetime

def to_mysql_date(d):
    if not d or str(d).strip() == "":
        return None

    formats = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(d).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None

def save_installment_payments(case_id, rows):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM installment_payments WHERE case_id=%s", (case_id,))
    for r in rows:
        c.execute("""
            INSERT INTO installment_payments
                (case_id, inst_no, inst_date, recv_date, receipt_no, amount, balance)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (case_id,
              r.get('inst_no', 0),
              to_mysql_date(r.get('inst_date')),
              to_mysql_date(r.get('recv_date')),
              r.get('receipt_no', ''),
              _flt(r.get('amount', 0)),
              _flt(r.get('balance', 0))))

    total_recv = sum(_flt(r.get('amount', 0)) for r in rows if to_mysql_date(r.get('recv_date')))

    # ✅ FIX — use whichever finance field is actually filled
    c.execute("""
        UPDATE installment_cases
        SET balance = COALESCE(NULLIF(amount_financed, 0), finance_amt, 0) - %s
        WHERE id = %s
    """, (total_recv, case_id))

    conn.commit()
    c.close(); conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# CREDIT CASES
# ═══════════════════════════════════════════════════════════════════════════════

def _get_credit_rows(conn, case_id):
    c = conn.cursor()
    c.execute(
        "SELECT description, date, sale_amt, receipt FROM credit_payment_rows WHERE case_id=%s ORDER BY id",
        (case_id,))
    rows = c.fetchall()
    c.close()
    return [tuple('' if v is None else str(v) for v in row) for row in rows]


def get_all_credit_cases():
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM credit_cases ORDER BY id")
    rows = c.fetchall()
    result = []
    for r in rows:
        d = _stringify(r)
        d['payment_rows'] = _get_credit_rows(conn, d['id'])
        result.append(d)
    c.close(); conn.close()
    return result


def get_credit_case(case_id):
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM credit_cases WHERE id=%s", (case_id,))
    row = c.fetchone()
    if not row:
        c.close(); conn.close()
        return None
    d = _stringify(row)
    d['payment_rows'] = _get_credit_rows(conn, case_id)
    c.close(); conn.close()
    return d


def save_credit_case(data):
    conn = get_conn()
    c = conn.cursor()

    text_fields = [
        'file_no','date','customer','relation','address','village',
        'mobile_no','remarks','next_due_date',
        'g1_name','g1_relation','g1_address','g1_village','g1_mobile','g1_remarks',
    ]
    num_fields = ['amount','finance_amt','total_receipt','balance']
    all_fields = text_fields + num_fields

    DATE_FIELDS = {'date', 'next_due_date'}

    def val(f):
        if f in num_fields:   return _flt(data.get(f, 0))
        if f in DATE_FIELDS:  return _date(data, f)
        return _v(data, f)

    case_id = data.get('id')
    if case_id:
        sets = ", ".join(f"{f}=%s" for f in all_fields)
        vals = [val(f) for f in all_fields] + [case_id]
        c.execute(f"UPDATE credit_cases SET {sets} WHERE id=%s", vals)
    else:
        cols = ", ".join(all_fields)
        phs  = ", ".join("%s" for _ in all_fields)
        vals = [val(f) for f in all_fields]
        c.execute(f"INSERT INTO credit_cases ({cols}) VALUES ({phs})", vals)
        case_id = c.lastrowid
    c.execute("DELETE FROM credit_payment_rows WHERE case_id=%s", (case_id,))
    for row in data.get('payment_rows', []):
        raw_date = row[1] if len(row) > 1 else ''
        row_date = None if not raw_date or str(raw_date).strip() == '' else str(raw_date)
        c.execute("""
            INSERT INTO credit_payment_rows (case_id, description, date, sale_amt, receipt)
            VALUES (%s,%s,%s,%s,%s)
        """, (case_id,
              row[0] if len(row) > 0 else '',
              row_date,
              _flt(row[2]) if len(row) > 2 else 0,
              _flt(row[3]) if len(row) > 3 else 0))
    conn.commit()
    c.close(); conn.close()
    return case_id


def delete_credit_case(case_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM credit_cases WHERE id=%s", (case_id,))
    conn.commit()
    c.close(); conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# DUE REPORT & DUE PAYMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_due_report():
    """Due Report — ALL credit cases with any balance remaining."""
    conn = get_conn()
    c = conn.cursor(dictionary=True)
    c.execute("""
        SELECT id, file_no, date, customer, relation, village, mobile_no,
               finance_amt, balance, next_due_date
        FROM credit_cases
        WHERE balance > 0
        ORDER BY balance DESC
    """)
    rows = c.fetchall()
    c.close(); conn.close()
    return [_stringify(r) for r in rows]


def get_due_payments():
    conn = get_conn()
    c = conn.cursor(dictionary=True)

    c.execute("""
        SELECT
            ic.id,
            ic.file_no,
            ic.date,
            ic.customer,
            ic.relation,
            ic.village,
            ic.mobile_no,
            ic.finance_amt,
            ic.balance,
            ic.instalment_amt,

            -- Count instalments whose due date has passed and have NOT been received
            -- Also counts cases where NO chart rows exist at all (no_rows_case):
            --   if the case has no payment rows, we treat ALL expected instalments as missed.
            CASE
                WHEN COUNT(ip.id) = 0
                    THEN GREATEST(ic.no_instalments, 1)
                ELSE
                    COUNT(
                        CASE
                            WHEN ip.recv_date IS NULL
                             AND ip.inst_date IS NOT NULL
                             AND ip.inst_date < CURDATE()
                            THEN 1
                        END
                    )
            END AS missed_instalments,

            CASE
                WHEN COUNT(ip.id) = 0
                    THEN ic.finance_amt
                ELSE
                    SUM(
                        CASE
                            WHEN ip.recv_date IS NULL
                             AND ip.inst_date IS NOT NULL
                             AND ip.inst_date < CURDATE()
                            THEN
                                CASE
                                    WHEN COALESCE(ip.amount, 0) = 0 THEN ic.instalment_amt
                                    ELSE ip.amount
                                END
                            ELSE 0
                        END
                    )
            END AS total_overdue

        FROM installment_cases ic
        LEFT JOIN installment_payments ip ON ip.case_id = ic.id

        -- Include cases with any positive balance OR finance amount
        WHERE COALESCE(ic.balance, 0) > 0
           OR COALESCE(ic.finance_amt, 0) > 0

        GROUP BY ic.id

        -- Show if at least 1 instalment is missed OR no chart rows saved yet (all missed)
        HAVING missed_instalments > 0

        ORDER BY missed_instalments DESC
    """)

    rows = c.fetchall()
    c.close(); conn.close()

    return [_stringify(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# VILLAGES
# ═══════════════════════════════════════════════════════════════════════════════

def get_villages():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name FROM villages ORDER BY name")
    rows = c.fetchall()
    c.close(); conn.close()
    return [r[0] for r in rows]


def save_village(name):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT IGNORE INTO villages (name) VALUES (%s)", (name,))
        conn.commit()
    except Exception:
        pass
    c.close(); conn.close()


def delete_village(name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM villages WHERE name=%s", (name,))
    conn.commit()
    c.close(); conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# OVERVIEW STATS
# ═══════════════════════════════════════════════════════════════════════════════

def get_overview():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM installment_cases")
    total_inst = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(balance),0) FROM installment_cases WHERE balance>0")
    total_due_i = float(c.fetchone()[0])
    c.execute("SELECT COALESCE(SUM(balance),0) FROM credit_cases WHERE balance>0")
    total_due_c = float(c.fetchone()[0])
    c.execute("SELECT COUNT(*) FROM credit_cases WHERE balance>0")
    credit_act = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM villages")
    villages = c.fetchone()[0]
    c.close(); conn.close()
    return {
        'total_installments': total_inst,
        'total_due':          int(total_due_i + total_due_c),
        'credit_active':      credit_act,
        'villages':           villages,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _v(d, key):
    val = d.get(key, '')
    return '' if val is None else str(val)

def _date(d, key):
    """Return None for blank/missing date values so MySQL DATE columns get NULL, not ''."""
    v = d.get(key, None)
    if not v or str(v).strip() == '':
        return None
    return str(v)

def _flt(v):
    try:
        return float(str(v).replace(',', '') or 0)
    except Exception:
        return 0.0

def _stringify(row):
    """Convert all dict values to strings (handles Decimal, None, int, etc.)."""
    return {k: ('' if v is None else str(v)) for k, v in row.items()}


# ── Auto-initialise on import ─────────────────────────────────────────────────
try:
    init_db()
except Error as e:
    print(f"\n[database.py] MySQL connection error: {e}")
    print("  Make sure MySQL is running and check DB_CONFIG credentials.\n")
    raise
