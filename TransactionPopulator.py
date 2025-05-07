from locust import HttpUser, task, between
from faker import Faker
import logging
import random
import json

# Initialize
fake = Faker()
logging.basicConfig(level=logging.INFO)

# Constants
USERNAME = "Admin"
PASSWORD = "1"
DEVICE_NAME = "ActiveSystemsTablet"
DEFAULT_IMAGE = "sample-image.jpg"
AUTH_URL = "/Login"
TRANSACTIONS_URL = "/Transactions"

# Reference items
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
    {"Id": 3035, "Code": "010660", "Description": "Refreshing chilled drink", "Price": 45},
    {"Id": 3002, "Code": "SSM", "Description": "Summer Shake Mango", "Price": 75},
    {"Id": 3004, "Code": "SSP", "Description": "Summer Shake Pineapple", "Price": 75},
    {"Id": 2995, "Code": "CM", "Description": "Coke Medium", "Price": 30}
]

id_mapping = {
    2980: 2, 2985: 4, 2987: 20, 2979: 1, 2989: 7,
    3010: 10, 3013: 11, 3014: 22, 3016: 12, 2999: 6,
    2997: 8, 3035: 21, 3002: 9, 3004: 24, 2995: 5
}

class MyUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.token = self.get_token()

    def get_token(self):
        headers = {"DeviceName": DEVICE_NAME, "Content-Type": "application/json"}
        response = self.client.post(AUTH_URL, auth=(USERNAME, PASSWORD), headers=headers)
        if response.status_code == 200:
            try:
                return response.json().get("token")
            except json.JSONDecodeError:
                logging.error("JSON decode error.")
        logging.error(f"Token retrieval failed: {response.status_code}")
        return None

    def generate_invoice_items(self, count=2):
        items = []
        total_price = 0

        for _ in range(count):
            ref_item = random.choice(reference_items)
            mapped_id = id_mapping.get(ref_item["Id"])
            if not mapped_id:
                continue

            qty = random.randint(1, 3)
            subtotal = ref_item["Price"] * qty

            items.append({
                "Id": 0,
                "Item": {
                    "Id": mapped_id,
                    "ReferenceItem": {
                        "Id": ref_item["Id"],
                        "Code": ref_item["Code"],
                        "Description": ref_item["Description"],
                        "UnitOfMeasure": "",
                        "Taxable": 1,
                        "Price": ref_item["Price"]
                    },
                    "Image": DEFAULT_IMAGE,
                    "Subcategory": None,
                    "Category": None
                },
                "Quantity": qty,
                "Discounts": [],
                "Amount": subtotal,
                "DiscountAmount": 0.0,
                "DiscountedAmount": subtotal,
                "UniqueId": "TAureliusInvoiceItem"
            })

            total_price += subtotal

        return items, total_price

    @task
    def post_invoice(self):
        if not self.token:
            self.token = self.get_token()
            if not self.token:
                logging.warning("Token unavailable. Skipping task.")
                return

        invoice_items, total_price = self.generate_invoice_items()

        if not invoice_items:
            logging.warning("No valid items generated.")
            return

        now = fake.date_time_this_year().isoformat()
        vat = round(total_price * 0.12, 2)
        total_after_vat = round(total_price + vat, 2)

        json_data = {
            "Id": 0,
            "TotalPayment": total_price,
            "AmountDue": 0.0,
            "DateTime": now,
            "PrintName": "",
            "Address": "",
            "TinNumber": "",
            "BusinessStyle": "",
            "Payments": [{"Amount": total_price, "PaymentType": "Cash"}],
            "Invoice": {
                "Id": 0,
                "GuestDetail": {
                    "Count": 1,
                    "Guests": [{"Name": fake.first_name()}]
                },
                "InvoiceItems": invoice_items,
                "Discounts": None,
                "Coupons": [],
                "Table": None,
                "Cashier": {
                    "Id": 1,
                    "Image": "ff299968-d908-4f60-90aa-89e0595acb3f.jpg",
                    "UserAccount": {
                        "Id": 1,
                        "Name": USERNAME,
                        "Description": "Administrator",
                        "Password": "",
                        "PwdCreatedOn": "2020-09-16T08:50:24.000",
                        "UserType": 2,
                        "ContactId": 2348,
                        "Contact": None,
                        "RegisteredById": 0,
                        "LockoutCounter": 0
                    },
                    "AuthorizedScreen": []
                },
                "Subtotal": total_price,
                "InvoiceStatus": "Void",
                "DiningOption": "DineIn",
                "DiscountTotal": 0.0,
                "SeniorCitizenDiscount": 0.0,
                "PersonWithDisabilityDiscount": 0.0,
                "Customer": {"Id": 1, "Image": "", "Contact": None},
                "VatTypes": None,
                "VatRate": 0.12,
                "VatableSales": total_price,
                "VatAmount": vat,
                "VatExemptSales": 0.0,
                "ZeroRatedSales": 0.0,
                "TotalAfterVat": total_after_vat,
                "ReprintCount": 0,
                "Salesorders": None
            },
            "TotalCashPayment": total_price,
            "TotalGCashPayment": 0.0,
            "TotalPayMayaPayment": 0.0,
            "TotalVisaPayment": 0.0,
            "TotalMastercardPayment": 0.0,
            "TotalCheckPayment": 0.0
        }

        headers_with_auth = {
            "Authorization": f"Bearer {self.token}",
            "DeviceName": DEVICE_NAME,
            "Content-Type": "application/json"
        }

        with self.client.post(TRANSACTIONS_URL, json=json_data, headers=headers_with_auth, catch_response=True) as response:
            if response.status_code == 401:
                logging.warning("Token expired. Retrying...")
                self.token = self.get_token()
                response.failure("Unauthorized.")
            elif response.status_code != 200:
                logging.error(f"Failed: {response.status_code} - {response.text}")
                response.failure("Transaction failed.")
            else:
                response.success()
                logging.info("Invoice transaction successful.")
