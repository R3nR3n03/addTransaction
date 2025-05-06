from locust import HttpUser, task, between
import json


class MyUser(HttpUser):
    wait_time = between(1, 5)  # Simulate user behavior with a wait time

    # Use relative URL for Locust
    auth_url = "/Login"
    transactions_url = "/Transactions"
    headers = {
        "DeviceName": "ActiveSystemsTablet",
        "Content-Type": "application/json"
    }

    def get_token(self):
        """Authenticate and return access token."""
        response = self.client.post(self.auth_url, auth=("Admin", "1"), headers=self.headers)
        #print("Auth Response:", response.status_code, response.text)  # Debugging

        if response.status_code == 200:
            try:
                token = response.json().get("token")  # Ensure correct key
                if token:
                    return token
                else:
                    print("Token not found in response.")
            except json.JSONDecodeError:
                print("Failed to parse JSON response.")
        else:
            print("Failed to retrieve token")

        return None

    def on_start(self):
        """Runs once per user at the start of the test."""
        self.token = self.get_token()

    @task
    def post_invoice(self):
        """Send a POST request with the provided JSON body."""
        if not self.token:
            self.token = self.get_token()  # Refresh token if needed
            if not self.token:
                print("No token available. Skipping transaction.")
                return

        json_data = {
            "Id": 0,
            "TotalPayment": 100.0,
            "AmountDue": 0.0,
            "DateTime": "2025-04-04T11:25:58.698",
            "PrintName": "",
            "Address": "",
            "TinNumber": "",
            "BusinessStyle": "",
            "Payments": [
                {
                    "Amount": 100.0,
                    "PaymentType": "Cash"
                }
            ],
            "Invoice": {
                "Id": 0,
                "GuestDetail": {
                    "Count": 0,
                    "Guests": []
                },
                "InvoiceItems": [
                    {
                        "Id": 0,
                        "Item": {
                            "Id": 2,
                            "ReferenceItem": {
                                "Id": 2980,
                                "Code": "FCM",
                                "Description": "Fried Chicken Meal",
                                "UnitOfMeasure": "",
                                "Taxable": 1,
                                "Price": 100.0
                            },
                            "Image": "ee487ab6-6203-4d43-a3fd-3c919706073e.jpg",
                            "Subcategory": None,
                            "Category": None
                        },
                        "Quantity": 1,
                        "Discounts": [],
                        "Amount": 100.0,
                        "DiscountAmount": 0.0,
                        "DiscountedAmount": 100.0,
                        "UniqueId": "TAureliusInvoiceItem"
                    }
                ],
                "Discounts": None,
                "Coupons": [],
                "Table": None,
                "Cashier": {
                    "Id": 1,
                    "Image": "ff299968-d908-4f60-90aa-89e0595acb3f.jpg",
                    "UserAccount": {
                        "Id": 1,
                        "Name": "Admin",
                        "Description": "Administrator",
                        "Password": "",
                        "PwdCreatedOn": "2020-09-16T08:50:24.000",
                        "UserType": 2,
                        "ContactId": 2348,
                        "Contact": None,
                        "RegisteredById": 0,
                        "LockoutCounter": 0,
                        "LockoutOn": None,
                        "ExpirationDate": None,
                        "LoginFailedOn": None
                    },
                    "AuthorizedScreen": []
                },
                "Subtotal": 100.0,
                "InvoiceStatus": "Void",
                "DiningOption": "DineIn",
                "DiscountTotal": 0.0,
                "SeniorCitizenDiscount": 0.0,
                "PersonWithDisabilityDiscount": 0.0,
                "SalesRepresentative": None,
                "Customer": {
                    "Id": 1,
                    "Image": "",
                    "Contact": None
                },
                "VatTypes": None,
                "VatRate": 0.12,
                "VatableSales": 100.0,
                "VatAmount": 10.7143,
                "VatExemptSales": 0.0,
                "ZeroRatedSales": 0.0,
                "TotalAfterVat": 100.0,
                "ReprintCount": 0,
                "Salesorders": None
            },
            "TotalCashPayment": 100.0,
            "TotalGCashPayment": 0.0,
            "TotalPayMayaPayment": 0.0,
            "TotalVisaPayment": 0.0,
            "TotalMastercardPayment": 0.0,
            "TotalCheckPayment": 0.0

    }

        # Ensure Authorization is included in the request
        headers_with_auth = {
            "Authorization": f"Bearer {self.token}",
            "DeviceName": "ActiveSystemsTablet",
            "Content-Type": "application/json"
        }

        response = self.client.post(self.transactions_url, data=json.dumps(json_data), headers=headers_with_auth)
        print("Transaction Response:", response.status_code, response.text)
