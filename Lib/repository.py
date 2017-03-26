# adding the virtual env path, must be done before the libraries are imported
import envsetup

import os

import pydocumentdb.document_client as document_client

class Repository:
    COLLECTION = "dbs/devices/colls/deviceInfo"

    def __init__(self, host, token):
        self.client = document_client.DocumentClient(host, {"masterKey": token})

    def resolve(self, deviceId):
        # TODO ME fix the potential SQL-I issue with the deviceId
        docs = list(self.client.QueryDocuments(self.COLLECTION,
            "SELECT c.papayaId, c.papayaToken FROM c WHERE c.deviceId = '%s'" % deviceId))
        if len(docs) > 0:
            return docs[0]["papayaId"], docs[0]["papayaToken"]
        else:
            raise KeyError("Device '%s' could not be found" % deviceId)

    def insert(self, deviceId, deviceDetails):
        return self.client.CreateDocument(self.COLLECTION, deviceDetails)

repository = Repository(os.environ["docDBHost"], os.environ["docDBKey"])