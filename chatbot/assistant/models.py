from django.db import models

class Label(models.Model):
    name = models.CharField(max_length=50)

class Conversation(models.Model):
    user_id = models.IntegerField(null=True)
    role = models.CharField(max_length=50)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    predicted_categories = models.ManyToManyField(Label, through='PredictedCategory')

class DatasetEntry(models.Model):
    user_id = models.IntegerField(null=True)
    roles = models.CharField(max_length=50, blank=True, default='')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    labels = models.ManyToManyField(Label)

class PredictedCategory(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    predicted_label = models.ForeignKey(Label, on_delete=models.CASCADE)
    probability = models.FloatField()  # You might want to store the probability of the prediction as well
    timestamp = models.DateTimeField(auto_now_add=True)
