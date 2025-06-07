# -*- coding: utf-8 -*-
"""
Site-specific configurations for Webion
Bu dosya bilinen siteler için özel yapılandırmalar içerir
"""

import re
from urllib.parse import urlparse

class SiteConfigs:
    """Bilinen siteler için özel yapılandırmalar"""
    
    SITE_CONFIGS = {
        # İplik Fuarı
        'iplikfuari.com': {
            'name': 'İplik Fuarı',
            'requires_selenium': True,
            'company_links_selector': 'a.js-open-table-detail',
            'data_selectors': {
                'Firma Adı': 'h2.company-name',
                'Telefon': 'a[href^="tel:"]',
                'E-posta': 'a[href^="mailto:"]',
                'Web Sitesi': 'a[href^="http"]:not([href^="mailto:"]):not([href^="tel:"])',
                'Ülke': '.country',
                'Şehir': '.city'
            },            'next_page_selector': 'a.next:not(.disabled)',
            'wait_time': 2
        },
          # Texhibitionist
        'texhibitionist.com': {
            'name': 'Texhibitionist Türk Tekstil Fuarı',
            'requires_selenium': True,
            'company_links_selector': 'a[href*="/katilimcilar/"]',            'data_selectors': {
                'Firma Adı': '.title, [class*="company"] .title, [class*="company"], .company-name, .firm-name, h2:not(:contains("Katılımcılar")), h3',
                'Yetkili Kişi': '.authorized-person, .contact-person, .representative, .manager, .yetkili',
                'Telefon': 'a[href^="tel:"], .phone, .tel, .telephone, .telefon, [class*="phone"], [class*="tel"]',
                'E-posta': 'a[href^="mailto:"], .email, .mail, .e-mail, [class*="email"], [class*="mail"]',
                'Web Sitesi': 'a[href^="http"]:not([href*="texhibitionist"]):not([href*="facebook"]):not([href*="twitter"]):not([href*="linkedin"]):not([href*="instagram"]):not([href*="youtube"]):not([href^="mailto:"]):not([href^="tel:"])',
                'Adres': '.address, .location, .addr, .full-address, .postal-address, .adres',
                'Ülke': '.country, .nation, .ulke, .country-name',
                'Şehir': '.city, .town, .locality, .sehir, .city-name',
                'Faks': 'a[href^="fax:"], .fax, .fax-number, .faks',
                'Sektör': '.sector, .industry, .category, .business-type, .product-category, .sektor',
                'Açıklama': '.description, .about, .company-description, .profile, .overview, .aciklama, .hakkinda'
            },
            'next_page_selector': '.pagination a[href*="page="], .next, .pagination-next, a[aria-label*="next"]',
            'wait_time': 2,
            'pagination_pattern': '?page={}',
            'max_pages': 35
        },
        
        # HomeTex
        'hometex.com.tr': {
            'name': 'HomeTex Türkiye',
            'requires_selenium': True,
            'company_links_selector': 'a[href*="/firma/"]',
            'data_selectors': {
                'Firma Adı': 'h1.company-title',
                'Telefon': 'a[href^="tel:"]',
                'E-posta': 'a[href^="mailto:"]',
                'Web Sitesi': 'a[href^="http"]:not([href^="mailto:"]):not([href^="tel:"])',
                'Adres': '.company-address',
                'Sektör': '.company-sector'
            },
            'next_page_selector': '.pagination .next:not(.disabled)',
            'wait_time': 2
        }
    }
    
    @classmethod
    def get_config_for_url(cls, url):
        """URL için uygun konfigürasyonu döndürür"""
        if not url:
            return None
            
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Subdomain'leri de kontrol et
            for site_domain, config in cls.SITE_CONFIGS.items():
                if site_domain in domain or domain.endswith(site_domain):
                    return config
                    
        except Exception:
            pass
            
        return None
    
    @classmethod
    def get_all_sites(cls):
        """Desteklenen tüm siteleri döndürür"""
        return list(cls.SITE_CONFIGS.keys())
    
    @classmethod
    def is_javascript_site(cls, url):
        """Artık tüm siteler Selenium kullanıyor"""
        return True  # Tüm siteler için Selenium kullan

# Test fonksiyonu
def test_site_configs():
    """Site konfigürasyonlarını test eder"""
    test_urls = [
        'https://iplikfuari.com/katilimci-listesi',
        'https://www.texhibitionist.com/katilimcilar',
        'https://hometex.com.tr/firmalar'
    ]
    
    for url in test_urls:
        config = SiteConfigs.get_config_for_url(url)
        if config:
            print(f"✅ {url} -> {config['name']}")
            print(f"   Selenium gerekli: {config['requires_selenium']}")
        else:
            print(f"❌ {url} -> Yapılandırma bulunamadı")

if __name__ == "__main__":
    test_site_configs()
