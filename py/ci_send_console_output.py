import ci_utils

import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

print 'Send Console Output to Slack'

path_console_log = ci_utils.current_path + '/../consoleOutput.log'

environment = ci_utils.getOptionalConfigProperty('environment')
slack_filename = 'consoleOutput{0}.log'.format(environment)

ci_utils.sendSlackFile(path_console_log, slack_filename)
