import os
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ContactMessage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives,send_mail
from django.template.loader import render_to_string

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def services(request):
    return render(request, 'services.html')

def resume(request):
    return render(request, 'resume.html')

def portfolio_details(request):
    return render(request, 'portfolio-details.html')



from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, redirect
import os
from .models import ContactMessage

def contact(request):
    if request.method == "POST":
        # Get and clean form data
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # Validate all fields
        if not all([name, email, subject, message]):
            response_data = {
                "status": "error",
                "message": "All fields are required.",
                "errors": {
                    "name": "Name is required" if not name else "",
                    "email": "Email is required" if not email else "",
                    "subject": "Subject is required" if not subject else "",
                    "message": "Message is required" if not message else "",
                }
            }
            return JsonResponse(response_data) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else \
                render(request, "contact.html", {"error": "All fields are required.", "form_data": request.POST})

        # Validate email format
        if "@" not in email or "." not in email.split("@")[-1]:
            response_data = {
                "status": "error",
                "message": "Please enter a valid email address.",
                "errors": {"email": "Invalid email format"}
            }
            return JsonResponse(response_data) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else \
                render(request, "contact.html", {"error": "Please enter a valid email address.", "form_data": request.POST})

        # Save contact message
        try:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
        except Exception as e:
            print("Error saving contact message:", e)
            response_data = {
                "status": "error",
                "message": "An error occurred while saving your message. Please try again."
            }
            return JsonResponse(response_data, status=500) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else \
                render(request, "contact.html", {"error": "An error occurred while saving your message. Please try again.", "form_data": request.POST})

        # Prepare email context
        context_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }

        admin_email = getattr(settings, "ADMIN_EMAIL", os.getenv("ADMIN_EMAIL"))
        email_failed = False

        # Send admin notification
        try:
            admin_subject = f"New Contact Message from {name}"
            admin_text = render_to_string("admin_contact_notification.txt", context_data)
            admin_html = render_to_string("admin_contact_notification.html", context_data)

            EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
                reply_to=[email],
            ).attach_alternative(admin_html, "text/html").send()
        except Exception as e:
            print("Error sending admin email:", e)
            email_failed = True

        # Send user confirmation
        try:
            user_subject = "Thank you for contacting us!"
            user_text = render_to_string("user_contact_confirmation.txt", context_data)
            user_html = render_to_string("user_contact_confirmation.html", context_data)

            EmailMultiAlternatives(
                subject=user_subject,
                body=user_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            ).attach_alternative(user_html, "text/html").send()
        except Exception as e:
            print("Error sending user confirmation email:", e)
            email_failed = True

        if email_failed:
            response_data = {
                "status": "partial_success",
                "message": "Message received but email confirmation failed."
            }
            return JsonResponse(response_data) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else \
                redirect("/contact/?status=email_failed")

        response_data = {
            "status": "success",
            "message": "Your message has been sent successfully!"
        }
        return JsonResponse(response_data) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else \
            redirect("/contact/?status=success")

    # GET request handling
    status = request.GET.get("status", "")
    context = {}
    
    if status == "success":
        context["success"] = "Your message has been sent successfully!"
    elif status == "email_failed":
        context["error"] = "We received your message but couldn't send an email. Please try again."
    
    return render(request, "contact.html", context)