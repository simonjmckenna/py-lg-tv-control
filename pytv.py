#!/usr/bin/env python3
#Full list of commands
#http://developer.lgappstv.com/TV_HELP/index.jsp?topic=%2Flge.tvsdk.references.book%2Fhtml%2FUDAP%2FUDAP%2FAnnex+A+Table+of+virtual+key+codes+on+remote+Controller.htm
import http.client
from tkinter import *
import socket
import re
import sys
lgtv = {}

dialogMsg =""
lgtv["pairingKey"] = "676905"
lgtv["ipaddress"] = None
lgtv["ipaddress"] = "192.168.1.55"

def getip():
    strngtoXmit =   'M-SEARCH * HTTP/1.1' + '\r\n' + \
                    'HOST: 239.255.255.250:1900'  + '\r\n' + \
                    'MAN: "ssdp:discover"'  + '\r\n' + \
                    'ST: udap:rootservice\r\n' +  '\r\n' + \
                    'MX: 3'  + '\r\n' + \
                    'USER-AGENT: Linux/2.6.18 UDAP/2.0 \r\n\r\n'
    bytestoXmit = strngtoXmit.encode()
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.settimeout(3)
    found = False
    gotstr = 'notyet'
    i = 0
    ipaddress = None
    sock.sendto( bytestoXmit,  ('239.255.255.250', 1900 ) )
    while not found and i <= 5 and gotstr == 'notyet':
        try:
            gotbytes, addressport = sock.recvfrom(512)
            gotstr = gotbytes.decode()
        except:
            i += 1
            sock.sendto( bytestoXmit, ( '239.255.255.250', 1900 ) )
        if re.search('LOCATION:', gotstr):
            ipaddress = re.search(r'[0-9]+(?:\.[0-9]+){3}',gotstr).group()
            print("IPADDRESS=",ipaddress)
            found = True
        else:
            gotstr = 'notyet'
        i += 1
    sock.close()
    if not found : sys.exit("Lg TV not found")
    return ipaddress

def displayKey():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    XML = 	'<?xml version=\"1.0\" encoding=\"utf-8\"?>' \
		+ '<envelope>' \
		+ '<api type=\"pairing\">' \
		+ '<name>showKey</name>' \
		+ '</api>' \
		+ '</envelope>' 
    conn.putrequest("POST", "/udap/api/pairing")
    conn.putheader("Content-type","text/xml")
    conn.putheader("Accept","text/plain")
    conn.putheader("User-Agent","UDAP/2.0")
    conn.putheader("Content-length",len(XML))
    conn.endheaders()
    conn.send(XML.encode())
    httpResponse = conn.getresponse()
    conn.close()
    return httpResponse.reason

def pairwithTV():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    XML = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" \
	+ "<envelope>" \
	+ "<api type=\"pairing\">" \
	+ "<name>hello</name>" \
        + "<value>" + lgtv["pairingKey"] + "</value>" \
        + "<port>8080</port>" \
	+ "</api>" \
	+ "</envelope>" 
    conn.putrequest("POST", "/udap/api/pairing")
    conn.putheader("Content-type","text/xml")
    conn.putheader("Accept","text/plain")
    conn.putheader("User-Agent","UDAP/2.0")
    conn.putheader("Content-length",len(XML))
    conn.endheaders()
    conn.send(XML.encode())
    httpResponse = conn.getresponse()
    conn.close()
    return httpResponse.reason

def unpairwithTV():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    XML = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" \
	+ "<envelope>" \
	+ "<api type=\"pairing\">" \
	+ "<name>byebye</name>" \
        + "<port>8080</port>" \
	+ "</api>" \
	+ "</envelope>" 
    conn.putrequest("POST", "/udap/api/pairing")
    conn.putheader("Content-type","text/xml")
    conn.putheader("Accept","text/plain")
    conn.putheader("User-Agent","UDAP/2.0")
    conn.putheader("Content-length",len(XML))
    conn.endheaders()
    conn.send(XML.encode())
    httpResponse = conn.getresponse()
    conn.close()
    return httpResponse.reason

def handleCommand(cmdcode):
    print ("5")
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    XML = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" \
		+ "<envelope>" \
		+ "<api type=\"command\">" \
                + "<name>HandleKeyInput</name><value>" \
                + cmdcode \
                + "</value>" \
		+ "</api>" \
		+ "</envelope>" 
    conn.putrequest("POST", "/udap/api/command")
    conn.putheader("Content-type","text/xml")
    conn.putheader("Accept","text/plain")
    conn.putheader("User-Agent","UDAP/2.0")
    conn.putheader("Content-length",len(XML))
    conn.endheaders()
    conn.send(XML.encode())
    httpResponse = conn.getresponse()
    conn.close()
    return httpResponse.reason
#main()

if lgtv["ipaddress"] == None : lgtv["ipaddress"] = getip()

command = str(sys.argv[1])

if command == "showkey":
    result = displayKey()
elif command == "pair":
    result =  pairwithTV()
elif command == "fail":
    print("1")
    result = "FAIL"
elif command == "unpair":
    result = unpairwithTV()
else: 
    result = handleCommand(command)

if result != "OK" :
    print("Command [{0}] Failed Result: {1}".format(command,result))
    exit(1)
exit(0) 
