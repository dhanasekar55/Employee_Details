from django.urls import path
from . import views

urlpatterns = [
    # Home page, listing all employees
    
    path('', views.dashboard, name='dashboard'),
    path('homepage', views.homepage, name='homepage'),
    path('employee/<int:id>/', views.employee_detail, name='employee_detail'),
    path('<int:company_id>/', views.dashboard, name='dashboard'),
     # Dashboard with company_id
    path('add_company/', views.add_company, name='add_company'),
    
    path('company/<int:company_id>/', views.company_employees, name='company_employees'),
    path('company/<int:company_id>/employees/', views.company_employees, name='company_employees'),
    
    path('company/<int:company_id>/employees/', views.company_employees, name='company_employeess'),
    # path('employee/<int:id>/', views.company_employees, name='company_employees'),

    
    path('company/<int:company_id>/add_employee/', views.add_employee, name='add_employee_with_company'),  # Add employee with company_id
   
    path('home/', views.home, name='home'),
    path('home/<int:company_id>/', views.home, name='home_by_company'),  # URL for employees of a specific company
    path('add_employee/', views.add_employee, name='add_employee'),
    
    path('add_employee/<int:company_id>/', views.add_employee, name='add_employee'),
    
    path('employee/add/', views.add_employee, name='add_employee'),
   
    # Update the add_employee URL to accept company_id
    path('company/<int:company_id>/add_employee/', views.add_employee, name='add_employee'),
    
    path('employee/<int:id>/', views.employee_detail, name='employee_detail'),
    path('employee/update/<int:id>/', views.update_employee, name='update_employee'),  # This is correct
    path('employee/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    path('employee/<int:id>/transaction/add/', views.add_transaction, name='add_transaction'),
    path('transaction/update/<int:transaction_id>/', views.update_transaction, name='update_transaction'),
    path('transaction/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    
    path('company/edit/<int:company_id>/', views.edit_company, name='edit_company'),
    path('company/delete/<int:company_id>/', views.delete_company, name='delete_company'),
    
  

]
