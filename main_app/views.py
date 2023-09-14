from django.shortcuts import render, redirect

# old finch list - will add new via admin portal/models
# finches = [
#   {'name': 'Lilo', 'breed': 'house', 'description': 'furry little demon', 'age': 3},
#   {'name': 'Zach', 'breed': 'zebra', 'description': 'gentle and loving', 'age': 2},
# ]
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Finch, Toy
from .forms import FeedingForm


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
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    id_list = finch.toys.all().values_list('id')
    toys_finch_doesnt_have = Toy.objects.exclude(id__in=id_list)
    return render(request, 'finches/detail.html', { 'finch': finch, 'feeding_form': feeding_form, 'toys': toys_finch_doesnt_have })

def add_feeding(request, finch_id):
    # create a ModelForm instance using the data in request.POST
    form = FeedingForm(request.POST)
    # validate the form
    if form.is_valid():
      # don't save the form to the db until it
      # has the cat_id assigned
        new_feeding = form.save(commit=False)
        new_feeding.finch_id = finch_id
        new_feeding.save()
    return redirect('detail', finch_id=finch_id)

def assoc_toy(request, finch_id, toy_id):
    # Note that you can pass a toy's id instead of the whole toy object
    Finch.objects.get(id=finch_id).toys.add(toy_id)
    return redirect('detail', finch_id=finch_id)

def unassoc_toy(request, finch_id, toy_id):
    # Note that you can pass a toy's id instead of the whole toy object
    Finch.objects.get(id=finch_id).toys.remove(toy_id)
    return redirect('detail', finch_id=finch_id)

class FinchCreate(CreateView):
    model = Finch
    fields = ['name', 'breed', 'description', 'age']

class FinchUpdate(UpdateView):
    model = Finch
    fields = ['breed', 'description', 'age']

class FinchDelete(DeleteView):
    model = Finch
    success_url = '/finches'

# ToyList
class ToyList(ListView):
    model = Toy
    template_name = 'toys/index.html'

# ToyDetail
class ToyDetail(DetailView):
    model = Toy
    template_name = 'toys/detail.html'

# ToyCreate
class ToyCreate(CreateView):
    model = Toy
    fields = ['name', 'color']

    def form_valid(self, form):
        return super().form_valid(form)
    
# ToyUpdate
class ToyUpdate(UpdateView):
    model = Toy
    fields = ['name', 'color']

# ToyDelete
class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys/'