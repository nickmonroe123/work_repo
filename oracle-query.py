Traceback (most recent call last):
  File "C:\Users\p3270115\Desktop\FuzzySearch\spectrum_core_api_test.py", line 94, in <module>
    response = requests.request(**request_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\p3270115\Desktop\FuzzySearch\venv\Lib\site-packages\requests\api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\p3270115\Desktop\FuzzySearch\venv\Lib\site-packages\requests\sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\p3270115\Desktop\FuzzySearch\venv\Lib\site-packages\requests\sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\p3270115\Desktop\FuzzySearch\venv\Lib\site-packages\requests\adapters.py", line 639, in send
    self.cert_verify(conn, request.url, verify, cert)
  File "C:\Users\p3270115\Desktop\FuzzySearch\venv\Lib\site-packages\requests\adapters.py", line 350, in cert_verify
    raise OSError(
OSError: Could not find the TLS certificate file, invalid path: b'-----BEGIN CERTIFICATE-----\
