import datetime
import hashlib
import hmac
import random
import time
import uuid

import requests
from django.conf import settings


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return (
        datetime.datetime.now()
        .replace(tzinfo=datetime.timezone(offset=utc_offset))
        .isoformat()
    )


def get_signature(key="", msg=""):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(api_key="", api_secret_key=""):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {
        "Authorization": "HMAC-SHA256 ApiKey="
        + api_key
        + ", Date="
        + date
        + ", salt="
        + salt
        + ", signature="
        + get_signature(api_secret_key, data),
        "Content-Type": "application/json; charset=utf-8",
    }


def send_message(phone, message):
    headers = get_headers(settings.SOLAPI_API_KEY, settings.SOLAPI_API_SECRET)
    url = "https://api.solapi.com/messages/v4/send-many"
    data = {"messages": [message]}
    output = requests.post(url, headers=headers, json=data)
    print(output.json())


# {
#             'to': '01027061463',
#             'from': '01096709732',
#             'kakaoOptions': {
#                     'pfId': 'KA01PF200323182344986oTFz9CIabcx',
#                     'templateId': 'KA01TP200323182345741y9yF20aabcx',
#                     'variables': {
#                         '#{변수1}': '변수1의 값',
#                         '#{변수2}': '변수2의 값',
#                         '#{버튼링크1}': '버튼링크1의 값',
#                         '#{버튼링크2}': '버튼링크2의 값',
#                         '#{강조문구}': '강조문구의 값'
#                          }
#                 },
#             },
