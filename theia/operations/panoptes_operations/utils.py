from os import getenv


class PanoptesUtils:
    @classmethod
    def panoptes_client_id():
        return getenv('PANOPTES_CLIENT_ID')

    @classmethod
    def panoptes_client_secret():
        return getenv('PANOPTES_CLIENT_SECRET')
