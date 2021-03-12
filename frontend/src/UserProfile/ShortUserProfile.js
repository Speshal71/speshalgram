import React from "react";
import { Link } from "react-router-dom";
import { Media } from "react-bootstrap";

import config from "../Config";

function ShortUserProfile({ profile, useName = true }) {
  return (
    <Link className="plain-text" to={`/profiles/${profile.username}`}>
      <Media className="align-items-center">
        <img
          className="mr-3 ml-2"
          width={config.imgSize.avatar.small}
          height={config.imgSize.avatar.small}
          src={profile.avatar}
          alt={`${profile.username} avatar`}
        />
        <Media.Body>
          <div className="font-weight-bold">
            <span>{profile.username}</span>
          </div>
          {useName && (
            <div className="font-italic">
              <span>
                {profile.first_name} {profile.last_name}
              </span>
            </div>
          )}
        </Media.Body>
      </Media>
    </Link>
  );
}

export default ShortUserProfile;
