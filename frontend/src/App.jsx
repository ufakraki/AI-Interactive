import { useState } from 'react';
import './App.css';


function App() {
  const [selectedCity, setSelectedCity] = useState(null);

  return (
    <div className="App" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ textAlign: 'center', margin: '32px 0 0 0' }}>
        <h1>Türkiye Balık Avı Verim Tahmini</h1>
        <p>Şehir seçmek için haritadan bir noktaya tıklayın.</p>
      </header>
      <main style={{ flex: 1 }}>
        {/* Türkiye haritası SVG olarak eklendi */}
        <div style={{ display: 'flex', justifyContent: 'center', margin: '32px 0' }}>
          <img src="/src/assets/turkiye-simplemaps.svg" alt="Türkiye Haritası" style={{ maxWidth: '100%', height: 'auto', border: '1px solid #eee', boxShadow: '0 2px 8px #0001', background: '#fff', borderRadius: 8 }} />
        </div>
        {selectedCity && (
          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <h2>{selectedCity}</h2>
            <p>Seçilen şehir için balık avı verim tahmini yakında burada görünecek.</p>
          </div>
        )}
      </main>
      <footer style={{ textAlign: 'center', margin: '32px 0 8px 0', color: '#888', fontSize: 15 }}>
        Bu proje, <b>Altaion Interactive</b> tarafından geliştirilmiştir.
      </footer>
    </div>
  );
}

export default App;
