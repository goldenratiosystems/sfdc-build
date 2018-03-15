import requests
import json
import urllib
import datetime
import time

import ci_utils

import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

print 'Run Local Apex Tests'

sf_session = ci_utils.getSalesforceSession()
sf_headers = ci_utils.getSalesforceRequestsHeader(sf_session)

url = sf_session['serverUrl'] + \
      '/services/data/v39.0/tooling/runTestsAsynchronous/'
payload = {'testLevel': 'RunLocalTests'}

response = requests.post(url, headers=sf_headers, data=json.dumps(payload))

if 'ALREADY_IN_PROCESS' in response.text:
    raise ValueError(response.text)

job_id = response.text.replace('"', '')

query = {
    'q': 'SELECT Id, JobItemsProcessed, JobType, Status FROM AsyncApexJob WHERE Id = \'' + job_id + '\''}
url = sf_session['serverUrl'] + \
      '/services/data/v39.0/tooling/query/?' + urllib.urlencode(query)

print query['q']

response = requests.get(url, headers=sf_headers)
if response.status_code != 200:
    raise ValueError(response.text)
json_result = response.json()

print 'Total size of records: ' + str(json_result['totalSize'])

while True:
    response = requests.get(url, headers=sf_headers)
    if response.status_code != 200:
        raise ValueError(response.text)
    json_result = response.json()

    print json_result['records'][0]['Status']

    if json_result['totalSize'] != 1 or json_result['records'][0]['Status'] != 'Processing' and \
                    json_result['records'][0]['Status'] != 'Queued':
        break

    time.sleep(10)

print 'Complete'
print ''
print ''
