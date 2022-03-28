from typing_extensions import Required
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
        item = models.CharField(max_length=100)
        price = models.DecimalField(max_digits=8, decimal_places=2)
        description = models.CharField(max_length=500000)
        image_url = models.URLField()
        current_bid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
        category = models.CharField(max_length=20, default=None)
        created_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name="created_listings", default=None)
        status = models.BooleanField(default=True)
        winner = models.ForeignKey(User,on_delete=models.CASCADE, related_name="bid_winner", default=None)

class Comments(models.Model):
        commented_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item_commented")
        comment_user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user_commenting")
        comment = models.CharField(max_length=500000)

class Bids(models.Model):
        bid_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
        bid_price = models.DecimalField(max_digits=8, decimal_places=2)
        bid_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")

class Watchlist(models.Model):
        watchlist_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
        watchlist_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist_item")