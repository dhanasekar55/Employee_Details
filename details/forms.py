from django import forms
from .models import Company, Employee, ProductTransaction

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'price']  # Include the price field here

    price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True, 
        initial=0.0,  # Set a default value if needed
        widget=forms.NumberInput(attrs={'step': '0.01'})  # Optional: Set a step value for decimal input
    )

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name','phone', 'address','company']


class ProductTransactionForm(forms.ModelForm):
    class Meta:
        model = ProductTransaction
        fields = ['price_per_unit', 'quantity', 'advance_amount','paid']
    

    advance_amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0.0)
    # advance_date = forms.DateField(widget=forms.SelectDateWidget(), required=False)
    paid = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0.0)
    # paid_date = forms.DateField(widget=forms.SelectDateWidget(), required=False)
    
    
    def __init__(self, *args, **kwargs):
        super(ProductTransactionForm, self).__init__(*args, **kwargs)

        # Set the price_per_unit field based on the company's price
        if 'employee' in self.initial:
            employee = self.initial['employee']
            company_price = employee.company.price
            self.fields['price_per_unit'] = forms.DecimalField(
                initial=company_price,
                disabled=True,  # Make this field readonly
                widget=forms.NumberInput(attrs={'readonly': 'readonly'})
            )
        else:
            # Set a default value if no employee is selected yet
            self.fields['price_per_unit'] = forms.DecimalField(
                initial=0.0,
                disabled=True,  # Make this field readonly
                widget=forms.NumberInput(attrs={'readonly': 'readonly'})
            )
