import requests
from OpenSSL import crypto
import tempfile
import os
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

class CustomHttpAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.ssl_context = create_urllib3_context(
            cert_reqs='CERT_NONE',
            options=0x4  # OP_LEGACY_SERVER_CONNECT
        )
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)

class SpectrumCoreAuth:
    def __init__(self, pfx_path: str, pfx_password: str, digicert_path: str = None):
        """
        Initialize authentication with PFX certificate and optional DigiCert root certificate
        
        Args:
            pfx_path: Path to the .pfx/.p12 file
            pfx_password: Password for the PFX file
            digicert_path: Optional path to DigiCert root certificate
        """
        self.pfx_path = pfx_path
        self.pfx_password = pfx_password
        self.digicert_path = digicert_path
        self._temp_files = []
        
        # Extract certificate and private key from PFX
        self.cert_path, self.key_path = self._extract_pfx()
        self.cert = (self.cert_path, self.key_path)

    def _extract_pfx(self):
        """Extract certificate and private key from PFX file into temporary files"""
        # Read PFX file
        with open(self.pfx_path, 'rb') as pfx_file:
            pfx_data = pfx_file.read()
            
        # Load PFX
        p12 = crypto.load_pkcs12(pfx_data, self.pfx_password.encode())
        
        # Create temporary files for cert and key
        cert_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.crt')
        key_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.key')
        self._temp_files.extend([cert_temp.name, key_temp.name])
        
        # Write certificate
        cert_data = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
        cert_temp.write(cert_data)
        cert_temp.close()
        
        # Write private key
        key_data = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
        key_temp.write(key_data)
        key_temp.close()
        
        return cert_temp.name, key_temp.name

    def cleanup(self):
        """Remove temporary certificate and key files"""
        for temp_file in self._temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass

    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.cleanup()

def make_spectrum_request(phone_number: str, cert_auth: SpectrumCoreAuth, verify_ssl: bool = False):
    """
    Make a request to the Spectrum Core API
    
    Args:
        phone_number: Phone number to query
        cert_auth: SpectrumCoreAuth instance
        verify_ssl: Whether to verify SSL certificate
    """
    system_id = "ComplianceService"
    url = "https://spectrumcore.charter.com:7443/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"

    # Set up the request payload
    payload = {
        "getSpcAccountDivisionRequest": {
            "systemID": system_id,
            "telephoneNumber": phone_number
        }
    }

    # Create a session with custom SSL handling
    session = requests.Session()
    adapter = CustomHttpAdapter()
    session.mount('https://', adapter)

    # Configure request parameters
    request_kwargs = {
        "method": "POST",
        "url": url,
        "json": payload,
        "verify": verify_ssl,
        "cert": cert_auth.cert
    }

    try:
        # Make the request
        response = session.request(**request_kwargs)
        response.raise_for_status()
        
        # Process response
        return response.json()['getSpcAccountDivisionResponse']['spcAccountDivisionList']
    except requests.exceptions.SSLError as ssl_err:
        print(f"SSL Certificate Error: {ssl_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request Error: {req_err}")
        return None
    except Exception as e:
        print(f"Error processing response: {e}")
        return None
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    # Disable SSL verification warnings if we're not verifying
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    PFX_FILE = "your_cert.pfx"  # Replace with your PFX file path
    PFX_PASSWORD = "your_password"  # Replace with your PFX password
    DIGICERT_FILE = "digicert_root.cer"  # Optional, replace with your DigiCert file path

    # Initialize authentication
    cert_auth = SpectrumCoreAuth(
        pfx_path=PFX_FILE,
        pfx_password=PFX_PASSWORD,
        digicert_path=DIGICERT_FILE
    )

    try:
        # Make the request with SSL verification disabled
        results = make_spectrum_request(
            phone_number="9809149590",
            cert_auth=cert_auth,
            verify_ssl=False  # Set to True if you want to verify SSL
        )
        
        if results is not None:
            print("Results:")
            print(results)
    finally:
        # Cleanup temporary files
        cert_auth.cleanup()
