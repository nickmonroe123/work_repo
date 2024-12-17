I'll help you integrate PFX certificate authentication into your API call. Here's how to modify your code to use PFX authentication:

```python
import requests
import msgspec
from pathlib import Path
from OpenSSL import crypto
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SpectrumCoreAuth:
    def __init__(self, pfx_path: str, pfx_password: str):
        self.pfx_path = pfx_path
        self.pfx_password = pfx_password
        self._cert = None
        self._key = None
        self.load_pfx()

    def load_pfx(self):
        """Load certificate and private key from PFX file."""
        try:
            pfx_data = Path(self.pfx_path).read_bytes()
            p12 = crypto.load_pkcs12(pfx_data, self.pfx_password.encode())
            
            # Get certificate
            cert_data = crypto.dump_certificate(
                crypto.FILETYPE_PEM, 
                p12.get_certificate()
            )
            
            # Get private key
            key_data = crypto.dump_privatekey(
                crypto.FILETYPE_PEM, 
                p12.get_privatekey()
            )
            
            self._cert = cert_data
            self._key = key_data
            
        except Exception as e:
            logger.error(f"Failed to load PFX certificate: {str(e)}")
            raise

    @property
    def cert(self):
        """Return certificate and private key as tuple."""
        return (self._cert, self._key) if self._cert and self._key else None

def _parse_spectrum_core_api(
        self,
        payload: dict,
        function_url: str,
        function_name: str,
        post_processing_function=None,
        response_key='getSpcAccountDivisionResponse',
        response_list_key='spcAccountDivisionList',
        cert_auth: Optional[SpectrumCoreAuth] = None,
    ) -> list[InternalRecord]:
        """Helper function for parsing information from spectrum core services
        account API."""
        try:
            # Setup request kwargs
            request_kwargs = {
                "method": "POST",
                "url": function_url,
                "json": payload,
                "verify": True,  # Verify SSL cert from server
            }

            # Add certificate auth if provided
            if cert_auth:
                request_kwargs["cert"] = cert_auth.cert
            
            # Make the post request call out to spectrum core services
            response = requests.request(**request_kwargs)
            
            # Will return an HTTPError object if an error has occurred during the process
            response.raise_for_status()
            
            # For now if it fails return empty list. Its possible there are just no records here
            response_key_contents = response.json().get(response_key)
            if response_key_contents is None:
                logger.error(
                    f"The format of the JSON has been changed during {function_name}! New format: {response.json()}"
                )
                raise ValueError('Format of Spectrum Core Account API has changed')
                
            core_services_list_to_add = response_key_contents.get(response_list_key, [])
            if post_processing_function is not None:
                core_services_list_to_add = post_processing_function(
                    core_services_list_to_add
                )
            
            core_services_list_to_add = [
                msgspec.convert(x, type=InternalRecord)
                for x in core_services_list_to_add
            ]
            return core_services_list_to_add
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in spectrum core api search: {function_name}")
            raise e

# Usage example:
"""
# In your settings.py or similar configuration file
SPECTRUM_CORE_AUTH = {
    'PFX_PATH': '/path/to/your/certificate.pfx',
    'PFX_PASSWORD': 'your-pfx-password'
}

# In your code
from django.conf import settings

# Initialize the auth handler
cert_auth = SpectrumCoreAuth(
    settings.SPECTRUM_CORE_AUTH['PFX_PATH'],
    settings.SPECTRUM_CORE_AUTH['PFX_PASSWORD']
)

# Use in your API call
result = self._parse_spectrum_core_api(
    payload=payload,
    function_url=url,
    function_name="get_account_info",
    cert_auth=cert_auth
)
"""
```

Key changes and additions:

1. Added `SpectrumCoreAuth` class to handle PFX certificate loading and management
2. Added certificate authentication to the requests call
3. Made certificate auth optional with a default of None
4. Added proper error handling for certificate loading
5. Added configuration structure for PFX details

To use this in your project:

1. Install required packages:
```bash
pip install pyOpenSSL requests
```

2. Add settings to your Django configuration:
```python
# settings.py
SPECTRUM_CORE_AUTH = {
    'PFX_PATH': '/path/to/your/certificate.pfx',
    'PFX_PASSWORD': 'your-pfx-password'
}
```

3. Create the auth handler where needed:
```python
cert_auth = SpectrumCoreAuth(
    settings.SPECTRUM_CORE_AUTH['PFX_PATH'],
    settings.SPECTRUM_CORE_AUTH['PFX_PASSWORD']
)
```

4. Use it in your API calls:
```python
result = self._parse_spectrum_core_api(
    payload=payload,
    function_url=url,
    function_name="get_account_info",
    cert_auth=cert_auth
)
```

Would you like me to:
1. Add more error handling cases?
2. Add certificate validation checks?
3. Show how to handle certificate expiration?
4. Add testing examples?
