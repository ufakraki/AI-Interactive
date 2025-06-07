import os
import sys
import time
import json
from scraper import Scraper
from excel_exporter import ExcelExporter
from utils import setup_logger, validate_url
from site_configs import SiteConfigs

logger = setup_logger("main")

def clear_screen():
    """Ekranı temizler"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Program başlık bilgisini gösterir"""
    print("="*50)
    print("WEBION - Web Sitesi Veri Çekme Aracı")
    print("Altaion Interactive")
    print("="*50)
    print()

def get_user_input(prompt, validator=None, error_message=None):
    """Kullanıcıdan giriş alır ve opsiyonel doğrulama yapar"""
    while True:
        value = input(prompt)
        if validator is None or validator(value):
            return value
        print(error_message or "Geçersiz giriş. Lütfen tekrar deneyin.")

def load_config(config_file="config.json"):
    """Yapılandırma dosyasını yükler"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Yapılandırma dosyası yüklenirken hata: {str(e)}")
    
    return {
        "recent_urls": [],
        "selector_presets": {}
    }

def save_config(config, config_file="config.json"):
    """Yapılandırma dosyasını kaydeder"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Yapılandırma dosyası kaydedilirken hata: {str(e)}")

def get_site_url(config):
    """Kullanıcıdan site URL'sini alır"""
    recent_urls = config.get("recent_urls", [])
    
    if recent_urls:
        print("Son kullanılan URL'ler:")
        for i, url in enumerate(recent_urls, 1):
            print(f"{i}. {url}")
        print("0. Yeni URL gir")
        
        choice = get_user_input("Seçiminiz (0-{}): ".format(len(recent_urls)), 
                               lambda x: x.isdigit() and 0 <= int(x) <= len(recent_urls),
                               "Geçersiz seçim. Lütfen listeden bir sayı seçin.")
        
        if choice == "0":
            url = get_user_input("Web sitesi URL'si: ", validate_url, "Geçersiz URL. http:// veya https:// ile başlamalıdır.")
        else:
            url = recent_urls[int(choice)-1]
    else:
        url = get_user_input("Web sitesi URL'si: ", validate_url, "Geçersiz URL. http:// veya https:// ile başlamalıdır.")
    
    # URL'yi recent listesine ekle (zaten varsa en üste taşı)
    if url in recent_urls:
        recent_urls.remove(url)
    recent_urls.insert(0, url)
    
    # Son 5 URL'yi tut
    config["recent_urls"] = recent_urls[:5]
    save_config(config)
    
    return url

def get_selector_info(url):
    """Sadece firma linklerini tespit eder - Veri seçicileri artık universal"""
    print("\n🔍 Web sitesi otomatik analiz ediliyor...")
    print("⏳ Lütfen bekleyin...")
    
    # Otomatik seçici tespiti
    scraper = Scraper()  # Sadece Selenium kullan
    scraper.set_base_url(url)
    suggestions = scraper.suggest_selectors(url)
    scraper.close()
    
    if not suggestions:
        print("❌ Otomatik tespit başarısız oldu. Temel seçiciler kullanılacak.")
        return get_fallback_selectors()
    
    print("✅ Otomatik tespit tamamlandı!")
    
    # En yüksek güven oranına sahip seçicileri otomatik seç
    company_links_selector = auto_select_best_suggestion(
        "Firma Linkleri", 
        suggestions.get('company_links', [])
    )
    
    if not company_links_selector:
        print("\n❌ Firma linkleri otomatik tespit edilemedi. Fallback seçiciler kullanılıyor.")
        return get_fallback_selectors()
    
    # Artık veri seçicilerine ihtiyaç yok - universal toplama kullanıyoruz
    print("\n🎯 UNIVERSAL VERİ TOPLAMA MODUna geçildi!")
    print("   📋 Sistem sayfadaki TÜM verileri otomatik toplayacak")
    print("   📞 Telefon, email, web sitesi, adres, sosyal medya vs.")
    print("   🔍 CSS seçicileri artık gerekmiyor!")
    
    # Sayfalama seçicisini otomatik seç
    next_page_selector = auto_select_best_suggestion(
        "Sayfalama", 
        suggestions.get('pagination', [])
    )
    
    # Başarılı tespit özeti
    print(f"\n🎯 Tespit Özeti:")
    print(f"   📋 Firma linki seçici: ✅")
    print(f"   📋 Veri toplama: ✅ UNIVERSAL MOD (Tüm veriler otomatik)")
    print(f"   📋 Sayfalama: {'✅' if next_page_selector else '❌ (Tek sayfa işlenecek)'}")
    return company_links_selector, {}, next_page_selector  # Boş dict döndür, artık gerekmiyor

def get_max_pages():
    """Maksimum sayfa sayısını belirler"""
    max_pages = None  # Sınırsız sayfa
    print(f"\n📄 TÜM SAYFALAR işlenecek (sınırsız)")
    print("   (Maksimum veri toplama modu)")
    return max_pages

def run_scraper(url, use_selenium, company_links_selector, selectors, next_page_selector, max_pages):
    """Ana scraping işlemini çalıştırır - Her zaman Selenium kullanır"""
    print(f"\n🚀 Veri çekme işlemi başlıyor...")
    print(f"📍 URL: {url}")
    print(f"🔧 Mod: Selenium (JavaScript optimized)")
    print(f"📄 Maksimum sayfa: {max_pages or 'Sınırsız'}")
    
    scraper = None
    try:
        # Scraper'ı başlat (her zaman Selenium)
        scraper = Scraper()
        scraper.set_base_url(url)
        
        # Yeni iş akışı ile tüm firma verilerini çek
        all_companies = scraper.scrape_all_companies(
            start_url=url,
            company_links_selector=company_links_selector,
            data_selectors=selectors,
            next_page_selector=next_page_selector,
            max_pages=max_pages
        )
        
        if not all_companies:
            print("❌ Hiç veri çekilemedi!")
            return False
        
        print(f"\n✅ Toplam {len(all_companies)} firma verisi çekildi!")
        
        # Excel'e aktar
        exporter = ExcelExporter()
        excel_file = exporter.export_to_excel(all_companies)
        
        if excel_file:
            print(f"📊 Veriler Excel dosyasına kaydedildi: {excel_file}")
            
            # Özet bilgileri göster
            show_summary(all_companies)
            return True
        else:
            print("❌ Excel dosyası oluşturulamadı!")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu!")
        logger.info("İşlem kullanıcı tarafından durduruldu")
        return False
    except Exception as e:
        logger.error(f"Scraping sırasında hata: {str(e)}")
        print(f"❌ Hata oluştu: {str(e)}")
        return False
    finally:
        if scraper:
            scraper.close()

def select_from_suggestions(title, suggestions):
    """Önerilen seçiciler arasından kullanıcıya seçim yaptırır"""
    if not suggestions:
        return None
    
    print(f"\n{title} için öneriler:")
    print("0. Manuel giriş yap")
    
    for i, suggestion in enumerate(suggestions, 1):
        confidence_percent = int(suggestion['confidence'] * 100)
        print(f"{i}. {suggestion['selector']} ({confidence_percent}% güven)")
        print(f"   └─ {suggestion['description']}")
    
    choice = get_user_input(
        f"Seçiminiz (0-{len(suggestions)}): ",
        lambda x: x.isdigit() and 0 <= int(x) <= len(suggestions),
        "Geçersiz seçim. Lütfen listeden bir sayı seçin."
    )
    
    choice_num = int(choice)
    if choice_num == 0:
        return None
    
    return suggestions[choice_num - 1]['selector']

def get_manual_selector_info():
    """Manuel seçici girişi"""
    print("\n📝 Manuel seçici girişi:")
    
    company_links_selector = input("Firma linkleri için CSS seçici: ")
    
    print("\nFirma detay bilgileri için seçiciler:")
    selectors = get_manual_data_selectors()
    
    next_page_selector = input("Sonraki sayfa butonu için CSS seçici (opsiyonel): ")
    
    return company_links_selector, selectors, next_page_selector

def get_manual_data_selectors():
    """Manuel veri seçici girişi"""
    selectors = {}
    
    fields = [
        "Firma Adı",
        "Telefon", 
        "E-posta",
        "Adres",
        "Web Sitesi",
        "Açıklama"
    ]
    
    for field in fields:
        selector = input(f"{field} için CSS seçici (boş bırakılabilir): ").strip()
        if selector:
            selectors[field] = selector
    
    # Özel alanlar
    while True:
        custom_field = input("Özel alan adı (bitirmek için boş bırakın): ").strip()
        if not custom_field:
            break
        
        custom_selector = input(f"{custom_field} için CSS seçici: ").strip()
        if custom_selector:
            selectors[custom_field] = custom_selector
    
    return selectors

def show_summary(data):
    """Çekilen verilerin özetini gösterir"""
    print(f"\n📋 Veri Özeti:")
    print(f"├─ Toplam firma sayısı: {len(data)}")
    
    # Sayfa bazında dağılım
    pages = set(item.get('Sayfa', 1) for item in data)
    print(f"├─ İşlenen sayfa sayısı: {len(pages)}")
    
    # Alan doluluk oranları
    if data:
        fields = [field for field in data[0].keys() if field not in ['Sayfa', 'Sıra', 'URL', 'Toplam_Sıra']]
        print(f"├─ Çekilen alan sayısı: {len(fields)}")
        
        for field in fields:
            filled_count = sum(1 for item in data if item.get(field, '').strip())
            percentage = (filled_count / len(data)) * 100
            print(f"│  ├─ {field}: %{percentage:.1f} dolu")
    
    print(f"└─ ✅ İşlem tamamlandı!")

def main():
    """Ana program fonksiyonu - TAM OTOMATİK VERİ TOPLAMA SİSTEMİ"""
    clear_screen()
    print_header()
    
    config = load_config()
    
    # Sadece URL al - geri kalan her şey otomatik
    url = get_site_url(config)
    
    print(f"\n🤖 TAM OTOMATİK VERİ TOPLAMA MODUna geçiliyor...")
    print(f"📍 Hedef Site: {url}")
    print(f"🎯 Yeni Teknoloji: UNIVERSAL VERİ ÇIKARMA (CSS seçici yok!)")
    print(f"🔍 Otomatik Toplar: Firma adı, telefon, email, web sitesi, adres, sosyal medya, sektör...")
    print(f"🔧 Motor: Selenium (JavaScript optimized)")
    print(f"📊 Çıktı: Excel dosyası")
    print("="*60)
    
    # Seçicileri tam otomatik tespit et
    company_links_selector, selectors, next_page_selector = get_selector_info(url)
    
    # Otomatik sayfa limiti
    max_pages = get_max_pages()
    
    print("\n🚀 VERİ TOPLAMA İŞLEMİ BAŞLIYOR...")
    print("   🔥 YENİ UNIVERSAL SİSTEM: Sayfadaki TÜM verileri otomatik çıkarır")
    print("   📋 CSS seçicilerine artık ihtiyaç yok!")
    print("   🎯 Maksimum veri kalitesi garantili")
    
    # Scraping işlemini çalıştır
    success = run_scraper(url, True, company_links_selector, selectors, next_page_selector, max_pages)
    
    if success:
        print("\n🎉 VERİ TOPLAMA İŞLEMİ BAŞARIYLA TAMAMLANDI!")
        print("📊 Veriler Excel dosyasına kaydedildi")
        print("🔥 Yeni universal sistem kullanıldı - maksimum veri kalitesi!")
    else:
        print("\n❌ İşlem sırasında bir hata oluştu.")
        print("💡 Farklı bir URL deneyebilir veya tekrar çalıştırabilirsiniz.")
    
    # Devam seçeneği
    print(f"\n" + "="*60)
    devam = input("Başka bir web sitesi taramak istiyor musunuz? (E/h): ").lower()
    if devam in ['e', 'evet', 'y', 'yes']:
        main()  # Programı yeniden başlat
    else:
        print("\n🙏 Webion kullandığınız için teşekkürler!")
        print("💼 Altaion Interactive - Profesyonel Web Scraping Çözümleri")

def auto_select_best_suggestion(category, suggestions):
    """En yüksek güven oranına sahip seçiciyi otomatik seçer - Agresif mod"""
    if not suggestions:
        return None
    
    # Güven oranına göre sırala
    best_suggestion = max(suggestions, key=lambda x: x.get('confidence', 0))
    
    # Çok agresif threshold - %50 bile kabul et
    if best_suggestion['confidence'] >= 0.5:  # %50 güven ve üzeri otomatik kabul (çok düşürüldü)
        print(f"✅ {category}: {best_suggestion['confidence']:.0%} güven ile otomatik seçildi")
        print(f"   Seçici: {best_suggestion['selector']}")
        return best_suggestion['selector']
    else:
        print(f"\n⚠️ {category} için en iyi tespit: {best_suggestion['confidence']:.0%} güven - Fallback kullanılacak")
        return None

def get_fallback_selectors():
    """Otomatik tespit başarısız olduğunda kullanılacak kapsamlı fallback seçiciler"""
    print("🔄 Kapsamlı fallback seçiciler deneniyor...")
    
    # Çok agresif ve akıllı link seçicileri (debug sonuçlarına göre güncellenmiş)
    fallback_company_links = "a[href*='exhibitor'], a[href*='company'], a[href*='firm'], a[href*='business'], a[href*='profile'], .item a[href], .result a[href], .listing a[href], a[href]:not([href^='mailto:']):not([href^='tel:']):not([href^='#']):not([href^='javascript']):not([href='/'])"
    
    # Çok kapsamlı sayfalama seçicileri
    fallback_pagination = """
    a:contains('Next'), 
    a:contains('Sonraki'), 
    a:contains('İleri'),
    a:contains('>'),
    a:contains('→'),
    .next, 
    .pagination a:last-child, 
    [class*='next'], 
    [class*='forward'],
    [aria-label*='Next'],
    [aria-label*='next'],
    button[aria-label*='Next'],
    button[aria-label*='next'],
    .pager-next,
    .page-next
    """.replace('\n', '').replace(' ', '')
    
    print("🔗 Agresif firma linki seçicileri hazırlandı")
    print("🎯 UNIVERSAL VERİ TOPLAMA modu - CSS seçicileri artık gerekmiyor!")
    
    return fallback_company_links, {}, fallback_pagination  # Boş dict döndür

def get_basic_data_selectors():
    """Sadece temel iş bilgilerini toplar - Sosyal medya ve gereksiz veriler hariç"""
    return {
        # Sadece temel iş bilgileri
        'Firma Adı': 'h1:not(:contains("Search")):not(:contains("Menu")), h2:not(:contains("Search")), h3:not(:contains("Search")), .company-name, .firm-name, .business-name, .organization, .exhibitor-name, .title:not(:contains("Search")), .name:not(:contains("Search"))',
        'Telefon': 'a[href^="tel:"], .phone, .tel, .telephone, .contact-phone, .mobile, .gsm, [class*="phone"], [class*="tel"]',
        'E-posta': 'a[href^="mailto:"]:not([href*="recommend"]):not([href*="page"]), .email, .mail, .contact-email, .e-mail, [class*="email"], [class*="mail"]',
        'Web Sitesi': 'a[href^="http"]:not([href*="messefrankfurt"]):not([href*="facebook"]):not([href*="twitter"]):not([href*="linkedin"]):not([href*="instagram"]):not([href*="youtube"]):not([href^="mailto:"]):not([href^="tel:"]), .website, .web, .url, .link, [class*="website"], [class*="web"]',
        
        # Adres ve konum bilgileri
        'Adres': '.address, .addr, .location, .contact-address, .full-address, .street-address, [class*="address"], [class*="location"]',
        'Şehir': '.city, .town, .locality, .city-name, [class*="city"], [class*="town"]',
        'Ülke': '.country, .nation, .country-name, .nationality, [class*="country"], [class*="nation"]',
        
        # İş bilgileri (sadece temel)
        'Sektör': '.sector, .industry, .business-type, .category, .field, .expertise, [class*="sector"], [class*="industry"], [class*="category"]'
    }

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error(f"Program hatası: {str(e)}")
        print(f"\nBeklenmeyen bir hata oluştu: {str(e)}")
        print("Lütfen tekrar deneyin veya destek alın.")
