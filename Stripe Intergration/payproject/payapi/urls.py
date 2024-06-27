from django.urls import path
from .views import *


urlpatterns = [
    path('', HomePageView.as_view(), name='home'), 
    
    path('config/', stripe_config, name= "configure-public-key"), # to enable fetching of public key
    
    path('create-checkout-session', create_checkout_session, name="create-checkout-session"),   #to create checkout session and make payments
    
    path('stripe-webhook', my_webhook_view, name="stripe-webhook"),   #to create checkout session and make payments
    
    path('cancel/', cancel),
    path('success/', success)
    ]