from employee.models import Employee
from employee.models import Employee, DeliveryUnitMapping
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def prepare_email(transfer_status, current_du_id, target_du_id, html_page, html_content_object, assigned_pm=None):
    
    recipient_to_email = []
    recipient_cc_email = []

    if transfer_status == 1 or transfer_status == 3:
        current_du_head_id = DeliveryUnitMapping.objects.filter(du_id=current_du_id, du_head_id__isnull=False).first().du_head_id
        current_du_head_email = Employee.objects.filter(id=current_du_head_id.id).first().mail_id  if current_du_head_id else None
        recipient_to_email.append(current_du_head_email)
        print(current_du_head_email)
   
    elif transfer_status == 2:
        target_du_head_id = DeliveryUnitMapping.objects.filter(du_id=target_du_id, du_head_id__isnull=False).first().du_head_id
        target_du_head_email = Employee.objects.filter(id=target_du_head_id.id).first().mail_id  if target_du_head_id else None
        recipient_to_email.append(target_du_head_email)
        print(target_du_head_email)

    if transfer_status == 2 or transfer_status == 3:
        if transfer_status == 3:
            if assigned_pm is not None:
                pm_mail = assigned_pm.mail_id 
                recipient_to_email.append(pm_mail)
                print(pm_mail)

        current_du_hrbp = DeliveryUnitMapping.objects.filter(du_id=current_du_id, hrbp_id__isnull=False).first()
        target_du_hrbp = DeliveryUnitMapping.objects.filter(du_id=target_du_id, hrbp_id__isnull=False).first()
        if current_du_hrbp:
            current_du_hrbp_email = current_du_hrbp.hrbp_id.mail_id
        else:
            current_du_hrbp_email = None
        if target_du_hrbp:
            target_du_hrbp_email = target_du_hrbp.hrbp_id.mail_id
        else:
            target_du_hrbp_email = None

        recipient_cc_email.append(current_du_hrbp_email)
        recipient_cc_email.append(target_du_hrbp_email)

    test_email = 'jittytresathomas@gmail.com'
    recipient_to_email.append(test_email)
    html_content = render_to_string(html_page, html_content_object )
    text_content = strip_tags(html_content)

    email_parameters = [recipient_to_email, recipient_cc_email, html_content, text_content]

    return email_parameters



def send_email(subject, recipient_to_email, recipient_cc_email, text_content, html_content):
    print("in send_email fn")
    try:
        if not subject or not recipient_to_email:
            return Response({'error': 'Provide all required email data.'}, status=status.HTTP_400_BAD_REQUEST)
        print("before multi alternatives")
        email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=settings.DEFAULT_FROM_EMAIL, to=recipient_to_email, cc=recipient_cc_email)
        print("after multi alternatives")
        email.attach_alternative(html_content, "text/html")
        print("before send")
        email.send()
        print("after send")
        
    except Exception as e:
        return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        