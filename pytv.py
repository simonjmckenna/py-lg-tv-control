#!/usr/bin/env python3
#
# Class for control of a LG 2013 Smart TV (pre webos) 
#
# Based on some Original work by Martin Harizanov 
# Updated by Simon McKenna
#
#Full list of commands
#http://developer.lgappstv.com/TV_HELP/index.jsp?topic=%2Flge.tvsdk.references.book%2Fhtml%2FUDAP%2FUDAP%2FAnnex+A+Table+of+virtual+key+codes+on+remote+Controller.htm
import http.client
from tkinter import *
import socket
import re
import sys

#  TVCOMMANDS is the list of commands and the codes 
# - see the command codes fil in the git repo for the complete list 
# supplied by LG

class tvControl():
    TVCOMMANDS = { "ON": 0, "OFF": 1, "MUTE": 26, "VOLUP": 24 , "VOLDN": 25, "CHANUP": 27, "CHANDN": 28 }


    def __init__(self,ip,port,pairingKey):
        self.pairingKey = pairingKey
        self.ipaddress = ip
        self.tcpport   = port
        self.connected = False
      
    def connect(self):

        if self.connected == True :
           return True

        if self.ipaddress == None :
           self.ipaddress = self.get_tv_ip()

        if self.ipaddress == None :
           return False
  
        if self.pairingKey == None :
           self.request_displayKey()
           return False

        if self.pair_with_TV() == True :
           self.connected = True
           return True

        return False

    def disconnect(self):
   
        if self.connected == False :
           return True

        if unpair_with_TV() == True :
           self.connected = False
           return True

        return False

    def get_tv_ip(self):
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
       self.ipaddress = None
       sock.sendto( bytestoXmit,  ('239.255.255.250', 1900 ) )
       while not found and i <= 5 and gotstr == 'notyet':
           try:
               gotbytes, addressport = sock.recvfrom(512)
               gotstr = gotbytes.decode()
           except:
               i += 1
               sock.sendto( bytestoXmit, ( '239.255.255.250', 1900 ) )
           if re.search('LOCATION:', gotstr):
               self.ipaddress = re.search(r'[0-9]+(?:\.[0-9]+){3}',gotstr).group()
               found = True
           else:
               gotstr = 'notyet'
           i += 1
       # Finished looking for TV
       sock.close()
       return ipaddress

    def transmit_request(self,request,apifamily):
        conn = http.client.HTTPConnection( self.ipaddress, self.tcpport)
        conn.putrequest("POST", "/udap/api/"+apifamily)
        conn.putheader("Content-type","text/xml")
        conn.putheader("Accept","text/plain")
        conn.putheader("User-Agent","UDAP/2.0")
        conn.putheader("Content-length",len(request))
        conn.endheaders()
        conn.send(request.encode())
        httpResponse = conn.getresponse()
        conn.close()
        return httpResponse.reason

    def request_displayKey(self):
        XML = 	'<?xml version=\"1.0\" encoding=\"utf-8\"?>' \
		+ '<envelope>' \
		+ '<api type=\"pairing\">' \
		+ '<name>showKey</name>' \
		+ '</api>' \
		+ '</envelope>' 
        return self.transmit_request(XML,"pairing")

    def pair_with_TV(self):
        XML = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" \
		+ "<envelope>" \
		+ "<api type=\"pairing\">" \
		+ "<name>hello</name>" \
       	        + "<value>" + self.pairingKey + "</value>" \
                + "<port>" + str(self.tcpport) + "</port>" \
	        + "</api>" \
	        + "</envelope>"
        return self.transmit_request(XML,"pairing")

    def unpairwithTV(self):
        XML = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" \
		+ "<envelope>" \
		+ "<api type=\"pairing\">" \
		+ "<name>byebye</name>" \
                + "<port>" + str(self.tcpport) + "</port>" \
		+ "</api>" \
		+ "</envelope>" 
        return self.transmit_request(XML,"pairing")

    def handleCommand(self,command):
  
        cmdcode = self.TVCOMMANDS.get(command,-1)
        if cmdcode == -1 :
           return "BAD COMMAND"         
        XML = "<?xml version=\"1.0\" encoding=\"utf-8\"?>" \
		+ "<envelope>" \
		+ "<api type=\"command\">" \
                + "<name>HandleKeyInput</name><value>" \
                + str(cmdcode) \
                + "</value>" \
		+ "</api>" \
		+ "</envelope>" 

        return self.transmit_request(XML,"command")

