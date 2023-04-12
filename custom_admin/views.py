from django.shortcuts import render,redirect
from accounts.models import Account
from store.models import Variations
from category.models import category
from django.contrib import messages,auth
from django.contrib.auth import logout,login,authenticate
from .forms import UserForm,CForm,PForm,VForm
from django.http import  HttpResponseRedirect

from category.models import category

from store.models import Product,Variations

# Create your views here.
def login_admin(request):
    if 'email' in request.session:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST['email']
        pass1 = request.POST['pass1']
        user_obj = Account.objects.filter(email=email)
        if not user_obj.exists():
                messages.info(request, 'Account not found')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        user_obj = auth.authenticate(email=email, password=pass1)
        if user_obj.is_admin and user_obj:
                login(request, user_obj)
                return redirect('admin_dashboard')
                
        messages.info(request, 'Invalid Password')
        return render(request,'custom_admin/admin_log.html')
    return render(request, 'custom_admin/admin_log.html')
     
        
 



    
def AdminDashboard(request):
    return render (request,"custom_admin/dashboard.html")

# user management////////////////////////////////////////////////////////////////////////////////////////


def user_management(request):

    if request.user.is_authenticated:
        
        user_det = Account.objects.all()
        
        return render(request, 'custom_admin/user.html', {'user_det': user_det})

    else:
        return redirect('login_admin')   

def signout_admin(request):
    logout(request)
    # if 'username' in request.session:
    #     request.session.flush()
    # request.session.flush()
  
    messages.success(request, "Logged Out Successfully!!")
    return redirect('login_admin')  
def block_user(request, pk):
    user = Account.objects.get(id=pk)
    if request.method == 'POST':

        if user.is_active == True:

            user.is_active = False
            user.save()
        else:
            user.is_active = True
            user.save()

        return redirect('user_management')
def edit_user(request, pk):
    user = Account.objects.get(id=pk)
    uform = UserForm(instance=user)

    if request.method == 'POST':
        uform = UserForm(request.POST, instance=user)
        if uform.is_valid():
            uform.save()
        return redirect('user_management')

    context = {
        'uform': uform
    }
    return render(request, 'custom_admin/user_edit.html', context)        


# category management/////////////////////////////////////////////////////////////////////////////////////

def CategoryManagement(request):
    
        Category_obj = category.objects.all()

        context = {
            'Category_obj' : Category_obj
        }
        return render(request,'custom_admin/category/category.html',context)

def add_category(request):

    if request.method == 'POST':

        cform = CForm(request.POST)
        print(cform.errors)
        if cform.is_valid():
            cform.save()
            return redirect('category_management')
    cform = CForm
    context = {
        'cform': cform
    }
    return render(request, 'custom_admin/category/add_category.html', context)

def edit_category(request,pk):
    category_item = category.objects.get(id=pk)
    if request.method == 'POST':
         cform = CForm(request.POST,instance=category_item)
         if cform.is_valid():
              cform.save()
              return redirect('category_management')
    cform = CForm(instance=category_item)
    context = {
         'cform':cform,
    } 
    return render(request,'custom_admin/category/edit_category.html',context)

# product management//////////////////////////////////////////////////////////////////////////////////////////

def ProductManagement(request):
    product_obj = Product.objects.all().order_by()
    return render(request,'custom_admin/products/products.html',{'product_obj':product_obj})

def add_product(request):
    if request.method == 'POST':
        pform = PForm(request.POST,request.FILES)
        print(pform.errors)
        if pform.is_valid():
            pform.save()
            return redirect('product_management')
        else:
            print('form is not valid')    
    pform = PForm
    context = {
        'pform': pform
    }
    return render(request, 'custom_admin/products/add_product.html', context)

def edit_product(request,pk):
    product= Product.objects.get(id=pk)

    if request.method == "POST":
        Eform = PForm(request.POST,instance=product)
        if Eform.is_valid():
            Eform.save()
            return redirect('product_management')
        
    Eform = PForm(instance=product)    
    context={
        'Eform':Eform, 
    }     
    return render(request,'custom_admin/products/edit_product.html',context)


# Variations to list ----------------------------------------------------------------------------------------
def Variation_management(request):
    variation_obj = Variations.objects.all()
    return render(request,'custom_admin/variation/variation_list.html',{'variation_obj':variation_obj})

def Add_variation(request):
        
        if request.method == 'POST':
                vform = VForm(request.POST,request.FILES)                
                if vform.is_valid():
                    vform.save()
                    print('after')
                    return redirect('variation_management')
                else:
                    print('form is not valid')
        vform = VForm
        context = {
            'vform':vform,
        }
        return render(request,'custom_admin/variation/add_variation.html',context)

def edit_variation(request,pk):
    variation_item = Variations.objects.get(id=pk)
    if request.method == 'POST':
          vform = VForm(request.POST,instance=variation_item)
          if vform.is_valid():
               vform.save()
               return redirect('variation_management')
    vform= VForm(instance=variation_item) 
    context = {
         'vform': vform,
    }                      
    return render(request,'custom_admin/variation/edit_variation.html',context)   
# -------------------------------------------------------------------------------------------------------------

def order_management(request):
    
    return render(request,'custom_admin/orders/order_management.html')

    