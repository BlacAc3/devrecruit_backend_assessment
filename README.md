# Django REST Framework Invoice Management API

## Description

This project is a RESTful API built with Django and Django REST Framework for managing customers and invoices. It allows you to create, retrieve, update, and list customers and invoices, including invoice items.

## Prerequisites

*   Python 3.x
*   Django (version 5.2.4)
*   Django REST Framework

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/BlacAc3/devrecruit_backend_assessment  # Replace with the actual repository URL
    cd devrecruit_backend_assessment
    ```

2.  Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\\Scripts\\activate  # On Windows
    ```

3.  Install dependencies:

    ```bash
    pip install -r requirements.txt # Assuming there is a requirements.txt file
    ```

4. Make migrations:
    ```bash
    python manage.py makemigrations
    ```

5.  Apply database migrations:

    ```bash
    python manage.py migrate
    ```

## Running the Application

1.  Run the development server:

    ```bash
    python manage.py runserver
    ```

    The API will be available at `http://127.0.0.1:8000/api/`.

    You can also access the API documentation interfaces:
    *   **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger-ui/`
    *   **Redoc**: `http://127.0.0.1:8000/api/schema/redoc/`

## Running Tests

1.  Run the tests:

    ```bash
    python manage.py test
    ```


## API Endpoints

The API provides the following endpoints:

### Customers

*   `GET /api/customers/`:  List all customers.
*   `POST /api/customers/`: Create a new customer.
    *   Request body:
        ```json
        {
            "name": "Customer Name",
            "email": "customer@example.com"
        }
        ```

### Invoices

*   `GET /api/invoices/`: List all invoices.
*   `POST /api/invoices/`: Create a new invoice.
    *   Request body:
        ```json
        {
            "customer": 1,  // Customer ID
            "due_date": "YYYY-MM-DD",
            "status": "pending",  // or "paid", "overdue"
            "items": [
                {
                    "description": "Item description",
                    "quantity": 1,
                    "unit_price": "10.00"
                }
            ]
        }
        ```

*   `GET /api/invoices/<int:pk>/`: Retrieve an invoice by ID.
*   `PATCH /api/invoices/<int:pk>/`: Update an invoice (partial update - only status is allowed).
    *   Request body:
        ```json
        {
            "status": "paid"  // or "pending", "overdue"
        }
        ```



## Technologies Used

*   Python
*   Django
*   Django REST Framework
*   DRF Spectacular (For swagger documentation)
*   SQLite (for development)
