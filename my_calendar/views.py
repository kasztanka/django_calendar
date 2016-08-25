from django.shortcuts import render


def index(request):
    return render(request, "my_calendar/index.html")