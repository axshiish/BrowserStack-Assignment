import threading
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

USERNAME = "ashishsingh_iyqBNU"
ACCESS_KEY = "xKesdsevqPbwVsv9zF2E"

browsers = [
    {
        "os": "Windows",
        "osVersion": "10",
        "browserName": "Chrome",
        "browserVersion": "latest"
    },
    {
        "os": "OS X",
        "osVersion": "Monterey",
        "browserName": "Safari",
        "browserVersion": "latest"
    },
    {
        "os": "Windows",
        "osVersion": "11",
        "browserName": "Edge",
        "browserVersion": "latest"
    },
    {
        "deviceName": "Samsung Galaxy S22",
        "realMobile": "true",
        "osVersion": "12.0"
    },
    {
        "deviceName": "iPhone 13",
        "realMobile": "true",
        "osVersion": "15"
    }
]

def mark_test_status(session_id, status, reason):
    url = f"https://api.browserstack.com/automate/sessions/{session_id}.json"
    response = requests.put(
        url,
        auth=(USERNAME, ACCESS_KEY),
        json={"status": status, "reason": reason}
    )
    print(f"Marked session {session_id} as {status}: {reason}")

def run_test(capabilities):
    options = webdriver.ChromeOptions()
    for key, value in capabilities.items():
        options.set_capability(key, value)

    options.set_capability("browserstack.user", USERNAME)
    options.set_capability("browserstack.key", ACCESS_KEY)
    options.set_capability("name", "BrowserStack Parallel Test")

    driver = webdriver.Remote(
        command_executor="https://hub-cloud.browserstack.com/wd/hub",
        options=options
    )

    session_id = driver.session_id
    try:
        driver.get("https://elpais.com/")
        print(f"[{capabilities.get('browserName', capabilities.get('deviceName'))}] Title: {driver.title}")
        mark_test_status(session_id, "passed", "Test completed successfully")
    except Exception as e:
        print(f"Error on {capabilities.get('browserName', capabilities.get('deviceName'))}: {e}")
        mark_test_status(session_id, "failed", str(e))
    finally:
        driver.quit()

threads = []
for caps in browsers:
    t = threading.Thread(target=run_test, args=(caps,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
