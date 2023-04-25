
__version__ = '0.0.1'

import frappe
from frappe import model

model.data_field_options = (
    'Email',
    'Name',
    'Phone',
    'URL',
    'Barcode',
    'Hijri Date'
)

update_fields_props = {
    "Company": [
        {
            "field": "create_chart_of_accounts_based_on",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "chart_of_accounts",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "tax_id",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "default_finance_book",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "default_selling_terms",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "default_buying_terms",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "default_warehouse_for_sales_return",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "default_in_transit_warehouse",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "sales_settings",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "default_settings",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "credit_limit",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "payment_terms",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "auto_accounting_for_stock_settings",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "fixed_asset_defaults",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        {
            "field": "budget_detail",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Company",
            "value": 1
        },
        
    ],
    "Employee": [
        {
            "field": "payroll_cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Employee",
            "value": 1
        },
    ],
    "Department": [
        {
            "field": "payroll_cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Department",
            "value": 1
        },
    ],
    "Travel Request": [
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Travel Request",
            "value": 1
        }
    ],
    "Additional Salary": [
        {
            "field": "deduct_full_tax_on_selected_payroll_date",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Additional Salary",
            "value": 1
        },
    ],
    "Expense Claim Type": [
        {
            "field": "deferred_expense_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim Type",
            "value": 1
        },
        # Child Table
        {
            "field": "accounts",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim Type",
            "value": 1
        },
        {
            "field": "accounts",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Expense Claim Type",
            "value": 1
        }
    ],
    "Expense Claim": [
        {
            "field": "project",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": 1
        },
        {
            "field": "payable_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": '0'
        },
        {
            "field": "payable_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": 1
        },
        {
            "field": "payable_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": 1
        },
        {
            "field": "taxes",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": 1
        },
        {
            "field": "total_taxes_and_charges",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": 1
        },
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim",
            "value": 1
        },
        {
            "field": "accounting_details",
            "prop": "label",
            "prop_type": "Data",
            "doctype":  "Expense Claim",
            "value": "Clearance Details"
        }
    ],
    "Expense Claim Detail": [
        # 1 Field (default_account) => Fetch From ExpenceClaimType
        # No Neet to customize
        {
            "field": "default_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim Detail",
            "value": 1
        },
        {
            "field": "default_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Expense Claim Detail",
            "value": 1
        },
        # 2 Field (cost_center) => Read value from Expense Claim
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim Detail",
            "value": 1
        },
    ],
    "Employee Advance": [
        {
            "field": "advance_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Employee Advance",
            "value": '0'
        },
        {
            "field": "advance_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Employee Advance",
            "value": 1
        },
        {
            "field": "advance_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Employee Advance",
            "value": 1
        },
        {
            "field": "mode_of_payment",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Employee Advance",
            "value": 1
        }
    ],
    "Expense Claim Advance": [
        # Fetch Value From ( Employee Advance )
        {
            "field": "advance_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Expense Claim Advance",
            "value": 1
        },
        {
            "field": "advance_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Expense Claim Advance",
            "value": 1
        }
    ],
    "Mode of Payment": [
        {
            "field": "accounts",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Mode of Payment",
            "value": 1
        },
    ],
    "Loan Type": [
        {
            "field": "mode_of_payment",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "mode_of_payment",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": '0'
        },
        {
            "field": "disbursement_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "disbursement_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": '0'
        },
        {
            "field": "disbursement_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": '0'
        },
        {
            "field": "payment_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": '0'
        },
        {
            "field": "loan_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "interest_income_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "interest_income_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": '0'
        },
        {
            "field": "interest_income_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "penalty_income_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "penalty_income_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": '0'
        },
        {
            "field": "penalty_income_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "rate_of_interest",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": "0"
        },
        {
            "field": "rate_of_interest",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        },
        {
            "field": "penalty_interest_rate",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Type",
            "value": 1
        }
    ],
    "Loan": [
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        # All Data fetched from Loan Type
        {
            "field": "rate_of_interest",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": "0"
        },
        {
            "field": "rate_of_interest",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "mode_of_payment",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "mode_of_payment",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": '0'
        },
        {
            "field": "disbursement_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "disbursement_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": '0'
        },
        {
            "field": "disbursement_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": '0'
        },
        {
            "field": "payment_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": '0'
        },
        {
            "field": "loan_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "interest_income_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "interest_income_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": '0'
        },
        {
            "field": "interest_income_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "penalty_income_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "penalty_income_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": '0'
        },
        {
            "field": "penalty_income_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
    ],
    "Loan Disbursement": [
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Disbursement",
            "value": 1
        },
        {
            "field": "disbursement_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Disbursement",
            "value": 1
        },
        {
            "field": "disbursement_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Disbursement",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Disbursement",
            "value": 1
        },
        {
            "field": "bank_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Disbursement",
            "value": 1
        },
    ],
    "Loan Repayment": [
        {
            "field": "rate_of_interest",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": "0"
        },
        {
            "field": "rate_of_interest",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "payroll_payable_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "payroll_payable_account",
            "prop": "mandatory_depends_on",
            "prop_type": "Data",
            "doctype":  "Loan Repayment",
            "value": 'false'
        },
        {
            "field": "payroll_payable_account",
            "prop": "depends_on",
            "prop_type": "Data",
            "doctype":  "Loan Repayment",
            "value": 'false'
        },
        {
            "field": "payroll_payable_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "interest_payable",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "penalty_income_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "penalty_income_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
        {
            "field": "loan_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Repayment",
            "value": 1
        },
    ],
    "Loan Write Off": [
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Write Off",
            "value": 1
        },
        {
            "field": "write_off_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Write Off",
            "value": 1
        },
        {
            "field": "write_off_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Write Off",
            "value": '0'
        },
        {
            "field": "write_off_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Loan Write Off",
            "value": 1
        },
    ],
    "Loan Application": [
        {
            "field": "rate_of_interest",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Loan Application",
            "value": "0"
        },
        {
            "field": "rate_of_interest",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Loan Application",
            "value": 1
        }
    ],
    "Salary Component": [
        {
            "field": "is_tax_applicable",
            "prop": "default",
            "prop_type": "Check",
            "doctype":  "Salary Component",
            "value": 0
        },
        {
            "field": "is_tax_applicable",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Component",
            "value": 1
        },
        {
            "field": "deduct_full_tax_on_selected_payroll_date",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Component",
            "value": 1
        },
        {
            "field": "is_flexible_benefit",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Component",
            "value": 1
        },
        {
            "field": "accounts",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Component",
            "value": 1
        },
        {
            "field": "accounts",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Salary Component",
            "value": 1
        }
    ],
    "Salary Structure": [
        {
            "field": "max_benefits",
            "prop": "default",
            "prop_type": "Check",
            "doctype":  "Salary Structure",
            "value": 0
        },
        {
            "field": "max_benefits",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Structure",
            "value": 1
        },
        {
            "field": "mode_of_payment",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Structure",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Structure",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Salary Structure",
            "value": 1
        }
    ],
    "Salary Detail":[
        {
            "field": "is_tax_applicable",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Detail",
            "value": 1
        },
        {
            "field": "is_flexible_benefit",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Detail",
            "value": 1
        },
        {
            "field": "deduct_full_tax_on_selected_payroll_date",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Detail",
            "value": 1
        },
        {
            "field": "exempted_from_income_tax",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Detail",
            "value": 1
        },
    ],
    "Salary Structure Assignment": [
        {
            "field": "payroll_payable_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Structure Assignment",
            "value": 1
        },
        {
            "field": "payroll_payable_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Salary Structure Assignment",
            "value": 1
        },
        {
            "field": "income_tax_slab",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Structure Assignment",
            "value": 1
        },
    ],
    "Salary Slip": [
        {
            "field": "payroll_cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Slip",
            "value": 1
        },
        {
            "field": "mode_of_payment",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Slip",
            "value": 1
        },
        {
            "field": "deduct_tax_for_unclaimed_employee_benefits",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Slip",
            "value": 1
        },
        {
            "field": "deduct_tax_for_unsubmitted_tax_exemption_proof",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Salary Slip",
            "value": 1
        },
    ],
    "Payroll Entry": [
        {
            "field": "deduct_tax_for_unsubmitted_tax_exemption_proof",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "deduct_tax_for_unclaimed_employee_benefits",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "payroll_payable_account",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": '0'
        },
        {
            "field": "payroll_payable_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "payroll_payable_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "project",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "cost_center",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "cost_center",
            "prop": "reqd",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": '0'
        },
        {
            "field": "payment_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "payment_account",
            "prop": "ignore_User_Permissions",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
        {
            "field": "bank_account",
            "prop": "hidden",
            "prop_type": "Check",
            "doctype":  "Payroll Entry",
            "value": 1
        },
    ],
    "User":[
        {
            "field": "user_type",
            "prop": "permlevel",
            "prop_type": "Int",
            "doctype":  "User",
            "value": 3
        },
    ]   
}

def create_cost_center(cost_center_name, company, check_company=False, company_fields=[]):
    if check_company and isinstance(company_fields, list) and len(company_fields) > 0:
        if frappe.db.exists("Company", company):
            company_doc = frappe.get_doc("Company", company)
            for field in company_fields:
                cost_center = company_doc.get(field, None)
                if cost_center: return cost_center
    # Check Root Cost Center
    cost_center = frappe.db.get_value("Cost Center", filters={"cost_center_name": cost_center_name, "company": company})
    if cost_center: return cost_center
    parent_cc = None
    pcc = {
        "cost_center_name": company,
        "company": company,
        "is_group": 1,
        "parent_cost_center": "",
    }
    costs = frappe.get_list("Cost Center", filters=pcc)
    if len(costs) > 0:
        parent_cc = costs[0].name
    else:
        cc_doc = frappe.new_doc("Cost Center")
        cc_doc.update(pcc)
        cc_doc.flags.ignore_permissions = True
        cc_doc.flags.ignore_mandatory = True
        cc_doc.insert()
        frappe.db.commit()
        parent_cc = cc_doc.name
    cc = {
        "cost_center_name": "Main",
        "company": company,
        "is_group": 0,
        "doctype": "Cost Center",
        "parent_cost_center": parent_cc
    }
    cc_doc = frappe.get_doc(cc)
    cc_doc.validate_mandatory = lambda : ''
    cc_doc.flags.ignore_permissions = True
    cc_doc.flags.ignore_mandatory = True
    cc_doc.insert()
    cost_center = cc_doc.name

def create_account(account_name, company, parent_account, root_type, account_type=None, check_company=False, company_field=None):
    account_currency = frappe.get_value("Company", company, "default_currency") or "USD"
    # Check Company value First
    c_account_name = None
    if check_company and company_field:
        try:
            c_account_name = frappe.get_value("Company",  company, f'{company_field}') or None
        except: pass
    if c_account_name: return c_account_name
    account = frappe.db.get_value("Account", filters={"account_name": account_name, "company": company})
    if account: return account
    parent_account = frappe.db.get_value(
            "Account", filters={
                "account_name": parent_account,
                "company": company,
                "is_group": 1
            }
        ) or None
    if not parent_account:
        parent_account = frappe.db.get_value(
                "Account", filters={
                    "company": company,
                    "root_type": root_type,
                    "is_group": 1
                    }, order_by="creation"
                ) or None
    account = frappe.get_doc(dict(
            doctype="Account",
            account_name=account_name,
            account_type=account_type,
            parent_account=parent_account,
            company=company,
            account_currency=account_currency))
    if not parent_account:
        account.flags.ignore_mandatory = True
    account.flags.ignore_permissions = True
    account.insert(ignore_if_duplicate=True)
    frappe.db.commit()
    return account.name

def create_mode_payment(title, mode_type):
    mode = frappe.db.exists("Mode of Payment", title)
    if not mode:
        mop = frappe.new_doc("Mode of Payment")
        mop.mode_of_payment = title
        mop.type = mode_type
        mop.flags.ignore_mandatory = True
        mop.flags.ignore_permissions = True
        mop.insert(ignore_if_duplicate=True)
        mode = mop.name
    return mode

def create_bank_account(company):
    account = create_account(company, company, "Bank Accounts", "Asset", "Bank")
    bank = create_bank(company)
    name_to_search = f"{company} - {company}"
    bank_account = frappe.db.exists("Bank Account", name_to_search)
    if bank_account:
        bank_account = frappe.get_doc("Bank Account", name_to_search)
        bank_account.is_default = 1
        bank_account.is_company_account = 1
        bank_account.company = company
        bank_account.flags.ignore_mandatory = True
        bank_account.flags.ignore_permissions = True
        bank_account.save()
        return bank_account.name
    else:
        bank_account = frappe.new_doc("Bank Account")
        bank_account.account_name = company
        bank_account.is_default = 1
        bank_account.is_company_account = 1
        bank_account.company = company
        bank_account.bank = bank
        bank_account.account = account
    bank_account.flags.ignore_mandatory = True
    bank_account.flags.ignore_permissions = True
    bank_account.insert(ignore_if_duplicate=True)
    return bank_account.name

def create_bank(title):
    bank = frappe.db.exists("Bank", title)
    if bank: return bank
    bank = frappe.new_doc("Bank")
    bank.bank_name = title
    bank.flags.ignore_mandatory = True
    bank.flags.ignore_permissions = True
    bank.insert(ignore_if_duplicate=True)
    return bank.name



#################
### Overrides ###
#################
from erpnext.hr.report.monthly_attendance_sheet import monthly_attendance_sheet
from mosyr.overrides.reports.monthly_attendance_sheet import execute

monthly_attendance_sheet.execute = execute
