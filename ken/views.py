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

from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactMessage
import os

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not name or not email or not subject or not message:
            return render(request, "contact.html", {
                "error": "All fields are required.",
                "form_data": request.POST,
            })

        # Save contact message
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        # Prepare merge data
        context_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }

        # Send email to admin
        try:
            admin_subject = f"New Contact Message from {name}"
            admin_text = render_to_string("emails/admin_contact.txt", context_data)
            admin_html = render_to_string("emails/admin_contact.html", context_data)

            admin_email = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text,
                from_email=settings.EMAIL_HOST_USER,
                to=[os.getenv("ADMIN_EMAIL") or "admin@example.com"],
            )
            admin_email.attach_alternative(admin_html, "text/html")
            admin_email.send()
        except Exception as e:
            print("Error sending admin email:", e)
            return redirect("/contact/?status=email_failed")

        # Send confirmation to user
        try:
            user_subject = "Thank you for contacting us!"
            user_text = render_to_string("emails/user_confirmation.txt", context_data)
            user_html = render_to_string("emails/user_confirmation.html", context_data)

            user_email = EmailMultiAlternatives(
                subject=user_subject,
                body=user_text,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            user_email.attach_alternative(user_html, "text/html")
            user_email.send()
        except Exception as e:
            print("Error sending user confirmation email:", e)

        return redirect("/contact/?status=success")

    return render(request, "contact.html")
