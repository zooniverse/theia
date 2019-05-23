from os import getenv


class Utils:
    @classmethod
    def get_username(cls):
        return getenv('USGS_USERNAME')

    @classmethod
    def get_password(cls):
        return getenv('USGS_PASSWORD')
