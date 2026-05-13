from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout

from .models import OsasCGPARecord

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
    # Fetch user history immediately for display
    records = OsasCGPARecord.objects.filter(user=request.user).order_by('-created_at')
    context = {"records": records}

    if request.method == "POST":
        try:
            semester_name = request.POST.get("semester_name", "Untitled Semester")
            units = request.POST.getlist("units[]")
            scores = request.POST.getlist("scores[]")

            total_units = 0
            total_credit_points = 0

            for u, s in zip(units, scores):
                if u and s: # Ensure fields aren't empty
                    val_u = int(u)
                    val_s = int(s)
                    total_units += val_u
                    total_credit_points += val_u * get_grade_point(val_s)
            
            if total_units > 0:
                cgpa = round(total_credit_points / total_units, 2)

                # Save the new record
                OsasCGPARecord.objects.create(
                    user=request.user,
                    semester=semester_name,
                    cgpa=cgpa,
                    total_units=total_units,
                    total_credit_points=total_credit_points
                )

                # Refresh records to include the new entry
                context.update({
                    "cgpa": cgpa,
                    "result_semester": semester_name,
                    "records": OsasCGPARecord.objects.filter(user=request.user).order_by('-created_at')
                })

        except (ValueError, TypeError):
            context["error"] = "Invalid input. Please ensure all units and scores are numbers."

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




