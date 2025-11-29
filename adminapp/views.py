from django.shortcuts import get_object_or_404, render

# Create your views here.

from django.shortcuts import render, redirect
from django.http import HttpResponse

from femitimeapp.models import Register
from .models import Admin

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin = Admin.objects.get(username=username, password=password)
            # Store admin in session
            request.session["admin_id"] = admin.id
            request.session["admin_username"] = admin.username
            return redirect("index")  # redirect after login
        except Admin.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid email or password"})

    return render(request, "login.html")

def index(request):
    return render(request, "index.html")

def view_users(request):
    users = Register.objects.all()
    return render(request, 'view_users.html', {'users': users})

def delete_user(request, user_id):
    user = get_object_or_404(Register, id=user_id)
    user.delete()
    return redirect('view_users')