Here's the implementation using both a .cert file and .pem key file:

```python
import requests
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SpectrumCoreAuth:
    def __init__(self, cert_path: str, key_path: str):
        self.cert_path = cert_path
        self.key_path = key_path
        self.cert = (self.cert_path, self.key_path)

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
            request_kwargs = {
                "method": "POST",
                "url": function_url,
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
            
            # Process response
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
            
            return [
                msgspec.convert(x, type=InternalRecord)
                for x in core_services_list_to_add
            ]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in spectrum core api search: {function_name}")
            raise e

# Usage example:
if __name__ == "__main__":
    # Example configuration
    CERT_FILE = "path/to/your/certificate.cert"
    KEY_FILE = "path/to/your/private.pem"

    try:
        cert_auth = SpectrumCoreAuth(CERT_FILE, KEY_FILE)
        
        # Example API call
        payload = {"some": "data"}
        url = "https://api.example.com/endpoint"
        
        result = _parse_spectrum_core_api(
            None,  # self
            payload=payload,
            function_url=url,
            function_name="example",
            cert_auth=cert_auth
        )
        
    except Exception as e:
        logger.error(f"Failed to make API call: {str(e)}")
```

You would use it like this:
```python
# In your settings.py or similar:
SPECTRUM_CORE_AUTH = {
    'CERT_PATH': '/path/to/your/certificate.cert',
    'KEY_PATH': '/path/to/your/private.pem'
}

# In your code:
from django.conf import settings

cert_auth = SpectrumCoreAuth(
    settings.SPECTRUM_CORE_AUTH['CERT_PATH'],
    settings.SPECTRUM_CORE_AUTH['KEY_PATH']
)

# Then use cert_auth in your API calls
```

This is much simpler than the previous versions because:
1. Uses requests' built-in cert parameter
2. Doesn't require custom adapters
3. Files are read directly by requests
4. No need to handle the certificate data ourselves

Would you like me to add any error handling or validation for the file paths?
