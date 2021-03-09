#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Zachary
# @license: commercial
# @contact:


import socket
from mt5_protocol import *
from mt5_utils import *
from mt5_retcode import *


class MTConnect:
    """
    Create connect to MetaTrader 5 server
    """

    # The serial number must be within the range 0000-FFFF:
    # 0-3FFF (0-16383) — client commands.
    MAX_CLIENT_COMMAND = 16383
    # socket connect
    _connect = None
    # ip to mt5 server
    _ip_mt5 = None
    # port o mt5 server
    _port_mt5 = None
    # timeout
    _timeout_connection = 5
    # crypto random string
    _crypt_rand = ""
    # crypto array
    _crypt_iv = None
    #
    _aes_out = None
    #
    _aes_in = None
    # class crypt aes 256
    _crypt_out = None
    #
    _crypt_in = None
    # number of client packet
    _client_command = 0

    def __init__(self, ip_mt5, port_mt5, timeout, is_crypt):
        """
        Create MetaTrader 5 Web Api class

        @param  string ip_mt5              host or ip for MetaTrader 5 server
        @param  int    port_mt5            port to MetaTrader 5 server
        @param  int    timeout             time out of try connection to MetaTrader 5 server
        @param bool    is_crypt            - need crypt connection

        @return MTConnect
        """

        self._ip_mt5 = ip_mt5
        self._port_mt5 = port_mt5
        self._timeout_connection = timeout
        # if need  crypt lets begin
        self.is_crypt = is_crypt
        self._client_command = 0
        # create socket
        self._connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect.settimeout(self._timeout_connection)

    def Disconnect(self):
        """
        Close connection
        """

        self._connect.close()
        del (self._connect)

    def Connect(self):
        """
        Authentication on MetaTrader 5 server
        @return boolean
        """

        # connect to server
        self._connect.connect((self._ip_mt5, self._port_mt5))
        return MTRetCode.MT_RET_OK

    def Send(self, command, data, first_request=False):
        """
        Send data to MetaTrader 5 server

        @param string  command       - command, for example AUTH_START, AUTH_ANSWER and etc.
        @param dict data
        @param bool    first_request bool is ot first

        @return bool
        """

        # number packet
        self._client_command += 1
        # packet max, than first
        if self._client_command > self.MAX_CLIENT_COMMAND:
            self._client_command = 1
        # create query
        body_request = ''
        q = command
        # create string for query
        if len(data) != 0:
            q += "|"
            for param, value in data.items():
                if param == MTProtocolConsts.WEB_PARAM_BODYTEXT:
                    body_request = value
                else:
                    q += param + '=' + value + '|'
            q += "\r\n"
            # add body request
            if body_request != '':
                q += body_request
        else:
            q += "|\r\n"
        #
        query_body = q.encode('utf-16le')
        # if need we crypt packet, crypt did not for auth_start and auth_start_answer
        if command != MTProtocolConsts.WEB_CMD_AUTH_START and command != MTProtocolConsts.WEB_CMD_AUTH_ANSWER and \
                self.is_crypt:
            query_body, query_hexlen = self.CryptPacket(query_body, len(query_body))
        else:
            query_hexlen = hex(len(query_body))[2:].rjust(4, '0')

        # send request
        if first_request:
            header = MTProtocolConsts.WEB_PREFIX_WEBAPI + query_hexlen + hex(self._client_command)[2:].rjust(4, '0')
            query = header + '0' + query_body
        else:
            header = query_hexlen + hex(self._client_command)[2:].rjust(4, '0')
            query = header + '0' + query_body
        # send data to MetaTrader 5 server
        self._connect.send(query)
        return True

    def CryptPacket(self, packet_body, len_packet):
        pass

    def DeCryptPacket(self, packet_body, len_packet):
        pass

    def GetPacket(self, buffer_size, response_only):
        """
        Get a whole packet from socket buffer
        @param int buffer_size socket buffer size

        @return string packet the whole packet in hex format
        @return dict header of the packet
        """

        # get first sub packet
        packet = self._connect.recv(buffer_size)
        recv_size = buffer_size
        # empty packet
        if packet == '' or len(packet) < 9:
            return None, None
        # get header data
        header_data = packet[:MTHeaderProtocol.HEADER_LENGTH]
        # Process header data
        header = MTHeaderProtocol(header_data)
        # recieve more data from buffer
        while recv_size < header.SizeBody:
            sub_packet = self._connect.recv(buffer_size)
            if len(sub_packet) >= 9:
                # remove ping packet
                if sub_packet.find('0000') != -1:
                    sub_packet = sub_packet[:sub_packet.index('0000')]
                    # continue
            # connect sub packets
            packet += sub_packet
            recv_size += buffer_size
        # get the response line only
        if response_only:
            packet = packet.splitlines(False)[0]
        return packet, header

    def Read(self, auth_packet=False, is_binary=False, response_only=False):
        """
        Get data from MetaTrader 5 server

        @param bool auth_packet wait the auth packet
        @param bool is_binary
        @return None|string
        """

        result = ''
        while True:
            response, header = self.GetPacket(1024, response_only)
            # get result body
            data = response[9:]
            if header is None:
                # if(MTLogger.getIsWriteLog()) MTLogger.write(MTLoggerType.DEBUG, 'incorrect header data "' + $header_data + '"')
                break
            if data is None and header.SizeBody > 0:
                # if(MTLogger.getIsWriteLog()) MTLogger.write(MTLoggerType.DEBUG, "read incorrect packet, length " + $header.SizeBody + ", but data is None")
                break
            # if need decrypt packet do it
            if self.is_crypt and not auth_packet:
                data = self.DeCryptPacket(data, header.SizeBody)
            # check number of packet
            if header.NumberPacket != self._client_command:
                # check packet length
                if header.SizeBody != 0:
                    pass
                    # if(MTLogger.getIsWriteLog()) MTLogger.write(MTLoggerType.DEBUG, "number of packet incorrect need: " + self._client_command + ", but get " + $header.NumberPacket)
                else:
                    # this is PING packet
                    # if(MTLogger.getIsWriteLog()) MTLogger.write(MTLoggerType.DEBUG, "PING packet")
                    pass
                # read next packet
                continue
            # get result
            result += data
            # read to end
            if header.Flag == 0:
                break

        # decoding data
        if is_binary:
            """
            pos        = strpos($result, "\n")
            first_line = substr($result, 0, $pos)
            result     = mb_convert_encoding($first_line, "utf-8", "utf-16le") + "\r\n" + substr($result, $pos)
            """
            pass
        else:
            result = result.decode('utf-16le')
            # if(MTLogger.getIsWriteLog()) MTLogger.write(MTLoggerType.DEBUG, "result: " + $result)
        # return result
        return result

    def ParseAnswer(self, answer):
        """
        Get command answer

        @param string answer

        @return command param dict
        """

        answer_list = answer.split('|')
        command = answer_list[0]
        param = {}
        for item in answer_list[1:]:
            if item != '' and item.find('=') != -1:
                key = item.split('=')[0].upper()
                value = item.split('=')[1]
                param[key] = value
        return command, param

    def GetJson(self, answer):
        """
        Get json from answer

        @param string answer

        @return None|string
        """

        return None

    def GetBinary(self, answer):
        """
        """

        return None

    @staticmethod
    def GetRetCode(ret_code_string):
        """
        Get code from string
        @param string $ret_code_string
        @return int
        """

        if ret_code_string == '':
            return ''
        return int(ret_code_string.split(' ')[0])

    def SetCryptRand(self, crypt, password):
        """
        @param string $crypt    hash random string from MT server
        @param string $password password to connection mt server

        @return void
        """

        self._crypt_rand = crypt
        # out = md5(md5(mb_convert_encoding(password, 'utf-16le', 'utf-8'), true) + MTProtocolConsts.WEB_API_WORD)
        for i in range(0, 16):
            # out = md5(MTUtils.GetFromHex(substr(self._crypt_rand, i * 32, 32)) + MTUtils.GetFromHex(out))
            self._crypt_iv[i] = out
        return None
