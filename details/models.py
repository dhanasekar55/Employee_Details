from django.db import models
from decimal import Decimal

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")

    def __str__(self):
        return self.name


class ProductTransaction(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))  # Default value
    quantity = models.PositiveIntegerField(default=0)  # Default value
    paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    remaining_quantity_from_balance = models.PositiveIntegerField(default=0)
    additional_quantity = models.PositiveIntegerField(default=0)
    remaining_cash_owed = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    # advance_date = models.DateField()  # Mandatory field (required)

    # The date when the payment is actually paid
    paid_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Ensure Decimal values are set properly
        self.paid = Decimal(self.paid)
        self.advance_amount = Decimal(self.advance_amount)
        self.total_amount = Decimal(self.total_amount)
        
        if not self.price_per_unit:  # If price_per_unit is not set, use the company's price
          self.price_per_unit = self.employee.company.price
        
        # Calculate the total amount based on price_per_unit * quantity
        self.total_amount = self.price_per_unit * self.quantity

        # Calculate the total paid so far
        total_paid = self.advance_amount + self.paid

        # Calculate the delivered value
        delivered_value = self.price_per_unit * self.quantity

        # Calculate balance: Total Amount - Paid - Advance Amount
        self.balance = self.total_amount - self.paid - self.advance_amount

        # Calculate remaining quantity from balance: balance / price_per_unit
        if self.price_per_unit > 0 and self.balance >= 0:
            self.remaining_quantity_from_balance = max(int(self.balance // self.price_per_unit), 0)
        else:
            self.remaining_quantity_from_balance = 0

        # Calculate excess amount if total_paid exceeds delivered value
        excess_amount = total_paid - delivered_value

        if excess_amount > 0:
            if self.price_per_unit > 0:  # Prevent division by zero
                self.additional_quantity = int(excess_amount // self.price_per_unit)
                self.remaining_cash_owed = excess_amount % self.price_per_unit
            else:
                self.additional_quantity = 0
                self.remaining_cash_owed = 0.0
        else:
            self.additional_quantity = 0
            self.remaining_cash_owed = 0.0

        super(ProductTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - {self.employee.name}"
