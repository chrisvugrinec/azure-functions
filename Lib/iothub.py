# adding the virtual env path, must be done before the libraries are imported
import envsetup

import base64
import hashlib
import hmac
import os
import time
import urllib

import requests

class IoTHub:
    ENCODING = "UTF-8"
    API_VERSION = "2016-02-03"

    def __init__(self, host, keyName, keyValue):
        self.host = host
        self.keyName = keyName
        self.keyValue = keyValue

    def _sas(self, resource_uri, valid_secs):
        targetUri = resource_uri.lower()
        expiryTime = "%d" % (time.time() + valid_secs)
        toSign = '%s\n%s' % (targetUri, expiryTime)
        key = base64.b64decode(self.keyValue.encode(self.ENCODING))
        signature = urllib.quote(
            base64.b64encode(hmac.HMAC(key, toSign.encode(self.ENCODING), hashlib.sha256).digest())
        ).replace("/", "%2F")
        return "SharedAccessSignature sr=%s&sig=%s&se=%s&skn=%s" % (targetUri, signature, expiryTime, self.keyName)

    def _headers(self, resource_uri=None, valid_secs=(365 * 24 * 60 * 60)):
        if not resource_uri:
            resource_uri = self.host
        sasToken = self._sas(resource_uri, valid_secs)
        return {"Content-Type": "application/json", "Authorization": sasToken}

    def _url(self, deviceId):
        return "https://%s/devices/%s?api-version=%s" % (self.host, deviceId, self.API_VERSION)

    def add_device(self, deviceId):
        body = "{deviceId: '%s'}" % deviceId
        url = self._url(deviceId)
        r = requests.put(url, headers=self._headers(), data=body)
        return r.text, r.status_code

    def retrieve_device(self, deviceId):
        url = self._url(deviceId)
        r = requests.get(url, headers=self._headers())
        return r.text, r.status_code

    def list_devices(self, top=1000):
        url = "https://%s/devices?top=%d&api-version=%s" % (self.host, top, self.API_VERSION)
        r = requests.get(url, headers=self._headers())
        return r.text, r.status_code

    def emit_message(self, deviceId, message):
        url = "https://%s/devices/%s/messages/events?api-version=%s" % (self.host, deviceId, self.API_VERSION)
        resource_uri = "%s/devices/%s" % (self.host, deviceId)
        r = requests.post(url, headers=self._headers(resource_uri, 10), data=message)
        return r.text, r.status_code


iothub = IoTHub(os.environ["iotHost"], os.environ["iotKeyName"], os.environ["iotKey"])
