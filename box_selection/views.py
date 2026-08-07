from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Order, OrderItem
from .serializers import OrderSerializer, ShipmentRecommendationSerializer
from .services import update_recommendation


class OrderListCreateAPIView(APIView):
    def get(self, request):
        orders = Order.objects.all().order_by("-created_at")
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        order = serializer.save()
        update_recommendation(order)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        return Response(OrderSerializer(order).data)


class OrderRecommendAPIView(APIView):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        recommendation, _ = update_recommendation(order)
        return Response(ShipmentRecommendationSerializer(recommendation).data)


def order_dashboard(request):
    error_message = None

    if request.method == "POST":
        order_number = request.POST.get("order_number", "").strip()
        customer_name = request.POST.get("customer_name", "").strip()

        if order_number and customer_name:
            if Order.objects.filter(order_number=order_number).exists():
                error_message = f"Order number '{order_number}' already exists. Please use a different one."
            else:
                order = Order.objects.create(order_number=order_number, customer_name=customer_name)
                has_items = False
                for product in Product.objects.all():
                    try:
                        qty = int(request.POST.get(f"qty_{product.id}", "0"))
                    except ValueError:
                        continue
                    if qty > 0:
                        OrderItem.objects.create(order=order, product=product, quantity=qty)
                        has_items = True

                if has_items:
                    update_recommendation(order)
                    return redirect(f"/?order_id={order.id}")

                order.delete()
                error_message = "Please select at least one product with a quantity greater than zero."
        else:
            error_message = "Order number and customer name are required."

    selected_order = None
    recommendation = None
    order_id = request.GET.get("order_id")
    if order_id:
        selected_order = get_object_or_404(Order, pk=order_id)
        recommendation = getattr(selected_order, "recommendation", None)
        if recommendation is None:
            recommendation, _ = update_recommendation(selected_order)

    return render(
        request,
        "box_selection/dashboard.html",
        {
            "products": Product.objects.all(),
            "orders": Order.objects.all().order_by("-created_at"),
            "selected_order": selected_order,
            "recommendation": recommendation,
            "error_message": error_message,
        },
    )