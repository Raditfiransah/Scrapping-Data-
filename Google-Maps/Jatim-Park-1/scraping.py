from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Setup Chrome with automatic driver management
options = Options()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')

# Use webdriver_manager to automatically handle ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Buka halaman Maps
url = "https://www.google.com/maps/place/Jawa+Timur+Park+1/@-7.8841467,112.5222466,1065m/data=!3m2!1e3!4b1!4m6!3m5!1s0x2e78872ad61d07b9:0x59a848ad52479780!8m2!3d-7.884152!4d112.5248269!16s%2Fg%2F1q5bkzmkt?entry=ttu&g_ep=EgoyMDI1MTAyOS4yIKXMDSoASAFQAw%3D%3D"

try:
    driver.get(url)
    time.sleep(5)

    # Klik tombol More Reviews jika ada
    try:
        more_reviews = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ulasan lainnya') or contains(text(), 'More reviews')]/ancestor::button"))
        )
        more_reviews.click()
        print("[INFO] Klik tombol More reviews.")
        time.sleep(3)
    except:
        print("[INFO] Tidak ada tombol More reviews.")

    # Loop scroll berdasarkan elemen terakhir
    reviews_data = []
    seen_reviews = set()
    scroll_attempt = 0
    max_scroll_attempts = 200
    print("[INFO] Mulai scroll...")

    jumlah_data = 500

    while scroll_attempt < max_scroll_attempts and len(reviews_data) < jumlah_data:
        # Ambil semua container review
        review_containers = driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf')

        for container in review_containers:
            try:
                username = container.find_element(By.CSS_SELECTOR, '.d4r55').text.strip()
            except:
                username = 'Unknown'

            try:
                review = container.find_element(By.CSS_SELECTOR, '.wiI7pd').text.strip()
            except:
                review = ''

            try:
                rating_element = container.find_element(By.CSS_SELECTOR, '.kvMYJc')
                rating = rating_element.get_attribute('aria-label').split()[0]  # contoh: "2 stars"
            except:
                try:
                    # Alternative way to get rating
                    rating_element = container.find_element(By.CSS_SELECTOR, '[aria-label*="star"]')
                    rating = rating_element.get_attribute('aria-label').split()[0]
                except:
                    rating = 'Unknown'

            # Cek duplikat review
            unique_key = (username, review)
            if review and unique_key not in seen_reviews:
                seen_reviews.add(unique_key)
                reviews_data.append({
                    'user': username,
                    'review': review,
                    'rating': rating
                })

        # Scroll ke bawah dengan elemen terakhir
        if review_containers:
            driver.execute_script("arguments[0].scrollIntoView(true);", review_containers[-1])
            time.sleep(2)
        else:
            print("[INFO] Tidak ada container review ditemukan.")
            break

        print(f"[INFO] Total ulasan terkumpul: {len(reviews_data)}")
        time.sleep(2)
        scroll_attempt += 1

        # Check if we can't load more reviews
        if scroll_attempt > 10 and len(review_containers) == 0:
            print("[INFO] Tidak ada review baru yang dimuat, berhenti scrolling.")
            break

        if len(reviews_data) >= jumlah_data:
            print(f"[INFO] Sudah mencapai {jumlah_data} ulasan, berhenti scrolling.")
            break

    # Cetak hasil
    print(f"\n=== Hasil Ulasan ({len(reviews_data)} ulasan) ===")
    for i, item in enumerate(reviews_data[:jumlah_data], 1):
        print(f"{i}. User: {item['user']}")
        print(f"   Rating: {item['rating']}")
        print(f"   Review: {item['review'][:100]}{'...' if len(item['review']) > 100 else ''}\n")

    # Simpan ke CSV
    if reviews_data:
        df = pd.DataFrame(reviews_data)
        df.to_csv('Jatim-Park-1.csv', index=False)
        print(f"[INFO] Data berhasil disimpan ke CSV dengan {len(reviews_data)} ulasan.")
    else:
        print("[INFO] Tidak ada data ulasan yang berhasil dikumpulkan.")

except Exception as e:
    print(f"[ERROR] Terjadi kesalahan: {str(e)}")

finally:
    # Always quit driver
    driver.quit()
    print("[INFO] Browser ditutup.")