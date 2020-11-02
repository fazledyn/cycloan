from django.core.mail import send_mail


def send_dummy_mail():
    print("will send mail")

    send_mail(  subject='Test Mail Django Cycloan', 
                message='Hi. This is a test mail !',
                from_email='rabid@dhaka-ai.com',
                recipient_list=['rabidahamed@gmail.com'],
                fail_silently=True)

    print("Mail sent complete")
