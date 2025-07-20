from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from googletrans import Translator
import time
import os
import requests

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://elpais.com/")
time.sleep(5)

try:
    accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceptar')]")
    accept_button.click()
    time.sleep(2)
except:
    print("No cookie popup found.")

try:
    opinion_link = driver.find_element(By.XPATH, "//a[contains(@href, '/opinion/')]")
    opinion_link.click()
    time.sleep(5)
except:
    print("Opinion section not found.")

articles = driver.find_elements(By.CSS_SELECTOR, "article h2 a")[:5]

os.makedirs("images", exist_ok=True)

spanish_titles = []

print("\n📰 First 5 Opinion Articles with Content and Images:\n")

for i, article in enumerate(articles, 1):
    article_url = article.get_attribute("href")

    
    driver.execute_script("window.open(arguments[0]);", article_url)
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(5)

    try:
        title = driver.find_element(By.TAG_NAME, "h1").text
        spanish_titles.append(title)

        paragraphs = driver.find_elements(By.CSS_SELECTOR, "div[data-dtm-region='articulo_cuerpo'] p")
        content = "\n".join([p.text for p in paragraphs if p.text.strip() != ""])

        try:
            img = driver.find_element(By.CSS_SELECTOR, "figure img")
            img_url = img.get_attribute("src")
            img_data = requests.get(img_url).content
            img_filename = f"images/article_{i}.jpg"
            with open(img_filename, "wb") as f:
                f.write(img_data)
        except:
            img_url = "No image found"

        print(f"Article {i}: {title}")
        print(f"URL: {article_url}")
        print(f"Image: {img_url}")
        print("Content Preview:")
        print(content[:500], "...\n")

    except Exception as e:
        print(f"Error reading article {i}: {e}")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)

driver.quit()

print("\n🌐 Translated Titles:\n")
translator = Translator()
for i, title in enumerate(spanish_titles, 1):
    translated = translator.translate(title, src='es', dest='en')
    print(f"{i}. {translated.text}")
