from django.shortcuts import render

from django.conf import settings
from django.http.response import JsonResponse # new
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt #NEW
import json
import stripe
from django.shortcuts import redirect

from rest_framework.decorators import api_view


# Create your views here.
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = 'home.html'
    
# to enable fetching of public key
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    


@api_view(['POST'])
def create_checkout_session(request):
    
    phone = '7206168859'
    quantiy = 4
    print("checkout session function called")
    
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        existing_customer = stripe.Customer.list(email="xyz@ghanta.com", limit=1)
        print("Existing Customer:", existing_customer)
        
        if existing_customer and len(existing_customer.data) > 0:
            # existing_customer.data[0].phone = phone
            customer_id = existing_customer.data[0].id
            print("Customer already exists:", customer_id, "\n\n")
        else:
            # Create a customer if not exists
            customer = stripe.Customer.create(
                name="Jenny Rosen",
                address={
                    "line1": "510 Townsend St",
                    "postal_code": "98140",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "US",
                },
                email="xyz@ghanta.com",
                phone = phone
            )
            print("New customer created!")
            customer_id = customer.id
            # print('New customer created:', customer_id)
        # print(customer)
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            # product details
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 10000,  # Amount in cents
                        'product_data': {
                            'name': "Sheela's Toy",
                            'images': ['./payapi/static/PHOTO.JPG'],
                            
                            # Add more product details as needed
                        },
                    },
                    'quantity': quantiy,
                },
            ],
            
            mode='payment',

            customer=customer_id,  # Pass customer ID instead of name and email
            
            payment_intent_data={
                'description': 'Payment for the purchase of XYZ product',
                'statement_descriptor': 'XYZ Purchase',
            },
            success_url="http://127.0.0.1:8000/success",
            cancel_url="http://127.0.0.1:8000/cancel",
        )
        print('\n\n\nSession created:', checkout_session)
        
        payment_intent = checkout_session.payment_intent
        
        # # Construct the checkout URL using the session ID
        # checkout_url = f"https://checkout.stripe.com/{checkout_session.id}"

        # # Return JSON response with session ID and checkout URL
        # return JsonResponse({'sessionId': checkout_session.id, 'checkoutUrl': checkout_url})
        
        
        # Redirect to the checkout session URL
        print(checkout_session.url)

        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        print('Error:', str(e))
        return HttpResponse(str(e), status=500)

def success(request):
    # redirect("https:")
    return render(request, 'success.html')

def cancel(request):
    return render(request, 'cancel.html')


endpoint_secret = settings.STRIPE_WEBHOOK_SECRET_KEY

@csrf_exempt
def my_webhook_view(request):
    
    print("webhook view called")
    
    payload = request.body
    
    # print("\n\n\n____________payload_________\n\n")
    # print(payload)
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    
    # To Update DataBase
    if event['type'] == 'checkout.session.completed':
        
        
        session = event['data']['object']
        
        print("\n\n\n\n----------session---------\n")
        print(session)
        
        # print("\n\n\n\n----------line items---------\n")
        # line_items = session['display_items'] 
        # print(line_items)

        print("\n\n\n\n----------payment Intent---------\n")
        payment_intent_id = session['payment_intent']
        # Retrieve payment intent to get more details if needed
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        print(payment_intent)    
        
        if session.payment_status == "paid":
            
            
            
            # Call some function that can update the database    
            # fullfill_order()
            pass

    # Passed signature verification
    return HttpResponse(status=200)