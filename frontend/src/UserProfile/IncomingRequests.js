import React from "react";
import { Row, Col, Button, ListGroup, Spinner } from "react-bootstrap";

import api from "../API";
import AppContext from "../App/AppContext";
import { Centered } from "../Common";
import ShortUserProfile from "./ShortUserProfile";

class IncomingRequests extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      incomingRequests: [],
    };
  }

  async componentDidMount() {
    const response = await api.fetchPendingProfiles();

    if (response.status === 200) {
      const json = await response.json();

      this.setState({
        isLoading: false,
        incomingRequests: json,
      });
    }

    this.context.checkLoggedIn();
  }

  async acceptRequest(i) {
    const response = await api.acceptRequest(
      this.state.incomingRequests[i].username
    );

    if (response.status === 200) {
      this.setState({
        incomingRequests: this.state.incomingRequests.filter(
          (req, j) => j !== i
        ),
      });
    }

    this.context.checkLoggedIn();
  }

  async rejectRequest(i) {
    const response = await api.rejectRequest(
      this.state.incomingRequests[i].username
    );

    if (response.status === 200) {
      this.setState({
        incomingRequests: this.state.incomingRequests.filter(
          (req, j) => j !== i
        ),
      });
    }

    this.context.checkLoggedIn();
  }

  render() {
    if (this.state.isLoading) {
      return (
        <Centered>
          <Spinner animation="border" />
        </Centered>
      );
    }

    return (
      <>
        {this.state.incomingRequests.length === 0 ? (
          <Centered>You don't have any incoming followers</Centered>
        ) : (
          <ListGroup>
            {this.state.incomingRequests.map((profile, i) => (
              <ListGroup.Item
                key={profile.username}
                className="mb-2 mt-2 border"
              >
                <Row>
                  <Col>
                    <ShortUserProfile profile={profile} />
                  </Col>
                  <Col xs="auto" className="d-flex align-items-center">
                    <Button
                      variant="dark"
                      className="p-1"
                      onClick={this.acceptRequest.bind(this, i)}
                    >
                      Accept
                    </Button>
                  </Col>
                  <Col xs="auto" className="d-flex align-items-center">
                    <Button
                      variant="dark"
                      className="p-1"
                      onClick={this.rejectRequest.bind(this, i)}
                    >
                      Reject
                    </Button>
                  </Col>
                </Row>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </>
    );
  }
}

export default IncomingRequests;
