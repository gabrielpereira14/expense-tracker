from django.shortcuts import render
from home.models import Expense

# Create your views here.
def home(request):
    expenses = Expense.objects.all()
    expenses = [ exp.to_json() for exp in expenses]
    return render(request, 'home.html', {"expenses" : expenses})