from django.db import models
from django.contrib.auth.models import User


class SearchHistory(models.Model):
    city = models.CharField(max_length=100)
    search_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.city}: {self.search_count}"


class UserSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched for {self.city} on {self.search_date}"
