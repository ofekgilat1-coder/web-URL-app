import sys
import requests
from urllib.parse import parse_qs, urlparse, urlunparse
from bs4 import BeautifulSoup
from bs4.element import Comment
import lxml
from html import unescape
from html import escape
import re
if len(sys.argv) > 1:
    x = sys.argv[1]
    print(f"DEBUG: Scanner received URL: {x}")
else:
    x = "http://example.com"
parsed= urlparse(x)
if parsed.scheme=="":
    x="https://"+x
    parsed = urlparse(x)
if parsed.scheme not in ("https","http") :
    URL1= urlunparse(("https", parsed.netloc, parsed.path, parsed.query, parsed.params,""))
    print(URL1)
    parsed = urlparse(URL1)
HEADERS = {"User-Agent": "Mozilla/5.0"}
URL_Scheme=parsed.scheme
URL_HostName=parsed.hostname
URL_path=parsed.path
URL_Query=parsed.query
URL_Fragment=parsed.fragment
URL= urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.query, parsed.params,""))
try:
    if URL_Scheme not in ("https", "http") or URL_HostName == "":
        raise Exception("Invalid URL")
except Exception as e:
    print(e)
finally:
    URL_HostName=URL_HostName.lower()
    try:
        Need_Slash1 = requests.get(URL, timeout=5, headers=HEADERS)
        if Need_Slash1.status_code >= 400:
            print("URL reachable but returned", Need_Slash1.status_code)
    except requests.RequestException:
        print("INVALID URL")
    if URL_path and URL_path[-1] == "/":
        try:
            URL_CHECK= urlunparse((URL_Scheme, parsed.netloc, parsed.path[:-1],parsed.query, parsed.params, ""))
            Need_Slash2 = requests.get(URL_CHECK, timeout=5, headers=HEADERS)
        except requests.RequestException:
            pass
        if (Need_Slash1.text==Need_Slash2.text and Need_Slash1.status_code==Need_Slash2.status_code):
            URL=URL_CHECK
Redirect_Response= requests.get(URL, timeout=5,allow_redirects=False, headers=HEADERS)
if 300 <= Redirect_Response.status_code < 400:
    print("Redirect detected")
    original_host = urlparse(URL).hostname
    redirect_host = urlparse(Redirect_Response.headers['Location']).hostname
    if redirect_host != original_host:
        print("the redirect gives differend host")
final_URL=URL
parsed= urlparse(final_URL)
def findHTTPONLY(URL):
    r = requests.get(URL, headers=HEADERS)
    for c in r.cookies:
        if c._rest.get("HttpOnly"):
            return 1
    return 0
def findSecure(URL):
    r = requests.get(URL, headers=HEADERS)
    for c in r.cookies:
        if c.secure:
            return 1
    return 0
def findSameSite(URL):
    history = []
    mainRequest = requests.session()
    req = mainRequest.request("GET",url=URL)
    history.append(req)
    if not req.cookies.get("Samesite") == None:
        return 3
    return 0
# XSS check
#List of dangerous tags
DANGEROUS_TAGS = [
    "script",
    "img",
    "svg",
    "iframe",
    "object",
    "embed",
    "link",
    "meta",
    "base",
    "video",
    "audio",
    "style"
]
level_of_risk="None"
#all type of risk level
RISK_ORDER = ["None","found but None", "low risk", "medium risk", "high risk", "critical"]
#function which sets the risk level
def set_risk(new):
    global level_of_risk
    if RISK_ORDER.index(new) > RISK_ORDER.index(level_of_risk):
        level_of_risk = new
#takes from the query the params
params = parse_qs(parsed.query)
if not params:
    params = {"xss": ["test"]}
#the payload
MARKER = "XSS_TEST_123"
def create_payloads():
    return {
        "event_plain": f'"><img src=x onerror={MARKER}>'
    }
payloads= create_payloads()
BASE_URL = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
for param in params:
    for payload in payloads.values():
        test_params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}
        #injecting the payload in the param value
        test_params[param] = payload
        try:  
            response=requests.get(BASE_URL, params=test_params, timeout=5, headers=HEADERS)
            decodedBody = unescape(response.text)
            headers_string = str(response.headers)
            if MARKER not in decodedBody and MARKER not in headers_string:
                continue
            set_risk("found but None")
            HTML_CHECK_Body = BeautifulSoup(decodedBody, "lxml")
            #checking if its in a comment
            comments = HTML_CHECK_Body.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                if MARKER in comment.text:
                    set_risk("found but None")
                if MARKER in unescape(comment.text):
                    set_risk("found but None")
            #cheking if its in a regular text 
            ALL_TEXT=HTML_CHECK_Body.find_all(string=True)
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
            #checking if in the enescaped text there is dangerous tag 
                text = unescape(Z).lower()
                for tag in DANGEROUS_TAGS:
                        if f"<{tag}" in text:
                            set_risk("low risk")
            #checking if its in a script
            list_scripts=HTML_CHECK_Body.find_all("script")
            for x in list_scripts:        
                if (MARKER in x.text or MARKER in unescape(x.text)):
                    if "</script>" in decodedBody.lower().split(MARKER)[0]:
                        set_risk("high risk")
            #checking if its in attribute
            List_all_tags= HTML_CHECK_Body.find_all(True)         
            for tag in List_all_tags:
                dict_attributes=tag.attrs
                for attribute_name,attribute_value in tag.attrs.items():  
                    val = unescape(str(attribute_value))
                    if MARKER in val:
                        if attribute_name.lower().startswith("on"):
                            set_risk("critical")
                        elif attribute_name.lower() in ["href", "src", "style"]:
                            if level_of_risk != "critical":
                                set_risk("high risk")
                            elif attribute_name.lower() in ["alt", "title"]:
                                set_risk("low risk")
            for h_name, h_val in response.headers.items():
                if MARKER in h_val:
                    set_risk("medium risk")
                    print(f"[!] Marker reflected in Header: {h_name}")
        except Exception as e:
            print(e)
#checking if the site is HTTPONLY and Secure
def Risk_inc_HTTPONLY(risk_level):
    x=findHTTPONLY(final_URL)
    if x==1:
        return
    if(risk_level=="low risk"):
        set_risk("medium risk")
    elif(risk_level=="medium risk"):
        set_risk("high risk")
    elif(risk_level=="high risk"):
        set_risk("critical")
additional_warning="None"
def Risk_inc_Secure(risk_level):
    global additional_warning
    if(findSecure(final_URL)==0):
        additional_warning = "Secure flag missing - Vulnerable to MitM"
Risk_inc_HTTPONLY(level_of_risk)
Risk_inc_Secure(level_of_risk)
print("the risk of reflected xss in your website is:"+level_of_risk)
print("additional risk is:"+additional_warning)
#example: https://httpbin.org/get?xss=test
#example: ynet.co.il



