import os
from urllib.parse import urljoin


class PanoptesUtils:
    @classmethod
    def client_id(cls):
        return os.getenv('PANOPTES_CLIENT_ID')

    @classmethod
    def client_secret(cls):
        return os.getenv('PANOPTES_CLIENT_SECRET')

    @classmethod
    def url(cls, path):
        return urljoin(cls.base_url(), path)

    @classmethod
    def base_url(cls):
        return os.getenv('PANOPTES_URL')
