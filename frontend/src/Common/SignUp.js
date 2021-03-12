import React from "react";
import { Redirect } from "react-router-dom";
import { Form, Button } from "react-bootstrap";

import api from "../API";
import AppContext from "../App/AppContext";
import Centered from "./CenteredComponent";

class SignUp extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      repeatedPassword: "",
      errors: {},
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

    if (this.state.password !== this.state.repeatedPassword) {
      this.setState({
        errors: {
          repeatedPassword: "passwords must much",
        },
      });
      return;
    }

    const response = await api.registerUser(
      this.state.username,
      this.state.password
    );

    if (response.status === 201) {
      this.setState({ isSubmited: true });
    } else if (response.status === 400) {
      const json = await response.json();

      this.setState({
        errors: {
          username: json.username,
          password: json.password,
        },
      });
    }

    this.context.checkLoggedIn();
  }

  render() {
    if (this.state.isSubmited) {
      return <Redirect to="/login" />;
    }

    return (
      <Centered>
        <div style={{ minWidth: "300px" }}>
          <div className="text-center">Sign Up</div>

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
                {this.state.errors.username}
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
              <Form.Text className="text-danger">
                {this.state.errors.password}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="repeatedPassword">
              <Form.Label>Repeat Your Password</Form.Label>
              <Form.Control
                required
                type="password"
                placeholder="Repeat Password"
                value={this.state.repeatedPassword}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.errors.repeatedPassword}
              </Form.Text>
            </Form.Group>

            <Button variant="dark" type="submit">
              Submit
            </Button>
          </Form>
        </div>
      </Centered>
    );
  }
}

export default SignUp;
