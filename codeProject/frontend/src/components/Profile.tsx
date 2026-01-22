import React, { useState, useEffect } from 'react';
import { userApi } from '../api/api';
import { useTelegramId } from '../hooks/useTelegramId';

interface UserProfile {
  id: number;
  first_name?: string;
  username?: string;
  bonus_balance: number;
  referral_code?: string;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);

  const { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();

  console.log('profile tsx { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();:', telegramId);
  console.log('profile tsx telegramError:', telegramError);

  useEffect(() => {
    const fetchProfile = async () => {
      if (telegramId) {
        try {
          setProfileLoading(true);
          setProfileError(null);
          console.log(`Fetching profile for telegramId: ${telegramId}`);
          const response = await userApi.getUserProfile(telegramId);
          console.log(`Profile response.data:`, response.data);
          setProfile(response.data);
        } catch (err) {
          console.error('Error fetching profile:', err);
          setProfileError('Не удалось загрузить профиль');
        } finally {
          setProfileLoading(false);
        }
      }
    };

    fetchProfile();
  }, [telegramId]);

  // Если идет загрузка Telegram ID
  if (telegramLoading) {
    return (
      <div className="profile">
        <h2>Ваш профиль</h2>
        <div className="loading">Инициализация пользователя...</div>
      </div>
    );
  }

  // Если ошибка получения Telegram ID, но у нас есть telegramId (TEST_MODE)
  // или если нет telegramId совсем
  if (!telegramId) {
    return (
      <div className="profile">
        <h2>Ваш профиль</h2>
        <div className="error">
          {telegramError || 'Не удалось получить ID пользователя'}
          {telegramError && <p style={{ marginTop: '10px', fontSize: '14px' }}>
            Работаем в тестовом режиме. Профиль недоступен.
          </p>}
        </div>
      </div>
    );
  }

  // Если загружается профиль с сервера
  if (profileLoading) {
    return (
      <div className="profile">
        <h2>Ваш профиль</h2>
        <div className="loading">Загрузка профиля...</div>
        <div className="debug-info" style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
          Telegram ID: {telegramId}
        </div>
      </div>
    );
  }

  // Если ошибка загрузки профиля
  if (profileError) {
    return (
      <div className="profile">
        <h2>Ваш профиль</h2>
        <div className="error">
          {profileError}
          <div className="debug-info" style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
            Telegram ID: {telegramId}
            {telegramError && <div>Telegram WebApp initData недоступен (тестовый режим)</div>}
          </div>
        </div>
      </div>
    );
  }

  // Если профиль не загружен
  if (!profile) {
    return (
      <div className="profile">
        <h2>Ваш профиль</h2>
        <div className="error">
          Данные профиля не найдены
          <div className="debug-info" style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
            Telegram ID: {telegramId}
          </div>
        </div>
      </div>
    );
  }

  // Определяем отображаемое имя по приоритету: first_name > username > "Гость"
  const displayName = profile.first_name || profile.username || "Гость";

  return (
    <div className="profile">
      <h2>Ваш профиль</h2>

      {telegramError && (
        <div className="warning-message" style={{
          background: '#fff3cd',
          border: '1px solid #ffeaa7',
          padding: '10px',
          borderRadius: '4px',
          marginBottom: '15px',
          fontSize: '14px'
        }}>
          ⚠️ Работаем в тестовом режиме. Telegram WebApp initData недоступен.
        </div>
      )}

      <div className="profile-info">
        <div className="info-item">
          <label>Имя:</label>
          <span>{displayName}</span>
        </div>

        <div className="info-item">
          <label>Telegram ID:</label>
          <span>{telegramId}</span>
        </div>

        <div className="info-item">
          <label>ID в системе:</label>
          <span>{profile.id}</span>
        </div>

        <div className="info-item">
          <label>Баланс бонусов:</label>
          <span>{profile.bonus_balance} баллов</span>
        </div>

        {profile.referral_code && (
          <div className="info-item">
            <label>Реферальный код:</label>
            <span>{profile.referral_code}</span>
          </div>
        )}
      </div>

      {/* Дополнительная информация для отладки */}
      <details className="debug-info" style={{ marginTop: '20px', fontSize: '12px' }}>
        <summary>Информация для отладки</summary>
        <div>
          <p><strong>Telegram ID:</strong> {telegramId}</p>
          <p><strong>Telegram Error:</strong> {telegramError || 'нет'}</p>
          <p><strong>Данные профиля:</strong> {JSON.stringify(profile, null, 2)}</p>
        </div>
      </details>
    </div>
  );
};

export default Profile;