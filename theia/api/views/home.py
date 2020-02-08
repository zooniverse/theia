from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    social_user = request.user.social_auth.get(provider="panoptes")

    request.session['bearer_token'] = social_user.extra_data['access_token']
    request.session['refresh_token'] = social_user.extra_data['refresh_token']

    bearer_expiry = str(datetime.now() + timedelta(seconds=social_user.extra_data['expires_in']))
    request.session['bearer_expiry'] = bearer_expiry

    context = {
        "projects": social_user.extra_data['projects']
    }
    return render(request, "home.html", context)
