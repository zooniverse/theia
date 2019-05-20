import os


class PanoptesUtils:
    @classmethod
    def client_id(cls):
        return os.getenv('PANOPTES_CLIENT_ID')

    @classmethod
    def client_secret(cls):
        return os.getenv('PANOPTES_CLIENT_SECRET')

    @classmethod
    def url(cls):
        return os.getenv('PANOPTES_URL', 'https://panoptes.zooniverse.org/')
