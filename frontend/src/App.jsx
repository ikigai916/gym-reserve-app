import { useState, useEffect } from 'react';
import { getUserId, setUserId } from './utils/userStorage';

const API_BASE = '/api';

function App() {
  const [activeTab, setActiveTab] = useState('reserve');
  const [selectedDate, setSelectedDate] = useState('');
  const [timeSlots, setTimeSlots] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [userId, setUserIdState] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // マイページ用のフォーム状態
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editPhone, setEditPhone] = useState('');

  // 今日の日付を YYYY-MM-DD 形式で取得
  const getToday = () => {
    return new Date().toISOString().split('T')[0];
  };

  // 初期化時に今日の日付を設定、ユーザーIDを読み込む
  useEffect(() => {
    setSelectedDate(getToday());
    const savedUserId = getUserId();
    if (savedUserId) {
      setUserIdState(savedUserId);
      loadUser(savedUserId);
    }
  }, []);

  // ユーザー情報を読み込む
  const loadUser = async (id) => {
    try {
      const response = await fetch(`${API_BASE}/users/${id}`);
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setEditName(userData.name);
        setEditEmail(userData.email || '');
        setEditPhone(userData.phone || '');
      }
    } catch (err) {
      console.error('ユーザー情報の読み込みに失敗しました', err);
    }
  };

  // 日付またはユーザーIDが変更されたら時間枠を取得
  useEffect(() => {
    if (selectedDate) {
      loadTimeSlots(selectedDate);
    }
  }, [selectedDate, userId]);

  // マイ予約タブがアクティブになったら予約を読み込む
  useEffect(() => {
    if (activeTab === 'my-reservations' && userId) {
      loadMyReservations();
    }
  }, [activeTab, userId]);

  // マイページタブがアクティブになったらユーザー情報を読み込む
  useEffect(() => {
    if (activeTab === 'mypage' && userId) {
      loadUser(userId);
    }
  }, [activeTab, userId]);

  // 時間枠を読み込む
  const loadTimeSlots = async (date) => {
    setLoading(true);
    setError('');
    try {
      const url = userId 
        ? `${API_BASE}/time-slots/${date}?userId=${encodeURIComponent(userId)}`
        : `${API_BASE}/time-slots/${date}`;
      const response = await fetch(url);
      const data = await response.json();
      setTimeSlots(data.timeSlots || []);
    } catch (err) {
      setError('時間枠の読み込みに失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 自分の予約を読み込む
  const loadMyReservations = async () => {
    if (!userId) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/reservations?userId=${encodeURIComponent(userId)}`);
      const data = await response.json();
      setReservations(data.reservations || []);
    } catch (err) {
      setError('予約の読み込みに失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ユーザーを作成または取得
  const ensureUser = async (name, email = '', phone = '') => {
    if (userId) {
      return userId;
    }

    try {
      const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          phone: phone.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'ユーザー作成に失敗しました');
      }

      const newUserId = data.id;
      setUserId(newUserId);
      setUserIdState(newUserId);
      setUser(data);
      setEditName(data.name);
      setEditEmail(data.email || '');
      setEditPhone(data.phone || '');
      return newUserId;
    } catch (err) {
      throw err;
    }
  };

  // 予約を作成
  const createReservation = async (timeSlot) => {
    if (!userId && !user) {
      setError('まずマイページでユーザー情報を登録してください');
      setActiveTab('mypage');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let currentUserId = userId;
      
      // ユーザーIDが存在しない場合（初回予約時など）
      if (!currentUserId) {
        if (!user) {
          setError('ユーザー情報がありません。マイページで登録してください。');
          setActiveTab('mypage');
          return;
        }
        currentUserId = await ensureUser(user.name, user.email, user.phone);
      }
      
      const response = await fetch(`${API_BASE}/reservations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: currentUserId,
          date: selectedDate,
          timeSlot,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || '予約に失敗しました');
        return;
      }

      setSuccess(`予約が完了しました: ${selectedDate} ${timeSlot}`);
      // 時間枠を再読み込み
      loadTimeSlots(selectedDate);
      // マイ予約も再読み込み
      if (activeTab === 'my-reservations') {
        loadMyReservations();
      }
    } catch (err) {
      setError(err.message || '予約に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 予約をキャンセル
  const cancelReservation = async (reservationId) => {
    if (!confirm('この予約をキャンセルしますか？')) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const url = userId 
        ? `${API_BASE}/reservations/${reservationId}?userId=${encodeURIComponent(userId)}`
        : `${API_BASE}/reservations/${reservationId}`;
      
      const response = await fetch(url, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'キャンセルに失敗しました');
        return;
      }

      setSuccess('予約をキャンセルしました');
      // 予約一覧を再読み込み
      loadMyReservations();
      // 時間枠も再読み込み
      loadTimeSlots(selectedDate);
    } catch (err) {
      setError('キャンセルに失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ユーザー情報を保存
  const saveUserInfo = async () => {
    if (!editName.trim()) {
      setError('名前は必須です');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let currentUserId = userId;
      
      // ユーザーが存在しない場合は新規作成
      if (!currentUserId) {
        currentUserId = await ensureUser(editName, editEmail, editPhone);
      } else {
        // 既存ユーザーの場合は更新
        const response = await fetch(`${API_BASE}/users/${currentUserId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: editName.trim(),
            email: editEmail.trim(),
            phone: editPhone.trim(),
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          setError(data.error || '更新に失敗しました');
          return;
        }

        setUser(data);
      }

      setSuccess('ユーザー情報を保存しました');
    } catch (err) {
      setError(err.message || '保存に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>🏋️ ジム予約管理システム</h1>
        </div>
      </header>

      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'reserve' ? 'active' : ''}`}
            onClick={() => setActiveTab('reserve')}
          >
            予約する
          </button>
          <button
            className={`tab ${activeTab === 'my-reservations' ? 'active' : ''}`}
            onClick={() => setActiveTab('my-reservations')}
          >
            マイ予約
          </button>
          <button
            className={`tab ${activeTab === 'mypage' ? 'active' : ''}`}
            onClick={() => setActiveTab('mypage')}
          >
            マイページ
          </button>
        </div>

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        {activeTab === 'reserve' && (
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem' }}>予約する</h2>

            {!user && (
              <div className="error" style={{ marginBottom: '1rem' }}>
                予約するには、まずマイページでユーザー情報を登録してください。
              </div>
            )}

            {user && (
              <div style={{ marginBottom: '1.5rem', padding: '0.75rem', backgroundColor: '#e8f4f8', borderRadius: '4px' }}>
                <strong>ログイン中:</strong> {user.name}
              </div>
            )}

            <div className="form-group date-selector">
              <label htmlFor="date">予約日</label>
              <input
                id="date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={getToday()}
              />
            </div>

            {loading && <div className="loading">読み込み中...</div>}

            {!loading && (
              <div>
                <h3 style={{ marginBottom: '1rem' }}>
                  {selectedDate} の時間枠
                </h3>
                {timeSlots.length === 0 ? (
                  <div className="empty">時間枠が見つかりません</div>
                ) : (
                  <div className="time-slots">
                    {timeSlots.map((item, index) => {
                      return (
                        <div
                          key={index}
                          className={`time-slot ${
                            item.available
                              ? 'available'
                              : item.isMyReservation
                              ? 'my-reservation'
                              : 'reserved'
                          }`}
                          onClick={() => item.available && createReservation(item.slot)}
                          style={{ cursor: item.available ? 'pointer' : 'default' }}
                        >
                          <div className="time">{item.slot}</div>
                          <div className="status">
                            {item.available
                              ? '予約可能'
                              : item.isMyReservation
                              ? 'あなたの予約'
                              : '満席'}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'my-reservations' && (
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem' }}>マイ予約</h2>

            {!user && (
              <div className="error">
                予約を表示するには、まずマイページでユーザー情報を登録してください。
              </div>
            )}

            {user && (
              <>
                {loading && <div className="loading">読み込み中...</div>}

                {!loading && (
                  <>
                    {reservations.length === 0 ? (
                      <div className="empty">予約がありません</div>
                    ) : (
                      <div className="reservations-list">
                        {reservations.map((reservation) => (
                          <div key={reservation.id} className="reservation-item">
                            <div className="reservation-info">
                              <div className="date">{reservation.date}</div>
                              <div className="time">{reservation.timeSlot}</div>
                              <div className="name">{reservation.name}</div>
                            </div>
                            <button
                              className="btn btn-danger"
                              onClick={() => cancelReservation(reservation.id)}
                            >
                              キャンセル
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'mypage' && (
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem' }}>マイページ</h2>
            <p style={{ marginBottom: '1.5rem', color: '#666' }}>
              個人情報を入力・編集してください。初回は新規登録、2回目以降は更新されます。
            </p>

            <div className="form-group">
              <label htmlFor="edit-name">お名前 *</label>
              <input
                id="edit-name"
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="例: 山田太郎"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="edit-email">メールアドレス</label>
              <input
                id="edit-email"
                type="email"
                value={editEmail}
                onChange={(e) => setEditEmail(e.target.value)}
                placeholder="例: yamada@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="edit-phone">電話番号</label>
              <input
                id="edit-phone"
                type="tel"
                value={editPhone}
                onChange={(e) => setEditPhone(e.target.value)}
                placeholder="例: 090-1234-5678"
              />
            </div>

            {loading && <div className="loading">保存中...</div>}

            <button
              className="btn btn-primary"
              onClick={saveUserInfo}
              disabled={loading || !editName.trim()}
            >
              保存
            </button>

            {user && (
              <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                <h3 style={{ marginBottom: '0.5rem' }}>登録情報</h3>
                <p><strong>ユーザーID:</strong> {user.id}</p>
                <p><strong>登録日:</strong> {new Date(user.createdAt).toLocaleString('ja-JP')}</p>
                {user.updatedAt && (
                  <p><strong>更新日:</strong> {new Date(user.updatedAt).toLocaleString('ja-JP')}</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

