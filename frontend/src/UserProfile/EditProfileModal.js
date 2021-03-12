import React from "react";
import { Modal, Form, Button } from "react-bootstrap";
import { Redirect } from "react-router-dom";

import api from "../API";
import AppContext from "../App/AppContext";

class EditProfileModal extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      profile: {},
      errors: {},
      redirectToNewProfile: false,
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  clearState() {
    this.setState({
      profile: {},
      errors: {},
      redirectToNewProfile: false,
    });
  }

  syncState() {
    this.setState({
      profile: { ...this.props.profile, avatar: null },
      errors: {},
      redirectToNewProfile: false,
    });
  }

  componentDidUpdate(prevProps) {
    if (this.props.show !== prevProps.show) {
      if (this.props.show === false) {
        this.clearState();
      } else {
        this.syncState();
      }
    }
  }

  handleChange(e) {
    const name = e.target.id;
    const value =
      e.target.type === "file"
        ? e.target.files[0]
        : e.target.type === "checkbox"
        ? e.target.checked
        : e.target.value;

    this.setState({ profile: { ...this.state.profile, [name]: value } });
  }

  async handleSubmit(e) {
    e.preventDefault();

    const response = await api.patchMyProfile(this.state.profile);

    if (response.status === 200) {
      const newProfile = await response.json();

      if (this.props.profile.username !== newProfile.username) {
        this.setState({ redirectToNewProfile: true });
      } else {
        this.props.toggleModal();
        this.props.updateParentProfile(newProfile);
      }
    } else if (response.status === 400) {
      const errors = await response.json();

      this.setState({ errors: errors });
    }

    this.context.checkLoggedIn();
  }

  render() {
    if (this.state.redirectToNewProfile) {
      return <Redirect to={`/profiles/${this.state.profile.username}`} />;
    }

    return (
      <Modal
        show={this.props.show}
        size="lg"
        aria-labelledby="edit-modal"
        centered
      >
        <Modal.Header closeButton onClick={this.props.toggleModal}>
          <Modal.Title id="edit-modal">Edit profile</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={this.handleSubmit}>
            <Form.Group controlId="avatar">
              <Form.File label="Avatar" onChange={this.handleChange} />
              <Form.Text className="text-danger">
                {this.state.errors.avatar}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="username">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                placeholder="Username"
                value={this.state.profile.username}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.errors.username}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="first_name">
              <Form.Label>First Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="First name"
                value={this.state.profile.first_name}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.errors.first_name}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="last_name">
              <Form.Label>Last Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Last name"
                value={this.state.profile.last_name}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.errors.last_name}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="description">
              <Form.Label>Description</Form.Label>
              <Form.Control
                type="text"
                as="textarea"
                placeholder="Description"
                value={this.state.profile.description}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.errors.description}
              </Form.Text>
            </Form.Group>

            <Form.Group controlId="is_opened">
              <Form.Check
                type="checkbox"
                label="Is profile open?"
                checked={this.state.profile.is_opened}
                onChange={this.handleChange}
              />
              <Form.Text className="text-danger">
                {this.state.errors.is_opened}
              </Form.Text>
            </Form.Group>

            <Button variant="dark" type="submit">
              Submit
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    );
  }
}

export default EditProfileModal;
