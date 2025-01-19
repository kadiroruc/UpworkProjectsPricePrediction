
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv

import json

# config.json dosyasını oku
with open('config.json') as config_file:
    config = json.load(config_file)

# Değişkeni al
variable_value = config['variable_value']


# Chrome seçeneklerini ayarla
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--window-size=1920,1080")  # Büyük pencere boyutu

# WebDriver'ı başlat
driver = webdriver.Chrome(options=options)

url = f"https://www.upwork.com/nx/search/jobs/?q=development&page={variable_value}&per_page=50"  # Veri almak istediğiniz URL

# Değişkeni güncelle
value = int(variable_value) + 1
config['variable_value'] = str(value)

# config.json dosyasını güncelle
with open('config.json', 'w') as config_file:
    json.dump(config, config_file, indent=4)
driver.get(url)

# JavaScript tarafından yüklenen içeriği beklemek için zaman ekleyin
time.sleep(3)  # Yeterli bekleme süresi ekleyin

# CSV dosyasını aç ve başlıkları ekle
csv_file = "upwork_jobs.csv"
with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    if value == 2:
        writer.writerow(["Job Title", "Hourly/Fixed", "Budget", "Level", "Skills"])

    # İş başlıklarını al
    titles = driver.find_elements(By.CSS_SELECTOR, "h2.h5.mb-0.mr-2.job-tile-title")

    # İş ilanlarının detaylarını al
    uls = driver.find_elements(By.CSS_SELECTOR, "ul.job-tile-info-list.text-base-sm.mb-4")
    for i, ul in enumerate(uls):
        try:
            # İş başlığı
            job_title = titles[i].text if i < len(titles) else "N/A"

            # Saatlik ya da sabit fiyat
            liElements = ul.find_elements(By.TAG_NAME, "li")
            hourly_fixed = liElements[0].text if len(liElements) > 0 else "N/A"

            # Bütçe (eğer sabit fiyatlıysa)
            budget = liElements[-1].text if "Fixed price" in hourly_fixed else "N/A"

            level = liElements[1].text if len(liElements) > 0 else "N/A"

            # Yetenekler (sonraki siblinglerden alınıyor)
            siblings = ul.find_elements(By.XPATH, "following-sibling::*")
            skills = []
            if siblings:
                parentSkillDiv = siblings[-1]
                skill_elements = parentSkillDiv.find_elements(By.CLASS_NAME, "air3-token-wrap")
                skills = [skill.text for skill in skill_elements]

            # Verileri CSV'ye yaz
            writer.writerow([job_title, hourly_fixed, budget, level, ", ".join(skills)])
        except Exception as e:
            print(f"Error processing job listing: {e}")

# Tarayıcıyı kapat
driver.quit()

print(f"Veriler '{csv_file}' dosyasına kaydedildi!")