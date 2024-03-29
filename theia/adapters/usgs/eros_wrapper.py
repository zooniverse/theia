from .utils import Utils
import json
import requests
import sys
import datetime
from sentry_sdk import capture_message
EROS_SERVICE_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"
TOKEN_EXPIRY_HOURS = 2

class ErosWrapper():
    def __init__(self):
        self.api_key = None
        self.login_time = None
        self.download_request_label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")



    def login(self):
        if self.login_time is None or self.is_token_expired():
            loginParameters = {
                'username': Utils.get_username(),
                'password': Utils.get_password()
            }
            self.api_key = self.send_request(EROS_SERVICE_URL + "login", loginParameters)
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
        return self.send_request(EROS_SERVICE_URL + "scene-list-add", scene_list_add_payload)

    def available_products(self, list_id, search):
        self.login()

        download_options_payload = {
            "listId": list_id,
            "datasetName": search['datasetName']
        }
        results =  self.send_request(EROS_SERVICE_URL + "download-options", download_options_payload)
        products = []

        if results is not None:
            for result in results:
                if result["bulkAvailable"] and result['downloadSystem'] != 'folder':
                    products.append(
                    {
                    "entityId": result['entityId'],
                    "productId": result['id'],
                    "displayId": result['displayId']
                    })
        return products

    def request_download(self, products):
        self.login()

        download_request_payload = {
            "downloads": products,
            "label": self.download_request_label
        }

        #returns format like
        #{
        #     "requestId": 1591674034,
        #     "version": "stable",
        #     "data":  # {
            #    "availableDownloads":[

            #    ],
            #    "duplicateProducts":[

            #    ],
            #    "preparingDownloads":[
            #       {
            #          "downloadId":550754832,
            #          "eulaCode":"None",
            #          "url":"https://dds.cr.usgs.gov/download-staging/eyJpZCI6NTUwNzU0ODMyLCJjb250YWN0SWQiOjI2MzY4NDQ1fQ=="
            #       },
            #       {
            #          "downloadId":550752861,
            #          "eulaCode":"None",
            #          "url":"https://dds.cr.usgs.gov/download-staging/eyJpZCI6NTUwNzUyODYxLCJjb250YWN0SWQiOjI2MzY4NDQ1fQ=="
            #       }
            #    ],
            #    "failed":[

            #    ],
            #    "newRecords":{
            #       "550754832":"20240131_143747",
            #       "550752861":"20240131_143747"
            #    },
            #    "numInvalidScenes":0
        #     },
        #     "errorCode": null,
        #     "errorMessage": null
        # }

        return self.send_request(EROS_SERVICE_URL + "download-request", download_request_payload)


    def parse_result_set(self, result_set):
        if not result_set:
            return []

        return [scene.get('displayId', None) for scene in result_set if 'displayId' in scene]

    def send_request(self, url, data):
        json_data = json.dumps(data)

        if self.api_key == None:
            response = requests.post(url, json_data)
        else:
            headers = {'X-Auth-Token': self.api_key}
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
