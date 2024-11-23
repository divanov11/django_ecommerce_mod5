from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
import datetime
from django.db.models import Q
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomerForm
import stripe
from django.conf import settings

# Add these settings at the top of the file
stripe.api_key = settings.STRIPE_SECRET_KEY

def store(request):
	data = cartData(request)
	cartItems = data['cartItems']
	
	# Start with all products
	products = Product.objects.filter(is_available=True)
	
	# Get all filter parameters
	filters = {}
	category_slug = request.GET.get('category')
	brand = request.GET.get('brand')
	min_price = request.GET.get('min_price')
	max_price = request.GET.get('max_price')
	sort_by = request.GET.get('sort')
	
	# Apply category filter
	if category_slug:
		filters['category'] = category_slug
		try:
			category = Category.objects.get(slug=category_slug)
			if category.is_department:
				subcategories = Category.objects.filter(parent=category)
				products = products.filter(category__in=subcategories)
			else:
				products = products.filter(category=category)
		except Category.DoesNotExist:
			pass
	
	# Apply brand filter
	if brand:
		filters['brand'] = brand
		products = products.filter(brand=brand)
	
	# Apply price filters
	if min_price:
		try:
			filters['min_price'] = min_price
			products = products.filter(price__gte=float(min_price))
		except ValueError:
			pass
	
	if max_price:
		try:
			filters['max_price'] = max_price
			products = products.filter(price__lte=float(max_price))
		except ValueError:
			pass
	
	# Apply sorting
	if sort_by:
		filters['sort'] = sort_by
		if sort_by == 'price_asc':
			products = products.order_by('price')
		elif sort_by == 'price_desc':
			products = products.order_by('-price')
	
	# Get all categories for the sidebar
	main_categories = Category.objects.filter(is_department=True)
	subcategories = Category.objects.filter(is_department=False)
	
	# Get all unique brands
	brands = Product.objects.values_list('brand', flat=True).distinct().order_by('brand')
	
	# Debug print categories
	print("\nMain Categories:")
	for cat in main_categories:
		print(f"- {cat.name} (slug: {cat.slug})")
	
	print("\nSubcategories:")
	for cat in subcategories:
		print(f"- {cat.name} (slug: {cat.slug}, parent: {cat.parent})")
	
	context = {
		'products': products,
		'cartItems': cartItems,
		'main_categories': main_categories,
		'subcategories': subcategories,
		'brands': brands,
		'active_filters': filters,
		'current_category': category_slug,
		'current_brand': brand,
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

	# If user is not authenticated, redirect to login/register choice page
	if not request.user.is_authenticated:
		return redirect('login_register_choice')

	context = {
		'items': items,
		'order': order,
		'cartItems': cartItems,
		'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
	}
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

def product_detail(request, product_id):
	data = cartData(request)
	cartItems = data['cartItems']
	
	product = get_object_or_404(Product, id=product_id)
	
	# Get related products from the same category
	related_products = Product.objects.filter(
		category=product.category
	).exclude(id=product.id)[:4]
	
	context = {
		'product': product,
		'cartItems': cartItems,
		'related_products': related_products,
	}
	return render(request, 'store/product_detail.html', context)

def register_user(request):
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			# Create customer profile
			Customer.objects.create(
				user=user,
				name=user.username,
				email=user.email
			)
			login(request, user)
			return redirect('checkout')
	else:
		form = CustomUserCreationForm()
	return render(request, 'store/register.html', {'form': form})

def login_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('checkout')
	return render(request, 'store/login.html')

def create_payment_intent(request):
	data = cartData(request)
	order = data['order']
	
	intent = stripe.PaymentIntent.create(
		amount=int(order.get_cart_total * 100),  # Convert to cents
		currency='usd',
		metadata={'order_id': order.id}
	)
	
	return JsonResponse({
		'clientSecret': intent.client_secret
	})

def process_order(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		# Handle guest user case
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment complete!', safe=False)

def login_register_choice(request):
	"""View to let users choose between login, register, or guest checkout"""
	# If user is already authenticated, redirect to checkout
	if request.user.is_authenticated:
		return redirect('checkout')
		
	return render(request, 'store/login_register_choice.html')
