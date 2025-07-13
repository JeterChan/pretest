from django.db import models


# Create your models here.
class Order(models.Model):
    # Add your model here
    order_number = models.CharField(max_length=20, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.order_number} - Total: {self.total_price}"

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE) # 保留product欄位是為了反向查詢, ex. 查詢該 product 的銷售紀錄
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.FloatField()

    def __str__(self):
        return f"{self.quantity} x {self.unit_price}"