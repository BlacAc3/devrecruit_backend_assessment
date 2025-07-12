from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .serializers import CustomerSerializer, InvoiceSerializer
from .models import Customer, Invoice


class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class InvoiceRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
