from datetime import datetime
import zlib

from Connect import XTSConnect
from MarketDataSocketClient import MDSocket_io
from Connect import XTSCommon
from TouchlineEvent import Touchline
from MarketDepthEvent import MarketDepthEvent
from OpenInterestEvent import OpenInterest
from binary_reader import BinaryReader


API_KEY = "15cb10473a729b424cf932"
API_SECRET = "Deej832$Nc" 
source = "WEBAPI"
b = bytearray()
xt = XTSConnect(API_KEY, API_SECRET, source,"","")
response = xt.marketdata_login()
print("Login: ", response)

set_marketDataToken = response['result']['token']
set_muserID = response['result']['userID'] 
soc = MDSocket_io(set_marketDataToken, set_muserID)


# Callback for connection
def on_connect():
    """Connect from the socket."""
    print('Market Data Socket connected successfully!')
    Instruments = [ {'exchangeSegment':1, 'exchangeInstrumentID': 22}]
    response = xt.send_subscription(Instruments, 1501)


# Callback on receiving message
def on_message(data):
    print('I received a message!')



def on_xts_binary_packet(data):
    try:
        a = bytearray(data)   
        offset = 0
        count = 0
        currentsize = 0
        isnextpacket = True
        datalen=len(a)
        packetcount = 0
        br = BinaryReader(data)
        packetSize = 0
        uncompressedPacketSize = 0
        nextdata = a
        while (isnextpacket): 
            nextdata = a[offset:datalen]
            br = BinaryReader(nextdata)
            isGzipCompressed = br.read_int8()
            offset=offset+1
            if (isGzipCompressed == 1): 
                nextdata = a[offset:datalen]
                br = BinaryReader(nextdata)
                messageCode = br.read_uint16()
                exchangeSegment = br.read_int16()
                exchangeInstrumentID = br.read_int32()
                bookType = br.read_int16()
                marketType = br.read_int16()
                uncompressedPacketSize = br.read_uint16()
                compressedPacketSize = br.read_uint16()
                offset += 16
                filteredByteArray = a[offset:(offset + compressedPacketSize)]
                inflate = pako_inflate_raw(filteredByteArray)
                result = bytearray(inflate)
                r = BinaryReader(result)
                currentsize = compressedPacketSize  + offset
                if (currentsize < len(a)): 
                    isnextpacket = True
                    packetcount = 1
                    offset = currentsize
                else: isnextpacket = False
                messageCode = str(r.read_uint16())
                if ("1501" in str(messageCode)) :
                    Touchline.deserialize(r,count)
                elif ("1502" in str(messageCode)):
                    MarketDepthEvent.deserialize(r,count)
                elif ("1510" in str(messageCode)):
                    OpenInterest.deserialize(r,count)
                elif ("1512" in messageCode):
                    LTPEvent.deserialize(r,count)
            elif (isGzipCompressed == 0): 
                messageCode = str(br.read_uint16())
                exchangeSegment = br.read_int16()
                exchangeInstrumentID = br.read_int32()
                bookType = br.read_int16()
                marketType = br.read_int16()
                uncompressedPacketSize = br.read_uint16()
                compressedPacketSize = br.read_uint16()
                offset += 14
                count = offset                
                if ("1501" in messageCode) :
                    Touchline.deserialize(br,count)
                elif ("1502" in messageCode):
                    MarketDepthEvent.deserialize(br,count)
                elif ("1510" in messageCode):
                    OpenInterest.deserialize(br,count)
                currentsize = offset+ uncompressedPacketSize  
                if (currentsize < len(a)): 
                    isnextpacket = True
                    packetcount = 1
                    offset = currentsize 
                else: isnextpacket = False
    except Exception as e:
        print(e)


# Callback for disconnection
def on_disconnect():
    print('Market Data Socket disconnected!')


# Callback for error
def on_error(data):
    """Error from the socket."""
    print('Market Data Error', data)


def pako_inflate_raw(data):
    decompress = zlib.decompressobj(-15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data



# Assign the callbacks.
soc.on_connect = on_connect
soc.on_message = on_message
soc.on_xts_binary_packet = on_xts_binary_packet
soc.on_disconnect = on_disconnect
soc.on_error = on_error


# Event listener
el = soc.get_emitter()
el.on('connect', on_connect)
el.on('xts-binary-packet', on_xts_binary_packet)


# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
soc.connect()
