import requests
from OpenSSL import crypto
import tempfile
import os
from pathlib import Path
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import (
    create_urllib3_context,
    DEFAULT_CIPHERS,
    OP_NO_SSLv2,
    OP_NO_SSLv3,
    OP_NO_TLSv1,
    OP_NO_TLSv1_1,
    CERT_REQUIRED
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecureHTTPAdapter(HTTPAdapter):
    """Custom HTTP adapter with strong SSL/TLS settings"""
    
    SECURE_CIPHERS = (
        'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:'
        'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
        'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:'
        'DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384'
    )

    def __init__(self, ssl_context=None):
        self.ssl_context = ssl_context
        super().__init__()

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(
            ciphers=self.SECURE_CIPHERS,
            cert_reqs=CERT_REQUIRED,
            options=OP_NO_SSLv2 | OP_NO_SSLv3 | OP_NO_TLSv1 | OP_NO_TLSv1_1
        )
        
        if self.ssl_context:
            context = self.ssl_context
            
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

class CertificateValidator:
    """Handles certificate validation and chain verification"""
    
    def __init__(self, trusted_ca_path: str):
        self.trusted_ca_path = trusted_ca_path
        self._validate_ca_cert()

    def _validate_ca_cert(self):
        """Validate the CA certificate"""
        try:
            with open(self.trusted_ca_path, 'rb') as ca_file:
                ca_data = ca_file.read()
                crypto.load_certificate(crypto.FILETYPE_PEM, ca_data)
        except Exception as e:
            raise ValueError(f"Invalid CA certificate: {e}")

    def verify_cert_chain(self, cert_path: str) -> bool:
        """Verify certificate chain against trusted CA"""
        try:
            with open(cert_path, 'rb') as cert_file:
                cert_data = cert_file.read()
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            
            with open(self.trusted_ca_path, 'rb') as ca_file:
                ca_data = ca_file.read()
                ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_data)
            
            # Create a certificate store and add the CA cert
            store = crypto.X509Store()
            store.add_cert(ca_cert)
            
            # Create a certificate context
            store_ctx = crypto.X509StoreContext(store, cert)
            
            # Verify the certificate
            store_ctx.verify_certificate()
            return True
            
        except Exception as e:
            logger.error(f"Certificate chain verification failed: {e}")
            return False

class SpectrumCoreAuth:
    """Handles authentication and certificate management for Spectrum Core API"""
    
    def __init__(self, pfx_path: str, pfx_password: str, digicert_path: str):
        """
        Initialize authentication with PFX certificate and DigiCert root certificate
        
        Args:
            pfx_path: Path to the .pfx/.p12 file
            pfx_password: Password for the PFX file
            digicert_path: Path to DigiCert root certificate
        """
        self.pfx_path = Path(pfx_path)
        self.pfx_password = pfx_password
        self.digicert_path = Path(digicert_path)
        self._temp_files = []
        
        # Validate input files
        self._validate_input_files()
        
        # Extract and validate certificates
        self.cert_path, self.key_path = self._extract_pfx()
        self.cert = (self.cert_path, self.key_path)
        
        # Initialize certificate validator
        self.validator = CertificateValidator(self.digicert_path)
        
        # Verify certificate chain
        if not self.validator.verify_cert_chain(self.cert_path):
            raise ValueError("Certificate chain validation failed")

    def _validate_input_files(self):
        """Validate that all required files exist"""
        if not self.pfx_path.exists():
            raise FileNotFoundError(f"PFX file not found: {self.pfx_path}")
        if not self.digicert_path.exists():
            raise FileNotFoundError(f"DigiCert file not found: {self.digicert_path}")

    def _extract_pfx(self):
        """Extract certificate and private key from PFX file"""
        try:
            with open(self.pfx_path, 'rb') as pfx_file:
                pfx_data = pfx_file.read()
            
            # Load PFX
            p12 = crypto.load_pkcs12(pfx_data, self.pfx_password.encode())
            
            # Create temporary files
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
            
        except Exception as e:
            logger.error(f"Error extracting PFX: {e}")
            self.cleanup()
            raise

    def cleanup(self):
        """Remove temporary certificate and key files"""
        for temp_file in self._temp_files:
            try:
                os.remove(temp_file)
            except OSError as e:
                logger.warning(f"Error removing temporary file {temp_file}: {e}")

    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.cleanup()

def create_secure_session(cert_auth: SpectrumCoreAuth) -> requests.Session:
    """Create a secure session with proper SSL configuration"""
    session = requests.Session()
    adapter = SecureHTTPAdapter()
    session.mount('https://', adapter)
    return session

def make_spectrum_request(phone_number: str, cert_auth: SpectrumCoreAuth) -> dict:
    """
    Make a secure request to the Spectrum Core API
    
    Args:
        phone_number: Phone number to query
        cert_auth: SpectrumCoreAuth instance
    
    Returns:
        API response as dictionary
    """
    system_id = "ComplianceService"
    url = "https://spectrumcore.charter.com:7443/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"

    payload = {
        "getSpcAccountDivisionRequest": {
            "systemID": system_id,
            "telephoneNumber": phone_number
        }
    }

    session = create_secure_session(cert_auth)

    try:
        response = session.post(
            url=url,
            json=payload,
            cert=cert_auth.cert,
            verify=cert_auth.digicert_path
        )
        response.raise_for_status()
        
        return response.json()['getSpcAccountDivisionResponse']['spcAccountDivisionList']
        
    except requests.exceptions.SSLError as ssl_err:
        logger.error(f"SSL Certificate Error: {ssl_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request Error: {req_err}")
        raise
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        raise
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize authentication with proper certificate paths
        cert_auth = SpectrumCoreAuth(
            pfx_path="path/to/your/cert.pfx",
            pfx_password="your_pfx_password",
            digicert_path="path/to/your/digicert.cer"
        )

        # Make the secure request
        results = make_spectrum_request(
            phone_number="9809149590",
            cert_auth=cert_auth
        )
        
        print("Results:", results)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        if 'cert_auth' in locals():
            cert_auth.cleanup()
