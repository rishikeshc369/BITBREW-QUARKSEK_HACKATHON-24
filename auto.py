from zapv2 import ZAPv2
import time

get_url=input("Enter the Url:")
target_url = get_url

# Replace the API key with your ZAP API key
api_key = 'vc83kmprrkkg7g2is47ghfa6v1'

# Create a ZAP instance
zap = ZAPv2(apikey=api_key)

# Set the target URL
zap.target = target_url

# Spider the target URL
print('Spidering target {}'.format(target_url))
zap.spider.scan(target_url)

# Wait for the spider to finish
while (int(zap.spider.status()) < 100):
    print('Spider progress %: {}'.format(zap.spider.status()))
    time.sleep(5)

print('Spider completed')

# Scan the target URL
print('Scanning target {}'.format(target_url))
zap.ascan.scan(target_url)

# Wait for the scan to finish
while (int(zap.ascan.status()) < 100):
    print('Scan progress %: {}'.format(zap.ascan.status()))
    time.sleep(5)

print('Scan completed')

# Get the alerts
alerts = zap.core.alerts()
if alerts:
    print('Alerts:')
    for alert in alerts:
        print('Alert: {} at URL: {}'.format(alert['alert'], alert['url']))
else:
    print('No alerts found')

# Shutdown ZAP
zap.core.shutdown()
