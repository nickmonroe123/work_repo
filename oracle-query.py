Let's use the `cryptography` library instead, which is more stable for handling PKCS12 certificates:

```python
import requests
from pathlib import Path
import logging
from typing import Optional
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.pkcs12 import load_pkcs12

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
            # Read the PFX file
            with open(self.pfx_path, 'rb') as pfx_file:
                pfx_data = pfx_file.read()
            
            # Load the PKCS12 certificate
            p12 = load_pkcs12(
                pfx_data, 
                self.pfx_password.encode()
            )
            
            # Extract the private key and certificate
            private_key = p12.key
            cert = p12.cert
            
            # Convert to PEM format
            self._key = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            self._cert = cert.public_bytes(Encoding.PEM)
            
        except Exception as e:
            logger.error(f"Failed to load PFX certificate: {str(e)}")
            raise

    @property
    def cert(self):
        """Return certificate and private key as tuple for requests library."""
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
    PFX_PATH = "path/to/your/cert.pfx"
    PFX_PASSWORD = "your-password"

    try:
