from locust import HttpUser, task, between
from faker import Faker
import json
import logging
import random

# Initialize Faker and logging
fake = Faker()
logging.basicConfig(level=logging.INFO)

# Reference items (you can load this list from a file if needed)
reference_items = [
    {"Id": 2980, "Code": "FCM", "Description": "Fried Chicken Meal", "Price": 150},
    {"Id": 2985, "Code": "2FCM", "Description": "2pc Fried Chicken Meal", "Price": 155},
    {"Id": 2987, "Code": "10FCB", "Description": "10pc Fried Chicken Bucket", "Price": 600},
    {"Id": 2979, "Code": "ER", "Description": "Extra Rice", "Price": 15},
    {"Id": 2989, "Code": "CN", "Description": "Chicken Nuggets", "Price": 55},
    {"Id": 3010, "Code": "CFM", "Description": "Cheesy Fries Medium", "Price": 50},
    {"Id": 3013, "Code": "CFL", "Description": "Cheesy Fries Large", "Price": 80},
    {"Id": 3014, "Code": "CFF", "Description": "Cheesy Fries Family", "Price": 120},
    {"Id": 3016, "Code": "CC", "Description": "Cheese Cake", "Price": 95},
    {"Id": 2999, "Code": "HB", "Description": "Hot Brew", "Price": 65},
    {"Id": 2997, "Code": "IC", "Description": "Iced Chocoffee", "Price": 75},
    {"Id": 3035, "Code": "010660", "Description": "Refreshing chilled drink with natural fruit flavor blend.", "Price": 45},
    {"Id": 3002, "Code": "SSM", "Description": "Summer Shake Mango", "Price": 75},
    {"Id": 3004, "Code": "SSP", "Description": "Summer Shake Pineapple", "Price": 75},
    {"Id": 2995, "Code": "CM", "Description": "Coke Medium", "Price": 30}
]

# Mapping of referenceItem Id to the correct Item Id the system expects
id_mapping = {
    2980: 2,  # Fried Chicken Meal
    2985: 3,  # 2pc Fried Chicken Meal
    2987: 4,  # 10pc Fried Chicken Bucket
    2979: 5,  # Extra Rice
    2989: 6,  # Chicken Nuggets
    # Add other mappings as needed
}

class MyUser(HttpUser):
    wait_time = between(1, 5)

    auth_url = "/Login"
    transactions_url = "/Transactions"
    headers = {
        "DeviceName": "ActiveSystemsTablet",
        "Content-Type": "application/json"
    }

    def get_token(self):
        """Authenticate and return access token."""
        response = self.client.post(self.auth_url, auth=("Admin", "1"), headers=self.headers)
        if response.status_code == 200:
            try:
                token = response.json().get("token")
                if token:
                    return token
                logging.warning("Token not found in response.")
            except json.JSONDecodeError:
                logging.error("Failed to parse JSON response.")
        else:
            logging.error(f"Failed to retrieve token: {response.status_code} - {response.text}")
        return None

    def on_start(self):
        self.token = self.get_token()

    @task
    def post_invoice(self):
        if not self.token:
            self.token = self.get_token()
            if not self.token:
                logging.warning("No token available. Skipping transaction.")
                return

        now = fake.date_time_this_year().isoformat()

        # Randomly select an item from the reference list
        item = random.choice(reference_items)

        # Map the referenceItem's Id to the actual Item's Id
        mapped_item_id = id_mapping.get(item["Id"])

        if not mapped_item_id:
            logging.error(f"Mapping for Item with referenceId {item['Id']} not found.")
            return

        json_data = {
            "Id": 0,
            "TotalPayment": item["Price"],
            "AmountDue": 0.0,
            "DateTime": now,
            "PrintName": "",
            "Address": "",
            "TinNumber": "",
            "BusinessStyle": "",
            "Payments": [
                {
                    "Amount": item["Price"],
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
                            "Id": mapped_item_id,  # Use the mapped Item Id
                            "ReferenceItem": {
                                "Id": item["Id"],
                                "Code": item["Code"],
                                "Description": item["Description"],
                                "UnitOfMeasure": "",
                                "Taxable": 1,
                                "Price": item["Price"]
                            },
                            "Image": "sample-image.jpg",  # Use a generic image
                            "Subcategory": None,
                            "Category": None
                        },
                        "Quantity": 1,
                        "Discounts": [],
                        "Amount": item["Price"],
                        "DiscountAmount": 0.0,
                        "DiscountedAmount": item["Price"],
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
                "Subtotal": item["Price"],
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
                "VatableSales": item["Price"],
                "VatAmount": item["Price"] * 0.12,
                "VatExemptSales": 0.0,
                "ZeroRatedSales": 0.0,
                "TotalAfterVat": item["Price"] * 1.12,
                "ReprintCount": 0,
                "Salesorders": None
            },
            "TotalCashPayment": item["Price"],
            "TotalGCashPayment": 0.0,
            "TotalPayMayaPayment": 0.0,
            "TotalVisaPayment": 0.0,
            "TotalMastercardPayment": 0.0,
            "TotalCheckPayment": 0.0
        }

        headers_with_auth = {
            "Authorization": f"Bearer {self.token}",
            "DeviceName": "ActiveSystemsTablet",
            "Content-Type": "application/json"
        }

        with self.client.post(self.transactions_url, json=json_data, headers=headers_with_auth, catch_response=True) as response:
            if response.status_code == 401:
                logging.warning("Token expired, refreshing...")
                self.token = self.get_token()
                response.failure("Unauthorized. Token expired.")
            elif response.status_code != 200:
                logging.error(f"Transaction failed: {response.status_code} - {response.text}")
                response.failure("Transaction failed.")
            else:
                response.success()
                logging.info("Transaction succeeded.")
