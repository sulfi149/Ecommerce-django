from django.urls import path
from . import views

urlpatterns = [
      path('', views.login_admin, name='login_admin'),
      path('admin_dashboard/', views.AdminDashboard, name= "admin_dashboard"),
      path('signout_admin/', views.signout_admin, name='signout_admin'),
      #usermanagement
      path('user_management',views.user_management,name='user_management'),
      path('block_user/<str:pk>/', views.block_user, name='block_user'),
      path('edit_user/<str:pk>/', views.edit_user, name='edit_user'),
      
      #category
      path('category_management/',views.CategoryManagement,name="category_management"),
      path('add_category/', views.add_category, name='add_category'),
      #products 
      path('product_management/',views.ProductManagement,name="product_management"),
      path('add_product/', views.add_product, name='add_product'),
      #variations
      path('variation_management/',views.Variation_management,name="variation_management"),
      path('add_variation/',views.Add_variation,name="add_variation"),
      
]
