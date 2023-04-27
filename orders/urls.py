from django.urls import path
from . import views


urlpatterns = [
    path('placeOrder/',views.place_order,name="place_order"),
    path('orderPlaceCod/',views.order_place_cod,name="order_place_cod"),
    path('payments/',views.payments,name="payments"),
    path('orderComplete/',views.order_complete,name="order_complete"),   
]