Here's the implementation using certificate and key strings directly in the code:

```python
import requests
from pathlib import Path
import logging
from typing import Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class SpectrumCoreAuth:
    def __init__(self, cert_string: str, key_string: str):
        """Initialize with certificate and key strings."""
        self.cert_string = cert_string
        self.key_string = key_string
        self._cert_file = None
        self._key_file = None
        self.create_temp_files()

    def create_temp_files(self):
        """Create temporary files for the certificate and key."""
        try:
            # Create temp file for cert
            self._cert_file = tempfile.NamedTemporaryFile(delete=False, suffix='.crt')
            self._cert_file.write(self.cert_string.encode())
            self._cert_file.flush()

            # Create temp file for key
            self._key_file = tempfile.NamedTemporaryFile(delete=False, suffix='.key')
            self._key_file.write(self.key_string.encode())
            self._key_file.flush()

        except Exception as e:
            logger.error(f"Failed to create temporary certificate files: {str(e)}")
            self.cleanup()
            raise

    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self._cert_file:
                os.unlink(self._cert_file.name)
            if self._key_file:
                os.unlink(self._key_file.name)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")

    @property
    def cert(self):
        """Return certificate and key file paths as tuple."""
        return (self._cert_file.name, self._key_file.name) if self._cert_file and self._key_file else None

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()

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
                "verify": True
            }

            if cert_auth:
                request_kwargs["cert"] = cert_auth.cert
            
            response = requests.request(**request_kwargs)
            response.raise_for_status()
            
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
    # Certificate and key strings directly in code
    CERT_STRING = """-----BEGIN CERTIFICATE-----
    Your certificate content here
    -----END CERTIFICATE-----"""

    KEY_STRING = """-----BEGIN PRIVATE KEY-----
    Your private key content here
    -----END PRIVATE KEY-----"""

    try:
        cert_auth = SpectrumCoreAuth(CERT_STRING, KEY_STRING)
        
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
    finally:
        if 'cert_auth' in locals():
            cert_auth.cleanup()
```

Key features of this implementation:
1. Takes certificate and key as strings directly
2. Creates temporary files in the background (required for requests library)
3. Automatically cleans up temporary files
4. Handles errors appropriately

You would use it like this:
```python
# Your certificate strings
CERT_STRING = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiIMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
...rest of your certificate...
-----END CERTIFICATE-----"""

KEY_STRING = """-----BEGIN PRIVATE KEY-----
MIIBPQIBAAJBAKWXp/qrjL9QNcuKQR2PGzyexBaGNN2vYPq4PW3Q/L/zqKR0yN0T
...rest of your private key...
-----END PRIVATE KEY-----"""

# Initialize auth
cert_auth = SpectrumCoreAuth(CERT_STRING, KEY_STRING)

# Use in your API calls
result = _parse_spectrum_core_api(
    payload=payload,
    function_url=url,
    function_name="get_account_info",
    cert_auth=cert_auth
)
```

Would you like me to:
1. Add validation for the certificate/key string format?
2. Add more error handling?
3. Show how to store these strings securely in settings?
