Yes, you can store PFX certificates in Centrify (now part of Delinea). Here's a general approach for managing certificates with Centrify:

1. Using Centrify's Secret Management:
```python
from centrify.platform import Platform
import base64
import logging

logger = logging.getLogger(__name__)

class CentrifyPFXAuth:
    def __init__(self, secret_id: str):
        self.secret_id = secret_id
        self.platform = None
        self.session = None
        self.setup_centrify()

    def setup_centrify(self):
        """Setup connection to Centrify and retrieve PFX."""
        try:
            # Initialize Centrify Platform
            self.platform = Platform()
            
            # Retrieve secret from Centrify
            secret = self.platform.get_secret(self.secret_id)
            
            # The secret should contain both the PFX and password
            pfx_data = base64.b64decode(secret['pfx'])
            pfx_password = secret['password']
            
            # Setup the session with PFX data
            self.setup_session(pfx_data, pfx_password)
            
        except Exception as e:
            logger.error(f"Failed to retrieve certificate from Centrify: {str(e)}")
            raise

    def setup_session(self, pfx_data: bytes, pfx_password: str):
        """Setup a session with the PFX certificate."""
        try:
            # Create a session with our custom adapter
            self.session = requests.Session()
            adapter = PFXAdapter(pfx_data, pfx_password)
            self.session.mount('https://', adapter)
            
        except Exception as e:
            logger.error(f"Failed to setup certificate session: {str(e)}")
            raise
```

2. Store the certificate in Centrify:
```bash
# Using Centrify CLI (adjust commands based on your Centrify version)
centrify vault secret add --name "spectrum_core_pfx" --secret-file "/path/to/cert.pfx" --description "Spectrum Core API Certificate"
centrify vault secret set-password --name "spectrum_core_pfx" --password "your-pfx-password"
```

3. Configuration in settings:
```python
# settings.py
CENTRIFY_CONFIG = {
    'CERT_SECRET_ID': 'spectrum_core_pfx',
    # Other Centrify configuration...
}
```

4. Usage in your code:
```python
def _parse_spectrum_core_api(
        self,
        payload: dict,
        function_url: str,
        function_name: str,
        post_processing_function=None,
        response_key='getSpcAccountDivisionResponse',
        response_list_key='spcAccountDivisionList',
        cert_auth: Optional[CentrifyPFXAuth] = None,
    ) -> list[InternalRecord]:
        """Helper function for parsing information from spectrum core services
        account API."""
        try:
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
            
            # Rest of your code...
```

5. Example implementation:
```python
from django.conf import settings

# Initialize with secret ID from settings
cert_auth = CentrifyPFXAuth(settings.CENTRIFY_CONFIG['CERT_SECRET_ID'])

# Use in your API calls
result = _parse_spectrum_core_api(
    payload=payload,
    function_url=url,
    function_name="get_account_info",
    cert_auth=cert_auth
)
```

You'll need to:
1. Install Centrify SDK:
```bash
pip install centrify-platform-python
```

2. Configure Centrify authentication:
```python
# settings.py
CENTRIFY_CONFIG = {
    'TENANT_URL': 'your-tenant-url',
    'CLIENT_ID': 'your-client-id',
    'CLIENT_SECRET': 'your-client-secret',
    'SCOPE': 'your-scope',
    'CERT_SECRET_ID': 'spectrum_core_pfx'
}
```

3. Set up proper permissions in Centrify:
- Create a service account
- Grant necessary permissions for secret access
- Configure secret rotation policies if needed

Benefits of using Centrify:
1. Secure certificate storage
2. Centralized management
3. Access control
4. Audit logging
5. Automatic rotation if configured
6. No local certificate storage needed

Let me know if you need help with any specific part of the implementation!
