from django.contrib import admin

from home.models import CartItem, Product, ProductCode, Establishment, Expense
# Register your models here.
admin.site.register(CartItem)
admin.site.register(Product)
admin.site.register(ProductCode)
admin.site.register(Establishment)
admin.site.register(Expense)