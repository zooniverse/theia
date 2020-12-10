from .utils import Utils
import json
import requests
import sys

class ErosWrapper():

    def search(self, search):
        serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"

        loginParameters = {
            'username': Utils.get_username(),
            'password': Utils.get_password()
        }
        apiKey = self.send_request(serviceUrl + "login", loginParameters)
        scenes = self.send_request(serviceUrl + "scene-search", search, apiKey)

        results = self.parse_result_set(scenes['results'])
        return results

    def parse_result_set(self, result_set):
        if not result_set:
            return []

        return [scene.get('displayId', None) for scene in result_set if 'displayId' in scene]

    def send_request(self, url, data, apiKey=None):
        json_data = json.dumps(data)

        if apiKey == None:
            response = requests.post(url, json_data)
        else:
            headers = {'X-Auth-Token': apiKey}
            response = requests.post(url, json_data, headers=headers)

        try:
            httpStatusCode = response.status_code
            if response == None:
                print("No output from service")
                sys.exit()
            output = json.loads(response.text)
            if output['errorCode'] != None:
                print(output['errorCode'], "- ", output['errorMessage'])
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



