from django.shortcuts import render
from django.http import HttpResponseBadRequest,JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view
# Create your views here.
from .models import Order,Product, OrderItem
from datetime import datetime
from django.db import IntegrityError
from .decorators import require_token

ACCEPTED_TOKEN = 'omni_pretest_token'

@api_view(['POST'])
@require_token
def import_order(request):
    """ Import order data from request. """
    # 1. 取得並驗證data
    order_number = request.data.get('order_number')
    total_price = request.data.get('total_price')
    created_time = request.data.get('created_time')
    items = request.data.get('items', []) # list of { product_id, product_name, quantity, price } 

    # 錯誤處理, 判斷是否每個 order 需要的值都有傳入
    if not order_number or not total_price or not created_time or not items:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    # 轉換 total_price 為 float, created_time 為 datetime
    try:
        total_price = float(total_price)
        created_time = datetime.fromisoformat(created_time)
    except Exception as e:
        return JsonResponse({'error': 'Invalid data format'}, status=400)

    # 2. 儲存Order至資料庫
    try:
        with transaction.atomic():
            order = Order.objects.create(
                order_number = order_number,
                total_price = total_price,
                created_time = created_time,
            )
        

            # 3. 建立每一筆 OrderItem
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                unit_price = float(item['unit_price'])
                subtotal = unit_price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
    except IntegrityError:
        return JsonResponse({'error': 'Order with this order_number already exists'}, status=400)
    except (Product.DoesNotExist, KeyError, ValueError) as e:
        return JsonResponse({'error': 'Invalid item data or product not found'}, status=400)

    return JsonResponse({'message': 'Order created successfully'}, status=201)

@api_view(['POST'])
@require_token
def create_products(request):
    """ Create a new product. """
    name = request.data.get('name')
    price = request.data.get('price')
    description = request.data.get('description', '')

    if not name or not price:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        product = Product.objects.create(
            name=name,
            price=float(price),
            description=description
        )
    except IntegrityError:
        return JsonResponse({'error': 'Product with this name already exists'}, status=400)
    
    return JsonResponse({'message': 'Product created successfully', 'id':product.id}, status=201)

@api_view(['GET'])
def get_products(request):
    """ get all products. """
    products = Product.objects.all().values('name','price','description')
    return JsonResponse({'products': list(products)}, status=200)
