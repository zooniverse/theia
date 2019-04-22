from urllib.parse import urljoin
class EspaWrapper:
    @classmethod
    def api_url(cls, path):
        # return urljoin('https://demo1580318.mockable.io/', path)
        return urljoin('https://espa.cr.usgs.gov/api/v1/', path)

    def foo():
        return 'bar'