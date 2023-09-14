from django.db import models

from django.urls import reverse

from datetime import date

# Create your models here.

MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)

#  Finches >---< Toys 
class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.color} {self.name}'
    
    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk': self.id})

class Finch(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    toys = models.ManyToManyField(Toy)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'finch_id': self.id})

    def fed_for_today(self):
        # filter produces an <QuerySet> for all feedings from current date
        # count the items in that array, compare to the length of MEALS (tuple)
        # we'll return a boolean that we can use in our template
        return self.feeding_set.filter(date=date.today()).count() >= len(MEALS)

# Model for Feedings (Finch -|---< Feeding)
class Feeding(models.Model):
    date = models.DateField('feeding date')
    meal = models.CharField(
        max_length=1,
        # add the 'choices' field option
        choices=MEALS,
        # set the default value for meal to be 'B'
        default=MEALS[0][0]
    )
    finch = models.ForeignKey(Finch, on_delete=models.CASCADE)

    def __str__(self):
    # Nice method for obtaining the friendly value of a Field.choice
        return f"{self.get_meal_display()} on {self.date}"

    class Meta:
        ordering = ['-date']
