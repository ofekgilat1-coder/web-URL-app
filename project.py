import requests
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import lxml

x = input("Give a URL to check: ")
parsed= urlparse(x)
if parsed.scheme not in ("https","http") :
    URL1= urlunparse(("https", parsed.netloc, parsed.path, "", "", ""))
    print(URL1)
    parsed = urlparse(URL1)
URL_Scheme=parsed.scheme
URL_HostName=parsed.hostname
URL_path=parsed.path
URL_Query=parsed.query
URL_Fragment=parsed.fragment
URL= urlunparse((URL_Scheme, parsed.netloc, parsed.path, "", "", ""))
print(URL_path)
print(URL_Fragment)
try:
    if URL_Scheme not in ("https", "http") or URL_HostName == "":
        raise Exception("Invalid URL")
except Exception as e:
    print(e)
finally:
    URL_HostName=URL_HostName.lower()
    try:
        Need_Slash1 = requests.get(URL, timeout=5)
    except requests.RequestException:
        print("URL לא זמין")
    if URL_path and URL_path[-1] == "/":
        try:
            URL_CHECK= urlunparse((URL_Scheme, parsed.netloc, parsed.path[:-1], "", "", ""))
            Need_Slash2 = requests.get(URL_CHECK, timeout=5)
        except requests.RequestException:
            print("URL לא זמין")
        if (Need_Slash1.text==Need_Slash2.text and Need_Slash1.status_code==Need_Slash2.status_code):
            URL=URL_CHECK
Redirect_Response= requests.get(URL, timeout=5,allow_redirects=False)
if 300 <= Redirect_Response.status_code < 400:
    print("Redirect detected")
    original_host = urlparse(URL).hostname
    redirect_host = urlparse(Redirect_Response.headers['Location']).hostname
    if redirect_host != original_host:
        print("the redirect gives differend host")




    






