import React from "react";
import { Link, Redirect } from "react-router-dom";
import { Form, Button } from "react-bootstrap";

import config from "../Config";
import api from "../API";
import AppContext from "../App/AppContext";
import Centered from "./CenteredComponent";

class Login extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      error: false,
      isSubmited: false,
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(e) {
    this.setState({ [e.target.id]: e.target.value });
  }

  async handleSubmit(e) {
    e.preventDefault();

    const response = await api.fetchTokens(
      this.state.username,
      this.state.password
    );

    if (response.status === 200) {
      const json = await response.json();
      localStorage.setItem(config.accessToken, json.access);
      localStorage.setItem(config.refreshToken, json.refresh);

      this.context.checkLoggedIn();
      this.setState({ isSubmited: true });
    } else if (response.status === 401) {
      this.setState({ error: true });
    }
  }

  render() {
    if (this.state.isSubmited) {
      return (
        <Redirect
          to={
            this.props.redirectTo ||
            new URLSearchParams(this.props.location.search).get("redirect") ||
            "/profile"
          }
        />
      );
    }

    return (
      <Centered>
        <div style={{ minWidth: "300px" }}>
          <div className="text-center">Login</div>

          <Form onSubmit={this.handleSubmit}>
            <Form.Group controlId="username">
              <Form.Label>Username</Form.Label>
              <Form.Control
                required
                type="text"
                placeholder="Username"
                value={this.state.username}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.error &&
                  "No active account found with the given credentials"}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="password">
              <Form.Label>Password</Form.Label>
              <Form.Control
                required
                type="password"
                placeholder="Password"
                value={this.state.password}
                onChange={this.handleChange}
              />
            </Form.Group>

            <Button variant="dark" type="submit">
              Submit
            </Button>
          </Form>

          <div>
            Don't have an account yet? <Link to="/signup">Register</Link> now!
          </div>
        </div>
      </Centered>
    );
  }
}

export default Login;
