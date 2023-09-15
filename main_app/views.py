

from django.shortcuts import render, redirect

# old finch list - will add new via admin portal/models
# finches = [
#   {'name': 'Lilo', 'breed': 'house', 'description': 'furry little demon', 'age': 3},
#   {'name': 'Zach', 'breed': 'zebra', 'description': 'gentle and loving', 'age': 2},
# ]
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
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
def finches_index(request):
  # We pass data to a template very much like we did in Express!
    finches = Finch.objects.all() # Retrieve all 
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
      # has the id assigned
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

# def add_photo(request, finch_id):
#     # photo-file will be the "name" attribute on the <input type="file">
#     photo_file = request.FILES.get('photo-file', None)
#     AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
#     AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
#     if photo_file:
#         s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#         # need a unique "key" for S3 / needs image file extension too
#         key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
#         # just in case something goes wrong
#         try:
#             bucket = os.environ['S3_BUCKET']
#             s3.upload_fileobj(photo_file, bucket, key)
#             # build the full url string
#             url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
#             Photo.objects.create(url=url, finch_id=finch_id)
#         except Exception as e:
#             print('An error occurred uploading file to S3')
#             print(e)
#     return redirect('detail', finch_id=finch_id)

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