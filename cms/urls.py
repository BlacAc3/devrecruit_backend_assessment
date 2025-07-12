from django.urls import path
from .views import CustomerListCreateAPIView, InvoiceListCreateAPIView, InvoiceRetrieveUpdateAPIView

urlpatterns = [
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('invoices/', InvoiceListCreateAPIView.as_view(), name='invoice-list-create'),
    path('invoices/<int:pk>/', InvoiceRetrieveUpdateAPIView.as_view(), name='invoice-detail-update'),
]
