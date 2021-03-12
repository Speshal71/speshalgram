import React from "react";

function Centered(props) {
  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{ minHeight: "500px" }}
      {...props}
    />
  );
}

export default Centered;
