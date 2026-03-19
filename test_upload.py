import urllib.request
import urllib.parse
boundary = "someboundary123"
body = (
    b"--" + boundary.encode() + b"\r\n"
    b"Content-Disposition: form-data; name=\"file\"; filename=\"dummy.csv\"\r\n"
    b"Content-Type: text/csv\r\n\r\n"
    b"id,value\n1,10\n2,20\r\n"
    b"--" + boundary.encode() + b"--\r\n"
)
req = urllib.request.Request("http://127.0.0.1:8000/upload/")
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
try:
    with urllib.request.urlopen(req, data=body) as f:
        print("Success:", f.read().decode("utf-8"))
except Exception as e:
    if hasattr(e, 'read'):
        print("Error Payload:", e.read().decode("utf-8"))
    print("Error:", str(e))
