import requests
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.contrib.sessions.models import Session
from .models import SearchHistory

def index(request):
    city = request.session.get('last_city')
    weather_data = None
    error = None

    if request.method == 'POST':
        city = request.POST.get('city')

        if city:
            params = {
                'q': city,
                'units': 'metric',
                'lang': 'en',
                'appid': '1912624fd49c501f2986b6ff90fd4a0b'
            }
            response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)

            if response.status_code == 200:
                res = response.json()
                weather_data = {
                    'city': city,
                    'temperature': round(res['main']['temp']),
                    'description': res['weather'][0]['description'],
                    'icon': res['weather'][0]['icon']
                }
                request.session['last_city'] = city

                # Update search history
                history, created = SearchHistory.objects.get_or_create(city=city)
                history.search_count += 1
                history.save()
            else:
                error = "Could not retrieve weather data for the specified city."
        else:
            error = "Please enter a city name."

    context = {'weather_data': weather_data, 'error': error, 'last_city': city}
    return render(request, 'weather/index.html', context)

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Такой страницы нет</h1>')
