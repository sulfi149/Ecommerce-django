from django.shortcuts import render,redirect
from accounts.models import Account
from store.models import Variations
from category.models import category
from orders.models import Order,OrderProduct
from django.contrib import messages,auth
from django.contrib.auth import logout,login,authenticate
from .forms import UserForm,CForm,PForm,VForm
from django.http import  HttpResponseRedirect,HttpResponse,JsonResponse

from category.models import category

from store.models import Product,Variations

from django.contrib.auth.decorators import login_required
import datetime
from datetime import date, timedelta
from django.db.models import Count,Sum
from .models import SalesReport,sales_report,monthly_sales_report
from django.template.loader import get_template
import io
from xhtml2pdf import pisa 
import xlwt
from django.http import FileResponse

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
     
        
 



    
def admin_dashboard(request):
    return render (request,"custom_admin/admin_dashboard.html")

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
    orders = Order.objects.all()
    context ={
         'orders': orders,
    }

    
    return render(request,'custom_admin/orders/order_management.html',context)

def order_detail_admin(request,order_id):
    order = Order.objects.get(id=order_id)
    # num = order.order_number
    orderdetail = OrderProduct.objects.filter(order=order)
    subtotal = 0

    for i in orderdetail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': orderdetail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'custom_admin/orders/order_detail_admin.html', context)    
def adminOrderUpdate(request,order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        print(order.status)
        if order.status == 'Accepted':
            order.status = 'Placed'
            order.save()
            print(order.status)
        elif order.status == 'Placed':
            order.status = 'Shipped'
            print(order.status)
            order.save()
            # return redirect('orders')
        elif order.status == 'Shipped':
            print(order.status)
            order.status = 'Out For Delivery'
            order.save()
            # return redirect('orders')
        elif order.status == 'Out For Delivery':
            print(order.status)
            order.status = 'Delivered'
            order.save()
            # return redirect('orders')
        else:
            order.status = 'Delivered'
            order.save()
            # return redirect('orders')
        
    return redirect('order_management')

@login_required(login_url='admin_login')
def returnUpdate(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        order.status = 'Return Accepted'
        order.save()

    return redirect('order_management')

def cancelorder(request,order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        order.status = 'Cancelled'
        order.save()

    return redirect('order_management')

current_date = datetime.date.today()
duration = 'Today'
@login_required(login_url='admin_login')
def dashboard(request):
    admin = ''
    # if 'admin' in request.session:
    #     admin = request.session['admin']
    # else:
    #     return redirect('/admin_sign_in')
    # this_admin = Account.objects.get(email=admin)
    sales_graph_data = []
    sales_graph_category = []
    user_graph_data = []
    user_graph_category = []
    if request.method == 'POST':
        duration = request.POST.get('duration')
        print('Getting Graph details of ', duration)
        orders = Order.objects.all()
        users = Account.objects.all()
        if duration == 'today':
            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0
            # finding the number of sales on today based on orders
            cycle = 0
            for sale in orders:
                cycle = cycle + 1
                # filtering sales based on year
                if str(sale.Order_year) == str(current_date.year):
                    # filtering sales based on month
                    if str(sale.Order_month) == str(current_date.month):
                        # filtering sales based on day
                        if str(sale.Order_day) == str(current_date.day):
                            # filterin sales which has the status as delivered based on orders
                            print(sale.status)
                            if str(sale.status == 'delivered'):
                                count = count + 1
                            sales_graph_data.append(count)
                            sales_graph_category.append(cycle)
            # printing the number of sales on today
            print('Number of sales In Today Is ', count)
            for user in users:
                # filtering sales based on year
                if str(user.signup_year) == str(current_date.year):
                    # filtering sales based on month
                    if str(user.signup_month) == str(current_date.month):
                        # filtering sales based on day
                        if str(user.signup_day) == str(current_date.day):
                            count = count + 1
                            user_graph_data.append(4)
                            user_graph_category.append(1)
        elif duration == 'last_7_days':
            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0
            # getting the sales of last  days
            # value of day is from 1 to 7
            for day in range(0, 7):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        # print(sale.Order_day,current_date.day-timedelta(days=day).days)
                        if str(sale.Order_day) == str(current_date.day - (timedelta(days=day).days)):
                            # print('count+',count)
                            count = count + 1
                sales_graph_data.append(count)
                sales_graph_category.append(current_date.day - (timedelta(days=day).days))
            print('Number of sales in the last 7 days is ', sales_graph_data)
            # getting the new users
            for day in range(0, 7):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(current_date.month):
                            # print(sale.Order_day,current_date.day-timedelta(days=day).days)
                            if str(user.signup_day) == str(current_date.day - (timedelta(days=day).days)):
                                # print('count+',count)
                                count = count + 1
                user_graph_data.append(count)
                user_graph_category.append(current_date.day - (timedelta(days=day).days))
            print('Number of revenue in the last 7 days is ', user_graph_data)
        # this month
        elif duration == 'last_month':
            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0
            for day in range(1, 32):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        if str(sale.Order_month) == str(current_date.month):
                            if str(sale.Order_day) == str(day):
                                count = count + 1
                sales_graph_data.append(count)
                sales_graph_category.append(day)
            for day in range(1, 32):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(current_date.month):
                            if str(user.signup_day) == str(day):
                                count = count + 1
                user_graph_data.append(count)
                user_graph_category.append(day)


        elif duration == 'last_month':
            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0
            for day in range(1, 32):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        if str(sale.Order_month) == str(current_date.month):
                            if str(sale.Order_day) == str(day):
                                count = count + 1
                sales_graph_data.append(count)
                sales_graph_category.append(day)
            for day in range(1, 32):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(current_date.month):
                            if str(user.signup_day) == str(day):
                                count = count + 1
                user_graph_data.append(count)
                user_graph_category.append(day)



        # this year
        else:
            sales_graph_data = []
            sales_graph_category = []
            user_graph_data = []
            user_graph_category = []
            count = 0
            for month in range(1, 13):
                count = 0
                for sale in orders:
                    if str(sale.Order_year) == str(current_date.year):
                        if str(sale.Order_month) == str(month):
                            count = count + 1
                sales_graph_data.append(count)
                sales_graph_category.append(month)
            for month in range(1, 13):
                count = 0
                for user in users:
                    if str(user.signup_year) == str(current_date.year):
                        if str(user.signup_month) == str(month):
                            count = count + 1
                user_graph_data.append(count)
                user_graph_category.append(month)
    user_count = Account.objects.all().count()
    sales = Order.objects.filter(status='Delivered')
    cod = Order.objects.filter(payment_mode='Cash on Delivery').count()
    paypal = Order.objects.filter(payment_mode='paypal').count()
    razorpay = Order.objects.filter(payment_mode='Paid by Razorpay').count()
    paypal_payment_method_graph_data = paypal
    razorpay_payment_method_graph_data = razorpay
    cod_payment_method_graph_data = cod
    rev = 0
    for sale in sales:
        rev = rev + sale.order_total
    revenue = round(rev,2)
    return render(request, 'custom_admin/a_dashboard.html', {
        # 'duration': duration,
        'customer_count': user_count,
        'sales': sales.count(),
        'revenue': revenue,
        # 'admin': this_admin,
        'sales_graph_data': sales_graph_data,
        'sales_graph_category': sales_graph_category,
        'user_graph_data': user_graph_data,
        'user_graph_category': [user_graph_category],
        'paypal_payment_method_graph_data': paypal_payment_method_graph_data,
        'razorpay_payment_method_graph_data': razorpay_payment_method_graph_data,
        'cod_payment_method_graph_data': cod_payment_method_graph_data,
    })


@login_required(login_url='admin_login')
def sales_report_date(request):
    data = OrderProduct.objects.all()
    if request.method == 'POST':
        if request.POST.get('month'):
            month = request.POST.get('month')
            print(month)
            data = OrderProduct.objects.filter(created_at__icontains=month)
            
            if data:
                if SalesReport.objects.all():
                    SalesReport.objects.all().delete()
                    for i in data:
                        sales = SalesReport()
                        sales.productName = i.product.product_name
                        sales.categoryName = i.product.category.category_name
                        sales.date = i.created_at
                        sales.quantity = i.quantity
                        sales.productPrice = i.product_price
                        sales.save()
                    sales = SalesReport.objects.all()
                    total = SalesReport.objects.all().aggregate(Sum('productPrice'))
                    context = { 'sales':sales,'total':total['productPrice__sum']}
                    return render(request,'custom_admin/sales_report_.html',context)
                else:
                    for i in data:
                        sales = SalesReport()
                        sales.productName = i.product.product_name
                        sales.categoryName = i.product.category.category_name
                        sales.date = i.created_at
                        sales.quantity = i.quantity
                        sales.productPrice = i.product_price
                        sales.save()
                    sales = SalesReport.objects.all()
                    total = SalesReport.objects.all().aggregate(Sum('productPrice'))
                    context = { 'sales':sales,'total':total['productPrice__sum']}
                    return render(request,'custom_admin/sales_report_.html',context)
            else:
                messages.warning(request,"Nothing Found!!")
        if request.POST.get('date'):
            date = request.POST.get('date')
            print("0,",date)
            
            date_check = OrderProduct.objects.filter(created_at__icontains=date)
            print(date_check)
            if date_check:
                if SalesReport.objects.all():
                    SalesReport.objects.all().delete()
            
                    for i in date_check:
                        sales = SalesReport()
                        sales.productName = i.product.product_name
                        sales.categoryName = i.product.category.category_name
                        sales.date = i.created_at
                        sales.quantity = i.quantity
                        sales.productPrice = i.product_price
                        sales.save()
                    sales = SalesReport.objects.all()
                    total = SalesReport.objects.all().aggregate(Sum('productPrice'))
                    context = { 'sales':sales,'total':total['productPrice__sum']}
                    return render(request,'custom_admin/sales_report_.html',context)
                else:
                    for i in date_check:
                        sales = SalesReport()
                        sales.productName = i.product.product_name
                        sales.categoryName = i.product.category.category_name
                        sales.date = i.created_at
                        sales.quantity = i.quantity
                        sales.productPrice = i.product_price
                        sales.save()
                    sales = SalesReport.objects.all()
                    total = SalesReport.objects.all().aggregate(Sum('productPrice'))
                    context = { 'sales':sales,'total':total['productPrice__sum']}
                    return render(request,'custom_admin/sales_report_.html',context)
            else:
                messages.warning(request,"Nothing Found!!")
        if request.POST.get('date1'):
            date1 = request.POST.get('date1')
            date2 = request.POST.get('date2')
            data_range = OrderProduct.objects.filter(created_at__gte=date1,created_at__lte=date2)
            if data_range:
                if SalesReport.objects.all():
                    SalesReport.objects.all().delete()
            
                    for i in data_range:
                        sales = SalesReport()
                        sales.productName = i.product.product_name
                        sales.categoryName = i.product.category.category_name
                        sales.date = i.created_at
                        sales.quantity = i.quantity
                        sales.productPrice = i.product_price
                        sales.save()
                    sales = SalesReport.objects.all()
                    total = SalesReport.objects.all().aggregate(Sum('productPrice'))
                    context = { 'sales':sales,'total':total['productPrice__sum']}
                    return render(request,'custom_admin/sales_report_.html',context)
                else:
                    for i in data_range:
                        sales = SalesReport()
                        sales.productName = i.product.product_name
                        sales.categoryName = i.product.category.category_name
                        sales.date = i.created_at
                        sales.quantity = i.quantity
                        sales.productPrice = i.product_price
                        sales.save()
                    sales = SalesReport.objects.all()
                    total = SalesReport.objects.all().aggregate(Sum('productPrice'))
                    context = { 'sales':sales,'total':total['productPrice__sum']}
                    return render(request,'custom_admin/sales_report_.html',context)
            else:
                messages.warning(request,"Nothing Found!!")
    if data:
        if SalesReport.objects.all():
            SalesReport.objects.all().delete()
            for i in data:
                sales = SalesReport()
                sales.productName = i.product.product_name
                sales.categoryName = i.product.category.category_name
                sales.date = i.created_at
                sales.quantity = i.quantity
                sales.productPrice = i.product_price
                sales.save()
            sales = SalesReport.objects.all()
            total = SalesReport.objects.all().aggregate(Sum('productPrice'))
            context = { 'sales':sales,'total':total['productPrice__sum']}
            return render(request,'custom_admin/sales_report_.html',context)

        else:
            for i in data:
                sales = SalesReport()
                sales.productName = i.product.product_name
                sales.categoryName = i.product.category.category_name
                sales.date = i.created_at
                sales.quantity = i.quantity
                sales.productPrice = i.product_price
                sales.save()
            sales = SalesReport.objects.all()
            total = SalesReport.objects.all().aggregate(Sum('productPrice'))
            context = { 'sales':sales,'total':total['productPrice__sum']}
            return render(request,'custom_admin/sales_report_.html',context)
        
    else:
        messages.warning(request,"Nothing Found!!")
    
    return render(request,'custom_admin/sales_report_.html')


@login_required(login_url='admin_login')
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='admin_login')
def export_to_excel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['content-Disposition'] = 'attachment; filename="sales.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sales Report') #this will generate a file named as sales Report

     # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Product Name','Category','Price','Quantity', ]

    for col_num in range(len(columns)):
        # at 0 row 0 column
        ws.write(row_num, col_num, columns[col_num], font_style)

    
    font_style = xlwt.XFStyle()
    total = 0

    rows = SalesReport.objects.values_list(
        'productName','categoryName', 'productPrice', 'quantity')
    for row in rows:
        total +=row[2]
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    row_num += 1
    col_num +=1
    ws.write(row_num,col_num,total,font_style)

    wb.save(response)

    return response

# @never_cache
@login_required(login_url='admin_login')
def export_to_pdf(request):
    prod = Product.objects.all()
    order_count = []
    # for i in prod:
    #     count = SalesReport.objects.filter(product_id=i.id).count()
    #     order_count.append(count)
    #     total_sales = i.price*count
    sales = SalesReport.objects.all()
    total_sales = SalesReport.objects.all().aggregate(Sum('productPrice'))



    template_path = 'custom_admin/sales_pdf.html'
    context = {
        'brand_name':prod,
        'order_count':sales,
        'total_amount':total_sales['productPrice__sum'],
    }
    
    # csv file can also be generated using content_type='application/csv
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response