# httpx client to call directly  into  a python web application  using WSGI protocol
from  flask from Flask
import httpx

app = Flask(___name___)

@app.route("/")
def hello():
    return " Hello World!"
with httpx.Client(app = app, base_url = "http://testserver") as client:
    r = client.get("/")
    print(r.text)
    assert r.status_code == 200
    assert r.text == "Hello World!"