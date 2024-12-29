import json

import requests
from django.conf import settings

from utils.helper.helper_functions import string_to_base64


class TossPayments:
    def __init__(self, secret_key):
        self.secret_key = string_to_base64(f"{secret_key}:")

    def _get_payment_headers(self):
        payment_headers = {
            "Authorization": f"Basic {self.secret_key}",
            "Content-Type": "application/json",
        }
        return payment_headers

    def authorize_payment(self, amount, order_id, payment_key):
        payment_headers = self._get_payment_headers()

        payload = {
            "paymentKey": payment_key,
            "amount": amount,
            "orderId": order_id,
        }

        response = requests.post(
            f"{settings.TOSS_API_URL}payments/confirm",
            data=json.dumps(payload),
            headers=payment_headers,
        )

        return response.status_code, response.json()

    def cancel_payment(self, payment_key: str, reason: str = "", amount: int = None):
        payment_headers = self._get_payment_headers()

        payload = {"cancelReason": reason}

        if amount:
            payload["cancelAmount"] = amount

        response = requests.post(
            f"{settings.TOSS_API_URL}payments/{payment_key}/cancel",
            data=json.dumps(payload),
            headers=payment_headers,
        )

        return response.status_code, response.json()
