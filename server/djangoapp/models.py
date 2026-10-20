from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    TYPES = [(value, value) for value in ("Sedan", "SUV", "Wagon", "Coupe", "Truck", "Hatchback")]
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPES)
    year = models.IntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2023)])

    class Meta:
        unique_together = ("car_make", "name", "year")

    def __str__(self):
        return f"{self.car_make} {self.name} ({self.year})"


class Review(models.Model):
    dealer_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=150)
    review = models.TextField()
    purchase = models.BooleanField(default=True)
    purchase_date = models.DateField()
    car_make = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_year = models.IntegerField()
    sentiment = models.CharField(max_length=20, default="neutral")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for dealer {self.dealer_id} by {self.name}"
