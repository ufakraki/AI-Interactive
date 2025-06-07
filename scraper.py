#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Texworld NYC Summer 2024 Infinite Scroll Scraper
ExpoPlattform tabanlı fuar sitesi için infinite scroll sistemi ile scraper

HEDEF SİTE: https://texworldnycsummer2024-messefrankfurt.expoplatform.com/
SİSTEM: Infinite scroll (scroll down ile yeni firmalar yüklenir)
VERİ: Firma Adı, Ülke, Website

ÖZELLİKLER:
- Infinite scroll sistemi
- Multi-tab navigation (ana sayfa korunur)
- Load More butonu otomatik tıklama
- 700+ firmaya kadar çekebilir
- Smart scroll detection

OLUŞTURULMA: 2025-06-07
DURUM: Test edilmeyi bekliyor 🧪
"""

import pandas as pd
import re
import time
import random
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TexworldScraper:
    def __init__(self):
        self.base_url = "https://texworldnycsummer2024-messefrankfurt.expoplatform.com/newfront/marketplace/exhibitors"
        self.companies = []
        self.processed_companies = set()
        self.processed_urls = set()
        
    def setup_selenium_driver(self):
        """Selenium WebDriver kurulumu"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebDriver/537.36')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def wait_for_page_load(self, driver):
        """JavaScript yüklenene kadar bekle"""
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(random.uniform(2, 4))  # Rastgele bekleme
        except TimeoutException:
            logger.warning("Sayfa yükleme timeout")
        
    def extract_company_details(self, driver):
        """Mevcut sayfadan şirket detaylarını çıkar"""
        try:
            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            company_info = {
                'Firma Adı': '',
                'Ülke': '',
                'Website': '',
                'Kaynak': 'TexworldNYC2024',
                'Detay URL': driver.current_url,
                'Çekilme Tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 1. Sayfa başlığından firma adını al
            try:
                title = driver.title
                if title and "Texworld" not in title and "Exhibitor" not in title:
                    company_info['Firma Adı'] = title.strip()
                
                # H1 elementinden de dene
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                for h1 in h1_elements:
                    text = h1.text.strip()
                    if text and len(text) > 3 and "Exhibitor" not in text:
                        company_info['Firma Adı'] = text
                        break
                        
                # Company name class'ından dene
                company_name_selectors = [
                    'h1.company-name',
                    '.company-name',
                    '.exhibitor-name',
                    '[class*="company"]',
                    '[class*="exhibitor"]'
                ]
                
                for selector in company_name_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.text.strip():
                            company_info['Firma Adı'] = element.text.strip()
                            break
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"Firma adı çıkarma hatası: {str(e)}")
            
            # 2. Ülke bilgisini çıkar
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # CSS selector'ları ile ülke bilgisi ara
                country_selectors = [
                    '[class*="country"]',
                    '[class*="location"]',
                    '[class*="address"]',
                    '.contact-info'
                ]
                
                for selector in country_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.text.strip()
                            if text and len(text) < 50:  # Ülke adı çok uzun olmaz
                                # Bilinen ülke isimlerini kontrol et
                                known_countries = ['Turkey', 'China', 'India', 'Bangladesh', 'Pakistan', 'Vietnam', 'Thailand', 'USA', 'United States', 'Germany', 'Italy', 'France', 'Spain', 'United Kingdom', 'Korea', 'Japan']
                                for country in known_countries:
                                    if country.lower() in text.lower():
                                        company_info['Ülke'] = country
                                        logger.info(f"Ülke bilgisi bulundu: {country}")
                                        break
                                if company_info['Ülke']:
                                    break
                    except:
                        continue
                        
                # Pattern matching ile ülke ara
                if not company_info['Ülke']:
                    country_patterns = [
                        r'Country[:\s]*([A-Za-z\s]+)',
                        r'Location[:\s]*([A-Za-z\s]+)',
                        r'Address[:\s]*.*?([A-Za-z\s]+)(?=\n|\s{3,})',
                        r'Based in[:\s]*([A-Za-z\s]+)',
                    ]
                    
                    for pattern in country_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            country = match.group(1).strip()
                            if len(country) < 30:  # Makul ülke adı uzunluğu
                                company_info['Ülke'] = country
                                logger.info(f"Pattern ile ülke bulundu: {country}")
                                break
                                
            except Exception as e:
                logger.debug(f"Ülke bilgisi çıkarma hatası: {str(e)}")
            
            # 3. Website bilgisini çıkar
            try:
                # Link elementlerinden website ara
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href") or ""
                    if (href and 
                        href.startswith('http') and 
                        'texworld' not in href.lower() and
                        'messefrankfurt' not in href.lower() and
                        'expoplatform' not in href.lower() and
                        'mailto:' not in href.lower()):
                        company_info['Website'] = href
                        logger.info(f"Website bulundu: {href}")
                        break
                
                # Text içinden website pattern'i ara
                if not company_info['Website']:
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    website_patterns = [
                        r'Website[:\s]*(https?://[^\s]+)',
                        r'Web[:\s]*(https?://[^\s]+)',
                        r'(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                        r'(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*)'
                    ]
                    
                    for pattern in website_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            website = match.group(1)
                            if ('texworld' not in website.lower() and 
                                'messefrankfurt' not in website.lower() and
                                'expoplatform' not in website.lower()):
                                if not website.startswith('http'):
                                    website = 'https://' + website
                                company_info['Website'] = website
                                logger.info(f"Pattern ile website bulundu: {website}")
                                break
                                
            except Exception as e:
                logger.debug(f"Website çıkarma hatası: {str(e)}")
            
            return company_info
            
        except Exception as e:
            logger.error(f"Detay çıkarma hatası: {str(e)}")
            return None

    def scrape_with_infinite_scroll(self, driver, max_companies=700):
        """Infinite scroll ile firmaları çek"""
        try:
            # Ana sayfa
            logger.info(f"Ana sayfa açılıyor: {self.base_url}")
            driver.get(self.base_url)
            self.wait_for_page_load(driver)
            
            processed_count = 0
            last_company_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 100  # Maksimum scroll sayısı
            no_new_companies_count = 0  # Yeni firma gelmeme sayacı
            
            while processed_count < max_companies and scroll_attempts < max_scroll_attempts:
                try:
                    # Mevcut firma linklerini topla
                    company_links = []
                    
                    # Farklı selector'lar dene
                    link_selectors = [
                        'a[href*="/exhibitor/"]',
                        'a[href*="/newfront/exhibitor/"]', 
                        '.exhibitor-card a',
                        '.company-card a',
                        '[class*="exhibitor"] a',
                        '[class*="company"] a'
                    ]
                    
                    for selector in link_selectors:
                        try:
                            links = driver.find_elements(By.CSS_SELECTOR, selector)
                            for link in links:
                                href = link.get_attribute("href")
                                if (href and '/exhibitor/' in href and 
                                    href not in self.processed_urls):
                                    company_links.append(href)
                                    self.processed_urls.add(href)
                            if company_links:
                                break
                        except:
                            continue
                    
                    # Eğer selector bulamazsa, tüm linklerden exhibitor olanları al
                    if not company_links:
                        all_links = driver.find_elements(By.TAG_NAME, "a")
                        for link in all_links:
                            href = link.get_attribute("href") or ""
                            if ('/exhibitor/' in href and 
                                href not in self.processed_urls):
                                company_links.append(href)
                                self.processed_urls.add(href)
                    
                    current_company_count = len(self.processed_urls)
                    logger.info(f"Scroll {scroll_attempts+1}: {current_company_count} toplam firma bulundu, {len(company_links)} yeni firma")
                    
                    # Yeni firmaları işle
                    for company_url in company_links:
                        if processed_count >= max_companies:
                            break
                            
                        try:
                            logger.info(f"İşleniyor ({processed_count+1}/{max_companies}): {company_url}")
                            
                            # Yeni tab'da aç (ana sayfayı kaybetmemek için)
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            
                            driver.get(company_url)
                            time.sleep(random.uniform(2, 4))
                            
                            company_data = self.extract_company_details(driver)
                            
                            if company_data and company_data['Firma Adı']:
                                self.companies.append(company_data)
                                processed_count += 1
                                
                                logger.info(f"✅ Başarılı: {company_data['Firma Adı']}")
                                logger.info(f"   Ülke: {company_data['Ülke']}")
                                logger.info(f"   Web: {company_data['Website']}")
                            else:
                                logger.warning(f"❌ Veri çıkarılamadı: {company_url}")
                            
                            # Tab'ı kapat ve ana sayfaya dön
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Firma işleme hatası {company_url}: {str(e)}")
                            # Tab cleanup
                            try:
                                if len(driver.window_handles) > 1:
                                    driver.close()
                                    driver.switch_to.window(driver.window_handles[0])
                            except:
                                pass
                            continue
                    
                    # Yeni firma gelmediyse scroll yap
                    if current_company_count == last_company_count:
                        no_new_companies_count += 1
                        logger.info(f"Yeni firma bulunamadı ({no_new_companies_count}/3), scroll yapılıyor...")
                        
                        # Sayfanın sonuna scroll yap
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(3)
                        
                        # JavaScript ile daha fazla içerik yüklenene kadar bekle
                        self.wait_for_page_load(driver)
                        
                        # "Load More" butonu varsa tıkla
                        try:
                            load_more_selectors = [
                                'button[class*="load"]',
                                'button[class*="more"]',
                                'a[class*="load"]',
                                '.load-more',
                                '.show-more',
                                '[class*="load-more"]',
                                '[class*="show-more"]'
                            ]
                            
                            for selector in load_more_selectors:
                                try:
                                    load_button = driver.find_element(By.CSS_SELECTOR, selector)
                                    if load_button.is_displayed() and load_button.is_enabled():
                                        driver.execute_script("arguments[0].click();", load_button)
                                        logger.info("Load More butonuna tıklandı")
                                        time.sleep(3)
                                        break
                                except:
                                    continue
                        except:
                            pass
                        
                        # 3 scroll'da yeni firma gelmiyorsa dur
                        if no_new_companies_count >= 3:
                            logger.info("3 scroll'da yeni firma gelmedi, işlem sonlandırılıyor")
                            break
                    else:
                        no_new_companies_count = 0  # Reset counter
                    
                    last_company_count = current_company_count
                    scroll_attempts += 1
                    
                except Exception as e:
                    logger.error(f"Scroll işleme hatası: {str(e)}")
                    scroll_attempts += 1
                    continue
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Infinite scroll hatası: {str(e)}")
            return 0

    def save_to_excel(self, filename=None):
        """Şirket verilerini Excel'e kaydet"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"texworld_nyc_firmalar_{timestamp}.xlsx"
        
        try:
            df = pd.DataFrame(self.companies)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Texworld NYC Firmaları', index=False)
                
                worksheet = writer.sheets['Texworld NYC Firmaları']
                for column_cells in worksheet.columns:
                    length = max(len(str(cell.value)) for cell in column_cells if cell.value)
                    worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50)
            
            logger.info(f"Veriler Excel'e kaydedildi: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Excel kaydetme hatası: {str(e)}")
            return None

    def run(self, max_companies=700):
        """Ana çalıştırma fonksiyonu - Infinite Scroll versiyonu"""
        logger.info(f"Texworld NYC Infinite Scroll Scraper başlatılıyor (max {max_companies} şirket)...")
        
        driver = None
        try:
            driver = self.setup_selenium_driver()
            
            # Infinite scroll ile firmalar çek
            processed_count = self.scrape_with_infinite_scroll(driver, max_companies)
            
            if processed_count > 0:
                filename = self.save_to_excel()
                
                print("\n" + "="*80)
                print("TEXWORLD NYC INFINITE SCROLL SCRAPER RAPORU")
                print("="*80)
                print(f"🎯 İşlenen şirket sayısı: {processed_count}")
                print(f"📁 Excel dosyası: {filename}")
                print("="*80)
                
                for i, company in enumerate(self.companies, 1):
                    print(f"{i:2d}. {company['Firma Adı']}")
                    if company['Ülke']:
                        print(f"    🌍 {company['Ülke']}")
                    if company['Website']:
                        print(f"    🌐 {company['Website']}")
                
                return self.companies
            else:
                logger.error("Hiç şirket verisi çekilemedi!")
                return []
                
        except KeyboardInterrupt:
            print("\n🛑 KULLANICI DURDURDU - VERİLER KAYDEDİLİYOR...")
            if self.companies:
                self.save_to_excel()
                print(f"✅ {len(self.companies)} firma kaydedildi!")
            return self.companies
        except Exception as e:
            logger.error(f"Ana çalıştırma hatası: {str(e)}")
            print("🚨 HATA NEDENİYLE VERİLER KAYDEDİLİYOR...")
            if self.companies:
                self.save_to_excel()
                print(f"✅ {len(self.companies)} firma kaydedildi!")
            return self.companies
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

if __name__ == "__main__":
    scraper = TexworldScraper()
    companies = scraper.run(max_companies=20)  # 20 şirkete kadar
