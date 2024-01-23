from .utils import Utils
from urllib.parse import urljoin
import json
import requests
import sys
import datetime
import time
from sentry_sdk import capture_message
EROS_SERVICE_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"
MAX_THREADS = 5
TOKEN_EXPIRY_HOURS = 2

class ErosWrapper():
    def __init__(self):
        self.api_key = None
        self.login_time = None

    def login(self):
        if self.login_time is None or self.is_token_expired():
            loginParameters = {
                'username': Utils.get_username(),
                'password': Utils.get_password()
            }
            self.apiKey = self.send_request(EROS_SERVICE_URL + "login", loginParameters)
            self.login_time = datetime.datetime.utcnow()


    def is_token_expired(self):
        if self.login_time:
            token_expiration_time = self.login_time + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS)
            # minusing 1 minute to expiry check to protect against race condition
            return datetime.datetime.utcnow() - datetime.timedelta(minutes=1) >= token_expiration_time
        return True

    def search(self, search):
        self.login()
        scenes = self.send_request(EROS_SERVICE_URL + "scene-search", search)

        results = self.parse_result_set(scenes['results'])
        return results

    def add_scenes_to_order_list(self, scene_id, search):
        self.login()
        scene_list_add_payload = {
            "listId": scene_id,
            "idField": "displayId", #default is search by entityId
            "entityId": scene_id,
            "datasetName": search['datasetName']
        }
        return self.send_request(EROS_SERVICE_URL + "scene-list-add", scene_list_add_payload, apiKey)

    def available_products(self, list_id, search):
        self.login()

        download_options_payload = {
            "listId": list_id,
            "datasetName": search['datasetName']
        }
        results =  self.send_request(EROS_SERVICE_URL + "download-options", download_options_payload, apiKey)
        products = []

        for result in results:
            if result["bulkAvailable"] and result['downloadSystem'] != 'folder':
                products.append({"entityId": result['entityId'], "productId": result['id']})
        return products

    def download_request(self, products):
        self.login()

        download_request_label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        download_request_payload = {
            "downloads": products,
            "label": download_request_label
        }

        product_urls = []

        results = self.send_request(EROS_SERVICE_URL + "download-request", download_request_payload, apiKey)

        for result in results['availableDownloads']:
            product_urls.append(result['url'])

        preparingDownloadCount = len(results['preparingDownloads'])
        preparingDownloadIds = []
        if preparingDownloadCount > 0:
            for result in results['preparingDownloads']:
                preparingDownloadIds.append(result['downloadId'])

            payload = {"label": download_request_label}
            results = self.send_request("download-retrieve", payload, apiKey)
            if results != False:
                for result in results['available']:
                    if result['downloadId'] in preparingDownloadIds:
                        preparingDownloadIds.remove(result['downloadId'])
                        product_urls.append(result['url'])

                for result in results['requested']:
                    if result['downloadId'] in preparingDownloadIds:
                        preparingDownloadIds.remove(result['downloadId'])
                        product_urls.append(result['url'])
            # Don't get all download urls, retrieve again after 30 seconds
            while len(preparingDownloadIds) > 0:
                print(f"{len(preparingDownloadIds)} downloads are not available yet. Waiting for 30s to retrieve again\n")
                time.sleep(30)
                results =  self.send_request("download-retrieve", payload, apiKey)
                if results != False:
                    for result in results['available']:
                        if result['downloadId'] in preparingDownloadIds:
                            preparingDownloadIds.remove(result['downloadId'])
                            product_urls.append(result['url'])

        return product_urls

    def parse_result_set(self, result_set):
        if not result_set:
            return []

        return [scene.get('displayId', None) for scene in result_set if 'displayId' in scene]

    def send_request(self, url, data):
        json_data = json.dumps(data)

        if self.apiKey == None:
            response = requests.post(url, json_data)
        else:
            headers = {'X-Auth-Token': self.apiKey}
            response = requests.post(url, json_data, headers=headers)

        try:
            httpStatusCode = response.status_code
            if response == None:
                print("No output from service")
                sys.exit()
            output = json.loads(response.text)
            if output['errorCode'] != None:
                print(output['errorCode'], "- ", output['errorMessage'])
                capture_message('USGS Connection Error - ' + output['errorCode'] + ' - ' + output['errorMessage'])
                sys.exit()
            if httpStatusCode == 404:
                print("404 Not Found")
                sys.exit()
            elif httpStatusCode == 401:
                print("401 Unauthorized")
                sys.exit()
            elif httpStatusCode == 400:
                print("Error Code", httpStatusCode)
                sys.exit()
        except Exception as e:
            response.close()
            print(e)
            sys.exit()
        response.close()

        return output['data']
