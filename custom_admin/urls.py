from django.urls import path
from . import views

urlpatterns = [
      path('', views.login_admin, name='login_admin'),
      path('adminDashboard/', views.dashboard, name= "admin_dashboard"),
      path('signoutAdmin/', views.signout_admin, name='signout_admin'),
      

      #usermanagement
      path('userManagement/',views.user_management,name='user_management'),
      path('blockUser/<str:pk>/', views.block_user, name='block_user'),
      path('editUser/<str:pk>/', views.edit_user, name='edit_user'),
      
      #category
      path('categoryManagement/',views.CategoryManagement,name="category_management"),
      path('addCategory/', views.add_category, name='add_category'),
      path('editCategory/<str:pk>/', views.edit_category, name='edit_category'),
      #products 
      path('productManagement/',views.ProductManagement,name="product_management"),
      path('addProduct/', views.add_product, name='add_product'),
      path('editProduct/<str:pk>/',views.edit_product,name="edit_product"),
      #variations
      path('variationManagement/',views.Variation_management,name="variation_management"),
      path('addVariation/',views.Add_variation,name="add_variation"),
      path('editVariation/<str:pk>/',views.edit_variation,name="edit_variation"),
      #orders
      path('orderManagement/',views.order_management,name="order_management"),
      path('orderDetailAdmin/<int:order_id>/',views.order_detail_admin,name="order_detail_admin"),
      path('adminOrderUpdate/<int:order_id>/',views.adminOrderUpdate,name="adminOrderUpdate"),
      path('cancelorder/<int:order_id>/',views.cancelorder,name="cancelorder"),
      path('returnUpdate/<int:order_id>/',views.returnUpdate,name='returnUpdate'),

      path('sales/',views.sales_report_date, name='sales'),
      path('exporttopdf/',views.export_to_pdf, name='export_to_pdf'),
      path('exporttoexcel/',views.export_to_excel, name='export_to_excel'),


      
]
