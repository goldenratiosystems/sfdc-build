import requests
import json
import os
import urllib
import zeep
import datetime
import time

from ConfigParser import SafeConfigParser

import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()


class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[asection]\n'

    def readline(self):
        if self.sechead:
            try:
                return self.sechead
            finally:
                self.sechead = None
        else:
            return self.fp.readline()


current_path = os.path.dirname(os.path.realpath(__file__))

config_parser = SafeConfigParser()
config_parser.readfp(FakeSecHead(open(current_path + '/../build.properties')))


def getSalesforceSession():
    sf_username = config_parser.get('asection', 'sf.username')
    sf_password = config_parser.get('asection', 'sf.password')

    print 'Salesforce Username: ' + sf_username
    client = zeep.Client(current_path + '/../lib/partner.xml')
    sf_auth_response = client.service.login(
        username=sf_username, password=sf_password)

    return {
        'sessionId': sf_auth_response['sessionId'],
        'serverUrl': sf_auth_response['serverUrl'].split('services')[0],
        'metadataUrl': sf_auth_response['metadataServerUrl']
    }


def getSalesforceRequestsHeader(sf_session):
    return {
        'Authorization': 'Bearer ' + sf_session['sessionId'],
        'Content-Type': 'application/json'
    }


def getOptionalConfigProperty(property_name):
    result = ''
    if config_parser.has_option('asection', property_name):
        result = config_parser.get('asection', property_name)
    return result


def sendSlackMessage(message, username, emoji, slack_channel=None):
    try:
        slack_token = config_parser.get('asection', 'slack.token')
        if slack_channel is None:
            slack_channel = config_parser.get('asection', 'slack.channel')
        url = 'https://slack.com/api/chat.postMessage'
        print 'Send Slack Message: \n  Message:{0}\n  Channel:{1}'.format(message, slack_channel)
        r = requests.post(url, params={
            'token': slack_token,
            'channel': slack_channel,
            'text': message,
            'username': username,
            'icon_emoji': emoji
        })
    except Exception as slack_e:
        print slack_e
        print 'Not send slack message :('


def sendSlackFile(filepath, slack_filename, slack_channel=None):
    if os.path.isfile(filepath):
        try:
            slack_token = config_parser.get('asection', 'slack.token')
            if slack_channel is None:
                slack_channel = config_parser.get('asection', 'slack.channel')
            url = 'https://slack.com/api/files.upload'
            print 'Send Slack File: \n  File Path:{0}\n  Channel:{1}'.format(filepath, slack_channel)
            with open(filepath, 'rb') as file:
                response = requests.post(url, files={'file': file}, params={
                    'token': slack_token,
                    'channels': slack_channel,
                    'filename': slack_filename
                })
                if response.status_code != 200:
                    raise ValueError(response.text)
        except Exception as slack_e:
            print slack_e
            print 'Not send slack file :('
    else:
        print 'file not found'
