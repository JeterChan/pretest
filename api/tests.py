from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Order, Product, OrderItem

# Create your tests here.

class OrderTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/import-order/'
        # 建立 Product 資料
        self.product1 = Product.objects.create(name="Product A", price=100)
        self.product2 = Product.objects.create(name="Product B", price=50)

        self.valid_payload = {
            "access_token": "omni_pretest_token",
            "order_number": "ORD0001",
            "total_price": "200.50",
            "created_time": "2025-07-12T15:30:00",
            "items": [
                {
                    "product_id": self.product1.id,
                    "quantity": 2,
                    "unit_price": str(self.product1.price)  # 使用 product.price
                },
                {
                    "product_id": self.product2.id,
                    "quantity": 1,
                    "unit_price": str(self.product2.price) # 使用 product.price
                }
            ]
        }
        self.invalid_token_payload = {
            **self.valid_payload, # 複製 valid_payload 內容
            "access_token": "invalid_token"
        }

    # 測試建立一個有效的 order
    def test_create_order_with_valid_data(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)
        self.assertEqual(Order.objects.first().order_number, "ORD0001")

        order = Order.objects.first()
        items = order.items.all()
        # 測試 orderItem 是不是屬於正確的 order
        self.assertEqual(items[0].order.order_number, "ORD0001")
        self.assertEqual(items[1].order.order_number, "ORD0001")

        # 測試 orderItem 的 product, unit_price, quantity 是否正確
        self.assertEqual(items[0].product.name, self.product1.name)
        self.assertEqual(items[0].unit_price, self.product1.price)
        self.assertEqual(items[0].quantity, 2)
        self.assertEqual(items[1].product.name, self.product2.name)
        self.assertEqual(items[1].unit_price, self.product2.price)
        self.assertEqual(items[1].quantity, 1)
    
    # 測試不正確的 access token
    def test_invalid_access_token(self):
        response = self.client.post(self.url, self.invalid_token_payload, format='json')
        self.assertEqual(response.status_code, 401)

    # 測試重複的 order_number
    def test_duplicate_order_number(self):
        # 建立第一筆order
        self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(Order.objects.count(), 1)

        # 用相同的order_number建立第二筆order
        response = self.client.post(self.url, self.valid_payload, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Order with this order_number already exists")

class CreateProductTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/create-products/'
        self.valid_payload = {
            "access_token": "omni_pretest_token",
            "name": "Test Product",
            "price": "99.99",
            "description": "This is a test product."
        }
        self.invalid_payload_missing_payloads = {
            **self.valid_payload, # 複製 valid_payload 內容
            "name": ""  # 缺少必要的 name 欄位   
        }
    # 測試建立商品成功
    def test_create_product_with_valid_data(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.first().name, "Test Product")

    # 測試建立商品失敗，缺少必要欄位
    def test_create_product_missing_fields(self):
        response = self.client.post(self.url, self.invalid_payload_missing_payloads, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    # 測試建立商品失敗，重複的商品名稱
    def test_create_product_duplicate_name(self):
        self.client.post(self.url, self.valid_payload, format='json')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], 'Product with this name already exists')

class GetProductsTestCase(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name="A", price='10.00', description="Product A")
        self.product2 = Product.objects.create(name="B", price='20.00', description="Product B")
        self.url = "/api/products/"

    def test_get_products_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('products', data)
        self.assertEqual(len(data['products']), 2)
        self.assertEqual(data['products'][0]['name'], self.product1.name)
        self.assertEqual(data['products'][0]['price'], self.product1.price)
        self.assertEqual(data['products'][0]['description'], self.product1.description)
        self.assertEqual(data['products'][1]['name'], self.product2.name)
        self.assertEqual(data['products'][1]['price'], self.product2.price)
        self.assertEqual(data['products'][1]['description'], self.product2.description)
