from django.urls import path
from couriers import views

app_name = 'courier'
urlpatterns = [
    path('couriers', views.courier_create),
    path('couriers/<int:pk>', views.courier_get_or_patch),
    path('orders', views.order_create),
    path('orders/assign', views.order_assign),
    path('orders/complete', views.order_complete),
    # path('order_list', views.OrdersListView.as_view()),
    # path('courier_list', views.CouriersListView.as_view()),
]
