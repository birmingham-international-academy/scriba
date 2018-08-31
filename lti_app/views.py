import sys

from django.shortcuts import render


def error_500(request):
    _, exception, _ = sys.exc_info()

    return render(request,'500.html', {'exception': exception})
