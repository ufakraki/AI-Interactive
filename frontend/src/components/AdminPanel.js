// frontend/src/components/AdminPanel.js
import React, { useEffect, useState } from 'react';
import api from '../api/axios';

const UserList = ({ companyId, canEdit }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [passwordForm, setPasswordForm] = useState({ new_password: '', confirm_password: '' });
  const [passwordError, setPasswordError] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await api.get('/users/');
        setUsers(response.data.filter(u => u.company === companyId));
      } catch (e) {
        setUsers([]);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, [companyId]);

  const handleDelete = async (id) => {
    if (!window.confirm('Kullanıcı silinsin mi?')) return;
    await api.delete(`/users/${id}/`);
    setUsers(users.filter(u => u.id !== id));
  };

  const handlePasswordChange = async (userId) => {
    try {
      setPasswordError('');
      if (passwordForm.new_password !== passwordForm.confirm_password) {
        setPasswordError('Şifreler eşleşmiyor');
        return;
      }
      await api.post(`/users/${userId}/set_password/`, passwordForm);
      setSelectedUser(null);
      setPasswordForm({ new_password: '', confirm_password: '' });
      alert('Şifre başarıyla değiştirildi');
    } catch (error) {
      setPasswordError(error.response?.data?.message || 'Şifre değiştirme başarısız');
    }
  };

  if (loading) return <div>Kullanıcılar yükleniyor...</div>;
  return (
    <div>
      <h5>Kullanıcılar</h5>
      <ul className="list-group">
        {users.map(user => (
          <li key={user.id} className="list-group-item">
            <div className="d-flex justify-content-between align-items-center">
              {user.first_name} {user.last_name} ({user.role})
              <div>
                {canEdit && (
                  <>
                    <button 
                      className="btn btn-primary btn-sm me-2" 
                      onClick={() => setSelectedUser(user.id)}
                    >
                      Şifre Değiştir
                    </button>
                    {user.role === 'user' && (
                      <button 
                        className="btn btn-danger btn-sm" 
                        onClick={() => handleDelete(user.id)}
                      >
                        Sil
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
            {selectedUser === user.id && (
              <div className="mt-2">
                <div className="mb-2">
                  <input
                    type="password"
                    className="form-control mb-2"
                    placeholder="Yeni Şifre"
                    value={passwordForm.new_password}
                    onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                  />
                  <input
                    type="password"
                    className="form-control mb-2"
                    placeholder="Şifreyi Tekrar Girin"
                    value={passwordForm.confirm_password}
                    onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                  />
                </div>
                {passwordError && <div className="text-danger mb-2">{passwordError}</div>}
                <button 
                  className="btn btn-success btn-sm me-2"
                  onClick={() => handlePasswordChange(user.id)}
                >
                  Şifreyi Kaydet
                </button>
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    setSelectedUser(null);
                    setPasswordForm({ new_password: '', confirm_password: '' });
                    setPasswordError('');
                  }}
                >
                  İptal
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

const UserForm = ({ companies, onUserCreated, canCreateAdmin, defaultCompany }) => {
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', role: 'user', company: defaultCompany });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.post('/users/', form);
      setForm({ first_name: '', last_name: '', email: '', role: 'user', company: defaultCompany });
      onUserCreated();
    } catch (err) {
      setError('Kullanıcı eklenemedi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-3">
      <div className="row g-2">
        <div className="col">
          <input name="first_name" value={form.first_name} onChange={handleChange} className="form-control" placeholder="Ad" required />
        </div>
        <div className="col">
          <input name="last_name" value={form.last_name} onChange={handleChange} className="form-control" placeholder="Soyad" required />
        </div>
        <div className="col">
          <input name="email" value={form.email} onChange={handleChange} className="form-control" placeholder="E-posta" required />
        </div>
        <div className="col">
          <select name="role" value={form.role} onChange={handleChange} className="form-select">
            <option value="user">User</option>
            {canCreateAdmin && <option value="company_admin">Company Admin</option>}
          </select>
        </div>
        <div className="col">
          <select name="company" value={form.company} onChange={handleChange} className="form-select" required>
            <option value="">Firma Seç</option>
            {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="col-auto">
          <button type="submit" className="btn btn-success" disabled={loading}>{loading ? 'Ekleniyor...' : 'Ekle'}</button>
        </div>
      </div>
      {error && <div className="text-danger mt-1">{error}</div>}
    </form>
  );
};

const AdminPanel = ({ user }) => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [refresh, setRefresh] = useState(false);
  const isSuperAdmin = user.role === 'superadmin';
  const isCompanyAdmin = user.role === 'company_admin';

  useEffect(() => {
    const fetchCompanies = async () => {
      const response = await api.get('/companies/');
      setCompanies(response.data);
      if (!selectedCompany && response.data.length > 0) {
        setSelectedCompany(isSuperAdmin ? response.data[0].id : user.company);
      }
    };
    fetchCompanies();
  }, [user, isSuperAdmin, selectedCompany]);

  const handleCompanyChange = e => setSelectedCompany(Number(e.target.value));
  const handleUserCreated = () => setRefresh(r => !r);

  return (
    <div>
      <h2 className="mb-3">Kullanıcı Yönetimi</h2>
      {isSuperAdmin && (
        <div className="mb-3">
          <select className="form-select" value={selectedCompany || ''} onChange={handleCompanyChange}>
            {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
      )}
      <UserForm
        companies={isSuperAdmin ? companies : companies.filter(c => c.id === user.company)}
        onUserCreated={handleUserCreated}
        canCreateAdmin={isSuperAdmin}
        defaultCompany={isSuperAdmin ? selectedCompany : user.company}
      />
      {selectedCompany && <UserList key={selectedCompany + refresh} companyId={selectedCompany} canEdit={isSuperAdmin || isCompanyAdmin} />}
    </div>
  );
};

export default AdminPanel;