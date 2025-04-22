// frontend/src/components/AdminPanel.js
import React, { useEffect, useState } from 'react';
import api from '../api/axios';

export default function AdminPanel() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/companies/')
      .then(res => {
        console.log('API Response:', res.data); // Konsola yazdır
        setData(res.data);
        setLoading(false);
      })
      .catch(error => console.error('API Error:', error));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Firma Listesi</h1>
      {loading ? (
        <div>Yükleniyor...</div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {data.map(item => (
            <div key={item.id} className="border p-4 rounded">
              <h3 className="font-bold">{item.name}</h3>
              <p>Sektör: {item.sector}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}