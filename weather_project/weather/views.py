from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import requests
from .models import SearchHistory, UserSearchHistory


class IndexView(View):
    template_name = 'weather/index.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        weather_data = None
        error = None
        city = request.POST.get('city')

        if city:
            try:
                params = {'q': city, 'units': 'metric', 'lang': 'en', 'appid': '1912624fd49c501f2986b6ff90fd4a0b'}
                response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
                response.raise_for_status()
                res = response.json()

                if 'main' in res and 'temp' in res['main'] and 'weather' in res and len(res['weather']) > 0:
                    weather_data = {
                        'city': city,
                        'temperature': round(res['main']['temp']),
                        'description': res['weather'][0]['description'],
                        'icon': res['weather'][0]['icon']
                    }
                    # Update SearchHistory
                    search_history, created = SearchHistory.objects.get_or_create(city=city)
                    search_history.search_count += 1
                    search_history.save()

                    # Save UserSearchHistory if user is authenticated
                    if request.user.is_authenticated:
                        UserSearchHistory.objects.create(user=request.user, city=city)
                else:
                    error = f"No weather data found for {city}. Please enter a valid city name."

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    error = f"City '{city}' not found. Please enter a valid city name."
                else:
                    error = f"An error occurred while retrieving weather data: {str(e)}"
            except requests.exceptions.RequestException as e:
                error = f"An error occurred while retrieving weather data: {str(e)}"

        context = {
            'weather_data': weather_data,
            'error': error
        }

        return render(request, self.template_name, context)


class SearchHistoryAPI(View):
    def get(self, request):
        search_history = SearchHistory.objects.all()
        data = {entry.city: entry.search_count for entry in search_history}
        return JsonResponse(data)
