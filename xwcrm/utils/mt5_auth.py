#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Zachary
# @license: commercial
# @contact:


from mt5_retcode import *
from mt5_protocol import *
from mt5_connect import *


class MTAuthProtocol:
    """
    Class authorization on MetaTrader 5 Server
    """

    m_connect = None
    m_agent = ''

    def __init__(self, connect, agent):
        """
        @param connect connection to server
        @param agent - name of agent
        @return MTAuthProtocol
        """

        self.m_connect = connect
        self.m_agent = agent

    def Auth(self, login, password, is_crypt):
        """
        Authorization on MetaTrader 5 server
        @param string login - manager login
        @param string password - manager password
        @param bool is_crypt - need crypt connection
        @return string crypt_rand - crypt rand string
        @return MTRetCode, crypt_rand
        """

        crypt_rand = ''
        # send request to mt server
        error_code, auth_start_answer = self.SendAuthStart(login, is_crypt)
        if error_code != MTRetCode.MT_RET_OK:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'auth start failed: [' + error_code + ']' + MTRetCode.GetError(error_code))
            return error_code, crypt_rand
        # get code from hex string
        # -rand_code = MTUtils.GetFromHex(auth_start_answer.SrvRand)
        # random string for MT server
        random_cli_code = MTUtils.GetRandomHex(16)
        # get hash password with random code
        answer_hash = MTUtils.GetHashFromPassword(password, auth_start_answer.SrvRand)
        # send answer to server
        error_code, auth_answer = self.SendAuthAnswer(answer_hash, random_cli_code)
        if error_code != MTRetCode.MT_RET_OK:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'auth answer failed: [' + error_code + ']' + MTRetCode.GetError(error_code))
            return error_code, crypt_rand
        # check password with another random code from MT server
        hash_password = MTUtils.GetHashFromPassword(password, random_cli_code)
        # check hash of password
        if hash_password != auth_answer.CliRand:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'server sent incorrect password hash: is:' + auth_answer.CliRand + ', my: ' + hash_password)
            return MTRetCode.MT_RET_AUTH_SERVER_BAD, crypt_rand
        # get crypt rand from MT server
        # -crypt_rand = auth_answer.CryptRand
        # ---
        return MTRetCode.MT_RET_OK, auth_answer.CryptRand

    def SendAuthAnswer(self, hash, random_cli_code):
        """
        Send AUTH_ANSWER to MT server
        @param string hash - password hash
        @param string random_cli_code client random string
        @return MTAuthAnswer auth_answer - result from server
        @return MTRetCode
        """

        auth_answer = MTAuthAnswer()
        answer = ''
        # send first request, with login, webapi version
        data = {
            MTProtocolConsts.WEB_PARAM_SRV_RAND_ANSWER: hash,
            MTProtocolConsts.WEB_PARAM_CLI_RAND: random_cli_code
        }
        # send request
        if not self.m_connect.Send(MTProtocolConsts.WEB_CMD_AUTH_ANSWER, data):
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'send auth answer failed')
            return MTRetCode.MT_RET_ERR_NETWORK, auth_answer
        # get answer
        answer = self.m_connect.Read(True, False)
        if answer is None:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'answer auth answer is empty')
            return MTRetCode.MT_RET_ERR_NETWORK, auth_answer
        # parse answer
        error_code, auth_answer, error = self.ParseAuthAnswer(answer)
        if error_code != MTRetCode.MT_RET_OK:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'parse auth answer failed: ' + error)
            return error_code, auth_answer
        # ok
        return MTRetCode.MT_RET_OK, auth_answer

    def ParseAuthStart(self, answer):
        """
        check answer from MetaTrader 5 server
        @param  string answer
        @return MTRetCode, auth_answer, error
        """

        auth_answer = MTAuthStartAnswer()
        error = 'Unknown error'
        # get command answer and param
        command, param = self.m_connect.ParseAnswer(answer)
        if command != MTProtocolConsts.WEB_CMD_AUTH_START:
            error = 'type answer "' + command + '" is incorrect, is not ' + MTProtocolConsts.WEB_CMD_AUTH_START
            return MTRetCode.MT_RET_ERR_DATA, auth_answer, error
        # ret code
        auth_answer.RetCode = param[MTProtocolConsts.WEB_PARAM_RETCODE]
        # srv rand
        auth_answer.SrvRand = param[MTProtocolConsts.WEB_PARAM_SRV_RAND]
        # check ret code
        error_code = MTConnect.GetRetCode(auth_answer.RetCode)
        if error_code != MTRetCode.MT_RET_OK:
            return error_code, auth_answer, error
        # get srv rand
        if auth_answer.SrvRand is None or auth_answer.SrvRand == 'none':
            error = 'srv rand incorrect'
            return MTRetCode.MT_RET_ERR_PARAMS, auth_answer, error
        #
        return MTRetCode.MT_RET_OK, auth_answer, error

    def SendAuthStart(self, login, is_crypt):
        """
        Send auth_start request
        @param string login  - user login
        @param bool is_crypt - need crypt protocol
        @return MTAuthStartAnswer auth_answer  - answer from server
        @return MTRetCode
        """

        auth_answer = MTAuthStartAnswer()
        # send first request, with login, webapi version
        crypt_method = MTProtocolConsts.WEB_VAL_CRYPT_AES256OFB if is_crypt else MTProtocolConsts.WEB_VAL_CRYPT_NONE
        data = {
            MTProtocolConsts.WEB_PARAM_VERSION: MTProtocolConsts.WEB_API_VERSION,
            MTProtocolConsts.WEB_PARAM_AGENT: self.m_agent,
            MTProtocolConsts.WEB_PARAM_LOGIN: login,
            MTProtocolConsts.WEB_PARAM_TYPE: 'MANAGER',
            MTProtocolConsts.WEB_PARAM_CRYPT_METHOD: crypt_method
        }
        # send request
        if not self.m_connect.Send(MTProtocolConsts.WEB_CMD_AUTH_START, data, True):
            return MTRetCode.MT_RET_ERR_NETWORK, auth_answer
        # get answer
        answer = self.m_connect.Read(True)
        if answer is None:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'answer auth start is empty')
            return MTRetCode.MT_RET_ERR_NETWORK, auth_answer
        # parse answer
        error_code, auth_answer, error = self.ParseAuthStart(answer)
        if auth_answer != MTRetCode.MT_RET_OK:
            # if MTLogger.getIsWriteLog():
            #     MTLogger.write(MTLoggerType.ERROR, 'parse auth start failed: [' + $error_code + ']' + error)
            return error_code, auth_answer
        #
        return MTRetCode.MT_RET_OK, auth_answer

    def ParseAuthAnswer(self, answer):
        """
        Parse answer from request AUTH_ANSWER
        @param string answer - answer from server
        @return MTAuthAnswer auth_answer - result
        @return string error
        @return MTRetCode
        """

        auth_answer = MTAuthAnswer()
        error = 'Unknown error'
        # get command answer and param
        command, param = self.m_connect.ParseAnswer(answer)
        if command != MTProtocolConsts.WEB_CMD_AUTH_ANSWER:
            error = 'type answer "' + command + '" is incorrect, is not ' + MTProtocolConsts.WEB_CMD_AUTH_ANSWER
            return MTRetCode.MT_RET_ERR_DATA, auth_answer, error
        # ret code
        auth_answer.RetCode = param[MTProtocolConsts.WEB_PARAM_RETCODE]
        # cli rand
        auth_answer.CliRand = param[MTProtocolConsts.WEB_PARAM_CLI_RAND_ANSWER]
        # crypt rand
        auth_answer.CryptRand = param[MTProtocolConsts.WEB_PARAM_CRYPT_RAND]
        # check ret code
        ret_code = MTConnect.GetRetCode(auth_answer.RetCode)
        if ret_code != MTRetCode.MT_RET_OK:
            return ret_code
        # check CliRand
        if auth_answer.CliRand is None or auth_answer.CliRand == 'none':
            error = 'cli rand answer incorrect'
            return MTRetCode.MT_RET_ERR_PARAMS, auth_answer, error
        return MTRetCode.MT_RET_OK, auth_answer, error


class MTAuthStartAnswer:

    def __init__(self):
        pass

    RetCode = '-1'
    SrvRand = 'none'


class MTAuthAnswer:

    def __init__(self):
        pass

    RetCode = '-1'
    CliRand = 'none'
    CryptRand = ''
