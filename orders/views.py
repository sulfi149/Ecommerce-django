from django.shortcuts import render,redirect
from cart.models import CartItem
from accounts.models import Address
from .forms import orderForm
from .models import Order,Payment,OrderProduct
from store.models import Product
import datetime
import json
from django.http import JsonResponse
from django.http import FileResponse,Http404
import os
import uuid

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'] )
    
    # store traction details in payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # move the cart items to order product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id  = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variations = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variations)
        order_product.save()
        # reduce the quantity of the product sold
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    # clear the cart item 
    CartItem.objects.filter(user=request.user).delete()

    # send order confirmation mail
    mail_subject = "Thank You for your order!"
    message = render_to_string('orders/order_recieved_email.html',{
                'user' : request.user,
                'order' : order,
                
            })
    to_mail = request.user.email
    send_mail = EmailMessage(mail_subject,message,to = [to_mail])
            
    send_mail.send()
    
    # send order number and transaction id to the send data function
    
    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
        
    }


    return JsonResponse(data)




def place_order(request,total=0,quantity=0):

    current_user = request.user
    address_id = request.POST.get('shipping_address')
    shipping_address = Address.objects.get(user=current_user,id=address_id)
    print(shipping_address)
    # if the cart count is less than 0 then redirect to the store page
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    tax=0
    grand_total =0

    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
    tax = (3*total) /100
    grand_total = total + tax
    if request.method =="POST":
        # get the form 
        
            # initialize the object of the order table
            data = Order()
            data.user = current_user
            data.shipping = shipping_address           
            data.order_total = grand_total
            data.payment_mode = "paypal"
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
             # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'shipping_id':address_id,
            }
            return render(request, 'orders/payments.html', context)
def order_place_cod(request,total=0,quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_item_count = cart_items.count()
    if cart_item_count <= 0:
        return redirect('store')
    tax=0
    grand_total =0

    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
    tax = (3*total) /100
    grand_total = total + tax
    if request.method == "POST":
        address_id = request.POST['cod']
        shipping_address = Address.objects.get(id=address_id)
        data = Order()
        data.user = current_user
        data.shipping = shipping_address
        data.order_total = grand_total
        data.tax = tax
        data.payment_mode = 'Cash On Delivery'
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
             # Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order = order
                #orderproduct.payment = payment
            orderproduct.user = current_user
            orderproduct.product = item.product
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation= cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()
                # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()
                # Clear cart
            CartItem.objects.filter(user=request.user).delete()
            ordered_product = OrderProduct.objects.filter(order_id = order.id)
            invoice_id = uuid.uuid4().hex
            context = {
                'order': order,
                'ordered_product': ordered_product,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'invoice_id' : invoice_id
            }
            return render(request,'orders/order_complete.html',context)








def order_complete(request,order_id=None):
    if request.method == "POST":
        order_id = order_id
        print(order_id)
        
    else:
        order_number = request.GET.get('order_number')
        transID = request.GET.get('payment_id')

        try:
            order = Order.objects.get(order_number=order_number,is_ordered=True)
            ordered_product = OrderProduct.objects.filter(order_id = order.id)
            sub_total = 0
            for _ in ordered_product:
                sub_total += _.product_price * _.quantity

            payment = Payment.objects.get(payment_id = transID)

            context = {
                'order' : order,
                'ordered_product' : ordered_product,
                'order_number' : order.order_number,
                'transID' : payment.payment_id,
                'payment' : payment,
                'sub_total': sub_total
            }
            return render(request,'orders/order_complete.html',context)
        except (Payment.DoesNotExist,Order.DoesNotExist):
            return redirect('home')
    return render(request,'orders/order_complete.html')

