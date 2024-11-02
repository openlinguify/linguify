import React from 'react';
import { Dropdown, DropdownButton } from 'react-bootstrap';
import { FaBell, FaSearch, FaCog } from 'react-icons/fa'; // Import icons

const HeaderProfile = ({ username, profilePicture }) => {
  return (
    <header className="d-flex justify-content-between align-items-center p-3 bg-primary text-white shadow">
      {/* Logo and Title */}
      <div className="d-flex align-items-center">
        <img
          src="/static/images/logos/layout.png" // Replace with your logo path
          alt="Linguify Logo"
          className="me-2"
          style={{ width: '40px', height: '40px' }}
        />
        <h1 className="m-0">Linguify</h1>
      </div>

      {/* Search Bar */}
      <div className="d-flex align-items-center">
        <div className="input-group me-3">
          <input
            type="text"
            className="form-control"
            placeholder="Search..."
            aria-label="Search"
            aria-describedby="search-icon"
          />
          <span className="input-group-text bg-white text-primary" id="search-icon">
            <FaSearch />
          </span>
        </div>

        {/* Notification Bell */}
        <button
          className="btn btn-link text-white position-relative me-3"
          style={{ fontSize: '1.5rem' }}
          aria-label="Notifications"
        >
          <FaBell />
          <span
            className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
            style={{ fontSize: '0.75rem' }}
          >
            3 {/* Example notification count */}
          </span>
        </button>

        {/* User Profile */}
        <div className="d-flex align-items-center">
          <span className="me-3 fw-bold">{username}</span>
          {profilePicture ? (
            <img
              src="/static/media/images/avatars/logo-moi.png"
              alt={`${username}'s profile`}
              className="rounded-circle border border-light"
              style={{ width: '45px', height: '45px', objectFit: 'cover' }}
            />
          ) : (
            <div
              className="rounded-circle bg-light text-dark d-flex justify-content-center align-items-center"
              style={{ width: '45px', height: '45px' }}
            >
              {username.charAt(0).toUpperCase()}
            </div>
          )}

          {/* User Dropdown Menu */}
          <DropdownButton
            id="dropdown-user-actions"
            variant="secondary"
            title=""
            className="ms-3"
          >
            <Dropdown.Item href="/profile">
              <FaCog className="me-2" /> Profile
            </Dropdown.Item>
            <Dropdown.Item href="/settings">
              <FaCog className="me-2" /> Settings
            </Dropdown.Item>
            <Dropdown.Divider />
            <Dropdown.Item href="/logout">
              <FaCog className="me-2" /> Logout
            </Dropdown.Item>
          </DropdownButton>
        </div>
      </div>
    </header>
  );
};

export default HeaderProfile;
