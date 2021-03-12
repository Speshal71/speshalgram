import React from "react";
import { Nav, Container } from "react-bootstrap";
import { NavLink } from "react-router-dom";

import { House, Easel } from "../Common/SVG";

function Navigation() {
  return (
    <Nav className="bg-primary-light">
      <Container className="d-flex flex-row justify-content-center">
        <NavLink className="nav-link link-dark" exact to="/profile">
          <House width="20" height="20" /> My Profile
        </NavLink>
        <NavLink className="nav-link link-dark" to="/feed">
          <Easel width="20" height="20" /> Feed
        </NavLink>
      </Container>
    </Nav>
  );
}

export default Navigation;
