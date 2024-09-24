import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Project, Transaction
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import os
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Transaction
import requests
from django.views.decorators.cache import cache_page


@cache_page(60 * 15)
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'payments/project_detail.html', {'project': project})

@cache_page(60 * 15)
def project_list(request):
    projects = Project.objects.all()
    for project in projects:
        project.price_in_kobo = int(project.price * 100)
    return render(request, 'payments/projects.html', {'projects': projects})

def process_payment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        amount = project.price * 100
        transaction = Transaction.objects.create(
            email=email, phone=phone, amount=project.price, project=project
        )

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "amount": int(amount),
            "reference": transaction.ref,
            "callback_url": "https://f65b-105-29-165-232.ngrok-free.app/payments/verify_payment"
        }

        url = "https://api.paystack.co/transaction/initialize"
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        if response_data['status']:
            transaction.ref = response_data['data']['reference']
            transaction.save()
            return redirect(response_data['data']['authorization_url'])

    return render(request, 'payments/payment.html', {'project': project})


def verify_payment(request):
    ref = request.GET.get('reference')
    transaction = get_object_or_404(Transaction, ref=ref)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"https://api.paystack.co/transaction/verify/{ref}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data['status'] and response_data['data']['status'] == "success":
        transaction.verified = True
        transaction.save()

        project = transaction.project
        email = transaction.email

        subject = f"Your Project: {project.title}"
        message = render_to_string('payments/project_email.html', {
            'project': project,
            'transaction': transaction,
        })

        email_message = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        email_message.content_subtype = 'html'
        pdf_path = project.pdf.path
        email_message.attach_file(pdf_path)

        email_message.send()

        return redirect('thankyou', transaction_id=transaction.id)

    return render(request, 'payments/payment_failed.html')

def thankyou(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, verified=True)
    project = transaction.project
    return render(request, 'payments/thankyou.html', {'project': project})
