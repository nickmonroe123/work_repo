import requests

class SpectrumCoreAuth:
    def __init__(self, cert_path: str, key_path: str):
        self.cert_path = cert_path
        self.key_path = key_path
        self.cert = (self.cert_path, self.key_path)


CERT_FILE = "server.crt"
KEY_FILE = "key.pem"
cert_auth = SpectrumCoreAuth(CERT_FILE, KEY_FILE)

system_id = "ComplianceService"
url = "https://spectrumcore.charter.com:7443/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"

"""/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1
Type of Possible Requests: Post
Determines the divisionID, unique account ID and other account information\
"""

# Set up the api call itself, only using phone number here
payload = {
    "getSpcAccountDivisionRequest": {
        "systemID": system_id,
        "telephoneNumber": "9809149590"
    }
}
request_kwargs = {
    "method": "POST",
    "url": url,
    "json": payload,
    "verify": True  # Verify SSL cert from server
}

# Add certificate auth if provided
if cert_auth:
    request_kwargs["cert"] = cert_auth.cert

# Make the post request call out to spectrum core services
response = requests.request(**request_kwargs)

# Will return an HTTPError object if an error has occurred during the process
response.raise_for_status()
# For now if it fails return empty list. Its possible there are just no records here
try:
    print("Results:")
    print(response.json()['getSpcAccountDivisionResponse']['spcAccountDivisionList'])
except Exception as e:
    print(f"Phone search found 0 matches, or the format of the JSON has been changed: {e}")
