from django.contrib import admin
from .models import CarMake, CarModel, Review


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "car_make", "type", "year")
    list_filter = ("car_make", "type", "year")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("dealer_id", "name", "sentiment", "created_at")
