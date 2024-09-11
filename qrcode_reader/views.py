from django.http.response import JsonResponse
from pyquery import PyQuery  
from qreader import QReader
from home.models import Expense, Product, ProductCode, CartItem, Establishment
from datetime import datetime
import cv2
import json
import numpy as np
import base64
import requests
import re

def process_expense_qrcode(request):
    data_url = request.POST['image']
    image_array = data_url_to_image_array(data_url)

    url, error = validate_qrcode(image_array)
    if error is not None:
        return error
    
    expense_dict, error = processQrcodeData(url)
    
    if error is not None:
        return error
    
    expense_json = json.dumps(expense_dict)
    return JsonResponse({ 'created': True, 'data' : expense_json}, status= 200)

def validate_qrcode(image_array):
    detector = QReader()
    try:

        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        data = detector.detect_and_decode(image,is_bgr=True) 

        if len(data) > 0:
            data = data[0]

        if data: 
            return (data, None)
        
        print('No QR code detected')
        return (None, JsonResponse({'created': False, 'error': 'No QR code detected'}, status = 400))
    
    except Exception as e: 
        print(str(e))
        return (None, JsonResponse({'created': False, 'error': 'Error decoding QR Code'}, status = 500))
        
def data_url_to_image_array(data_url):
    if data_url.startswith('data:image'):
        data_url = data_url.split(',')[1]

    image_data = base64.b64decode(data_url)
    image_array = np.frombuffer(image_data, np.uint8)

    return image_array

def processQrcodeData(url):
    response = requests.get(url)

    if not response.ok :
        return (None, JsonResponse({'message': 'error'}, status = response.status_code))

    html_content = response.content.decode("utf-8")

    expense_info = get_expense_info(html_content)

    establishment, _ = Establishment.objects.get_or_create(
        name= expense_info['establishment']
        )

    expense, expense_created = Expense.objects.get_or_create(
        establishment = establishment,
        date= datetime.strptime(expense_info['date'], "%d/%m/%Y"),
        cost= expense_info['total_cost']
        )
    
    if not expense_created:
        return (None, JsonResponse({'created': False, 'error': 'Object already exists'}, status = 409))

    for p in expense_info['products']:
        product, _ = Product.objects.get_or_create(
            name= p['name'],
            unit= p['unit'],
            )
        
        ProductCode.objects.get_or_create(
            code= p['code'],
            product= product,
            establishment = establishment
        )
        
        CartItem.objects.get_or_create(
            expense= expense,
            product= product,
            quantity= p['quantity'],
            unit_price= p['unit_price']
        )

    return (expense.to_json(), None)


def get_expense_info(html_content):
    pq = PyQuery(html_content)

    expense = {}
    establishment = pq('div#u20').text()
    expense['establishment']  = establishment

    table = pq('table#tabResult')
    receipt_info = pq('div#infos').find('div').eq(0).text()
    date_match  = re.search(r'Emissão: \b(\d{2}/\d{2}/\d{4})\b', receipt_info)
    expense['date']  = date_match.group(1) if date_match else None


    columns = [c.text() for c in table('tr td').items()]
    products = []
    for product in range(0, len(columns), 2):
        item = columns[product]
        value = columns[product + 1]
        description_match = re.search(r'^(.*) \(Código:', item)
        code_match = re.search(r'Código: (\d+)', item)
        quantity_match = re.search(r'Qtde\.:\s*(\d+(?:,\d+)?)', item)
        unit_match = re.search(r'UN: (\w{2})', item)
        unit_price_match = re.search(r'Vl\. Unit\.\: \xa0 (\d+,\d+)', item)
        total_price_match = re.search(r'Vl\. Total\n(\d+,\d+)', value)
        
        products.append({
            "name": description_match.group(1).strip() if description_match else None,
            "code": code_match.group(1).strip() if code_match else None,
            "quantity": float(quantity_match.group(1).strip().replace(',', '.')) if quantity_match else None,
            "unit": unit_match.group(1).strip() if unit_match else None,
            "unit_price": convert_price(unit_price_match.group(1).strip()) if unit_price_match else None,
            "total_price": convert_price(total_price_match.group(1).strip()) if total_price_match else None
        }) 
    expense['products'] = products

    expense['total_cost'] = sum([p['total_price'] for p in products if p['total_price'] is not None])
    return expense


def convert_price(price_str):
    return float(price_str.replace(',', '.'))