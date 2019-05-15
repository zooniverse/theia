from os import getenv


class PanoptesUtils:
    @classmethod
    def client_id(cls):
        return getenv('PANOPTES_CLIENT_ID')

    @classmethod
    def client_secret(cls):
        return getenv('PANOPTES_CLIENT_SECRET')

    @classmethod
    def url(cls):
        return getenv('PANOPTES_URL', 'https://panoptes.zooniverse.org/')
