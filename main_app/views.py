import requests
import os
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import NewsSource, Dose, FavoriteDose, BookmarkDose

BASE_URL = 'https://api.thenewsapi.com/v1/news/top?'

def fetch_doses():
    url = f'{BASE_URL}api_token={os.environ["API_KEY"]}'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(data)  # Debug: print the full response to check its structure

        doses = data.get('data', [])
        
        if isinstance(doses, list):  # Ensure doses is a list
            for dose in doses:
                if isinstance(dose, dict):  # Ensure dose is a dictionary
                    # Adjusted to reflect the response structure
                    source_name = dose['source']  # Source is now a string

                    # Get or create the source (assuming you want to keep track of sources)
                    source, created = NewsSource.objects.get_or_create(
                        name=source_name,
                    )

                    Dose.objects.create(
                        source=source,
                        author=dose.get('author'),  # 'author' may not be in the response; handle accordingly
                        title=dose.get('title'),
                        description=dose.get('description'),
                        url=dose.get('url'),
                        url_to_image=dose.get('image_url'),
                        published_at=parse_datetime(dose['published_at']),
                        content=dose.get('snippet'),  # Using snippet as content
                        category=dose['categories'][0] if dose.get('categories') else 'general'  # Get the first category or default
                    )
                else:
                    print(f"Unexpected dose format: {dose}")  # Log unexpected formats
        else:
            print("Doses is not a list.")
    else:
        print(f"Error fetching doses: {response.status_code} - {response.text}")


# Create your views here.
class Home(LoginView):
    template_name = 'home.html'


def dose_list (request):
    # fetch_doses() // try this again tomorrow to test if new top articles are fetched
    doses = Dose.objects.all()[:3]
    print(doses)
    return render(request, 'doses/index.html', {'doses': doses})


# @login_required 
def favorite_doses_list(request):
    user = request.user
    favorite_doses = FavoriteDose.objects.filter(user=user).select_related('dose')
    return render(request, 'doses/favorite_doses_list.html', {'favorite_doses': favorite_doses})


def bookmark_doses_list(request):
    return render(request, 'doses/bookmark_doses_list.html')


# refactor to class based view --> create a model, create a form, create a view, create template, map URL 
def upload(request):
    return render(request, 'main_app/upload_form.html')
