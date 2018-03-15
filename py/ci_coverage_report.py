import requests
import json
import os
import urllib
import zeep
import datetime
import ci_utils

import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

print 'Apex Tests Coverage Report'

path_coverage_report = ci_utils.getOptionalConfigProperty('path_coverage_report')

sf_session = ci_utils.getSalesforceSession()
sf_headers = ci_utils.getSalesforceRequestsHeader(sf_session)

query = {
    'q': 'SELECT ApexClassorTriggerId, ApexClassorTrigger.Name, NumLinesCovered, NumLinesUncovered FROM ApexCodeCoverageAggregate ORDER BY ApexClassorTrigger.Name'}
url = sf_session['serverUrl'] + \
      '/services/data/v39.0/tooling/query/?' + urllib.urlencode(query)

coverage_request = requests.get(url, headers=sf_headers)
coverage_response = coverage_request.json()
if coverage_request.status_code != 200:
    raise ValueError(coverage_response)

query = {
    'q': 'SELECT PercentCovered FROM ApexOrgWideCoverage'}
url = sf_session['serverUrl'] + \
      '/services/data/v39.0/tooling/query/?' + urllib.urlencode(query)

org_wide_request = requests.get(url, headers=sf_headers)
org_wide_response = org_wide_request.json()
if org_wide_request.status_code != 200:
    raise ValueError(org_wide_response)

org_wide_covered = org_wide_response['records'][0]['PercentCovered']

date_time_utc = datetime.datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
output = '<html><body><h2>Coverage Report - {0} (UTC)</h2><div>'.format(date_time_utc)
output += '<style>.green {color: green;} .red {color: red;} th {text-align: left; padding-right: 1.5em;} * {font-family: monospace;}</style>'

style_class = 'green' if org_wide_covered >= 75 else 'red'
output += '<h3>Org Wide Coverage: <span class="{0}">{1}</span></h3>'.format(
    style_class, org_wide_covered)

output += '<table>'
output += '<tr><th>Apex Class/Trigger</th><th>Coverage</th><th>Lines(Covered/Total)</th></tr>'

row_string_template = '<tr><td>{0}</td><td class="{1}">{2}</td><td>{3}/{4}</td></tr>'

for s in coverage_response['records']:
    class_or_trigger_name = s['ApexClassOrTrigger']['Name']
    covered = s['NumLinesCovered']
    uncovered = s['NumLinesUncovered']
    total = covered + uncovered
    coverage = int(covered / float(total) * 100) if covered != 0 else 0
    style_class = 'green' if coverage >= 75 else 'red'
    output += row_string_template.format(
        class_or_trigger_name, style_class, coverage, covered, total)

output += '</table>'
output += '</div></body></html>'

with open(path_coverage_report, 'w') as coverage_report:
    coverage_report.write(output)

print 'Complete'
print ''
print ''
