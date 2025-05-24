
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import TurkeyMap, { fixCityName, normalizeCityName } from './components/TurkeyMap';


function HomePage() {
  const [selectedCity, setSelectedCity] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const navigate = useNavigate();

  // İlçeler
  // Sadece API'den veri çekilen ilçeler
  const balikesirDistricts = [
    { value: '', label: 'İlçe seçiniz' },
    { value: 'ayvalik', label: 'Ayvalık' },
    { value: 'edremit', label: 'Edremit' },
  ];
  const canakkaleDistricts = [
    { value: '', label: 'İlçe seçiniz' },
    { value: 'merkez', label: 'Merkez' },
  ];

  // Şehir-ilçe eşleştirme (anahtarlar normalize fonksiyonu ile üretiliyor)
  const cityDistrictMap = {
    [normalizeCityName('balıkesir')]: balikesirDistricts,
    [normalizeCityName('çanakkale')]: canakkaleDistricts,
  };

  const normalizedCity = normalizeCityName(selectedCity);
  const districtList = cityDistrictMap[normalizedCity];
  // Debug loglar burada olmalı:
  console.log('cityDistrictMap keys:', Object.keys(cityDistrictMap));
  console.log('selectedCity:', JSON.stringify(selectedCity), '| normalized:', JSON.stringify(normalizedCity));
  if (selectedCity) {
    Object.keys(cityDistrictMap).forEach((key, i) => {
      console.log(
        `Karşılaştırma [${i}]:`,
        JSON.stringify(normalizedCity),
        '===',
        JSON.stringify(key),
        '->',
        normalizedCity === key
      );
    });
  }
  const showDropdown = !!districtList;
  const showPredictionButton = showDropdown && selectedDistrict;

  return (
    <div className="App" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ textAlign: 'center', margin: '32px 0 0 0' }}>
        <h1>Türkiye Balık Avı Verim Tahmini</h1>
        <p>Şehir seçmek için haritadan bir noktaya tıklayın.</p>
      </header>
      <main style={{ flex: 1 }}>
        {/* Türkiye haritası SVG olarak interaktif şekilde eklendi */}
        <div style={{ display: 'flex', justifyContent: 'center', margin: '32px 0' }}>
          <TurkeyMap selectedCity={selectedCity} setSelectedCity={city => {
            setSelectedCity(city);
            setSelectedDistrict(''); // Şehir değişince ilçe sıfırlansın
          }} />
        </div>
        {/* Balıkesir veya Çanakkale seçiliyse ilçe dropdown'u göster */}
        {showDropdown && (
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <label htmlFor="district-select" style={{ fontWeight: 500, marginRight: 8 }}>İlçe:</label>
            <select
              id="district-select"
              value={selectedDistrict}
              onChange={e => setSelectedDistrict(e.target.value)}
              style={{ fontSize: 16, padding: '4px 12px', borderRadius: 4 }}
            >
              {districtList.map(d => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>
        )}
        {/* Tahmine git butonu */}
        {showPredictionButton && (
          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <button
              style={{ fontSize: 18, padding: '8px 32px', borderRadius: 6, background: '#2e7d32', color: '#fff', border: 'none', cursor: 'pointer' }}
              onClick={() => navigate(`/tahmin?city=${encodeURIComponent(selectedCity)}&district=${encodeURIComponent(selectedDistrict)}`)}
            >
              Tahmine Git
            </button>
          </div>
        )}
      </main>
      <footer style={{ textAlign: 'center', margin: '32px 0 8px 0', color: '#888', fontSize: 15 }}>
        Bu proje, <b>Altaion Interactive</b> tarafından geliştirilmiştir.
      </footer>
    </div>
  );
}




  function PredictionPage() {
    // URL'den şehir ve ilçe bilgisini al
    const location = window.location;
    const params = new URLSearchParams(location.search);
    const city = params.get('city');
    const district = params.get('district');
    // Ana sayfaya yönlendirme için useNavigate'i HomePage'den prop olarak alabiliriz
    const navigate = useNavigate();


  // API'den canlı veri çek
  const [score, setScore] = useState(null);
  const [status, setStatus] = useState('');
  const [updatedAt, setUpdatedAt] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // useEffect hook'unu kullan
  useEffect(() => {
    // Eğer city veya district yoksa ana sayfaya yönlendir
    if (!city || !district) {
      navigate('/');
      return;
    }
    setLoading(true);
    setError(null);
    // API endpoint: /get_score?city=ilce_adi
    // Not: API'de ilçe adı normalize edilerek sorgu yapılmalı
    const normalizedDistrict = normalizeCityName(district);
    fetch(`http://localhost:5000/get_score?city=${encodeURIComponent(normalizedDistrict)}`)
      .then(res => {
        if (!res.ok) throw new Error('Veri alınamadı');
        return res.json();
      })
      .then(data => {
        setScore(data.score);
        setStatus(data.status);
        setUpdatedAt(data.updated_at || 'Bilinmiyor');
        setLoading(false);
      })
      .catch(e => {
        setError('Veri alınamadı.');
        setLoading(false);
      });
  }, [city, district, navigate]);


  // Yüzdesel değere göre renk hesaplama (yeşil-sarı-kırmızı arası geçiş)
  function getColor(percent) {
    if (percent <= 30) return '#d32f2f'; // kırmızı
    if (percent >= 80) return '#388e3c'; // yeşil
    if (percent > 30 && percent < 50) {
      const t = (percent - 30) / 20;
      const r = Math.round(211 + (251-211)*t);
      const g = Math.round(47 + (192-47)*t);
      const b = Math.round(47 + (45-47)*t);
      return `rgb(${r},${g},${b})`;
    }
    if (percent >= 50 && percent < 80) {
      const t = (percent - 50) / 30;
      const r = Math.round(251 + (56-251)*t);
      const g = Math.round(192 + (142-192)*t);
      const b = Math.round(45 + (60-45)*t);
      return `rgb(${r},${g},${b})`;
    }
    return '#fbc02d';
  }

  let mainColor = '#fbc02d';
  if (score !== null) {
    mainColor = getColor(score);
  }

  return (
    <div className="App" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ textAlign: 'center', margin: '32px 0 0 0' }}>
        <h1>Balık Avı Tahmini</h1>
        <p style={{ fontSize: 20, margin: '16px 0' }}>
          {fixCityName(city)} / {fixCityName(district)} için tahmini verim:
        </p>
        {updatedAt && (
          <div style={{ fontSize: 15, color: '#888', marginTop: 4 }}>
            Son güncelleme: <b>{updatedAt}</b>
          </div>
        )}
      </header>
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        {loading ? (
          <div style={{ fontSize: 22, color: '#888', marginBottom: 24 }}>Yükleniyor...</div>
        ) : error ? (
          <div style={{ fontSize: 20, color: '#d32f2f', marginBottom: 24 }}>{error}</div>
        ) : (
          <>
            <div style={{ width: 180, height: 180, borderRadius: '50%', background: mainColor, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 16px #0002', marginBottom: 24, transition: 'background 0.5s' }}>
              <span style={{ fontSize: 48, color: '#fff', fontWeight: 700 }}>{score}%</span>
            </div>
            <div style={{ fontSize: 18, color: '#333', marginBottom: 8 }}>
              Balık avı için verim tahmini oranı
            </div>
            <div style={{ fontSize: 17, color: '#2e7d32', marginBottom: 32 }}>
              Durum: <b>{status}</b>
            </div>
          </>
        )}
        <a href="/" style={{ color: '#2e7d32', fontWeight: 500, fontSize: 17 }}>← Haritaya Dön</a>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/tahmin" element={<PredictionPage />} />
      </Routes>
    </Router>
  );
}

export default App;
