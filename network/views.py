from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import User, Post, Like

#Views

def index(request):
    return render(request, "network/index.html")


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def posts(request):
    posts = Post.objects.all()

    return JsonResponse([post.serialize() for post in posts], safe=False)

def user_posts(request, username):
    try:
        user = User.objects.get(username=username)
        posts = user.posts.all()
        return JsonResponse([post.serialize() for post in posts], safe=False)
    except:
        return JsonResponse({"error": "No posts to show"}, status=404)
    

def profile(request, username):
    try:
        user = User.objects.get(username=username)
        return render(request, "network/profile.html", {
            "user": user
        })
    except:
        return JsonResponse({"error": "User not valid"}, status=404)

@login_required
def like(request, post_id):
    if request.method == "POST":
        try:
            user = request.user
            post = Post.objects.get(id=int(post_id))
            Like.objects.create(user=user, post=post)
            return JsonResponse({"message": "Post liked"})
        except:
            return JsonResponse({"error": "Post already liked"}, status=400)

@login_required
def dislike(request, post_id):
    if request.method == "POST":
        try:
            user = request.user
            post = Post.objects.get(id=int(post_id))
            Like.objects.get(user=user, post=post).delete()
            return JsonResponse({"message": "Post disliked"})
        except:
            return JsonResponse({"error": "Post already disliked"}, status=400)

@login_required
def follow(request, username):
    if request.method == "POST":
        try:
            user = User.objects.get(username=username)
            if user in request.user.following.all():
                raise ValidationError("User already followed")
            request.user.following.add(user)
            return JsonResponse({"message": f"User {user.username} followed"})
        except IntegrityError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except:
            return JsonResponse({"error": "An error ocurred"}, status=500)

@login_required
def unfollow(request, username):
    if request.method == "POST":
        try:
            user = User.objects.get(username=username)
            if user not in request.user.following.all():
                raise ValidationError("User already unfollowed")
            request.user.following.remove(user)
            return JsonResponse({"message": f"User {user.username} followed"})
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except:
            return JsonResponse({"error": "An error ocurred"}, status=500)
