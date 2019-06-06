from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import pdb

@login_required
def home(request):
    social_user = request.user.social_auth.get(provider="panoptes")
    context = {
        "projects": social_user.extra_data['projects']
    }
    return render(request, "home.html", context)
