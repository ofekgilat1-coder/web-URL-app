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
payload='<script>alert("Hi this is DAST test")</script>' #the xss payload
for param in params:
    test_params = params.copy()
    test_params[param] = payload   
    response=requests.get(URL, params=test_params, timeout=5)
    if payload in response.text: #checking if the payload in the HTML
        if ("&lt;"+payload) not in response.text and (payload+"&lt;") not in response.text and ("&quot;"+payload) not in response.text and (payload+"&quot;") not in response.text: #checking if its encripted
            HTML_CHECK = BeautifulSoup(response.text, "lxml")
            #checking if its in a comment
            comments = HTML_CHECK.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                if payload in comment.text:
                    print("no risk")
            #checking iff its in a script
            list_scripts=HTML_CHECK.find_all("script")
            for x in list_scripts:
                if payload in x.text:
                    print("high risk")
            #cheking if its in a regular text
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
            #checking if its in attribute
            List_all_tags= HTML_CHECK.find_all(True)           
            for tag in List_all_tags:
                dict_attributes=tag.attrs
                for attribute_name,attribute_value in tag.attrs.items():
                    if isinstance(attribute_value,list)==False:
                        if(payload in attribute_value):
                            if ("&lt;"+payload) not in attribute_value and (payload+"&lt;") not in attribute_value and ("&quot;"+payload) not in attribute_value and (payload+"&quot;") not in attribute_value:
                                if(attribute_name.startswith("on")):
                                    print("very high risk")
                                if(attribute_name=="href" or attribute_name=="src" or attribute_name=="style"):
                                    print("high risk")
                                if(attribute_name=="alt" or attribute_name=="title"):
                                    print("low risk")                   
                    else:
                        for att_val_inlist in attribute_value:
                            if(payload in att_val_inlist):
                                if ("&lt;"+payload) not in att_val_inlist and (payload+"&lt;") not in att_val_inlist and ("&quot;"+payload) not in att_val_inlist and (payload+"&quot;") not in att_val_inlist:
                                    if(attribute_name.startswith("on")):
                                        print("very high risk")
                                    if(attribute_name=="href" or attribute_name=="src" or attribute_name=="style"):
                                        print("high risk")
                                    if(attribute_name=="alt" or attribute_name=="title"):
                                        print("low risk")


             
                 
            




            














    






