import React, { useState } from 'react';

interface UserProfile {
  name: string;
  email: string;
  phone: string;
  address: string;
  bonusBalance: number;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>({
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1234567890',
    address: '123 Main St, New York, NY',
    bonusBalance: 15.50
  });
  
  const [editing, setEditing] = useState(false);
  const [tempProfile, setTempProfile] = useState<UserProfile>({...profile});

  const handleEdit = () => {
    setEditing(true);
    setTempProfile({...profile});
  };

  const handleSave = () => {
    setProfile({...tempProfile});
    setEditing(false);
  };

  const handleCancel = () => {
    setTempProfile({...profile});
    setEditing(false);
  };

  return (
    <div className="profile">
      <h2>Your Profile</h2>
      
      {editing ? (
        <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              value={tempProfile.name}
              onChange={(e) => setTempProfile({...tempProfile, name: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={tempProfile.email}
              onChange={(e) => setTempProfile({...tempProfile, email: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input
              id="phone"
              type="tel"
              value={tempProfile.phone}
              onChange={(e) => setTempProfile({...tempProfile, phone: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="address">Address</label>
            <textarea
              id="address"
              value={tempProfile.address}
              onChange={(e) => setTempProfile({...tempProfile, address: e.target.value})}
            />
          </div>
          
          <div className="form-actions">
            <button type="button" onClick={handleCancel}>Cancel</button>
            <button type="submit">Save Changes</button>
          </div>
        </form>
      ) : (
        <div className="profile-info">
          <div className="info-item">
            <label>Name:</label>
            <span>{profile.name}</span>
          </div>
          
          <div className="info-item">
            <label>Email:</label>
            <span>{profile.email}</span>
          </div>
          
          <div className="info-item">
            <label>Phone:</label>
            <span>{profile.phone}</span>
          </div>
          
          <div className="info-item">
            <label>Address:</label>
            <span>{profile.address}</span>
          </div>
          
          <div className="info-item bonus-balance">
            <label>Bonus Balance:</label>
            <span className="bonus-amount">${profile.bonusBalance.toFixed(2)}</span>
          </div>
          
          <button className="edit-btn" onClick={handleEdit}>Edit Profile</button>
        </div>
      )}
      
      <div className="bonus-info">
        <h3>Your Bonuses</h3>
        <p>You currently have <strong>${profile.bonusBalance.toFixed(2)}</strong> in bonus credits.</p>
        <p>Earn more bonuses by placing orders or referring friends!</p>
      </div>
    </div>
  );
};

export default Profile;