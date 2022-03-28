from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *

from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError

def index(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(username = request.user.username)
        users_watchlist = Watchlist.objects.filter(watchlist_user=current_user).values_list('watchlist_item', flat=True)
    else:
        current_user = None
        users_watchlist = []
    
    try:
        selected_category = request.GET["selected_category"]
    except MultiValueDictKeyError:
        return render(request, "auctions/index.html", {
            'ActiveListings': Listing.objects.filter(status=True),
            'ActiveWatchlist': users_watchlist,
            'current_user': current_user,
            'all_item': Listing.objects.all()
        })
    
    if selected_category == "all_categories":
        return render(request, "auctions/index.html", {
            'ActiveListings': Listing.objects.filter(status=True),
            'ActiveWatchlist': users_watchlist,
            'current_user': current_user,
            'all_item': Listing.objects.all()
        })
    selected_listings = Listing.objects.filter(category=selected_category, status=True)
    return render(request, "auctions/index.html", {
        'ActiveListings': selected_listings,
        'ActiveWatchlist': users_watchlist,
        'current_user': current_user,
        'all_item': Listing.objects.all()
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        new_name = request.POST["item_name"]
        new_price = request.POST["item_price"]
        new_description = request.POST["item_description"]
        new_image_url = request.POST["item_image_url"]
        new_category = request.POST["item_category"]
        new_item = Listing(item = new_name, price = new_price, description = new_description, image_url=new_image_url, current_bid = new_price, category = new_category, created_by = User.objects.get(username=request.user.username))
        new_item.save()
        return render(request, "auctions/index.html", {
            'message': "Listing successfully created!",
            'ActiveListings': Listing.objects.all()
        })
    else:
        class createForm(forms.Form):
            item_name = forms.CharField(label='Item', max_length=100)
            item_price = forms.DecimalField(label='Price')
            item_description = forms.CharField(label='About Item', widget=forms.Textarea)
            item_image_url = forms.URLField(label='Image URL', required=False)
            item_category = forms.CharField(label='Category')
        form = createForm()
        return render(request, "auctions/create_listing.html", {
            'form': form
        })

def bidding(request, item_id):
    if request.user.is_authenticated:
        comments = Comments.objects.filter(commented_item=Listing.objects.get(id=item_id))
        if request.method == "POST":
            offered_item = Listing.objects.get(id=item_id)
            bid_price = float(request.POST["bid_price"])
            past_bid = Bids.objects.filter(bid_item=offered_item).aggregate(Max('bid_price'))

            if past_bid['bid_price__max'] == None:
                past_bid['bid_price__max'] = 0

            if (bid_price > offered_item.price) and (bid_price > past_bid['bid_price__max']):
                new_bid = Bids(bid_item=offered_item, bid_price=bid_price, 
                bid_user=User.objects.get(username = request.user.username))
                new_bid.save()
                Listing.objects.filter(id=item_id).update(current_bid=bid_price, winner=User.objects.get(id=request.user.id))
                return render(request, "auctions/index.html", {
                    'message': "Your bid is placed.",
                    'ActiveListings': Listing.objects.all()
                })
            else:
                return render(request, "auctions/bidding.html", {
                    'message': "Your bid is lower than the current price.",
                    'bid_item': offered_item,
                    'comments': comments
                })
        else:
            # Need to add logic for checking the current highest price. Might add current bid to 
            # the Listing model, to avoid too many query back to the bid table.
            bid_item = Listing.objects.get(id=item_id)
            if bid_item.status == False:
                if User.objects.get(username=request.user.username) == bid_item.winner:
                    message = "You won this auction!"
                else:
                    message = "The auction is closed"
            return render(request, "auctions/bidding.html", {
                'bid_item': bid_item,
                'comments': comments,
                'message':message
            })
    else:
        return HttpResponseRedirect(reverse('login'))

def add_comment(request, item_id):
    new_comment = Comments(commented_item=Listing.object.get(id=item_id), comment_user=User.objects.get(pk=request.user.id))
    new_comment.save()
    return HttpResponseRedirect(reverse("bidding", args=(item_id,)))

def watchlist(request, item_id):
    selected_item = Listing.objects.get(id=item_id)
    try:
        Watchlist.objects.get(Q(watchlist_user=User.objects.get(
          username=request.user.username)) & Q(watchlist_item=selected_item))
    except Watchlist.DoesNotExist:
        add_watchlist = Watchlist(watchlist_user=User.objects.get(
          username=request.user.username), watchlist_item=selected_item)
        add_watchlist.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        remove_watchlist = Watchlist.objects.filter(watchlist_item=selected_item)
        remove_watchlist.delete()
        return HttpResponseRedirect(reverse('index'))

def myWatchlist(request):
    my_list = Watchlist.objects.filter(watchlist_user = User.objects.get(username = request.user.username))
    return render(request, "auctions/myWatchlist.html", {
        'myList': my_list
    })

def close(request, item_id):
    if User.objects.get(username=request.user.username) == Listing.objects.get(id=item_id).created_by:
        Listing.objects.get(id=item_id).update(status=False)
    
    closed_listing = Listing.objects.filter(status=False, created_by=User.objects.get(username=request.user.username))
    won_listing = Listing.objects.filter(status=False, winner=User.objects.get(username=request.user.username))
    return render(request, "auctions/closed.html", {
            'ActiveListings': closed_listing,
            'won_listing': won_listing
        })
