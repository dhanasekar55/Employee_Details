from django.shortcuts import render, get_object_or_404, redirect
from .models import Company, Employee, ProductTransaction
from .forms import CompanyForm,EmployeeForm, ProductTransactionForm
from decimal import Decimal
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.db.models import Sum
from collections import defaultdict



# def homepage(request):
#     transactions = ProductTransaction.objects.select_related('employee', 'employee__company').all()
#     return render(request, 'homepage.html', {'transactions': transactions})

# def homepage(request):
#     transactions = ProductTransaction.objects.select_related('employee', 'employee__company').all()
#     # Group transactions by employee
#     grouped_transactions = defaultdict(list)
#     for transaction in transactions:
#         grouped_transactions[transaction.employee].append(transaction)
#     # Prepare the data to be passed to the template
#     context = []
#     for employee, employee_transactions in grouped_transactions.items():
#         # Calculate totals for each employee's transactions
#         total_quantity = sum(transaction.quantity for transaction in employee_transactions)
#         total_paid = sum(transaction.paid for transaction in employee_transactions)
#         total_advance = sum(transaction.advance_amount for transaction in employee_transactions)
#         total_amount = sum(transaction.total_amount for transaction in employee_transactions)
#         total_balance = sum(transaction.balance for transaction in employee_transactions)
#         total_additional_quantity = sum(transaction.additional_quantity for transaction in employee_transactions)
#         context.append({
#             'employee': employee,
#             'transactions': employee_transactions,
#             'total_quantity': total_quantity,
#             'total_paid': total_paid,
#             'total_advance': total_advance,
#             'total_amount': total_amount,
#             'total_balance': total_balance,
#             'total_additional_quantity': total_additional_quantity,
#         })

#     return render(request, 'homepage.html', {'context': context})

def homepage(request):
    transactions = ProductTransaction.objects.select_related('employee', 'employee__company').all()
    
    # Group transactions by employee
    grouped_transactions = defaultdict(list)
    for transaction in transactions:
        grouped_transactions[transaction.employee].append(transaction)
    
    # Prepare the data to be passed to the template
    context = []
    employees = Employee.objects.all()  # Get all employees, even those with no transactions
    for employee in employees:
        # Get the transactions for this employee
        employee_transactions = grouped_transactions.get(employee, [])
        
        # Calculate totals for each employee's transactions
        total_quantity = sum(transaction.quantity for transaction in employee_transactions)
        total_paid = sum(transaction.paid for transaction in employee_transactions)
        total_advance = sum(transaction.advance_amount for transaction in employee_transactions)
        total_amount = sum(transaction.total_amount for transaction in employee_transactions)
        total_balance = sum(transaction.balance for transaction in employee_transactions)
        total_additional_quantity = sum(transaction.additional_quantity for transaction in employee_transactions)
        
        context.append({
            'employee': employee,
            'company': employee.company,
            'transactions': employee_transactions,
            'total_quantity': total_quantity,
            'total_paid': total_paid,
            'total_advance': total_advance,
            'total_amount': total_amount,
            'total_balance': total_balance,
            'total_additional_quantity': total_additional_quantity,
        })

    return render(request, 'homepage.html', {'context': context})


def dashboard(request, company_id=None):
    if company_id:
        companies = Company.objects.filter(id=company_id)
    else:
        companies = Company.objects.all()
    return render(request, 'dashboard.html', {'companies': companies})

def company_employees(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    employees = Employee.objects.filter(company=company)
    return render(request, 'company_employees.html', {'company': company, 'employees': employees})

# Add a new company
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new company
            return redirect('dashboard')  # Or redirect to a different view
    else:
        form = CompanyForm()  # If GET request, show empty form
    return render(request, 'add_company.html', {'form': form})

# Show employees on the home page (only those associated with a company)
def home(request, company_id=None):
    if company_id:
        company = get_object_or_404(Company, id=company_id)
        employees = Employee.objects.filter(company=company)  # Only get employees of this company
    else:
        employees = Employee.objects.all()  # Show all employees if no specific company is provided

    return render(request, 'home.html', {'employees': employees})



def employee_detail(request, id):
    employee = get_object_or_404(Employee, id=id)
    transactions = ProductTransaction.objects.filter(employee=employee)
    company = employee.company 

    total_products = transactions.count()
    grand_total = sum([transaction.total_amount for transaction in transactions])
    total_paids = sum([transaction.paid for transaction in transactions])
    total_advance = sum([transaction.advance_amount for transaction in transactions])
    balance_due = grand_total - (total_paids + total_advance)
    total_paid = total_paids + total_advance

    remaining_quantities = {}
    for transaction in transactions:
        remaining_quantities[transaction.id] = transaction.remaining_quantity_from_balance

    return render(request, 'employee_detail.html', {
        'employee': employee,
        'transactions': transactions,
        'total_products': total_products,
        'grand_total': grand_total,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'company': company,
        'remaining_quantities': remaining_quantities,
        'total_advance':total_advance
    })
    

def add_employee(request, company_id=None):
    company = None
    if company_id:
        try:
            company = Company.objects.get(id=company_id)  # Get the company object if company_id is provided
        except Company.DoesNotExist:
            return redirect('company_employees', company_id=company_id)  # Redirect even if company doesn't exist, to handle any missing cases
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            if company:
                employee.company = company  # Associate the employee with the company
            employee.save()

            # Redirect to the company_employees page for the given company_id
            if company:
                return redirect('company_employees', company_id=company.id)
            else:
                # If company is None, decide the appropriate fallback action:
                return redirect('dashboard')

    else:
        form = EmployeeForm()

    return render(request, 'add_employee.html', {'form': form, 'company_id': company_id})


def add_transaction(request, id):
    employee = get_object_or_404(Employee, id=id)
    company_price = employee.company.price  # Get the company's price

    if request.method == 'POST':
        form = ProductTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.employee = employee
            transaction.price_per_unit = company_price

            # Ensure default values are set if fields are empty or not provided
            if not transaction.paid:
                transaction.paid = Decimal('0.0')
            if not transaction.advance_amount:
                transaction.advance_amount = Decimal('0.0')
            if not transaction.total_amount:
                transaction.total_amount = Decimal('0.0')
            if not transaction.balance:
                transaction.balance = Decimal('0.0')
            if not transaction.remaining_cash_owed:
                transaction.remaining_cash_owed = Decimal('0.0')
            if not transaction.remaining_quantity_from_balance:
                transaction.remaining_quantity_from_balance = 0
            if not transaction.additional_quantity:
                transaction.additional_quantity = 0

            # If total_amount is not provided, calculate it using price_per_unit and quantity
            if transaction.total_amount == Decimal('0.0') and transaction.quantity > 0:
                transaction.total_amount = transaction.price_per_unit * transaction.quantity

            try:
                # Save the transaction
                transaction.save()
                return redirect('employee_detail', id=employee.id)
            except IntegrityError as e:
                error_message = 'There was an issue saving the transaction. Please try again.'
                return render(request, 'add_transaction.html', {
                    'form': form, 
                    'employee': employee, 
                    'error_message': error_message
                })
        else:
            error_message = "Form data is invalid. Please check the fields."
            return render(request, 'add_transaction.html', {
                'form': form, 
                'employee': employee, 
                'error_message': error_message
            })
    else:
        form = ProductTransactionForm()

    return render(request, 'add_transaction.html', {'form': form, 'employee': employee})


def update_transaction(request, transaction_id):
    transaction = get_object_or_404(ProductTransaction, id=transaction_id)
    if request.method == 'POST':
        form = ProductTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('employee_detail', id=transaction.employee.id)
    else:
        form = ProductTransactionForm(instance=transaction)
    return render(request, 'update_transaction.html', {'form': form, 'transaction': transaction})

def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(ProductTransaction, id=transaction_id)
    
    # If the user is confirming the deletion
    if request.method == 'POST':
        # Delete the transaction and redirect to employee detail page
        employee_id = transaction.employee.id
        transaction.delete()
        return redirect('employee_detail', id=employee_id)
    
    # If not confirming, show confirmation page
    return render(request, 'confirm_delete_transaction.html', {'transaction': transaction})

def update_employee(request, id):
    # Get the employee object by id
    employee = get_object_or_404(Employee, pk=id)
    
    if request.method == 'POST':
        # Create the form with the submitted data and the existing employee instance
        form = EmployeeForm(request.POST, instance=employee)
        
        if form.is_valid():
            form.save()
            
            # Get the company_id from the employee object and redirect to company_employeess
            company_id = employee.company.id if employee.company else None
            
            if company_id:
                return redirect('company_employeess', company_id=company_id)
            else:
                return redirect('dashboard')  # Redirect to dashboard if no company found
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'update_employee.html', {'form': form, 'employee': employee})

def delete_employee(request, employee_id):
    # Use get_object_or_404 to automatically handle the case where the employee is not found
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Perform delete operation
    employee.delete()
    
    # Redirect to the company employee list after deletion
    return redirect('company_employees', company_id=employee.company.id)



def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to company detail page (or another page)
    else:
        form = CompanyForm(instance=company)

    return render(request, 'edit_company.html', {'form': form, 'company': company})

def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        company.delete()
        return redirect('dashboard')  # Redirect to company list page or wherever you want

    return render(request, 'delete_company.html', {'company': company})
