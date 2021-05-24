from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import *
import datetime
from .utils import cookieCart, cartData, guestorder


# Create your views here.

def store(request):
    data = cartData(request)
    cartitems = data['cartitems']
    products = Product.objects.all()
    context = {'products': products, 'cartitems': cartitems, }
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartitems = data['cartitems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartitems': cartitems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartitems = data['cartitems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartitems': cartitems}
    return render(request, 'store/checkout.html', context)


def updateitem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']
    print('Action:', action)
    print('productID:', productID)

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False, )
    orderitem, created = Order_item.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderitem.quantity = (orderitem.quantity + 1)
    elif action == 'remove':
        orderitem.quantity = (orderitem.quantity - 1)

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()
    return JsonResponse('Item was Added', safe=False)


def processorder(request):
    print('Data:', request.body)
    trasaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False, )

    else:
        customer, order = guestorder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = trasaction_id
    if total == order.get_cart_total:
        order.complete = True
    order.save()
    if order.shipping == True:
        shippingaddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )
    return JsonResponse('Payment complete', safe=False)


def view(request):
    context = {}
    return render(request, 'store/view.html', context)
