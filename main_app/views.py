

from django.shortcuts import render, redirect

# old finch list - will add new via admin portal/models
# finches = [
#   {'name': 'Lilo', 'breed': 'house', 'description': 'furry little demon', 'age': 3},
#   {'name': 'Zach', 'breed': 'zebra', 'description': 'gentle and loving', 'age': 2},
# ]
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Finch, Toy, Photo
from .forms import FeedingForm

import uuid
import boto3
import os


# Create your views here.

# Define the home view
def home(request):
  # Include an .html file extension - unlike when rendering EJS templates
    return render(request, 'home.html')

# Define the about view
def about(request):
    return render(request, 'about.html')

# Add index view
@login_required
def finches_index(request):
  # We pass data to a template very much like we did in Express!
    finches = Finch.objects.filter(user=request.user)
    return render(request, 'finches/index.html', { 'finches': finches })

@login_required
def finches_detail(request, finch_id):
    finch = Finch.objects.get(id=finch_id)
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    id_list = finch.toys.all().values_list('id')
    toys_finch_doesnt_have = Toy.objects.exclude(id__in=id_list)
    return render(request, 'finches/detail.html', { 'finch': finch, 'feeding_form': feeding_form, 'toys': toys_finch_doesnt_have })

@login_required
def add_feeding(request, finch_id):
    # create a ModelForm instance using the data in request.POST
    form = FeedingForm(request.POST)
    # validate the form
    if form.is_valid():
      # don't save the form to the db until it
      # has the id assigned
        new_feeding = form.save(commit=False)
        new_feeding.finch_id = finch_id
        new_feeding.save()
    return redirect('detail', finch_id=finch_id)

@login_required
def assoc_toy(request, finch_id, toy_id):
    # Note that you can pass a toy's id instead of the whole toy object
    Finch.objects.get(id=finch_id).toys.add(toy_id)
    return redirect('detail', finch_id=finch_id)

@login_required
def unassoc_toy(request, finch_id, toy_id):
    # Note that you can pass a toy's id instead of the whole toy object
    Finch.objects.get(id=finch_id).toys.remove(toy_id)
    return redirect('detail', finch_id=finch_id)

@login_required
def add_photo(request, finch_id):
    # we need a photo file (named via the 'name' attribute in the form field)
    photo_file = request.FILES.get('photo-file', None)
    AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    # check if we actually got a photo, do something if we did, do something else if we didnt
    if photo_file:
        # here's where we'll do our S3 stuff
        # target s3
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        # we need a unique name for all of our files, so we'll use uuid to generate one automatically
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # we'll build the entire url string
            url = f'{os.environ["S3_BASE_URL"]}{bucket}/{key}'
            # we create the photo and associate it 
            Photo.objects.create(url=url, finch_id=finch_id)
        except Exception as e:
            print('An error occured uploading to s3')
            print(e)

    return redirect('detail', finch_id=finch_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
        # This will add the user to the database
            user = form.save()
        # This is how we log a user in via code
            login(request, user)
            return redirect('index')
    else:
        error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

#  CBVs -----------------------------------------

class FinchCreate(LoginRequiredMixin, CreateView):
    model = Finch
    fields = ['name', 'breed', 'description', 'age']

    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)

class FinchUpdate(LoginRequiredMixin, UpdateView):
    model = Finch
    fields = ['breed', 'description', 'age']

class FinchDelete(LoginRequiredMixin, DeleteView):
    model = Finch
    success_url = '/finches'

# ToyList
class ToyList(LoginRequiredMixin, ListView):
    model = Toy
    template_name = 'toys/index.html'

# ToyDetail
class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy
    template_name = 'toys/index.html'

# ToyCreate
class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = ['name', 'color']

    def form_valid(self, form):
        return super().form_valid(form)
    
# ToyUpdate
class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']

# ToyDelete
class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'