Yes, it's possible to send an RSA private key as a client certificate in the headers, though it's typically done through either the `cert` parameter or custom authentication header. Here are two approaches:

```python
import requests
from pathlib import Path
import logging
from typing import Optional
import base64

logger = logging.getLogger(__name__)

class SpectrumCoreAuth:
    def __init__(self, private_key_string: str):
        self.private_key = private_key_string
        
    def get_auth_headers(self):
        """Return headers with the private key."""
        # Option 1: Send as Bearer token
        return {
            'Authorization': f'Bearer {self.private_key}',
            # Or if you need a specific header name
            'X-Client-Cert': self.private_key,
        }

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
            headers = {}
            if cert_auth:
                headers.update(cert_auth.get_auth_headers())

            response = requests.post(
                function_url,
                json=payload,
                headers=headers,
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
    # Your RSA private key string
    PRIVATE_KEY = """
    -----BEGIN PRIVATE KEY-----
    Your key content here
    -----END PRIVATE KEY-----
    """
    
    try:
        cert_auth = SpectrumCoreAuth(PRIVATE_KEY)
        
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

Alternatively, if you need to encode the key:
```python
class SpectrumCoreAuth:
    def __init__(self, private_key_string: str):
        self.private_key = private_key_string
        
    def get_auth_headers(self):
        """Return headers with the encoded private key."""
        # Encode the key if needed
        encoded_key = base64.b64encode(self.private_key.encode()).decode()
        return {
            'X-Client-Cert': encoded_key,
        }
```

Important notes:
1. Make sure this aligns with how the server expects to receive the key
2. Consider security implications of sending private keys in headers
3. You might need to adjust the header name based on server requirements
4. You might need to encode/format the key string differently based on server requirements

Would you like me to show any specific header format or encoding method?
