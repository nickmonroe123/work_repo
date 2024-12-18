Here's the modified code to use an unencrypted .pem file instead of a PFX file:

```python
import requests
from pathlib import Path
import logging
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

logger = logging.getLogger(__name__)

class PEMAdapter(HTTPAdapter):
    """Custom HTTP adapter that uses PEM certificate data directly."""
    def __init__(self, cert_data, key_data, **kwargs):
        self.cert_data = cert_data
        self.key_data = key_data
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.load_cert_chain_from_buffer(
            certfile=self.cert_data,
            keyfile=self.key_data
        )
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

class SpectrumCoreAuth:
    def __init__(self, cert_path: str, key_path: str):
        self.cert_path = cert_path
        self.key_path = key_path
        self.session = None
        self.setup_session()

    def setup_session(self):
        """Setup a session with the PEM certificate and key."""
        try:
            # Read the certificate and key files
            with open(self.cert_path, 'rb') as cert_file:
                cert_data = cert_file.read()
            
            with open(self.key_path, 'rb') as key_file:
                key_data = key_file.read()
            
            # Create a session with our custom adapter
            self.session = requests.Session()
            adapter = PEMAdapter(cert_data, key_data)
            self.session.mount('https://', adapter)
            
        except Exception as e:
            logger.error(f"Failed to setup certificate session: {str(e)}")
            raise

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
            # Make the post request call out to spectrum core services
            if cert_auth and cert_auth.session:
                response = cert_auth.session.post(
                    function_url,
                    json=payload,
                    verify=True
                )
            else:
                response = requests.post(
                    function_url,
                    json=payload,
                    verify=True
                )
            
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
    CERT_PATH = "path/to/your/certificate.pem"
    KEY_PATH = "path/to/your/private_key.pem"

    try:
        cert_auth = SpectrumCoreAuth(CERT_PATH, KEY_PATH)
        
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

Alternatively, you could also use the simpler built-in requests cert parameter if you don't need the custom adapter:

```python
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
        try:
            request_kwargs = {
                "url": function_url,
                "json": payload,
                "verify": True
            }

            if cert_auth:
                request_kwargs["cert"] = cert_auth.cert

            response = requests.post(**request_kwargs)
            
            # Rest of your code...
```

The second version is simpler because requests natively supports PEM files through the cert parameter. You just need to provide the paths as a tuple.

To use this:

1. Make sure your certificate and key are in PEM format
2. Configure the paths in your settings:
```python
# settings.py
SPECTRUM_CORE_AUTH = {
    'CERT_PATH': '/path/to/certificate.pem',
    'KEY_PATH': '/path/to/private_key.pem'
}
```

3. Use in your code:
```python
from django.conf import settings

cert_auth = SpectrumCoreAuth(
    settings.SPECTRUM_CORE_AUTH['CERT_PATH'],
    settings.SPECTRUM_CORE_AUTH['KEY_PATH']
)
```

This approach is:
1. Simpler than using PFX files
2. Doesn't require password management
3. Works directly with requests without custom adapters (in the second version)
4. More transparent and easier to debug

Would you like me to show how to convert a PFX to PEM format if needed?
