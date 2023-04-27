from django.shortcuts import render,redirect,get_object_or_404
from .models import Account,UserProfile,Address,Return_request
from django.contrib import messages,auth
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm,UserForm,UserProfileForm
from django.http import HttpResponseRedirect
from cart.models import Cart,CartItem
from orders.models import Order,OrderProduct
from cart.views import _Cart_id

# for email verfication
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import requests




# Create your views here.
def login_view(request):
    if request.method =="POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:              
                cart = Cart.objects.get(cart_id=_Cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    # need to get the product variation of the cart before login
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    # get the variation of the user cart
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        ex_variation = item.variations.all()
                        existing_variation_list.append(list(ex_variation))
                        id.append(item.id)
                    # compare the current variation with the existing variation and increment the existing variartion withe user
                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except: 
                pass   
            auth.login(request,user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                   return redirect('dashboard')
        else:
            messages.error(request,'Invalid email id or password')    
    return render(request,"accounts/log.html")


   
    
@login_required(login_url="login")
def signout(request):
    auth.logout(request)
    messages.success(request,'logged out successfull')
    
    return redirect('login')
  

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user_name = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=user_name,password=password)
            user.phone_number=phone_number
            
            user.save()

            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default.jpg'
            profile.save()

            # email verfication
            current_site = get_current_site(request)
            mail_subject = "Please verify your Email"
            message = render_to_string('accounts/account_verification.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),

            })
            to_mail = email
            send_mail = EmailMessage(mail_subject,message,to = [to_mail])
            
            send_mail.send()
    
            #messages.info(request,'Registration Successfull')
            return redirect('/accounts/login/?command=verfication&email='+email) 
        else:
             messages.info(request,'Invalid Crdentials')
             
             return redirect('signup')   

    rform = RegistrationForm()
    context ={
        'rform' : rform
    }
    return render(request,"accounts/signup.html",context) 

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'congratulation! Your accont is Activated.')
        return redirect("login")
    else:
        messages.error(request,"Invalid credentials!")
        return redirect('signup')
    
# dashboard functionality _________________________________________________________________________________________
@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user=request.user)
    context = {
        "orders_count" : orders_count,
        'userprofile':userprofile
    }
    return render(request,"accounts/dashboard.html",context)
def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders,
        
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def editUserProfile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('editUserProfile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        context = {
                'user_form': user_form,
                'profile_form': profile_form,
                'userprofile': userprofile,
        }    
    return render(request,'accounts/editUserProfile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Your password has been changed!')
                return redirect('change_password') 
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')        
        else:
            messages.error(request, 'password dose not match')
            return redirect('change_password') 


    return render(request,'accounts/change_password.html')        

def forgotPassword(request):
    
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact = email)

            # email verfication

            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),

            })
            to_mail = email
            send_mail = EmailMessage(mail_subject,message,to = [to_mail])
            
            send_mail.send()

            messages.success(request,'Password reset email has been send to your email address')
            return redirect("login")


        else:
            messages.error(request,'Account Does Not Excist')
            return redirect('forgotPassword')    

    return render(request,'accounts/forgot_password.html')


def resetPassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] =  uid
        messages.success(request,'Please reset your password')
        return redirect('reset_password')

    else:
        messages.error(request,'link has been expired!')
        return redirect('login')
    

def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Reset Password Successfull!')
            return redirect('login')

        else:
            messages.error(request,"Password Do Not Match")
            return redirect('reset_password')
    return render(request,'accounts/reset_password.html')

def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal
    }

    return render(request,'accounts/order_detail.html',context)

def address_manage(request):
    try:
        address = Address.objects.filter(user=request.user)
        context = {
            'addresss':address,
        }
    except:
        pass    
    return render(request,'accounts/address.html',context)       

def add_address(request):
    if request.method == "POST":
            user = request.user
            name = request.POST.get('first_name')  
            address1 = request.POST.get('address_line_1')
            address2 = request.POST.get('address_line_2')
            city = request.POST.get('city')
            phone1 = request.POST.get('phone1')
            phone2 = request.POST.get('phone2')
            state = request.POST.get('state')
            country = request.POST.get('country')
            pincode = request.POST.get('pincode')
            Address.objects.create(user=user,name=name,address1=address1,address2=address2,city=city,
                                   phone1=phone1,phone2=phone2,state=state,country=country,pincode=pincode)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                print('error')
            return redirect('address_manage')
    return render(request,'accounts/add_address.html')

def user_cancel_order(request,order_id):
        order =  Order.objects.get(id=order_id)
        order.status = 'Cancelled'
        order.save()
        return redirect('my_orders')
def return_order(request,order_id):
    current_user= request.user
    order = Order.objects.get(id=order_id)
    if request.method == "POST":
        reason = request.POST['reason']
        return_request = Return_request.objects.create(
            user=current_user,reason=reason,order_number=order.order_number
        )
        return_request.save()
        order.status = 'Return Requested'
        order.save()
        return redirect('home')   
    return render(request,'accounts/return_order.html',{'order': order})
