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



from django.shortcuts import render
from femitimeapp.models import  tbl_hospital_doctor_register
from django.shortcuts import render, redirect, get_object_or_404

# ✅ View all pending doctors
def view_pending_doctors(request):
    hospital_pending = tbl_hospital_doctor_register.objects.filter(status='pending')
    return render(request, 'pending_doctors.html', {
        'hospital_pending': hospital_pending
    })



# ✅ Approve hospital doctor
def approve_hospital_doctor(request, doctor_id):
    doctor = get_object_or_404(tbl_hospital_doctor_register, id=doctor_id)
    doctor.status = 'approved'
    doctor.save()
    return redirect('view_pending_doctors')


# ✅ Reject hospital doctor
def reject_hospital_doctor(request, doctor_id):
    doctor = get_object_or_404(tbl_hospital_doctor_register, id=doctor_id)
    doctor.status = 'rejected'
    doctor.save()
    return redirect('view_pending_doctors')



def view_approved_doctors(request):
   
    hospital_approved = tbl_hospital_doctor_register.objects.filter(status='approved')
    return render(request, 'approved_doctors.html', {
        
        'hospital_approved': hospital_approved
    })


def view_rejected_doctors(request):
    hospital_rejected = tbl_hospital_doctor_register.objects.filter(status='rejected')
    return render(request, 'rejected_doctors.html', {
        'hospital_rejected': hospital_rejected
    })