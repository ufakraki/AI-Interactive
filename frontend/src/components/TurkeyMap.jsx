
import React from 'react';
import TurkeySVG from '../assets/turkiye-simplemaps.svg?react';
import './TurkeyMap.css';

// Şehir ismini normalize eden fonksiyon (küçük harf, Türkçe karakterleri İngilizce'ye çevir)
export function normalizeCityName(name) {
  if (!name) return '';
  // Escape edilmiş karakterleri çöz (örn. \\xC7 -> Ç)
  try {
    name = decodeURIComponent(escape(name));
  } catch (e) {
    // decode başarısız olursa orijinalini kullan
  }
  return name
    .trim()
    .toLocaleLowerCase('tr-TR')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/ç/g, 'c')
    .replace(/ğ/g, 'g')
    .replace(/ı/g, 'i')
    .replace(/ö/g, 'o')
    .replace(/ş/g, 's')
    .replace(/ü/g, 'u');
}
// Şehir ismini düzgün Türkçe karakterlerle gösteren fonksiyon
export function fixCityName(name) {
  // Gerekirse burada özel düzeltmeler yapılabilir
  // Şimdilik sadece baş harf büyük yapılıyor
  if (!name) return '';
  const lower = name.trim().toLocaleLowerCase('tr-TR');
  return lower.charAt(0).toLocaleUpperCase('tr-TR') + lower.slice(1);
}

function TurkeyMap({ selectedCity, setSelectedCity }) {
  // Tüm şehirler aktif olsun
  const enabledCitiesNormalized = null;
  const svgRef = React.useRef(null);

  // Seçili şehri vurgulamak ve sadece aktif şehirleri enable yapmak için style uygula
  React.useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    // Tüm path ve label_points circle'ları temizle
    svg.querySelectorAll('path, g#label_points > circle').forEach(el => {
      el.classList.remove('selected-city');
      el.classList.remove('city-disabled');
      el.style.pointerEvents = '';
      el.style.opacity = '';
    });
    // Sadece aktif şehirler tıklanabilir olsun, diğerleri pasif
    svg.querySelectorAll('path[name], g#label_points > circle[class]').forEach(el => {
      // enabledCitiesNormalized null ise tüm şehirler aktif
      if (enabledCitiesNormalized && enabledCitiesNormalized.length > 0) {
        const cityName = el.tagName === 'path' ? el.getAttribute('name') : el.getAttribute('class');
        if (!enabledCitiesNormalized.includes(normalizeCityName(cityName))) {
          el.classList.add('city-disabled');
          el.style.pointerEvents = 'none';
          el.style.opacity = '0.4';
        }
      }
    });
    if (selectedCity) {
      // path'lerde name ile, label_points'te class ile eşleşenleri vurgula
      const path = Array.from(svg.querySelectorAll('path[name]')).find(
        el => normalizeCityName(el.getAttribute('name')) === normalizeCityName(selectedCity)
      );
      if (path) path.classList.add('selected-city');
      const label = Array.from(svg.querySelectorAll('g#label_points > circle[class]')).find(
        el => normalizeCityName(el.getAttribute('class')) === normalizeCityName(selectedCity)
      );
      if (label) label.classList.add('selected-city');
    }
  }, [selectedCity]);

  // Tıklama olayını doğrudan SVG DOM'una ekle
  React.useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const handleCityClick = (e) => {
      let cityName = null;
      if (e.target.tagName === 'path' && e.target.getAttribute('name')) {
        cityName = e.target.getAttribute('name');
      } else if (e.target.tagName === 'circle' && e.target.parentNode.id === 'label_points') {
        cityName = e.target.getAttribute('class');
      }
      // Sadece aktif şehirler tıklanabilir (normalize karşılaştırma)
      // enabledCitiesNormalized null ise tüm şehirler tıklanabilir
      if (
        cityName &&
        (
          !enabledCitiesNormalized ||
          enabledCitiesNormalized.includes(normalizeCityName(cityName))
        )
      ) {
        // Çanakkale için özel düzeltme: başında '\xC7', 'Ç', 'Ã‡' gibi karakterlerle başlıyorsa düzelt
        let fixedCityName = cityName;
        if (typeof fixedCityName === 'string' &&
            (fixedCityName.startsWith('\xC7') || fixedCityName.startsWith('\\xC7') || fixedCityName.startsWith('Ç') || fixedCityName.startsWith('Ã‡'))
        ) {
          fixedCityName = 'Çanakkale';
        }
        console.log('Tıklanan şehir:', JSON.stringify(cityName), '| Düzeltilmiş:', fixedCityName, '| Normalize:', normalizeCityName(fixedCityName));
        setSelectedCity(fixedCityName);
      }
    };
    svg.addEventListener('click', handleCityClick);
    return () => svg.removeEventListener('click', handleCityClick);
  }, [setSelectedCity, enabledCitiesNormalized]);

  return (
    <div className="turkey-map-container">
      {/* SVG'yi React bileşeni olarak kullanıyoruz */}
      <TurkeySVG
        id="turkey-svg-root"
        className="turkey-svg"
        ref={svgRef}
        style={{ maxWidth: '100%', height: 'auto', cursor: 'pointer', background: '#fff', borderRadius: 8, border: '1px solid #eee', boxShadow: '0 2px 8px #0001' }}
      />
    </div>
  );
}

export default TurkeyMap;
