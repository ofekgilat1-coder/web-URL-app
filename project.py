import requests
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from bs4.element import Comment
import lxml

x = input("Give a URL to check: ")
parsed= urlparse(x)
if parsed.scheme=="":
    x="https://"+x
    parsed = urlparse(x)
if parsed.scheme not in ("https","http") :
    URL1= urlunparse(("https", parsed.netloc, parsed.path, parsed.query, parsed.params,""))
    print(URL1)
    parsed = urlparse(URL1)
URL_Scheme=parsed.scheme
URL_HostName=parsed.hostname
URL_path=parsed.path
URL_Query=parsed.query
URL_Fragment=parsed.fragment
URL= urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.query, parsed.params,""))
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
            URL_CHECK= urlunparse((URL_Scheme, parsed.netloc, parsed.path[:-1],parsed.query, parsed.params, ""))
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
final_URL=URL
parsed= urlparse(final_URL)
# XSS check
params = parse_qs(parsed.query)
payload='<script>alert("Hi this is DAST test")</script>'
for param in params:
    test_params = params.copy()
    test_params[param] = payload   
    response=requests.get(URL, params=test_params, timeout=5)
    if payload in response.text:
        if ("&lt;"+payload) not in response.text and (payload+"&lt;") not in response.text and ("&quot;"+payload) not in response.text and (payload+"&quot;") not in response.text:
            HTML_CHECK = BeautifulSoup(response.text, "lxml")
            comments = HTML_CHECK.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                if payload in comment.text:
                    print("no risk")
            list_scripts=HTML_CHECK.find_all("script")
            for x in list_scripts:
                if payload in x.text:
                    print("high risk")
            ALL_TEXT=HTML_CHECK.find_all(string=True)
            REG_TEXT=[]
            for checker in ALL_TEXT:
                if (isinstance(checker, Comment)):
                    continue
                elif(checker.parent.name=="script"):
                    continue
                elif(checker.parent.name=="style"):
                    continue
                elif(checker.strip()==""):
                    continue
                else:
                    REG_TEXT.append(checker)
            
            for Z in REG_TEXT:
                if payload in Z:
                    print("medium risk")       
            




            














    






