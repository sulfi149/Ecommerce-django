from django.shortcuts import render,redirect
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from django.http import HttpResponse
from cart.models import Cart,CartItem
from cart.views import _Cart_id

# for email verfication
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage






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
                    for item in cart_item:
                        item.user = user
                        item.save()

            except: 
                print('entered into the except')
                pass   
            auth.login(request,user)
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
    

@login_required(login_url="login")
def dashboard(request):
    return render(request,"accounts/dashboard.html")


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

       