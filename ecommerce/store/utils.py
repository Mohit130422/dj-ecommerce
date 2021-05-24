import json
from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('cart:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
    cartitems = order['get_cart_item']

    for i in cart:
        try:
            cartitems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_item'] += cart[i]['quantity']
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartitems': cartitems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False, )
        items = order.order_item_set.all()
        cartitems = order.get_cart_item
    else:
        cookieData = cookieCart(request)
        cartitems = cookieData['cartitems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartitems': cartitems, 'order': order, 'items': items}


def guestorder(request, data, customer=customer):
    print("User is not authenticated...")
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']
    customer,created = customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )
    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = Order_item.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer, order
