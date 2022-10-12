
__version__ = '0.0.1'

from frappe import model
model.data_field_options = (
    'Email',
    'Name',
    'Phone',
    'URL',
    'Barcode',
    'Hijri Date'
)

mosyr_accounts = {
    "LoanType":[
        {
            "fieldname":"loan_account",
            "account":{
                "account_name":"Loan Account",
                "parent_account":"Loans and Advances (Assets)",
                "root_type":"Asset"
            },
            "for_fields":[
                {
                    "fieldname":"loan_account",
                    "doctype":"Loan Type"
                }
            ]
        },
        {
			"fieldname":"disbursement_account",
            "account":{
                "account_name":"Loan Disbursement",
                "parent_account":"Loans and Advances (Assets)",
                "root_type":"Asset"
            },
            "for_fields":[
                {
                    "fieldname":"disbursement_account",
                    "doctype":"Loan Type"
                }
            ]
        },
        {
			"fieldname":"payment_account",
            "account":{
                "account_name":"Loan Repayment",
                "parent_account":"Loans and Advances (Assets)",
                "root_type":"Asset"
            },
            "for_fields":[
                {
                    "fieldname":"payment_account",
                    "doctype":"Loan Type"
                }
            ]
        },
        {
			"fieldname":"interest_income_account",
            "account":{
                "account_name":"Loan Inreset",
                "parent_account":"Income",
                "root_type":"Income"
            },
            "for_fields":[
                {
                    "fieldname":"interest_income_account",
                    "doctype":"Loan Type"
                }
            ]
        },
        {
			"fieldname":"penalty_income_account",
            "account":{
                "account_name":"Loan Penalty",
                "parent_account":"Income",
                "root_type":"Income"
            },
            "for_fields":[
                {
                    "fieldname":"penalty_income_account",
                    "doctype":"Loan Type"
                }
            ]
        }
    ],
    "LoanWriteOff":[
        {
            "fieldname":"write_off_account",
            "account":{
                "account_name":"Write Off",
                "parent_account":"Expenses",
                "root_type":"Expense"
            },
            "for_fields":[
                {
                    "fieldname":"write_off_account",
                    "doctype":"Loan Write Off"
                }
            ]
        }
    ],
    "EmployeeAdvance":[
        {
            "fieldname":"advance_account",
            "account":{
                "account_name":"Employee Advances",
                "parent_account":"Loans and Advances (Assets)",
                "root_type":"Asset",
                "check_company":1,
                "check_company_field":"default_employee_advance_account"
            },
            "for_fields":[
                {
                    "fieldname":"advance_account",
                    "doctype":"Employee Advance"
                }
            ]
        }
    ],
    "ExpenseClaim":[
        {
            "fieldname":"payable_account",
            "account":{
                "account_name":"Expense Claim",
                "parent_account":"Accounts Payable",
                "root_type":"Liability",
                "account_type":"Payable",
                "check_company":0
            },
            "for_fields":[
                {
                    "fieldname":"payable_account",
                    "doctype":"Expense Claim"
                }
            ]
        }
    ],
    "PayrollEntry":[
        {
            "fieldname":"payment_account",
            "account":{
                "account_name":"Payroll Payable",
                "parent_account":"Accounts Payable",
                "root_type":"Liability",
                "account_type":"Payable",
                "check_company":0
            },
            "for_fields":[
                {
                    "fieldname":"payment_account",
                    "doctype":"Payroll Entry"
                }
            ]
        },
        {
            "fieldname":"payroll_payable_account",
            "account":{
                "account_name":"Payroll Payable Account",
                "parent_account":"Accounts Payable",
                "root_type":"Liability",
                "account_type":"Payable",
                "check_company":0
            },
            "for_fields":[
                {
                    "fieldname":"payroll_payable_account",
                    "doctype":"Payroll Entry"
                }
            ]
        }
    ]
}

mosyr_mode_payments = {
    "LoanType": {
        "type": "Bank",
        "title": "Loan Payment",
		"for_fields":[
			{
				"fieldname":"mode_of_payment",
				"doctype":"Loan Type"
			}
		]
    },
    "EmployeeAdvance": {
        "type": "Bank",
        "title": "Advance Payment",
		"for_fields":[
			{
				"fieldname":"mode_of_payment",
				"doctype":"Employee Advance"
			}
		]
    },
    "SalaryStructure": {
        "type": "Bank",
        "title": "Salary Payment",
		"for_fields":[
			{
				"fieldname":"mode_of_payment",
				"doctype":"Salary Structure"
			}
		]
    }
}