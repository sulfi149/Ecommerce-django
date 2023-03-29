from django.urls import path
from . import views


urlpatterns = [
    path('',views.home_view,name="home"),
    path('store/',views.store,name="store"),
    path('category/<slug:category_slug>/',views.store,name="products_by_category"),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detaile,name="product_detaile"),
    path('search/',views.search,name="search"),

 
]