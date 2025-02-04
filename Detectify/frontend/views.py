from django.shortcuts import render

def toggle_processing_mode(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        # Save mode to settings or database
    return render(request, 'frontend/toggle.html', {'mode': 'local'})  # Placeholder for mode