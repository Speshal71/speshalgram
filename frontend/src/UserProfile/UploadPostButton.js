import React from "react";
import { Card, Button, Modal, Form } from "react-bootstrap";

import api from "../API";
import AppContext from "../App/AppContext";
import { PlusSquare } from "../Common/SVG";

class UploadPostButton extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      picture: null,
      description: null,
      pictureError: null,
      descriptionError: null,
    };

    this.toggleModal = this.toggleModal.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.uploadPost = this.uploadPost.bind(this);
  }

  toggleModal() {
    this.setState({ showModal: !this.state.showModal });
  }

  handleChange(e) {
    const name = e.target.id;
    const value = e.target.type === "file" ? e.target.files[0] : e.target.value;

    this.setState({ [name]: value });
  }

  async uploadPost(e) {
    e.preventDefault();

    const response = await api.uploadPost(
      this.state.picture,
      this.state.description
    );

    if (response.status === 201) {
      const newPost = await response.json();

      this.toggleModal();
      this.props.onUpload(newPost);
    } else {
      const errors = await response.json();

      this.setState({
        pictureError: errors.picture,
        descriptionError: errors.description,
      });
    }

    this.context.checkLoggedIn();
  }

  render() {
    return (
      <div>
        <Button
          className="justify-content-center text-center m-2 p-2"
          variant="transparent"
          as={Card}
          onClick={this.toggleModal}
        >
          <div>
            <PlusSquare width="32" height="32" />
          </div>
        </Button>

        <Modal
          show={this.state.showModal}
          size="lg"
          aria-labelledby="upload-modal"
          centered
        >
          <Modal.Header closeButton onClick={this.toggleModal}>
            <Modal.Title id="upload-modal">Upload new post</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit={this.uploadPost}>
              <Form.Group controlId="picture">
                <Form.File
                  required
                  label="Choose a picture for the post"
                  name="picture"
                  onChange={this.handleChange}
                />
                <Form.Text className="text-danger">
                  {this.state.pictureError}
                </Form.Text>
              </Form.Group>

              <Form.Group controlId="description">
                <Form.Label>Post description</Form.Label>
                <Form.Control
                  type="text"
                  as="textarea"
                  placeholder="Post description"
                  name="description"
                  value={this.state.description}
                  onChange={this.handleChange}
                />
                <Form.Text className="text-danger">
                  {this.state.descriptionError}
                </Form.Text>
              </Form.Group>

              <Button variant="dark" type="submit">
                Submit
              </Button>
            </Form>
          </Modal.Body>
        </Modal>
      </div>
    );
  }
}

export default UploadPostButton;
