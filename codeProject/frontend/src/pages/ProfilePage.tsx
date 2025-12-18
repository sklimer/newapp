import React from 'react';
import Profile from '../components/Profile';

const ProfilePage: React.FC = () => {
  return (
    <div className="profile-page">
      <h1>Your Profile</h1>
      <Profile />
    </div>
  );
};

export default ProfilePage;