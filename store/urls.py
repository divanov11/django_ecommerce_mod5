from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

	path('product/<int:product_id>/', views.product_detail, name="product_detail"),

	path('register/', views.register_user, name='register'),
	path('login/', views.login_view, name='login'),
	path('login-register-choice/', views.login_register_choice, name='login_register_choice'),
	path('create-payment-intent/', views.create_payment_intent, name='create-payment-intent'),

]