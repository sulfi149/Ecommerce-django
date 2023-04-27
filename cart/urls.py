
from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('addCart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('removeCart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('removeCart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),


]    
    