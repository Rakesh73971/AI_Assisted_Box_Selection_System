from django.urls import path

from . import views

urlpatterns = [
    path("", views.order_dashboard, name="order_dashboard"),
    path("api/orders/", views.OrderListCreateAPIView.as_view(), name="api_order_list_create"),
    path("api/orders/<int:pk>/", views.OrderDetailAPIView.as_view(), name="api_order_detail"),
    path("api/orders/<int:pk>/recommend/", views.OrderRecommendAPIView.as_view(), name="api_order_recommend"),
]
