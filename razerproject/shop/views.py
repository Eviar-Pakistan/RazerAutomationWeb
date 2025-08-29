from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,FileResponse
import subprocess
import sys
import os
import json
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.core.files import File
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import RazerUser,UserFileHistory
from .serializers import RazerUserSerializer
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.contrib.auth import login
# Django view for user signup
def django_user_signup_interface(request):
    return render(request, "django_user_signup.html")

def django_user_signup_view(request):
    error_message = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            error_message = "Username already taken, please choose another."
        else:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                login(request, user)
                return render(request, "form.html", {"success": "User created successfully!"})
            except Exception as e:
                error_message = f"Error creating user: {str(e)}"

    return render(request, "django_user_signup.html", {"error": error_message})



def django_user_login_interface(request):
    return render(request, "django_user_login.html")
@csrf_exempt
def django_user_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "message": "User logged in successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Invalid username or password."})

    return JsonResponse({"success": False, "message": "Invalid request method."})


def login_view(request):
    return render(request, "login.html")

def run_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
      
       

        # Call login.py with arguments
        script_path = os.path.join(os.path.dirname(__file__), "login.py")
        print("[LOGIN] DEBUG SCRIPT PATH:", script_path)
        print("[LOGIN] FILE EXISTS:", os.path.exists(script_path))
        print("[LOGIN] DEBUG EMAIL:", email)
        print("[LOGIN] DEBUG Password:", password)
        result = subprocess.run(
            [sys.executable, script_path, email, password],
            capture_output=True,
            text=True
        )
        if "Login successful" in result.stdout:
            print(f"<pre>{result.stdout}</pre><pre>{result.stderr}</pre>")
            return HttpResponse("Login successful", content_type="text/plain")
        else:
            return HttpResponse("Login failed", content_type="text/plain")

        

    return HttpResponse("Invalid request")

def form_view(request):
    return render(request, "form.html")
def form_view_operation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            selected_products = data.get("products", [])
            productName = data.get("productName")
            userEmail = data.get("userEmail")
            secretKey = data.get("secretKey")
            regionId = data.get("regionId")

            print("DEBUG SELECTED PRODUCTS:", selected_products)
            print("DEBUG PRODUCT NAME:", productName)
            print("DEBUG Email NAME:", userEmail)
            # Serialize the product list to pass as a single argument
            serialized = json.dumps(selected_products)

            script_path = os.path.join(os.path.dirname(__file__), "main2.py")
            print("DEBUG SCRIPT PATH:", script_path)
            print("FILE EXISTS:", os.path.exists(script_path))

            result = subprocess.run(
                [sys.executable, script_path, serialized,productName,userEmail,secretKey,regionId],
                capture_output=True,
                text=True
            )

            download_url = None
            stdout_text = result.stdout
            print("Main2 Output:", stdout_text)
            for line in stdout_text.splitlines():
                if "Download URL:" in line:
                 download_url = line.split("Download URL:")[1].strip()
            
            if download_url:
             return JsonResponse({"message": "Purchase Completed", "download_url": download_url,"error":stdout_text})
            else:
                return JsonResponse({"error":f"No download URL found. Check logs.{stdout_text}"}, status=500)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return HttpResponse("Invalid request", status=400)


def get_product_info(request):
    if request.method == "POST":
        body = json.loads(request.body)
        product = body.get("product")

        script_path = os.path.join(os.path.dirname(__file__), "products.py")
        result = subprocess.run(
            [sys.executable, script_path, product],
            capture_output=True,
            text=True
        )

        try:
            output = json.loads(result.stdout)
            return JsonResponse(output)
        except Exception as e:
            return JsonResponse({
                "error": "Failed to parse product info",
                "stdout": result.stdout,
                "stderr": result.stderr
            }, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def download_results(request):
    file_path = "results.txt"   # wherever your script saves it
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, "rb"), as_attachment=True, filename="results.txt")
        return response
    else:
        return HttpResponse("File not found.", status=404)


class RazerUserListCreateView(generics.ListCreateAPIView):
    serializer_class = RazerUserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # return only the RazerUsers of the logged-in user
        return RazerUser.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print(self.request.data.get("store_email"))
        if RazerUser.objects.filter(email=self.request.data.get("store_email")).exists():
           raise ValidationError("Email already exists")
        try:
             serializer.save(user=self.request.user)
        except Exception as e:
            print(e)

@csrf_exempt
def save_and_store_file(request):
    if request.method == "POST":
        content = request.POST.get("content")
        filename = request.POST.get("filename", "default.txt")
        email = request.POST.get("email")

        if not content or not email:
            return JsonResponse({"error": "Missing content or email"}, status=400)

        razer_user = get_object_or_404(RazerUser, email=email)

        # Save file directly through Django FileField
        file_history = UserFileHistory(razer_user=razer_user)
        file_history.file.save(filename, ContentFile(content))
        file_history.save()

        return JsonResponse({
            "message": "File saved and stored in model",
            "download_url": file_history.get_download_url()
        })

@csrf_exempt
def get_user_files(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_email = data.get("email")
            print("DEBUG USER EMAIL:", user_email)

            # 1. Get the RazerUser
            razer_user = get_object_or_404(RazerUser, email=user_email)

            # 2. Fetch related file history
            files = UserFileHistory.objects.filter(razer_user=razer_user)
            print("DEBUG FILES:", files)
            file_list = [
                {
                    "file_id": f.id,
                    "file_name": f.file.name,   
                    "download_url": f.file.url,
                    "uploaded_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for f in files
            ]
            print("DEBUG FILES:", files)

            return JsonResponse({
                "user_id": razer_user.id,
                "email": razer_user.email,
                "files": file_list
            }, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)