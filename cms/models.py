from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.pk} for {self.customer.name}"

    @property
    def total_amount(self):
        return sum(item.total for item in self.items.all())


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.description} @ {self.unit_price} (Invoice #{self.invoice.pk})"
