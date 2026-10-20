import json
from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarModel, Review
from .restapis import analyze_review_sentiments, get_request, post_review


def _payload(request):
    try:
        return json.loads(request.body or b'{}')
    except (ValueError, UnicodeDecodeError):
        return {}


@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data = _payload(request)
    user = authenticate(request, username=data.get('userName'), password=data.get('password'))
    if user is None:
        return JsonResponse({'error': 'Invalid username or password'}, status=401)
    login(request, user)
    return JsonResponse({'userName': user.username, 'firstName': user.first_name,
                         'lastName': user.last_name, 'status': 'Authenticated'})


def logout_request(request):
    logout(request)
    return JsonResponse({'status': 'Logged out'})


@csrf_exempt
def registration(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data = _payload(request)
    required = ('userName', 'firstName', 'lastName', 'email', 'password')
    if any(not data.get(key) for key in required):
        return JsonResponse({'error': 'All five fields are required'}, status=400)
    if len(data['password']) < 8:
        return JsonResponse({'error': 'Password must have at least 8 characters'}, status=400)
    if User.objects.filter(username=data['userName']).exists():
        return JsonResponse({'error': 'Username already exists'}, status=409)
    user = User.objects.create_user(username=data['userName'], email=data['email'],
                                    password=data['password'], first_name=data['firstName'],
                                    last_name=data['lastName'])
    login(request, user)
    return JsonResponse({'userName': user.username, 'firstName': user.first_name,
                         'lastName': user.last_name, 'status': 'Authenticated'}, status=201)


def get_dealerships(request, state=None):
    dealers = get_request('fetchDealers' + (f'/{state}' if state else ''))
    return JsonResponse({'status': 200, 'dealers': dealers})


def get_dealer_details(request, dealer_id):
    return JsonResponse({'status': 200, 'dealer': get_request(f'fetchDealer/{dealer_id}')})


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f'fetchReviews/dealer/{dealer_id}')
    seen = set()
    for item in reviews:
        item['sentiment'] = analyze_review_sentiments(item.get('review', ''))
        seen.add((item.get('name'), item.get('review')))
    for item in Review.objects.filter(dealer_id=dealer_id):
        if (item.name, item.review) in seen:
            continue
        reviews.append({'id': item.pk, 'name': item.name, 'dealership': item.dealer_id,
                        'review': item.review, 'purchase': item.purchase,
                        'purchase_date': item.purchase_date.isoformat(),
                        'car_make': item.car_make, 'car_model': item.car_model,
                        'car_year': item.car_year, 'sentiment': item.sentiment})
    return JsonResponse({'status': 200, 'reviews': reviews})


def get_cars(request):
    cars = [{'CarMake': model.car_make.name, 'CarModel': model.name, 'CarType': model.type,
             'CarYear': model.year} for model in CarModel.objects.select_related('car_make')]
    return JsonResponse({'status': 200, 'CarModels': cars})


@csrf_exempt
def add_review(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    data = _payload(request)
    required = ('dealership', 'review', 'purchase_date', 'car_make', 'car_model', 'car_year')
    if any(not data.get(key) for key in required):
        return JsonResponse({'error': 'Missing review details'}, status=400)
    try:
        purchase_date = date.fromisoformat(data['purchase_date'])
        dealer_id = int(data['dealership'])
        car_year = int(data['car_year'])
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid date, dealer, or car year'}, status=400)
    if not get_request(f'fetchDealer/{dealer_id}'):
        return JsonResponse({'error': 'Dealer not found'}, status=404)
    name = request.user.get_full_name() or request.user.username
    sentiment = analyze_review_sentiments(data['review'])
    review = Review.objects.create(dealer_id=dealer_id, name=name, review=data['review'],
                                   purchase=bool(data.get('purchase', True)),
                                   purchase_date=purchase_date, car_make=data['car_make'],
                                   car_model=data['car_model'], car_year=car_year,
                                   sentiment=sentiment)
    post_review({**data, 'name': name})
    return JsonResponse({'status': 200, 'id': review.pk, 'sentiment': sentiment})
