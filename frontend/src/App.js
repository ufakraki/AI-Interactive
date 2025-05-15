import React, { useState } from 'react';
import AdminPanel from './components/AdminPanel';
import Login from './components/Login';

function App() {
  const [user, setUser] = useState(null);

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  // Rol bazlı arayüz örneği
  return (
    <div className="App">
      <h1>Opion CRM Çalışıyor! 🚀</h1>
      <div className="mb-2">Hoşgeldin, {user.first_name} {user.last_name} ({user.role})</div>
      {user.role === 'superadmin' || user.role === 'company_admin' ? (
        <AdminPanel user={user} />
      ) : (
        <div>Kullanıcı paneli yakında...</div>
      )}
      <button className="btn btn-secondary mt-3" onClick={() => { setUser(null); localStorage.removeItem('access_token'); }}>Çıkış Yap</button>
    </div>
  );
}

export default App;