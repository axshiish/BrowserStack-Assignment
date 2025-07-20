import threading
import requests
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from googletrans import Translator

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


os.makedirs("images", exist_ok=True)


translated_titles = []
lock = threading.Lock()

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
        driver.implicitly_wait(10)

        
        opinion_link = driver.find_element(By.XPATH, "//a[contains(@href, '/opinion/')]")
        opinion_link.click()
        driver.implicitly_wait(10)

        
        articles = driver.find_elements(By.XPATH, "//article//a[contains(@href, '/opinion/')]")[:5]
        translator = Translator()

        for idx, article in enumerate(articles):
            try:
                article_url = article.get_attribute("href")
                driver.get(article_url)
                driver.implicitly_wait(10)

                title_elem = driver.find_element(By.TAG_NAME, "h1")
                title = title_elem.text.strip()

                content_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'article_body')]")
                content = content_elem.text.strip()[:300]

                print(f"\n[{capabilities.get('browserName', capabilities.get('deviceName'))}] Article {idx+1}")
                print("Title (Spanish):", title)
                print("Content (Preview):", content)

                
                try:
                    img_elem = driver.find_element(By.XPATH, "//figure//img")
                    img_url = img_elem.get_attribute("src")
                    img_data = requests.get(img_url).content
                    img_filename = f"images/{capabilities.get('browserName', capabilities.get('deviceName'))}_article{idx+1}.jpg"
                    with open(img_filename, "wb") as f:
                        f.write(img_data)
                except Exception:
                    pass

                
                translated = translator.translate(title, src='es', dest='en').text
                print("Translated Title:", translated)

                with lock:
                    translated_titles.append(translated)

            except Exception as e:
                print(f"Error processing article {idx+1}: {e}")

        mark_test_status(session_id, "passed", "Scraped and translated articles successfully")

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


word_count = {}
for title in translated_titles:
    words = re.findall(r'\b\w+\b', title.lower())
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

print("\nRepeated words in translated titles (appearing more than twice):")
for word, count in word_count.items():
    if count > 2:
        print(f"{word}: {count}")
