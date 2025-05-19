import os
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ContactMessage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
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



from .forms import ContactForm
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, redirect
import os
from .models import ContactMessage

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        
        if not form.is_valid():
            errors = form.errors.get_json_data()
            formatted_errors = {field: err[0]["message"] for field, err in errors.items()}
            response_data = {
                "status": "error",
                "message": "Please correct the errors below.",
                "errors": formatted_errors,
            }
            return JsonResponse(response_data) if request.headers.get("X-Requested-With") == "XMLHttpRequest" else \
                render(request, "contact.html", {"form": form})

        # Save the data
        data = form.cleaned_data
        try:
            ContactMessage.objects.create(
                name=data["name"],
                email=data["email"],
                subject=data["subject"],
                message=data["message"],
            )
        except Exception as e:
            print("Error saving contact message:", e)
            response_data = {
                "status": "error",
                "message": "An error occurred while saving your message. Please try again.",
            }
            return JsonResponse(response_data, status=500) if request.headers.get("X-Requested-With") == "XMLHttpRequest" else \
                render(request, "contact.html", {"form": form, "error": response_data["message"]})

        # Prepare email data
        context_data = data
        admin_email = getattr(settings, "ADMIN_EMAIL", os.getenv("ADMIN_EMAIL"))
        email_failed = False

        # Send admin email
        try:
            admin_subject = f"New Contact Message from {data['name']}"
            admin_text = render_to_string("admin_contact_notification.txt", context_data)
            admin_html = render_to_string("admin_contact_notification.html", context_data)

            admin_email_obj = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
                reply_to=[data["email"]],
            )
            admin_email_obj.attach_alternative(admin_html, "text/html")
            admin_email_obj.send()
        except Exception as e:
            print("Error sending admin email:", e)
            email_failed = True

        # Send user confirmation email
        try:
            user_subject = "Thank you for contacting us!"
            user_text = render_to_string("user_contact_confirmation.txt", context_data)
            user_html = render_to_string("user_contact_confirmation.html", context_data)

            user_email_obj = EmailMultiAlternatives(
                subject=user_subject,
                body=user_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[data["email"]],
            )
            user_email_obj.attach_alternative(user_html, "text/html")
            user_email_obj.send()
        except Exception as e:
            print("Error sending user confirmation email:", e)
            email_failed = True

        if email_failed:
            return JsonResponse({
                "status": "partial_success",
                "message": "Message received but email confirmation failed.",
            }) if request.headers.get("X-Requested-With") == "XMLHttpRequest" else \
                redirect("/contact/?status=email_failed")

        return JsonResponse({
            "status": "success",
            "message": "Your message has been sent successfully!",
        }) if request.headers.get("X-Requested-With") == "XMLHttpRequest" else \
            redirect("/contact/?status=success")

    # GET Request
    status = request.GET.get("status", "")
    context = {"form": ContactForm()}

    if status == "success":
        context["success"] = "Your message has been sent successfully!"
    elif status == "email_failed":
        context["error"] = "We received your message but couldn't send an email. Please try again."

    return render(request, "contact.html", context)
