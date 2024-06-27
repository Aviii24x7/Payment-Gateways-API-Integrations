from django.conf import settings

from django.http import JsonResponse
from rest_framework.response import Response

import requests
from rest_framework.decorators import api_view

CLIENT_ID = settings.PAYPAL_CLIENT_ID
APP_SECRET = settings.PAYPAL_CLIENT_SECRET

#   change at the time of production!!
BASE_URL = "https://api-m.sandbox.paypal.com"  # Sandbox Mode
# BASE_URL = "https://api-m.paypal.com"           # Live Mode


# STEP-1: Generate Access token
@api_view(['POST'])
def get_access_token(request):
    # URI to generate token
    url = f"{BASE_URL}/v1/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(
        url,
        auth=(CLIENT_ID, APP_SECRET),
        headers=headers,
        data=data
    )

    # It contains many items like expired_time, we only want access token for now
    print(response.json())

    return JsonResponse({"access_token": response.json()["access_token"], 'expires_in':response.json()["expires_in"] })



import uuid

def generate_request_id():
    return str(uuid.uuid4())


# STEP-2: Create Checkout Order
@api_view(['POST'])
def create_order(request):
    paypal_request_id = generate_request_id()
    access_token = request.data["access_token"]
    # paypal_request_id = request.data["paypal_request_id"]

    # URI for order creation
    url = f"{BASE_URL}/v2/checkout/orders"
    cancel_url = "https://www.negbuy.com"
    return_url = "https://www.seller.negbuy.com"

    headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': paypal_request_id ,
        'Authorization': f'Bearer {access_token}'
    }

    # "shipping_preference": "SET_PROVIDED_ADDRESS",
    
    # phone number and country code ARE REQUIRED

    data = """
    {   "intent": "CAPTURE",
        "purchase_units": [ {
            "reference_id": "d9f80740-38f0-11e8-b467-0ed5f89f718b", 
            "description" : "product title here",
            "amount": {
                "currency_code": "USD",
                "value": "33.00"
                }
            }
            ],  
            
        "payer":{
                "name": {
                    "given_name": "",
                    "surname": ""
                    },
                "phone": {
                    "phone_number": {
                        "national_number":  "121" 
                        }
                    },
                "address": {
                    "address_line_1": "",
                    "address_line_2": "",
                    "admin_area_2": "",
                    "admin_area_1": "",
                    "postal_code": "",
                    "country_code": ""
                    }
                
        },
            
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                    "brand_name": "NEGBUY Pvt. Ltd.",
                    "locale": "en-IN",
                    "landing_page": "LOGIN",
                    "user_action": "PAY_NOW",
                    "return_url": "https://returned.com",
                    "cancel_url": "https://cancelled.com"
                }
            }
        }
    }
    """
    response = requests.post(
        url,
        headers=headers,
        data=data
    )
    response_json = response.json()  # Parse JSON response

    # Check if order_id is None
    order_id = response_json.get('id')
    if order_id is None:
        error_message = "Invalid or Unavailable Phone Number Or Country Code of user (e.g. India: 'IN', United States: 'US', etc)"
        print(error_message)
        return Response({"status": "Error", "message": error_message, "data": {}})

    # Extract other necessary data
    checkout_urls = response_json.get('links')[1].get('href')
    paypal_request_id = paypal_request_id  # assuming you have it defined somewhere in your code

    print(response_json)  # Output the response JSON for debugging

    return JsonResponse({"order_id": order_id, "checkout_urls": checkout_urls, "paypal_request_id": paypal_request_id})


# Authorize Payment for Order
@api_view(['POST'])
def authorize_payment(request):
    order_id = request.data['order_id']
    paypal_request_id = request.data['paypal_request_id']
    access_token = request.data["access_token"]

    url = f"{BASE_URL}/v2/checkout/orders/{order_id}/authorize"

    headers = {
        'Content-Type': 'application/json',        
        'PayPal-Request-Id': paypal_request_id,
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(
        url,
        headers=headers
    )

    print(response.json())

    return JsonResponse(response.json())

# : capture created payment
@api_view(['POST'])
def capture_payment(request):
    order_id = request.data['order_id']
    paypal_request_id = request.data['paypal_request_id']
    access_token = request.data["access_token"]

    url = f"{BASE_URL}/v2/checkout/orders/{order_id}/capture"

    headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': paypal_request_id,
        'Authorization': f'Bearer {access_token}'

    }

    response = requests.post(
        url,
        headers=headers
    )

    print(response.json())

    return JsonResponse(response.json())



# : Show Order Details
@api_view(['GET'])
def order_details(request):
    order_id = request.data['order_id']
    access_token = request.data["access_token"]

    url = f"{BASE_URL}/v2/checkout/orders/{order_id}"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    print(response.json())

    return JsonResponse(response.json())