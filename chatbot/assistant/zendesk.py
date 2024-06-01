from django.shortcuts import render

def zendesk(request) :
    return render(request, 'zendesk.html')