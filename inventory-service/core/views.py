from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Inventory
from .serializers import InventorySerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    @action(detail=False, methods=['get'], url_path='check')
    def check_inventory(self, request):
        product_id = request.data.get('product_id', 0)
        quantity = int(request.data.get('quantity', 0))

        try:
            inventory = Inventory.objects.get(product_id=product_id)
        except Inventory.DoesNotExist:
            return Response({'error': 'Product not found in inventory'}, status=404)

        if inventory.stock < quantity:
            return Response({'error': 'Not enough inventory'}, status=400)

        serializer = InventorySerializer(inventory)
        return Response({
            'product_id': product_id,
            'product_name': inventory.product.name,
            'stock': serializer.data['stock'],
            'status': 'Sufficient inventory available'
        })

    @action(detail=False, methods=['post'], url_path='reserve')
    def reserve_inventory(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 0))

        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=400)

        try:
            inventory = Inventory.objects.get(product_id=product_id)
        except Inventory.DoesNotExist:
            return Response({'error': 'Product not found in inventory'}, status=404)

        if inventory.stock < quantity:
            return Response({'error': 'Not enough inventory'}, status=400)

        inventory.stock -= quantity
        inventory.save()
        return Response({'message': 'Inventory reserved successfully'})

    @action(detail=False, methods=['put'], url_path='return')
    def return_inventory(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 0))

        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=400)

        try:
            inventory = Inventory.objects.get(product_id=product_id)
        except Inventory.DoesNotExist:
            return Response({'error': 'Product not found in inventory'}, status=404)

        inventory.stock += quantity
        inventory.save()
        return Response({'message': 'Inventory returned successfully'})
