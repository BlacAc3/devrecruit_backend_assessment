from datetime import date
from rest_framework import serializers
from .models import Customer, Invoice, InvoiceItem # Assuming these models exist in .models


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email']
        # Default ModelSerializer validation ensures 'name' and 'email' are provided
        # and that 'email' is a valid format and unique, as per the model definition.


class InvoiceItemSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='total')

    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'amount']
        read_only_fields = ['id', 'amount']

    def validate_quantity(self, value):
        """
        Check that the quantity is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def validate_unit_price(self, value):
        """
        Check that the unit price is a positive decimal.
        """
        if value <= 0:
            raise serializers.ValidationError("Unit price must be a positive decimal.")
        return value


class InvoiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['status']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        # 'fields' defines the fields that will be included in serialized output (e.g., GET requests)
        # and can be provided during creation (POST requests).
        fields = ['id', 'customer', 'issue_date', 'due_date', 'status', 'items', 'total_amount']
        # 'read_only_fields' are always included in serialized output but cannot be provided on input.
        # For update operations (PUT/PATCH), fields not in 'read_only_fields' are typically expected.
        # However, the custom 'update' method in this serializer explicitly limits updates
        # to only the 'status' field. This means other fields (customer, due_date, items)
        # are effectively not required and will not be processed if provided during an update,
        # while still being required for initial creation (POST) and available for retrieval (GET).
        read_only_fields = ['id', 'issue_date', 'total_amount']

    def validate(self, data):
        """
        Custom validation for Invoice creation.
        Ensures due_date is not before issue_date and that at least one item is provided.
        """
        issue_date =  date.today()
        due_date = data.get('due_date')

        if issue_date and due_date and due_date < issue_date:
            raise serializers.ValidationError({"due_date": "Due date cannot be before issue date."})

        # This validation specifically for POST (create) requests for invoices.
        # It ensures that an invoice is created with at least one item.
        if self.context['request'].method == 'POST':
            items_data = data.get('items')
            if not items_data:
                raise serializers.ValidationError({"items": "At least one invoice item is required."})

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice

    def update(self, instance, validated_data):
        # This update method is designed to specifically handle updates to the 'status' field.
        # It checks if 'status' is provided in the validated data.
        if 'status' in validated_data:
            # If 'status' is present, update the instance's status attribute.
            instance.status = validated_data['status']
            instance.save()
            return instance
        # If 'status' is not present in the validated data, raise a validation error.
        raise serializers.ValidationError({"status": "Only the status field can be updated."})
