The error is occurring because the requests library expects file paths for certificates, but we're passing the raw certificate data. Let's modify the code to save the certificate and key to temporary files before making the request:

```python
import requests
from pathlib import Path
import logging
from typing import Optional
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
import tempfile
import os

logger = logging.getLogger(__name__)

class SpectrumCoreAuth:
    def __init__(self, pfx_path: str, pfx_password: str):
        self.pfx_path = pfx_path
        self.pfx_password = pfx_password
        self._cert_path = None
        self._key_path = None
        self.load_pfx()

    def load_pfx(self):
        """Load certificate and private key from PFX file."""
        try:
            # Read the PFX file
            with open(self.pfx_path, 'rb') as pfx_file:
                pfx_data = pfx_file.read()
            
            # Load the PKCS12 certificate
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                pfx_data, 
                self.pfx_password.encode()
            )
            
            # Convert private key to PEM
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Convert certificate to PEM
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
            
            # Save to temporary files
            cert_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.crt')
            key_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.key')
            
            with cert_temp as f:
                f.write(cert_pem)
            with key_temp as f:
                f.write(key_pem)
            
            self._cert_path = cert_temp.name
            self._key_path = key_temp.name
            
        except Exception as e:
            logger.error(f"Failed to load PFX certificate: {str(e)}")
            self.cleanup()
            raise

    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self._cert_path and os.path.exists(self._cert_path):
                os.unlink(self._cert_path)
            if self._key_path and os.path.exists(self._key_path):
                os.unlink(self._key_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")

    @property
    def cert(self):
        """Return certificate and private key file paths as tuple."""
        return (self._cert_path, self._key_path) if self._cert_path and self._key_path else None

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()

def _parse_spectrum_core_api(
        self,
        payloa
