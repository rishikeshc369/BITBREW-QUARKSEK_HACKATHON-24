import subprocess
import time
import os
from zapv2 import ZAPv2

def start_zap(zap_path, zap_port):
    # Start ZAP using subprocess
    subprocess.Popen(["java", "-Xmx512m", "-jar", zap_path, "-daemon", "-port", str(zap_port)])
    print("ZAP is starting up...")
    time.sleep(20)  # Adjust this delay as needed to ensure ZAP has started properly

def scan_with_zap(target_url, zap_proxy, api_key):
    # Path to ZAP JAR file
    zap_path = r"C:\Program Files\ZAP\Zed Attack Proxy\zap-2.14.0.jar"  # Modify this with the actual path to your ZAP JAR file

    # Port for ZAP
    zap_port = 9090

    # Start ZAP
    start_zap(zap_path, zap_port)

    # Create a ZAP instance with proxy settings
    zap = ZAPv2(proxies={'http': zap_proxy, 'https': zap_proxy}, apikey=api_key)

    try:
        # Set the target URL
        zap.target = target_url

        # Spider the target URL
        print('Spidering target {}'.format(target_url))
        zap.spider.scan(target_url)

        # Wait for the spider to finish
        while int(zap.spider.status()) < 100:
            print('Spider progress %: {}'.format(zap.spider.status()))
            time.sleep(5)

        print('Spider completed')

        # Scan the target URL
        print('Scanning target {}'.format(target_url))
        zap.ascan.scan(target_url)

        # Wait for the scan to finish
        while int(zap.ascan.status()) < 100:
            print('Scan progress %: {}'.format(zap.ascan.status()))
            time.sleep(10)

        print('Scan completed')

        # Get the alerts
        alerts = zap.core.alerts()

        # Generate reports
        spider_report = generate_report(alerts, 'Spider')
        scan_report = generate_report(alerts, 'Scan')

        # Save reports to text files
        with open('zap_spider_report.txt', 'w', encoding='utf-8') as f:
            f.write(spider_report)

        with open('zap_scan_report.txt', 'w', encoding='utf-8') as f:
            f.write(scan_report)

        print('Reports generated successfully')

    finally:
        # Shutdown ZAP
        zap.core.shutdown()

def generate_report(alerts, scan_type):
    # Initialize counters for different risk levels
    risk_levels = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}

    # Count the number of alerts for each risk level
    for alert in alerts:
        risk_levels[alert['risk']] += 1

    # Generate the summary table
    summary_table = 'Risk Level\tNumber of Alerts\n'
    for risk, count in risk_levels.items():
        summary_table += f'{risk}\t{count}\n'

    # Generate the alerts section
    alerts_section = f'\n{scan_type} Report\n\n'
    for alert in alerts:
        if alert['risk'] != 'Informational':  # Skip informational alerts
            alerts_section += f'Alert: {alert["alert"]}\nURL: {alert["url"]}\nParameter: {alert.get("param", "")}\n\n'

    # Combine the summary table and alerts section
    return summary_table + '\n' + alerts_section

# Example usage
# scan_with_zap('http://example.com/', 'http://localhost:9090', 'vc83kmprrkkg7g2is47ghfa6v1')
