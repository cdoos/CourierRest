from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from couriers.serializers import CouriersDetailSerializer, OrderDetailSerializer, CourierOrderSerializer
from couriers.models import Courier, Order, RegionTime
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist
import datetime


def string_to_time(time):
    times = time.split('-')
    return [datetime.datetime.strptime(times[0], '%H:%M'), datetime.datetime.strptime(times[1], '%H:%M')]


# class CouriersListView(generics.ListAPIView):
#     serializer_class = CouriersDetailSerializer
#     queryset = Courier.objects.all()
#
#
# class OrdersListView(generics.ListAPIView):
#     serializer_class = OrderDetailSerializer
#     queryset = Order.objects.all()


@api_view(['POST'])
def courier_create(request):
    serializer = CouriersDetailSerializer(data=request.data['data'], many=True)
    if serializer.is_valid():
        serializer.save()
        couriers = OrderedDict()
        couriers['couriers'] = []
        for i in range(len(request.data['data'])):
            courier_id = OrderedDict()
            courier_id['id'] = request.data['data'][i]['courier_id']
            couriers['couriers'].append(courier_id)
        return Response(couriers, status=status.HTTP_201_CREATED)
    else:
        validation_error = OrderedDict()
        validation_error['validation_error'] = OrderedDict()
        validation_error['validation_error']['couriers'] = []
        for i in range(len(request.data['data'])):
            courier_id = OrderedDict()
            courier_id['id'] = request.data['data'][i]['courier_id']
            serializer = CouriersDetailSerializer(data=request.data['data'][i])
            if not serializer.is_valid():
                validation_error['validation_error']['couriers'].append(courier_id)
        return Response(validation_error, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
def courier_get_or_patch(request, pk):
    if request.method == 'PATCH':
        try:
            courier = Courier.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CouriersDetailSerializer(courier, data=request.data, partial=True)
        if serializer.is_valid() and request.data.get("courier_id") is None:
            serializer.save()
            orders = [i for i in courier.assigned_orders]
            for courier_order in orders:
                order = Order.objects.get(pk=courier_order)
                fits = True
                if order.region not in courier.regions or (
                    courier.courier_type == 'bike' and order.weight > 15) or (
                        courier.courier_type == 'foot' and order.weight > 10):
                    fits = False
                else:
                    if len(courier.working_hours) == 0:
                        fits = False
                    for working_time in courier.working_hours:
                        courier_time = string_to_time(working_time)
                        for delivery_time in order.delivery_hours:
                            order_time = string_to_time(delivery_time)
                            if courier_time[0] > order_time[1] or courier_time[1] < order_time[0]:
                                fits = False
                                break
                        if not fits:
                            break
                if not fits:
                    courier.assigned_orders.remove(order.order_id)
                    order.courier_assigned = 0
                    order.save()
            courier.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            courier = Courier.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        response = OrderedDict()
        response['courier_id'] = courier.courier_id
        response['courier_type'] = courier.courier_type
        response['regions'] = courier.regions
        response['working_hours'] = courier.working_hours
        average_times = []
        for region_time in courier.region_time.all():
            if len(region_time.times) > 0:
                average = 0
                for time in region_time.times:
                    average = average + time
                average = int(average / len(region_time.times))
                average_times.append(average)
        if len(average_times) > 0:
            average_min = min(average_times)
            rating = (3600 - min(average_min, 3600)) / 3600 * 5
            response['rating'] = rating
        response['earnings'] = courier.earnings
        return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def order_create(request):
    serializer = OrderDetailSerializer(data=request.data['data'], many=True)
    if serializer.is_valid():
        serializer.save()
        orders = OrderedDict()
        orders['orders'] = []
        for i in range(len(request.data['data'])):
            order_id = OrderedDict()
            order_id['id'] = request.data['data'][i]['order_id']
            orders['orders'].append(order_id)
        return Response(orders, status=status.HTTP_201_CREATED)
    else:
        validation_error = OrderedDict()
        validation_error['validation_error'] = OrderedDict()
        validation_error['validation_error']['orders'] = []
        for i in range(len(request.data['data'])):
            order_id = OrderedDict()
            order_id['id'] = request.data['data'][i]['order_id']
            serializer = OrderDetailSerializer(data=request.data['data'][i])
            if not serializer.is_valid():
                validation_error['validation_error']['orders'].append(order_id)
        return Response(validation_error, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def order_assign(request):
    try:
        courier = Courier.objects.get(pk=request.data['courier_id'])
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    orders = Order.objects.all()
    orders_exist = False
    time_now = datetime.datetime.utcnow().isoformat()[:-4] + 'Z'
    if len(courier.assigned_orders) > 0:
        orders_exist = True
    for i in range(len(orders)):
        if orders[i].courier_assigned == 0 and orders[i].region in courier.regions and (
                courier.courier_type == 'car' or (courier.courier_type == 'bike' and orders[i].weight <= 15)
                or (courier.courier_type == 'foot' and orders[i].weight <= 10)):
            ok = False
            for j in range(len(courier.working_hours)):
                time = courier.working_hours[j].split('-')
                courier_start = datetime.datetime.strptime(time[0], '%H:%M').time()
                courier_end = datetime.datetime.strptime(time[1], '%H:%M').time()
                for k in range(len(orders[i].delivery_hours)):
                    time = orders[i].delivery_hours[k].split('-')
                    order_start = datetime.datetime.strptime(time[0], '%H:%M').time()
                    order_end = datetime.datetime.strptime(time[1], '%H:%M').time()
                    if courier_start <= order_end and courier_end >= order_start:
                        courier.assigned_orders.append(orders[i].order_id)
                        orders[i].courier_assigned = courier.courier_id
                        if not courier.region_time.filter(region=orders[i].region):
                            region = RegionTime.objects.create(region=orders[i].region)
                            if orders_exist:
                                region.last_finished_time = courier.assigned_time
                            else:
                                region.last_finished_time = time_now
                            region.save()
                            courier.region_time.add(region)
                        orders[i].save()
                        ok = True
                        break
                if ok:
                    break
    response = OrderedDict()
    response['orders'] = []
    if not orders_exist:
        if len(courier.assigned_orders) > 0:
            for order in courier.assigned_orders:
                id_order = OrderedDict()
                id_order['id'] = order
                response['orders'].append(id_order)
            response['assign_time'] = time_now
            courier.assigned_time = time_now
    else:
        if len(courier.assigned_orders) > 0:
            for order in courier.assigned_orders:
                id_order = OrderedDict()
                id_order['id'] = order
                response['orders'].append(id_order)
            response['assign_time'] = courier.assigned_time
    courier.save()
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def order_complete(request):
    serializer = CourierOrderSerializer(data=request.data)
    if serializer.is_valid():
        try:
            courier = Courier.objects.get(pk=request.data['courier_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        order_id = request.data['order_id']
        if order_id in courier.assigned_orders:
            region = Order.objects.filter(pk=order_id).first().region
            finished_time = datetime.datetime.fromisoformat(serializer.data['complete_time'])
            region_time = courier.region_time.get(region=region)
            region_time.times.append((finished_time - region_time.last_finished_time).total_seconds())
            region_time.last_finished_time = serializer.data['complete_time']
            region_time.save()
            courier.assigned_orders.remove(request.data['order_id'])
            Order.objects.filter(pk=request.data['order_id']).delete()
            if courier.courier_type == 'foot':
                courier.earnings = courier.earnings + 500 * 2
            elif courier.courier_type == 'bike':
                courier.earnings = courier.earnings + 500 * 5
            elif courier.courier_type == 'car':
                courier.earnings = courier.earnings + 500 * 9
            courier.save()
            response = OrderedDict()
            response['order_id'] = order_id
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
