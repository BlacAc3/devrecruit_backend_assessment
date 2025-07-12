from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Customer, Invoice, InvoiceItem
from .serializers import CustomerSerializer, InvoiceSerializer, InvoiceItemSerializer
import datetime

class CustomerTests(APITestCase):
    def test_create_customer(self):
        url = reverse('customer-list-create')
        data = {'name': 'Test Customer', 'email': 'test@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().name, 'Test Customer')

    def test_create_customer_invalid_email(self):
        url = reverse('customer-list-create')
        data = {'name': 'Invalid Customer', 'email': 'invalid-email'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(Customer.objects.count(), 0)

    def test_create_customer_duplicate_email(self):
        Customer.objects.create(name='Existing Customer', email='existing@example.com')
        url = reverse('customer-list-create')
        data = {'name': 'New Customer', 'email': 'existing@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(Customer.objects.count(), 1) # Still only one customer

    def test_list_customers(self):
        Customer.objects.create(name='Customer 1', email='customer1@example.com')
        Customer.objects.create(name='Customer 2', email='customer2@example.com')
        url = reverse('customer-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Customer 1')
        self.assertEqual(response.data[1]['name'], 'Customer 2')


class InvoiceTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Invoice Customer', email='invoice@example.com')
        self.today = datetime.date.today()
        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.invoice_url = reverse('invoice-list-create')

    def test_create_invoice_with_items(self):
        data = {
            'customer': self.customer.id,
            'due_date': self.tomorrow.isoformat(),
            'status': 'pending',
            'items': [
                {'description': 'Service A', 'quantity': 1, 'unit_price': '100.00'},
                {'description': 'Product B', 'quantity': 2, 'unit_price': '25.50'}
            ]
        }
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invoice.objects.count(), 1)
        invoice = Invoice.objects.get()
        self.assertEqual(invoice.customer, self.customer)
        self.assertEqual(invoice.items.count(), 2)
        self.assertEqual(invoice.total_amount, 151.00) # 1*100 + 2*25.50 = 100 + 51 = 151

    def test_create_invoice_no_items(self):
        data = {
            'customer': self.customer.id,
            'due_date': self.tomorrow.isoformat(),
            'status': 'pending',
            'items': []
        }
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_create_invoice_due_date_before_issue_date(self):
        data = {
            'customer': self.customer.id,
            'due_date': self.yesterday.isoformat(),
            'status': 'pending',
            'items': [
                {'description': 'Service C', 'quantity': 1, 'unit_price': '50.00'}
            ]
        }
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('due_date', response.data)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_create_invoice_item_negative_quantity(self):
        data = {
            'customer': self.customer.id,
            'due_date': self.tomorrow.isoformat(),
            'status': 'pending',
            'items': [
                {'description': 'Bad Item', 'quantity': -1, 'unit_price': '10.00'}
            ]
        }
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)
        self.assertIn('quantity', response.data['items'][0])
        self.assertEqual(Invoice.objects.count(), 0)

    def test_create_invoice_item_negative_unit_price(self):
        data = {
            'customer': self.customer.id,
            'due_date': self.tomorrow.isoformat(),
            'status': 'pending',
            'items': [
                {'description': 'Bad Item', 'quantity': 1, 'unit_price': '-5.00'}
            ]
        }
        response = self.client.post(self.invoice_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)
        self.assertIn('unit_price', response.data['items'][0])
        self.assertEqual(Invoice.objects.count(), 0)


    def test_list_invoices(self):
        invoice1 = Invoice.objects.create(customer=self.customer, due_date=self.tomorrow)
        InvoiceItem.objects.create(invoice=invoice1, description='Item 1', quantity=1, unit_price='10.00')
        invoice2 = Invoice.objects.create(customer=self.customer, due_date=self.tomorrow)
        InvoiceItem.objects.create(invoice=invoice2, description='Item 2', quantity=1, unit_price='20.00')

        response = self.client.get(self.invoice_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], invoice1.id)
        self.assertEqual(response.data[1]['id'], invoice2.id)

    def test_retrieve_invoice(self):
        invoice = Invoice.objects.create(customer=self.customer, due_date=self.tomorrow)
        item1 = InvoiceItem.objects.create(invoice=invoice, description='Service A', quantity=1, unit_price='100.00')
        item2 = InvoiceItem.objects.create(invoice=invoice, description='Product B', quantity=2, unit_price='25.50')

        detail_url = reverse('invoice-detail-update', kwargs={'pk': invoice.pk})
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], invoice.id)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['total_amount'], '151.00') # 1*100 + 2*25.50

    def test_update_invoice_status(self):
        invoice = Invoice.objects.create(customer=self.customer, status='pending', due_date=self.tomorrow)
        InvoiceItem.objects.create(invoice=invoice, description='Item', quantity=1, unit_price='10.00') # Ensure it has items for total_amount property

        detail_url = reverse('invoice-detail-update', kwargs={'pk': invoice.pk})
        update_data = {'status': 'paid'}

        # Use PATCH for partial update of status
        response = self.client.patch(detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')
        self.assertEqual(response.data['status'], 'paid')
        # Check that other fields like total_amount are still present and correct
        self.assertAlmostEqual(float(response.data['total_amount']), 10.00)

    def test_update_invoice_items_not_allowed_via_invoice_update(self):
        invoice = Invoice.objects.create(customer=self.customer, status='pending', due_date=self.tomorrow)
        InvoiceItem.objects.create(invoice=invoice, description='Old Item', quantity=1, unit_price='10.00')

        detail_url = reverse('invoice-detail-update', kwargs={'pk': invoice.pk})
        update_data = {
            'status': 'paid',
            'items': [ # Attempt to modify items
                {'description': 'New Item', 'quantity': 5, 'unit_price': '20.00'}
            ]
        }

        # This test ensures that sending 'items' in an update request for the Invoice
        # does not result in item changes, but only scalar fields are updated.
        response = self.client.put(detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')
        # Assert that the number of items has not changed and old item still exists
        self.assertEqual(invoice.items.count(), 1)
        self.assertTrue(invoice.items.filter(description='Old Item').exists())
        self.assertFalse(invoice.items.filter(description='New Item').exists())

    def test_retrieve_non_existent_invoice(self):
        detail_url = reverse('invoice-detail-update', kwargs={'pk': 999})
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
