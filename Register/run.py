import json
import os
import sys
import uuid

# adding the shared libraries path, must be done before the libraries are imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), "..", "Lib")))
# shared libraries
from iothub import iothub
from papaya import papaya
from repository import repository

with open(os.environ["REQ"]) as req:
    details = json.loads(req.read())

# random device id
did = str(uuid.uuid4())
# first register the device with the Azure IoT Hub
print "Registering %s with the Azure IoTHub" % did
rtext, rcode = iothub.add_device(did)
print "The Azure IoTHub responded with %s" % rtext
# then inform Papaya about the device
print "Informing Papaya about the new device and passing the payer/payee details"
pid, ptk = papaya.register(did, details["devicePublicKey"], details["payerId"], details["payeeId"], details["payeeToken"])
print "Papaya returned id %s" % pid
# extend the device details with Papaya & Azure ids
details["deviceId"] = did
details["papayaId"] = pid
details["papayaToken"] = ptk
# finally insert the full details in Azure Document DB
print "Storing the device details in Azure Document DB"
doc = repository.insert(did, details)
print "Repository returned %s" % doc
