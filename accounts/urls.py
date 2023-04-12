from django.urls import path
from . import views


urlpatterns = [
    # basic urls ............................
    path('login/',views.login_view, name = "login"),
    path('signout/',views.signout,name="signout"),
    path('register/',views.register, name = "signup"),
    path('dashboard/',views.dashboard, name = "dashboard"),
    
    # for forgot password.................................................................................
    path('activate/<uidb64>/<token>',views.activate,name="activate"),
    path('forgotPassword/',views.forgotPassword,name="forgotPassword"),
    path('resetPassword_validate/<uidb64>/<token>',views.resetPassword_validate,name="resetPassword_validate"),
    path('reset_password/',views.reset_password,name="reset_password"),


    # dashboard functionalities..............................................
    path('my_orders/',views.my_orders,name="my_orders"),
    path('editUserProfile/',views.editUserProfile,name="editUserProfile"),
    path('change_password/',views.change_password,name='change_password'),
    path('order_detail/<int:order_id>/',views.order_detail,name='order_detail'),


]
