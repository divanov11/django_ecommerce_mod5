from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.name


class Category(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True, blank=True)
	parent = models.ForeignKey(
		'self',
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		related_name='children'
	)
	is_department = models.BooleanField(default=False)
	
	class Meta:
		ordering = ('name',)
		verbose_name_plural = 'categories'
		
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)
		
	def __str__(self):
		return self.name

def get_default_category():
	return Category.objects.get_or_create(
		name='Uncategorized',
		slug='uncategorized'
	)[0].id

class Product(models.Model):
	name = models.CharField(max_length=200, null=True)
	price = models.FloatField()
	digital = models.BooleanField(default=False, null=True, blank=True)
	image = models.ImageField(null=True, blank=True)
	category = models.ForeignKey(
		Category, 
		on_delete=models.SET_NULL, 
		null=True,
		blank=True
	)
	brand = models.CharField(
		max_length=200,
		null=True,
		blank=True,
		default="Unbranded"
	)
	description = models.TextField(
		null=True,
		blank=True,
		default="No description available"
	)
	is_available = models.BooleanField(
		default=True
	)
	created_date = models.DateTimeField(
		auto_now_add=True,
		null=True
	)
	modified_date = models.DateTimeField(
		auto_now=True,
		null=True
	)
	stock = models.IntegerField(default=100)
	sku = models.CharField(
		max_length=100,
		null=True,
		blank=True,
		unique=True
	)

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

	def decrease_stock(self, quantity):
		if self.stock >= quantity:
			self.stock -= quantity
			self.save()
			return True
		return False

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address