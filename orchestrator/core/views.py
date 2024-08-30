import requests
from json import JSONDecodeError
from rest_framework import views
from rest_framework.response import Response

class PurchaseProductView(views.APIView):

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id', 0)
        quantity = request.data.get('quantity', 0)
        price = request.data.get('price', 0)

        # 1. Verificar disponibilidade do estoque no Inventory Service
        inventory_response = requests.get("http://localhost:8002/api/inventory/check/", json={
            'product_id': product_id,
            'quantity': quantity
        })
        try:
            inventory_response_data = inventory_response.json()
        except JSONDecodeError:
            return Response(data={"error": "There was an error contacting inventory service"}, status=500)
        
        not_enough_product_amount = inventory_response.status_code != 200
        if not_enough_product_amount:
            return Response(data=inventory_response_data, status=inventory_response.status_code)

        # 2. Criar o pedido no Product Service
        try:
            order_response = requests.post('http://localhost:8001/api/orders/', json={
                'product_id': product_id,
                'quantity': quantity
            })
            order_response.raise_for_status()

            if order_response.status_code != 200:
                return Response({'error': 'Failed to create order'}, status=400)

        except requests.RequestException:
            return Response({'error': 'Failed to create order'}, status=500)

        order_id = order_response.json().get('order_id')

        # 3. Reservar o inventário no Inventory Service
        try:
            inventory_reserve_response = requests.post('http://localhost:8002/api/inventory/reserve/', json={
                'product_id': product_id,
                'quantity': quantity
            })
            inventory_reserve_response.raise_for_status()

            if inventory_reserve_response.status_code != 200:
                return Response({'error': 'Failed to reserve inventory'}, status=400)
            
        except requests.RequestException:
            return Response({'error': 'Failed to reserve inventory'}, status=500)

        

        #4. Processar o pagamento no Payment Service
        try:
            payment_processing_response = requests.post('http://localhost:8003/api/payment/', json={
                'order_id': order_id,
                'value': int(price) * int(quantity)
            })

            payment_processing_response.raise_for_status()
        except requests.RequestException:
            try:
                inventory_return_response = requests.put('http://localhost:8002/api/inventory/return/', json={
                        'product_id': product_id,
                        'quantity': quantity
                    })
                inventory_return_response.raise_for_status()
            except requests.RequestException:
                return Response({'error': 'Failed to return item'})
            return Response({ 'error': 'Failed to completed purchase' })

        return Response({'status': 'Purchase completed'})
