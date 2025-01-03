import datetime
import hashlib
import hmac
import time
import uuid

import requests
from django.conf import settings


class SolApiClient:
    def __init__(
        self, api_key=settings.SOLAPI_API_KEY, api_secret_key=settings.SOLAPI_API_SECRET
    ):
        self.api_key = api_key
        self.api_secret_key = api_secret_key

    def _generate_signature(self, msg):
        return hmac.new(
            self.api_secret_key.encode(), msg.encode(), hashlib.sha256
        ).hexdigest()

    def _generate_unique_id(self):
        return str(uuid.uuid1().hex)

    def _get_iso_datetime(self):
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        return (
            datetime.datetime.now()
            .replace(tzinfo=datetime.timezone(offset=utc_offset))
            .isoformat()
        )

    def _generate_headers(self):
        date = self._get_iso_datetime()
        salt = self._generate_unique_id()
        data = date + salt
        signature = self._generate_signature(data)
        return {
            "Authorization": f"HMAC-SHA256 ApiKey={self.api_key}, Date={date}, salt={salt}, signature={signature}",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _handle_response(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            return None
        try:
            return response.json()
        except ValueError as err:
            print(f"JSON decoding error: {err}")
            return None

    def get_balance(self):
        headers = self._generate_headers()
        url = "https://api.solapi.com/cash/v1/balance"
        response = requests.get(url, headers=headers)
        print(response.json())
        return self._handle_response(response)

    def send_many(self, phone, message):
        headers = self._generate_headers()
        url = "https://api.solapi.com/messages/v4/send-many"

        data = {
            "messages": [
                {
                    "to": phone,
                    "from": settings.SOLAPI_PHONE_NUMBER,
                    "kakaoOptions": message,
                    # "country": "880",
                }
            ]
        }
        print(data)
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        return self._handle_response(response)

    def send_one(self, phone, message):
        headers = self._generate_headers()
        url = "https://api.solapi.com/messages/v4/send"
        data = {
            "message": {
                "to": phone,
                "from": settings.SOLAPI_PHONE_NUMBER,
                "kakaoOptions": message,
                # "country": "880",
            }
        }
        print(data)
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        return self._handle_response(response)


def get_sol_api_payload(order, template_id):
    phone = order.customer.user_information.phone_number

    if phone:
        product_names = order.order_products.all()
        product_full_name = ""
        flag = 0
        for product_name in product_names:
            if flag == 0:
                product_full_name = product_name.product.name
            else:
                product_full_name = product_full_name + "," + product_name.product.name
            flag += 1

        print(order.customer.user_information.full_name)
        print(order.order_id)
        print(order.updated_at)
        print(product_full_name)
        print(order.grand_total)
        print(order.shipping_address.detail_address)
        print(order.delivery_number)
        print(phone)
        message = {
            "pfId": settings.SOLAPI_PF_ID,
            "templateId": template_id,
            "variables": {
                "userName": (
                    order.customer.user_information.full_name
                    if order.customer.user_information
                    else order.customer.email
                ),
                "orderCode": order.order_id,
                "orderDate": str(order.created_at),
                "orderProduct": str(product_full_name),
                "orderPrice": order.grand_total,
                "address": order.shipping_address.detail_address,
                "deliveryCode": (
                    order.delivery_number if order.delivery_number else "None"
                ),
            },
        }
        return phone, message
