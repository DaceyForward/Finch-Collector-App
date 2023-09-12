from django.shortcuts import render

finches = [
  {'name': 'Lilo', 'breed': 'house', 'description': 'furry little demon', 'age': 3},
  {'name': 'Zach', 'breed': 'zebra', 'description': 'gentle and loving', 'age': 2},
]

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
  return render(request, 'finches/index.html', {'finches': finches})