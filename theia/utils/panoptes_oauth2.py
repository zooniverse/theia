from datetime import datetime, timedelta
from urllib.parse import urljoin

from social_core.backends.oauth import BaseOAuth2
from panoptes_client import Panoptes, Project

from theia.utils.panoptes_utils import PanoptesUtils


class PanoptesOAuth2(BaseOAuth2):
    name = 'panoptes'
    AUTHORIZATION_URL = PanoptesUtils.url('oauth/authorize')
    ACCESS_TOKEN_URL = PanoptesUtils.url('oauth/token')
    REVOKE_TOKEN_URL = PanoptesUtils.url('oauth/revoke')
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_METHOD = 'GET'

    EXTRA_DATA = [
        ('expires_in', 'expires_in'),
        ('refresh_token', 'refresh_token'),
        ('projects', 'projects')
    ]

    def get_user_details(self, response):
        authenticated_panoptes = Panoptes(
            endpoint=PanoptesUtils.base_url(),
            client_id=PanoptesUtils.client_id(),
            client_secret=PanoptesUtils.client_secret()
        )

        authenticated_panoptes.bearer_token = response['access_token']
        authenticated_panoptes.logged_in = True
        authenticated_panoptes.refresh_token = response['refresh_token']
        authenticated_panoptes.bearer_expires = (datetime.now() + timedelta(seconds=response['expires_in']))

        with authenticated_panoptes:
            user = authenticated_panoptes.get('/me')[0]['users'][0]

            ids = ['admin user']
            if not user['admin']:
                ids = [project.id for project in Project.where()]

            return {
                'username': user['login'],
                'email': user['email'],
                'is_superuser': user['admin'],
                'projects': ids,
            }

    def get_user_id(self, details, response):
        return details['username']
