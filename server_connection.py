import socket as ns
import threading
import os
import mimetypes as mt
import subprocess
from urllib.parse import unquote


status_codes = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    500: "Internal Server Error",
    403: "Forbidden",
    302: "Moved Temporarily",
    301: "Moved Permanently",
}

complex_types = {
    "text/html": "text/html; charset=UTF-8",
    "application/json": "application/json; charset=UTF-8",
    "application/xml": "application/xml; charset=UTF-8",
    "text/css": "text/css; charset=UTF-8",
    "application/javascript": "application/javascript; charset=UTF-8",
    "text/javascript": "text/javascript; charset=UTF-8",
}

default_access = "index.html"

return_adress = "return.txt"

server_path = "127.0.0.1"
server_port = 8080

#client to server functions
def connect_to_client():
    connection , adress = main_frame.accept()
    print("Connected to", adress)
    
    try:
        full_request = connection.recv(2048).decode() 
        if not full_request:
            connection.close()
            return

        # מפרידים את המתודה (GET)
        method = full_request.split(" ")[0]
        
        # בודקים במילון (תומכים גם עם רווח וגם בלי)
        func = options.get(method) or options.get(method + " ")
        
        if func:
            # חשוב: לא סוגרים את ה-connection כאן!
            func(connection, adress, full_request)
        else:
            first_check(connection, adress)
            
    except Exception as e:
        print(f"Error handling connection: {e}")
        try: connection.close() 
        except: pass
def GET_(connection, adress, raw_data):
    full_url = extractFile(raw_data)

    # פיצול query string
    if "?" in full_url:
        url, part = full_url.split("?", 1)
    else:
        url, part = full_url, ""

    params = toObj(part)
    lookup_url = url if url.startswith("/") else "/" + url

    # אם זה נתיב מיוחד (spicel)
    if lookup_url in spicel:
        print(f"Executing special function for {lookup_url}...")
        result = spicel[lookup_url](params)
        # אם הפונקציה מחזירה None, נמשיך להחזיר HTTP 200 ריק
        if result is None:
            connection.send(finish_for_sending(get_status_code(200)).encode())
            connection.close()
            return
        url = result

    file_to_open = url.lstrip("/")

    if not os.path.isfile(file_to_open):
        print(f"404 Not Found: {file_to_open}")
        connection.send(finish_for_sending(get_status_code(404)).encode())
        connection.close()
        return

    send_file(connection, adress, file_to_open)
    connection.close()
    print(f"Connection with {adress} closed successfully.")
    
def POST_(conection,adress):
    return True

def send_file(connection, adress, url):
    data=0
    try:
        with open (r"{}".format(url), "rb") as f:
            data = f.read()
    except :
            url = url[1:]
            with open (r"{}".format(url), "rb") as f:
                data = f.read()
    connection.send(finish_for_sending(get_status_code(200),data, **{"Content-Type": getType(url)}).encode())
    connection.send(data)
    print("File sent successfully")

def connect_loop():
    while True:
        connect_to_client()

def checkURL(data):
    #header
    if not (data.startswith("http://") or data.startswith("https://")):
        return False
    str = "1"
    if data.split("//")[1].startswith("{}".format(server_path)):
        return True
    #check for valid domain
    return (data.endswith(" HTTP/1.1\r\n"))

def extractFile(data):
    try:
        return data.split(" ")[1]
    except:
        return "/"
    
def finish_for_sending(massege,data="",**kwargs):
    ret = "HTTP/1.0 {} \r\n".format(massege)
    for key, value in kwargs.items():
        ret += "{}: {}\r\n".format(key, value)
    ret += "Content-Length: {}\r\n\r\n".format(len(data))
    return ret

def get_status_code(code):
    return "{} {}".format(code,status_codes[code])

def getType(url):
    type1 = mt.guess_type(url)[0]
    if(type1 in complex_types):
        type1+= "; charset=UTF-8"
    return type1

def first_check(connection, adress):
    print("{} failed first check".format(adress))
    connection.send(finish_for_sending(get_status_code(400)).encode())
    connection.close()
    return

def toObj(data):
    if not data: return {}
    str_list = data.split("&")
    ret = {}
    for i in str_list:
        if "=" in i:
            # גם כאן, מפצלים רק בסימן השווה הראשון
            key, value = i.split("=", 1)
            ret[key.strip()] = value.strip()
    return ret

#server to server functions

def enter_input() :
    while True:
        data = input(">>>")
        print("You entered:", data)
        data =data.lower()
        if(inner_options.get(data) is None):
            print("Invalid command.")
        else:
            inner_options[data]()
            if(data == "end"):
                break

def check_program():
    print("online")

def end_program():
    main_frame.close()
    print("Server stopped")


#spicel functions
def get_default_access(*args, **kwargs):
    print("Sending default")
    open(return_adress,"w").write(str(""))
    return default_access

def run_script(*args, **kwargs):
    params = args[0]
    target_url = unquote(params.get("URL", ""))

    if not target_url:
        return default_access

    # כותב בהתחלה
    with open(return_adress, "w", encoding="utf-8") as f:
        f.write("Scanning...\n")

    print(f"--- Starting Scan for: {target_url} ---")

    try:
        import sys
        process = subprocess.run(
            [sys.executable, "project.py", target_url],
            capture_output=True,
            text=True,
            timeout=15
        )

        output = process.stdout.strip()
        if not output:
            output = "None (No reflection)"

    except subprocess.TimeoutExpired:
        output = "Scan Timed Out (Safe/Slow)"
    except Exception as e:
        output = f"Error: {str(e)}"

    with open(return_adress, "w", encoding="utf-8") as f:
        f.write(output + "\n")
        f.flush()
        os.fsync(f.fileno())

    return return_adress
#dictioneries
options = {
    "GET": GET_,
    "POST": POST_,
}

inner_options = {
    "check": check_program,
    "end": end_program,
    "exit": end_program,
    "quit": end_program,
    "stop": end_program,
}

spicel = {
    "/": get_default_access,
    "/check": run_script,
}

main_frame = ns.socket()
main_frame.bind((server_path,server_port))
main_frame.listen(5)
threading.Thread(target=connect_loop,daemon=True).start()
enter_input()
open("return.txt", "w").close()