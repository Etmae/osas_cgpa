from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout

from .models import CGPARecord

# Create your views here.

def get_grade_point(score: int) -> float:
    if score < 0 or score > 100:
        raise ValueError("Score must be within the range 0 to 100")

    if score >= 70:
        return 5.0
    elif score >= 60:
        return 4.0
    elif score >= 50:
        return 3.0
    elif score >= 45:
        return 2.0
    elif score >= 40:
        return 1.0
    else:
        return 0.0
    


def landing(request):
    return render(request, "landing.html")

@login_required
def home(request):
    context = {}

    if request.method == "POST":
        try:
            units = request.POST.getlist("units[]")
            scores = request.POST.getlist("scores[]")

            total_units = 0
            total_credit_points = 0

            for u, s in zip(units, scores):
                u = int(u)
                s = int(s)

                total_units += u
                total_credit_points += u * get_grade_point(s)
            
            if total_units > 0:
                cgpa = round(total_credit_points / total_units, 2)

                CGPARecord.objects.create(
                    user=request.user,
                    semester="Current Semester",
                    cgpa=cgpa,
                    total_units=total_units,
                    total_credit_points=total_credit_points
                )

                context.update({
                    "cgpa": cgpa,
                    "total_units": total_units,
                    "total_credit_points": total_credit_points
                })

        except (ValueError, TypeError):
            context["error"] = "Invalid input. Please ensure all fields are filled correctly."
    return render(request, "index.html", context)


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists."})
        
        User.objects.create_user(username=username, password=password)
        return redirect("login")    
    
    
    return render(request, "signup.html")


def logout_view(request):
    auth_logout(request)
    return redirect("login")




