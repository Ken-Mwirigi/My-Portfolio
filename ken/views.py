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

def send_simple_message():
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_SENDER_DOMAIN')}/messages",  # Use environment variable for domain
            auth=("api", os.getenv('MAILGUN_API_KEY')),  # Use environment variable for API key
            data={
                "from": f"Mailgun Sandbox <postmaster@{os.getenv('MAILGUN_DOMAIN')}>", # Use environment variable for domain
                "to": "Ken Mwirigi <kenmwirigi7933@gmail.com>",
                "subject": "Hello Ken Mwirigi",
                "text": "Congratulations Ken Mwirigi, you just sent an email with Mailgun! You are truly awesome!"
            })
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print("Mailgun email sent successfully!")  # Optional: Print success message
        return True # Indicate success
    except requests.exceptions.RequestException as e:
        print(f"Error sending Mailgun email: {e}")
        return False # Indicate failure
    except Exception as e: # Catch any other potential exceptions
        print(f"An unexpected error occurred: {e}")
        return False # Indicate failure



def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not name or not email or not subject or not message:
            return HttpResponse("All fields are required.", status=400)

        mycontact = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        mycontact.save()

        merge_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }

        try:
            # Send email to site admin (using Django's built-in email)
            admin_subject = f"New Contact Form Submission from {name}"
            admin_text_body = render_to_string("admin_contact_notification.txt", merge_data)
            admin_html_body = render_to_string("admin_contact_notification.html", merge_data)

            admin_msg = EmailMultiAlternatives(
                subject=admin_subject,
                from_email=settings.EMAIL_HOST_USER,
                to=["kamakennedy362@gmail.com"],  # Or a list of admin emails
                body=admin_text_body
            )
            admin_msg.attach_alternative(admin_html_body, "text/html")
            admin_msg.send()

            # Send confirmation email to the user (using Django's built-in email)
            user_subject = "Thank you for contacting us!"
            user_text_body = render_to_string("user_contact_confirmation.txt", merge_data)
            user_html_body = render_to_string("user_contact_confirmation.html", merge_data)

            user_msg = EmailMultiAlternatives(
                subject=user_subject,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
                body=user_text_body
            )
            user_msg.attach_alternative(user_html_body, "text/html")
            user_msg.send()

            # Send with Mailgun (optional - can be used in addition to or instead of Django's email)
            mailgun_success = send_simple_message()

            if not mailgun_success:
                print("Mailgun email failed.  Check logs for details") # Log the failure, but don't necessarily interrupt the flow

        except Exception as e:
            print(f"Email sending error: {e}")
            return redirect('/contact/?status=email_failed')  # Redirect with error status

        return redirect('/contact/?status=success')  # Redirect with success status

    return render(request, 'contact.html')