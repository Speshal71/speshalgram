import React from "react";
import { Modal, Spinner } from "react-bootstrap";
import InfiniteScroll from "react-infinite-scroll-component";

import api from "../API";
import AppContext from "../App/AppContext";
import { ShortUserProfile } from "../UserProfile";

class ScrollableProfileListModal extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      profiles: null,
      next: null,
    };

    this.fetchInitialProfiles = this.fetchInitialProfiles.bind(this);
    this.fetchMoreProfiles = this.fetchMoreProfiles.bind(this);
  }

  async fetchInitialProfiles() {
    this.setState({ isLoading: true });

    const response = await this.props.fetchInitialProfiles();

    if (response.status === 200) {
      const json = await response.json();

      this.setState({
        isLoading: false,
        profiles: json.results,
        next: json.next,
      });
    } else {
      this.props.toggleModal();
    }

    this.context.checkLoggedIn();
  }

  async fetchMoreProfiles() {
    const response = await api.fetchNext(this.state.next);

    if (response.status === 200) {
      const json = await response.json();

      this.setState({
        isLoading: false,
        profiles: this.state.profiles.concat(json.results),
        next: json.next,
      });
    } else {
      this.props.toggleModal();
    }

    this.context.checkLoggedIn();
  }

  componentDidUpdate(prevProps) {
    if (this.props.show !== prevProps.show) {
      if (this.props.show === false) {
        this.setState({
          isLoading: false,
          profiles: null,
          next: null,
        });
      } else {
        this.fetchInitialProfiles();
      }
    } else if (
      this.props.show === true &&
      this.props.fetchInitialProfiles !== prevProps.fetchInitialProfiles
    ) {
      this.fetchInitialProfiles();
    }
  }

  render() {
    return (
      <Modal
        show={this.props.show}
        size="lg"
        aria-labelledby="scrollable-list-modal"
        centered
      >
        <Modal.Header closeButton onClick={this.props.toggleModal}>
          <Modal.Title id="scrollable-list-modal">
            {this.props.title}
          </Modal.Title>
        </Modal.Header>

        <Modal.Body>
          {this.state.profiles === null ? (
            <div className="d-flex justify-content-center">
              <Spinner animation="border" />
            </div>
          ) : (
            <div
              id="list-div"
              style={{
                maxHeight: 400,
                overflow: "auto",
              }}
            >
              {this.state.profiles.length === 0 ? (
                <div className="d-flex justify-content-center">
                  {this.props.emptyResultMsg}
                </div>
              ) : (
                <InfiniteScroll
                  dataLength={this.state.profiles.length}
                  next={this.fetchMoreProfiles}
                  hasMore={this.state.next !== null}
                  loader={
                    <p className="d-flex justify-content-center">
                      <Spinner animation="border" />
                    </p>
                  }
                  scrollableTarget="profiles-div"
                >
                  {this.state.profiles.map((profile) => (
                    <div className="mb-2" key={profile.username}>
                      <ShortUserProfile profile={profile} />
                    </div>
                  ))}
                </InfiniteScroll>
              )}
            </div>
          )}
        </Modal.Body>
      </Modal>
    );
  }
}

export default ScrollableProfileListModal;
