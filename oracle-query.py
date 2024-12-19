I'll help you modify the code to use the DigiCert certificate to establish trust with the SSL server certificate. Here's how you can modify your code:

```python
import requests
import ssl

class SpectrumCoreAuth:
    def __init__(self, cert_path: str, key_path: str, digicert_path: str = None):
        self.cert_path = cert_path
        self.key_path = key_path
        self.digicert_path = digicert_path
        self.cert = (self.cert_path, self.key_path)

CERT_FILE = "server.crt"
KEY_FILE = "key.pem"
DIGICERT_FILE = "path/to/your/digicert.cer"  # Add your DigiCert certificate path here
cert_auth = SpectrumCoreAuth(CERT_FILE, KEY_FILE, DIGICERT_FILE)

system_id = "ComplianceService"
url = "https://spectrumcore.charter.com:7443/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"

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
    "verify": cert_auth.digicert_path if cert_auth.digicert_path else True  # Use DigiCert certificate for verification
}

# Add client certificate auth if provided
if cert_auth:
    request_kwargs["cert"] = cert_auth.cert

try:
    # Make the post request call out to spectrum core services
    response = requests.request(**request_kwargs)
    
    # Will return an HTTPError object if an error has occurred during the process
    response.raise_for_status()
    
    print("Results:")
    print(response.json()['getSpcAccountDivisionResponse']['spcAccountDivisionList'])
except requests.exceptions.SSLError as ssl_err:
    print(f"SSL Certificate Error: {ssl_err}")
except requests.exceptions.RequestException as req_err:
    print(f"Request Error: {req_err}")
except Exception as e:
    print(f"Phone search found 0 matches, or the format of the JSON has been changed: {e}")
```

Key changes made:
1. Added `digicert_path` parameter to the `SpectrumCoreAuth` class
2. Modified the `verify` parameter in `request_kwargs` to use the DigiCert certificate
3. Added better exception handling for SSL-specific errors

If you're still experiencing SSL verification issues, you might need to create a custom SSL context:

```python
import requests
import ssl

class SpectrumCoreAuth:
    def __init__(self, cert_path: str, key_path: str, digicert_path: str = None):
        self.cert_path = cert_path
        self.key_path = key_path
        self.digicert_path = digicert_path
        self.cert = (self.cert_path, self.key_path)
        
        # Create custom SSL context if DigiCert is provided
        if self.digicert_path:
            self.ssl_context = ssl.create_default_context(cafile=self.digicert_path)
            self.ssl_context.load_cert_chain(self.cert_path, self.key_path)

# Rest of your code remains the same, but modify the request section:
try:
    if cert_auth.digicert_path:
        session = requests.Session()
        session.verify = cert_auth.digicert_path
        session.cert = cert_auth.cert
        response = session.post(url, json=payload)
    else:
        response = requests.request(**request_kwargs)
    
    response.raise_for_status()
    print("Results:")
    print(response.json()['getSpcAccountDivisionResponse']['spcAccountDivisionList'])
except requests.exceptions.SSLError as ssl_err:
    print(f"SSL Certificate Error: {ssl_err}")
except requests.exceptions.RequestException as req_err:
    print(f"Request Error: {req_err}")
except Exception as e:
    print(f"Phone search found 0 matches, or the format of the JSON has been changed: {e}")
```

Make sure to:
1. Replace `"path/to/your/digicert.cer"` with the actual path to your DigiCert certificate
2. Ensure all certificate files have proper read permissions
3. Verify that the DigiCert certificate is in the correct format (.cer)

If you're still getting SSL verification errors, you might need to:
1. Check if the DigiCert certificate is in the correct format
2. Verify that the certificate chain is complete
3. Ensure the certificate hasn't expired
4. Confirm that the hostname in the certificate matches the server's hostname

Would you like me to help you troubleshoot any specific SSL errors you're encountering?
