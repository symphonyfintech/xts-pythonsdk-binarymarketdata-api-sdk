import configparser
import os
from datetime import datetime

import socketio


class MDSocket_io(socketio.Client):
    """A Socket.IO client.
    This class implements a fully compliant Socket.IO web client with support
    for websocket and long-polling transports.
    :param reconnection: 'True'. if the client should automatically attempt to
                         reconnect to the server after an interruption, or
                         'False' to not reconnect. The default is 'True'.
    :param reconnection_attempts: How many reconnection attempts to issue
                                  before giving up, or 0 for infinity attempts.
                                  The default is 0.
    :param reconnection_delay: How long to wait in seconds before the first
                               reconnection attempt. Each successive attempt
                               doubles this delay.
    :param reconnection_delay_max: The maximum delay between reconnection
                                   attempts.
    :param randomization_factor: Randomization amount for each delay between
                                 reconnection attempts. The default is 0.5,
                                 which means that each delay is randomly
                                 adjusted by +/- 50%.
    :param logger: To enable logging set to 'True' or pass a logger object to
                   use. To disable logging set to 'False'. The default is
                   'False'.
    :param binary: 'True' to support binary payloads, 'False' to treat all
                   payloads as text. On Python 2, if this is set to 'True',
                   'unicode' values are treated as text, and 'str' and
                   'bytes' values are treated as binary.  This option has no
                   effect on Python 3, where text and binary payloads are
                   always automatically discovered.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have 'dumps' and 'loads'
                 functions that are compatible with the standard library
                 versions.f
    """

    def __init__(self, token, userID, reconnection=False, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=None,
                 **kwargs):
        self.sid = socketio.Client(logger=True, engineio_logger=True,ssl_verify=False)
        self.eventlistener = self.sid

        self.sid.on('connect', self.on_connect)
        self.sid.on('message', self.on_message)
        self.sid.on('xts-binary-packet', self.on_xts_binary_packet)
        self.sid.on('disconnect', self.on_disconnect)

        """Get the root url from config file"""
        currDirMain = os.getcwd()
        configParser = configparser.ConfigParser()
        configFilePath = os.path.join(currDirMain, 'config.ini')
        configParser.read(configFilePath)

        self.port = configParser.get('root_url', 'root')
        self.userID = userID
        publishFormat = 'JSON'
        self.broadcastMode = configParser.get('root_url', 'broadcastMode')
        self.token = token
        print("11111",self.token)
        port = f'{self.port}/?token='

        self.connection_url = port + token + '&userID=' + self.userID + '&publishFormat=' + publishFormat + '&broadcastMode=' + self.broadcastMode

    def connect(self, headers={}, transports='websocket', namespaces=None, socketio_path='apibinarymarketdata/socket.io',
                verify=False):
        """Connect to a Socket.IO server.
        :param verify: Verify SSL
        :param url: The URL of the Socket.IO server. It can include custom
                    query string parameters if required by the server.
        :param headers: A dictionary with custom headers to send with the
                        connection request.
        :param transports: The list of allowed transports. Valid transports
                           are 'polling' and 'websocket'. If not
                           given, the polling transport is connected first,
                           then an upgrade to websocket is attempted.
        :param namespaces: The list of custom namespaces to connect, in
                           addition to the default namespace. If not given,
                           the namespace list is obtained from the registered
                           event handlers.
        :param socketio_path: The endpoint where the Socket.IO server is
                              installed. The default value is appropriate for
                              most cases.

        self.url = self.connection_url
        self.connection_headers = headers
        self.connection_transports = transports
        self.connection_namespaces = namespaces
        self.socketio_path = socketio_path
        
        Connect to the socket.
        """
        url = self.connection_url
        """Connected to the socket."""
        self.sid.connect(url, headers, transports, namespaces, socketio_path)
        self.sid.wait()
        """Disconnected from the socket."""
        # self.sid.disconnect()

    def on_connect(self):
        """Connect from the socket."""
        print('Market Data Socket connected successfully!')

    def on_message(self, data):
        """On receiving message"""
        print('I received a message!' + data)

    def on_xts_binary_packet(self, data):
        print('I received a on_xts_binary_packet!' + data)
    
    def on_disconnect(self):
        """Disconnected from the socket"""
        print('Market Data Socket disconnected!')

    def on_error(self, data):
        """Error from the socket"""
        print('Market Data Error', data)

    def get_emitter(self):
        """For getting the event listener"""
        return self.eventlistener
