import React, { useState, useEffect } from 'react';
import { userApi } from '../api/api';

interface UserProfile {
  id: number;
  first_name?: string;
  username?: string;
  bonus_balance: number;
  referral_code?: string;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { telegramId, loading: telegramLoading, error: telegramError } = useTelegramId();
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await userApi.getUserProfile(telegramId);
        setProfile(response.data);
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError('Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="profile">
        <h2>Your Profile</h2>
        <div className="loading">Loading profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile">
        <h2>Your Profile</h2>
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile">
        <h2>Your Profile</h2>
        <div className="error">No profile data found</div>
      </div>
    );
  }

  // Determine display name based on priority: first_name > username > "Гость"
  const displayName = profile.first_name || profile.username || "Гость";

  return (
    <div className="profile">
      <h2>Your Profile</h2>

      <div className="profile-info">
        <div className="info-item">
          <label>Name:</label>
          <span>{displayName}</span>
        </div>

        <div className="info-item">
          <label>ID:</label>
          <span>{profile.id}</span>
        </div>

        <div className="info-item">
          <label>Balance:</label>
          <span>{profile.bonus_balance}</span>
        </div>

        <div className="info-item">
          <label>Bonuses:</label>
          <span>{profile.bonus_balance}</span>
        </div>

        <div className="info-item">
          <label>Referral Code:</label>
          <span>{profile.referral_code || "Not available"}</span>
        </div>
      </div>
    </div>
  );
};

export default Profile;