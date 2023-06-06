import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    hide_accounts_and_taxs_from_system()

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
    


def hide_accounts_and_taxs_from_system():
    for key in update_fields_props.keys():
        fields_props = update_fields_props.get(f"{key}", [])
        add_property_setter(fields_props)


def add_property_setter(fields_props):
    for props in fields_props:
        doctype = props.get("doctype", False)
        fieldname = props.get("field", False)
        property = props.get("prop", False)
        value = props.get("value", False)
        property_type = props.get("prop_type", False)
        if (
            not doctype
            or not fieldname
            or not property
            or not value
            or not property_type
        ):
            continue

        try:
            make_property_setter(
                doctype,
                fieldname,
                property,
                value,
                property_type,
                validate_fields_for_doctype=False,
            )
        except:
            pass
    frappe.db.commit()