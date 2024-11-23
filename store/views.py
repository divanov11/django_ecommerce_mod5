from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.db.models import Q
from .models import * 
from .utils import cookieCart, cartData, guestOrder

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.filter(is_available=True)
	categories = Category.objects.all()
	
	# Filter by category
	category = request.GET.get('category')
	if category:
		products = products.filter(category__slug=category)
	
	# Filter by price range
	min_price = request.GET.get('min_price')
	max_price = request.GET.get('max_price')
	if min_price and max_price:
		products = products.filter(price__gte=min_price, price__lte=max_price)
	
	# Filter by brand
	brand = request.GET.get('brand')
	if brand:
		products = products.filter(brand=brand)
	
	# Search functionality
	search_query = request.GET.get('q')
	if search_query:
		products = products.filter(
			Q(name__icontains=search_query) |
			Q(description__icontains=search_query)
		)
	
	# Sorting
	sort_by = request.GET.get('sort')
	if sort_by == 'price_asc':
		products = products.order_by('price')
	elif sort_by == 'price_desc':
		products = products.order_by('-price')
	elif sort_by == 'newest':
		products = products.order_by('-created_date')
	
	context = {
		'products': products,
		'categories': categories,
		'current_category': category,
		'brands': Product.objects.values_list('brand', flat=True).distinct()
	}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)
def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)
