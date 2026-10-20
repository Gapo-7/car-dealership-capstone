from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    path('register', views.registration, name='register'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('get_dealers', views.get_dealerships, name='dealers'),
    path('get_dealers/<str:state>', views.get_dealerships, name='dealers-state'),
    path('dealer/<int:dealer_id>', views.get_dealer_details, name='dealer'),
    path('reviews/dealer/<int:dealer_id>', views.get_dealer_reviews, name='reviews'),
    path('get_cars', views.get_cars, name='cars'),
    path('add_review', views.add_review, name='add-review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
