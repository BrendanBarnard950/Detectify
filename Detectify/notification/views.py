from django.shortcuts import render

def send_notification(request):
    # Placeholder for notification logic
    return render(request, 'notifications/send.html', {'message': 'Notification sent'})