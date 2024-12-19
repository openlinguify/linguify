import React from "react";

const HeaderProfile = ({
  username,
  profilePicture,
}: {
  username: string;
  profilePicture: string;
}) => {
  return (
    <div className="d-flex align-items-center p-3 bg-light shadow">
      <img
        src={profilePicture}
        alt={username}
        className="rounded-circle"
        style={{ width: "50px", height: "50px", marginRight: "10px" }}
      />
      <h5 className="mb-0">{username}</h5>
    </div>
  );
};

export default HeaderProfile;
