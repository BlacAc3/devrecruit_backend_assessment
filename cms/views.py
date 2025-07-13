from django.shortcuts import render

from rest_framework import generics
from drf_spectacular.utils import extend_schema

from .serializers import CustomerSerializer, InvoiceSerializer, InvoiceStatusSerializer
from .models import Customer, Invoice


class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer



@extend_schema(
    request={'PATCH': InvoiceStatusSerializer}
)
class InvoiceRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    http_method_names = ['get', 'patch', 'head', 'options']
