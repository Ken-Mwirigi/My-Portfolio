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



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, redirect
import os
from .models import ContactMessage  # Make sure to import your model

def contact(request):
    if request.method == "POST":
        # Get form data with proper fallbacks
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # Validate all fields
        if not all([name, email, subject, message]):
            return render(request, "contact.html", {
                "error": "All fields are required.",
                "form_data": {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                },
            })

        # Validate email format (basic check)
        if "@" not in email or "." not in email.split("@")[-1]:
            return render(request, "contact.html", {
                "error": "Please enter a valid email address.",
                "form_data": {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                },
            })

        # Save contact message
        try:
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
        except Exception as e:
            print("Error saving contact message:", e)
            return render(request, "contact.html", {
                "error": "An error occurred while saving your message. Please try again.",
                "form_data": {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                },
            })

        # Prepare context data for emails
        context_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }

        # Get admin email from settings with a fallback
        admin_email = getattr(settings, "ADMIN_EMAIL", os.getenv("ADMIN_EMAIL"))
        if not admin_email:
            print("Admin email not configured")
            return redirect("/contact/?status=email_failed")

        # Send email to admin
        try:
            admin_subject = f"New Contact Message from {name}"
            admin_text = render_to_string("admin_contact_notification.txt", context_data)
            admin_html = render_to_string("admin_contact_notification.html", context_data)

            admin_email_message = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text,
                from_email=settings.DEFAULT_FROM_EMAIL,  # Better to use DEFAULT_FROM_EMAIL
                to=[admin_email],
                reply_to=[email],  # Add reply-to header
            )
            admin_email_message.attach_alternative(admin_html, "text/html")
            admin_email_message.send()
        except Exception as e:
            print("Error sending admin email:", e)
            # Don't return here, still try to send user confirmation

        # Send confirmation to user
        try:
            user_subject = "Thank you for contacting us!"
            user_text = render_to_string("user_contact_confirmation.txt", context_data)
            user_html = render_to_string("user_contact_confirmation.html", context_data)

            user_email_message = EmailMultiAlternatives(
                subject=user_subject,
                body=user_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            user_email_message.attach_alternative(user_html, "text/html")
            user_email_message.send()
        except Exception as e:
            print("Error sending user confirmation email:", e)
            return redirect("/contact/?status=email_failed")

        return redirect("/contact/?status=success")

    # Handle GET request
    status = request.GET.get("status", "")
    context = {}
    
    if status == "success":
        context["success"] = "Your message has been sent successfully!"
    elif status == "email_failed":
        context["error"] = "We received your message but couldn't send a confirmation email."
    
    return render(request, "contact.html", context)