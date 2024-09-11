from django.db import models


class Product(models.Model):
    name = models.CharField( max_length= 255)
    unit = models.CharField( max_length= 7)
    def __str__(self):
        return self.name
    
class Establishment(models.Model):
    name = models.CharField( max_length= 255)

    def __str__(self):
        return self.name

class Expense(models.Model):
    establishment = models.ForeignKey(Establishment, null= True , on_delete= models.SET_NULL)
    date = models.DateField()
    cost = models.FloatField()
    products = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return self.name
    
    def to_json(self):
        return {
            'establishment': self.establishment.name if self.establishment else 'N/A',
            'date' : self.date.strftime("%d/%m/%Y"),
            'products' : [p.to_json() for p in self.cart_items.all()],
            'totalCost' : round(self.cost,2)
        }
    
    def __str__(self):
        return f"Expense on {self.date} at {self.establishment}"

class CartItem(models.Model):
    expense = models.ForeignKey(Expense,related_name='cart_items',  on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit_price = models.FloatField()

    def total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.quantity} {self.product.unit} de {self.product.name}"
    
    def to_json(self):
       return {
            'name': self.product.name,
            'unit' : self.product.unit,
            'quantity': self.quantity,
            'unitPrice': self.unit_price,
            'totalPrice': self.total_price(),
        }

class ProductCode(models.Model):
    code = models.BigIntegerField(unique=True)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Code {self.code} for {self.product.name}"
