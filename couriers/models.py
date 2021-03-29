from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

time_regex = RegexValidator('^([01]?\d|2[0-3]):([0-5]\d)-([01]?\d|2[0-3]):([0-5]\d)$', 'Incorrect time range.')


class RegionTime(models.Model):
    region = models.IntegerField()
    last_finished_time = models.DateTimeField(null=True)
    times = ArrayField(models.IntegerField(), default=list)


class Order(models.Model):
    order_id = models.IntegerField(unique=True, primary_key=True)
    weight = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(50)])
    region = models.IntegerField(validators=[MinValueValidator(1)])
    delivery_hours = ArrayField(models.CharField(validators=[time_regex], max_length=1000))
    courier_assigned = models.IntegerField(default=0)


class Courier(models.Model):
    courier_types = [('foot', 'foot'), ('bike', 'bike'), ('car', 'car')]
    courier_id = models.IntegerField(unique=True, validators=[MinValueValidator(1)], primary_key=True)
    courier_type = models.CharField(choices=courier_types, max_length=4)
    regions = ArrayField(models.IntegerField(validators=[MinValueValidator(1)]))
    working_hours = ArrayField(models.CharField(validators=[time_regex], max_length=1000), blank=True)
    assigned_orders = ArrayField(models.IntegerField(), default=list)
    assigned_time = models.DateTimeField(blank=True, null=True)
    earnings = models.IntegerField(default=0)
    region_time = models.ManyToManyField(RegionTime)
