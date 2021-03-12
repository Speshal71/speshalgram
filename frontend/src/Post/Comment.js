import React from "react";
import { Link } from "react-router-dom";

function Comment({ data, props }) {
  return (
    <div id="comment" {...props}>
      <Link className="plain-text" to={`/profiles/${data.owner.username}`}>
        <span id="comment-username" className="font-weight-bold">
          {data.owner.username}:{" "}
        </span>
      </Link>
      <span id="comment-content">{data.text}</span>
    </div>
  );
}

export default Comment;
