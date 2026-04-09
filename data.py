"""Updated mock data with uniform schema: file_no, date, customer, village, mobile_no, finance_amt, balance, id."""

COMMON_COLUMNS = ['file_no', 'date', 'customer', 'village', 'mobile_no', 'finance_amt', 'balance', 'id']

# Installment Cases
INSTALLMENT_CASES = [
    {'file_no': 'F001', 'date': '2024-01-01', 'customer': 'Ram s/o Shyam', 'village': 'Village A', 'mobile_no': '1234567890', 'finance_amt': 10000, 'balance': 8000, 'id': 1},
    {'file_no': 'F002', 'date': '2024-02-01', 'customer': 'Shyam s/o Gopal', 'village': 'Village B', 'mobile_no': '0987654321', 'finance_amt': 15000, 'balance': 13500, 'id': 2},
]

# Due Payments
DUE_PAYMENTS = [
    {'file_no': 'F003', 'date': '2024-03-15', 'customer': 'Gopal s/o Madhav', 'village': 'Village A', 'mobile_no': '1122334455', 'finance_amt': 5000, 'balance': 5000, 'id': 3},
    {'file_no': 'F004', 'date': '2024-04-10', 'customer': 'Madhav s/o Krishna', 'village': 'Village C', 'mobile_no': '5566778899', 'finance_amt': 3000, 'balance': 2800, 'id': 4},
]

# Credit Cases
CREDIT_CASES = [
    {'file_no': 'F005', 'date': '2024-01-20', 'customer': 'Krishna s/o Balram', 'village': 'Village B', 'mobile_no': '9988776655', 'finance_amt': 20000, 'balance': 5000, 'id': 5},
    {'file_no': 'F006', 'date': '2024-02-20', 'customer': 'Balram s/o Arjun', 'village': 'Village D', 'mobile_no': '4433221100', 'finance_amt': 10000, 'balance': 2000, 'id': 6},
]

# Due Payments Report
DUE_PAYMENTS_REPORT = [
    {'file_no': 'F007', 'date': '2024-05-01', 'customer': 'Arjun s/o Yudhishthir', 'village': 'Village A', 'mobile_no': '7778889990', 'finance_amt': 7000, 'balance': 7000, 'id': 7},
    {'file_no': 'F008', 'date': '2024-05-15', 'customer': 'Yudhishthir s/o Pandu', 'village': 'Village E', 'mobile_no': '1112223334', 'finance_amt': 4000, 'balance': 3500, 'id': 8},
]

# Setup Village (adapted)
VILLAGE_SETUP = [
    {'file_no': 'V001', 'date': '2024-06-01', 'customer': 'Village Manager A', 'village': 'Village A', 'mobile_no': '1234509876', 'finance_amt': 0, 'balance': 0, 'id': 101},
    {'file_no': 'V002', 'date': '2024-06-02', 'customer': 'Village Manager B', 'village': 'Village B', 'mobile_no': '5432109876', 'finance_amt': 0, 'balance': 0, 'id': 102},
]

# Overview (unchanged)
OVERVIEW = {
    'total_installments': 2,
    'total_due': 36800,
    'credit_active': 2,
    'villages': 2,
}

