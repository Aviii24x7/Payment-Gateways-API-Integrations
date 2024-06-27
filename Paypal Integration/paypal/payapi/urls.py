from django.urls import path
from . import views

urlpatterns = [
path('get_access_token', views.get_access_token, name= "get_access_token" ),
path('create_order', views.create_order, name= "create_order" ),
path('order_details', views.order_details, name= "order_details" ),
path('authorize_payment', views.authorize_payment, name= "authorize_payment" ),
path('capture_payment', views.capture_payment, name= "capture_payment" ),
]

