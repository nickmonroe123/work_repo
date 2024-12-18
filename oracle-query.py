Failed to load PFX certificate: module 'OpenSSL.crypto' has no attribute 'load_pkcs12'
ERROR:root:Failed to load PFX certificate: module 'OpenSSL.crypto' has no attribute 'load_pkcs12'
Traceback (most recent call last):
  File "C:\Users\p3270115\Desktop\FuzzySearch\spectrum_core_api_test.py", line 58, in <module>
    cert_auth = SpectrumCoreAuth(
                ^^^^^^^^^^^^^^^^^
  File "C:\Users\p3270115\Desktop\FuzzySearch\spectrum_core_api_test.py", line 22, in __init__
    self.load_pfx()
  File "C:\Users\p3270115\Desktop\FuzzySearch\spectrum_core_api_test.py", line 28, in load_pfx
    p12 = crypto.load_pkcs12(pfx_data, self.pfx_password.encode())
          ^^^^^^^^^^^^^^^^^^
  File "C:\Users\p3270115\Desktop\FuzzySearch\venv\Lib\site-packages\cryptography\utils.py", line 68, in __getattr__
    obj = getattr(self._module, attr)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'OpenSSL.crypto' has no attribute 'load_pkcs12'
