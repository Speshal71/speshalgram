import React from "react";
import {
  Navbar,
  Dropdown,
  Form,
  FormControl,
  Container,
  Row,
  Col,
} from "react-bootstrap";
import { NavLink } from "react-router-dom";

import api from "../API";
import { XSquare } from "../Common/SVG";
import { ShortUserProfile } from "../UserProfile";
import AppContext from "./AppContext";

import "./Header.css";

class SuggestUserInput extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      showDropdown: false,
      username: "",
      users: [],
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleToggle = this.handleToggle.bind(this);
    this.preventPropagationOnClose = this.preventPropagationOnClose.bind(this);
  }

  async handleChange(e) {
    this.setState({ username: e.target.value });

    if (e.target.value.length > 0) {
      const response = await api.fetchSuggestedUsers(e.target.value);

      if (response.status === 200) {
        const json = await response.json();
        this.setState({
          users: json,
        });
      }

      this.context.checkLoggedIn();
    } else {
      this.setState({
        users: [],
      });
    }
  }

  handleToggle(isOpen, event, metadata) {
    if (this.state.showDropdown !== isOpen) {
      if (isOpen === false && metadata.source === "click") {
        return;
      }
    }
    this.setState({ showDropdown: isOpen });
  }

  preventPropagationOnClose(e) {
    // for some reason click event gets fired twice on close
    // where second event is set to false wtf?
    if (e.currentTarget.className.includes("show")) {
      e.stopPropagation();
    }
  }

  render() {
    return (
      <Dropdown
        as="nav"
        className="w-100"
        show={this.state.showDropdown}
        onToggle={this.handleToggle}
        onClick={this.preventPropagationOnClose}
      >
        <Dropdown.Toggle className="w-100" as={Form} id="search-user-dropdown">
          <FormControl
            className="w-100"
            type="text"
            placeholder="Search user"
            value={this.state.username}
            onChange={this.handleChange}
          />
        </Dropdown.Toggle>

        {this.state.username.length > 0 && (
          <Dropdown.Menu className="w-100">
            {this.state.users.length === 0 ? (
              <Dropdown.Item
                as="div"
                className="d-flex justify-content-center"
                key="not-found"
                disabled
              >
                <XSquare width="25" height="25" /> &nbsp; No such users found
              </Dropdown.Item>
            ) : (
              this.state.users.map((profile) => (
                <Dropdown.Item as="div" key={profile.username}>
                  <ShortUserProfile profile={profile} />
                </Dropdown.Item>
              ))
            )}
          </Dropdown.Menu>
        )}
      </Dropdown>
    );
  }
}

class Header extends React.Component {
  static contextType = AppContext;

  handleLogout(e) {
    e.preventDefault();
    api.logout();
    this.context.checkLoggedIn();
  }

  render() {
    return (
      <Navbar as="header" bg="primary-main" variant="dark" expand="sm">
        <Container>
          <Row className="w-100">
            <Col xs={6} sm={3}>
              <Navbar.Brand>Speshalgram</Navbar.Brand>
            </Col>

            <Col xs={6} className="d-sm-none">
              <div className="w-100 m-1 d-flex justify-content-end">
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
              </div>
            </Col>

            <Col sm={6}>
              <Navbar.Collapse id="basic-navbar-nav">
                <div className="w-100 m-1">
                  <SuggestUserInput />
                </div>
              </Navbar.Collapse>
            </Col>

            <Col sm={3}>
              <Navbar.Collapse id="basic-navbar-nav">
                <div className="w-100 m-1 d-flex justify-content-end">
                  {this.context.isLoggedIn ? (
                    <NavLink
                      className="nav-link link-dark"
                      to="/logout"
                      onClick={(e) => this.handleLogout(e)}
                    >
                      Logout
                    </NavLink>
                  ) : (
                    <NavLink className="nav-link link-dark" to="/login">
                      Login
                    </NavLink>
                  )}
                </div>
              </Navbar.Collapse>
            </Col>
          </Row>
        </Container>
      </Navbar>
    );
  }
}

export default Header;
