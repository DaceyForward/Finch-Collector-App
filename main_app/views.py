from django.shortcuts import render

# old finch list - will add new via admin portal/models
# finches = [
#   {'name': 'Lilo', 'breed': 'house', 'description': 'furry little demon', 'age': 3},
#   {'name': 'Zach', 'breed': 'zebra', 'description': 'gentle and loving', 'age': 2},
# ]
from django.views.generic.edit import CreateView
from .models import Finch

# Create your views here.

# Define the home view
def home(request):
  # Include an .html file extension - unlike when rendering EJS templates
    return render(request, 'home.html')

# Define the about view
def about(request):
    return render(request, 'about.html')

# Add index view
def finches_index(request):
  # We pass data to a template very much like we did in Express!
    finches = Finch.objects.all() # Retrieve all cats
    return render(request, 'finches/index.html', { 'finches': finches })

def finches_detail(request, finch_id):
    finch = Finch.objects.get(id=finch_id)
    return render(request, 'finches/detail.html', { 'finch': finch })

class FinchCreate(CreateView):
  model = Finch
  fields = '__all__'