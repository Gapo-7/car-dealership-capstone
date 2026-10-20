from .models import CarMake, CarModel


def initiate():
    """Add sample makes and models used by the review form and admin lab."""
    examples = {
        'Audi': [('A4', 'Sedan', 2020), ('Q5', 'SUV', 2021)],
        'BMW': [('330i', 'Sedan', 2022), ('X3', 'SUV', 2023)],
        'Ford': [('Escape', 'SUV', 2021), ('Mustang', 'Coupe', 2022)],
        'Toyota': [('Camry', 'Sedan', 2023), ('RAV4', 'SUV', 2022)],
    }
    for name, models in examples.items():
        make, _ = CarMake.objects.get_or_create(name=name, defaults={'description': f'{name} cars'})
        for model_name, model_type, year in models:
            CarModel.objects.get_or_create(car_make=make, name=model_name, year=year,
                                           defaults={'type': model_type})
