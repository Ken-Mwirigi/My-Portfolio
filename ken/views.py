
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ContactMessage
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
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
            # Send email to site admin (you)
            admin_subject = f"New Contact Form Submission from {name}"
            admin_text_body = render_to_string("admin_contact_notification.txt", merge_data)
            admin_html_body = render_to_string("admin_contact_notification.html", merge_data)

            admin_msg = EmailMultiAlternatives(
                subject=admin_subject,
                from_email=settings.FROM_EMAIL,
                to= ["kamakennedy362@gmail.com"],
                body=admin_text_body
            )
            admin_msg.attach_alternative(admin_html_body, "text/html")
            admin_msg.send()

            # Send confirmation email to the user
            user_subject = "Thank you for contacting us!"
            user_text_body = render_to_string("user_contact_confirmation.txt", merge_data)
            user_html_body = render_to_string("user_contact_confirmation.html", merge_data)

            user_msg = EmailMultiAlternatives(
                subject=user_subject,
                from_email=settings.FROM_EMAIL,
                to=[email],
                body=user_text_body
            )
            user_msg.attach_alternative(user_html_body, "text/html")
            user_msg.send()

        except Exception as e:
            print(f"Email cannot be sent now! Error: {e}")

        # Redirect to a success page
        return redirect('ken:contact')

    return render(request, 'contact.html')


