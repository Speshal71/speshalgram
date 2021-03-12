import React from "react";
import { Media, Button, Row, Col, Spinner } from "react-bootstrap";
import { Redirect } from "react-router-dom";

import config from "../Config";
import api from "../API";
import AppContext from "../App/AppContext";
import { Centered, ScrollableProfileListModal } from "../Common";
import { Bell } from "../Common/SVG";
import { ScrollablePosts } from "../Post";
import EditProfileModal from "./EditProfileModal";
import UploadPostButton from "./UploadPostButton";

class UserInfo extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      redirectTo: null,
      showFollowers: false,
      showFollowings: false,
      showEditForm: false,
    };

    this.protectClosedProfile = this.protectClosedProfile.bind(this);
    this.loadFollowers = this.loadFollowers.bind(this);
    this.toggleFollowersModal = this.toggleFollowersModal.bind(this);
    this.loadFollowings = this.loadFollowings.bind(this);
    this.toggleFollowingsModal = this.toggleFollowingsModal.bind(this);
    this.toggleEditModal = this.toggleEditModal.bind(this);
    this.protectedSubscribeUser = this.protectedSubscribeUser.bind(this);
    this.cancelSubscription = this.cancelSubscription.bind(this);
    this.redirectToIncoming = this.redirectToIncoming.bind(this);
  }

  componentDidUpdate(prevProps) {
    if (this.props.profile.username !== prevProps.profile.username) {
      this.setState({
        showFollowers: false,
        showFollowings: false,
        showEditForm: false,
      });
    }
  }

  redirectToLogin() {
    this.setState({
      redirectTo: `/login?redirect=${window.location.pathname}`,
    });
  }

  protectClosedProfile(func) {
    return () => {
      if (
        this.props.profile.is_opened ||
        ["Accepted", "self"].includes(this.props.profile.followed_by_me_status)
      ) {
        func.apply(this, arguments);
      } else if (!this.context.isLoggedIn) {
        this.redirectToLogin();
      }
    };
  }

  async subscribeUser() {
    const response = await api.subscribeUser(this.props.profile.username);

    if (response.status === 200) {
      const newProfile = await response.json();

      this.props.updateParentProfile(newProfile);
    }
  }

  async protectedSubscribeUser() {
    if (this.context.isLoggedIn) {
      this.subscribeUser();
    } else {
      this.redirectToLogin();
    }
  }

  async cancelSubscription() {
    const response = await api.cancelSubscription(this.props.profile.username);

    if (response.status === 200) {
      const newProfile = await response.json();

      this.props.updateParentProfile(newProfile);
    }
  }

  getUsernameAndSubscriptionStatus() {
    const subscriptionStatus = {
      null: (
        <Button
          variant="light"
          className="p-0 pl-1 pr-1"
          onClick={this.protectedSubscribeUser}
        >
          Subscribe
        </Button>
      ),
      Accepted: (
        <>
          <span className="font-italic mr-1">(Subscrcibed)</span>
          <Button
            variant="light"
            className="p-0 pl-1 pr-1"
            onClick={this.cancelSubscription}
          >
            Cancel
          </Button>
        </>
      ),
      Pending: (
        <span className="font-italic mr-1">(Subcription request is sent)</span>
      ),
      self: (
        <Button
          variant="light"
          className="p-0 pl-1 pr-1"
          onClick={this.toggleEditModal}
        >
          Edit
        </Button>
      ),
    };

    return (
      <div className="d-flex align-center">
        <span className="font-weight-bold mr-2">
          {this.props.profile.username}
        </span>
        {subscriptionStatus[this.props.profile.followed_by_me_status]}
      </div>
    );
  }

  loadFollowers() {
    return api.fetchFollowers(this.props.profile.username);
  }

  toggleFollowersModal() {
    this.setState({ showFollowers: !this.state.showFollowers });
  }

  loadFollowings() {
    return api.fetchFollowings(this.props.profile.username);
  }

  toggleFollowingsModal() {
    this.setState({ showFollowings: !this.state.showFollowings });
  }

  redirectToIncoming() {
    this.setState({ redirectTo: "/incoming" });
  }

  getFollowersAndFollowings() {
    return (
      <Row className="d-flex flex-row mb-1 ml-0">
        <Col
          xs="auto"
          className="pl-0 pr-4"
          style={{ cursor: "pointer" }}
          onClick={this.protectClosedProfile(this.toggleFollowersModal)}
        >
          <span className="font-weight-bold">
            {this.props.profile.nfollowers}{" "}
          </span>
          followers
        </Col>

        <ScrollableProfileListModal
          title={`${this.props.profile.username} followers`}
          emptyResultMsg="The user hasn't any follower yet"
          show={this.state.showFollowers}
          toggleModal={this.toggleFollowersModal}
          fetchInitialProfiles={this.loadFollowers}
        />

        <Col
          xs="auto"
          className="pl-0 pr-4"
          style={{ cursor: "pointer" }}
          onClick={this.protectClosedProfile(this.toggleFollowingsModal)}
        >
          <span className="font-weight-bold">
            {this.props.profile.nfollows}{" "}
          </span>
          followings
        </Col>

        <ScrollableProfileListModal
          title={`${this.props.profile.username} followings`}
          emptyResultMsg="The user doesn't follow anybody yet"
          show={this.state.showFollowings}
          toggleModal={this.toggleFollowingsModal}
          fetchInitialProfiles={this.loadFollowings}
        />

        {this.props.profile.followed_by_me_status === "self" &&
          !this.props.profile.is_opened && (
            <Col
              xs="auto"
              className="pl-0 pr-4"
              style={{ cursor: "pointer" }}
              onClick={this.redirectToIncoming}
            >
              <Bell /> incomings
            </Col>
          )}
      </Row>
    );
  }

  getNameAndDescription() {
    return (
      <>
        <span className="font-italic">
          {this.props.profile.first_name} {this.props.profile.last_name}
        </span>
        <span>{this.props.profile.description}</span>
      </>
    );
  }

  toggleEditModal() {
    this.setState({ showEditForm: !this.state.showEditForm });
  }

  getEditForm() {
    return (
      <EditProfileModal
        show={this.state.showEditForm}
        toggleModal={this.toggleEditModal}
        profile={this.props.profile}
        updateParentProfile={this.props.updateParentProfile}
      />
    );
  }

  render() {
    if (this.state.redirectTo !== null) {
      return <Redirect to={this.state.redirectTo} />;
    }

    return (
      <div>
        <Media className="m-3 p-3 bg-light">
          <img
            width={config.imgSize.avatar.big}
            height={config.imgSize.avatar.big}
            className="mr-3"
            src={this.props.profile.avatar}
            alt={`${this.props.profile.username} avatar`}
          />
          <Media.Body className="d-flex flex-column">
            {this.getUsernameAndSubscriptionStatus()}
            {this.getFollowersAndFollowings()}
            {this.getNameAndDescription()}
            {this.getEditForm()}
          </Media.Body>
        </Media>
      </div>
    );
  }
}

class UserProfile extends React.Component {
  static contextType = AppContext;

  profileStates = {
    LOADING: "loading",
    LOADED: "loaded",
    NOT_FOUND: "notFound",
    ERROR: "erorr",
  };

  constructor(props) {
    super(props);
    this.state = {
      profileState: this.profileStates.LOADING,
      profile: null,
      posts: null,
      next: null,
    };

    this.handleUpload = this.handleUpload.bind(this);
    this.updateProfile = this.updateProfile.bind(this);
    this.updatePosts = this.updatePosts.bind(this);
  }

  async fetchData() {
    const [profileResp, postsResp] = await Promise.all([
      api.fetchProfile(this.props.username),
      api.fetchPosts(this.props.username),
    ]);

    let newState = {
      profileState: this.profileStates.ERROR,
      profile: null,
      posts: null,
      next: null,
    };

    if (profileResp.status === 200) {
      newState.profile = await profileResp.json();

      if ([200, 401, 403].includes(postsResp.status)) {
        if (postsResp.status === 200) {
          const postsRespJSON = await postsResp.json();

          newState.posts = postsRespJSON.results;
          newState.next = postsRespJSON.next;
        }

        newState.profileState = this.profileStates.LOADED;
      }
    } else if (profileResp.status === 404) {
      newState.profileState = this.profileStates.NOT_FOUND;
    }

    this.setState(newState);

    this.context.checkLoggedIn();
  }

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(prevProps) {
    if (this.props.username !== prevProps.username) {
      this.fetchData();
    }
  }

  handleUpload(post) {
    this.setState({ posts: [post].concat(this.state.posts) });
  }

  updateProfile(newProfile) {
    if (
      !this.state.profile.is_opened &&
      this.state.profile.followed_by_me_status === "Accepted" &&
      newProfile.followed_by_me_status === null
    ) {
      this.setState({ posts: null });
    }

    if (this.state.profile.avatar !== newProfile.avatar) {
      this.setState({
        posts: this.state.posts.map((post) => ({
          ...post,
          owner: { ...post.owner, avatar: newProfile.avatar },
        })),
      });
    }

    this.setState({
      profile: { ...this.state.profile, ...newProfile },
    });
  }

  updatePosts(newPosts, next) {
    this.setState({
      posts: newPosts,
      next: next,
    });
  }

  render() {
    if (this.state.profileState !== this.profileStates.LOADED) {
      return (
        <Centered>
          {this.state.profileState === this.profileStates.LOADING ? (
            <Spinner animation="border" />
          ) : this.state.profileState === this.profileStates.NOT_FOUND ? (
            "No such user found."
          ) : (
            "Some error occured."
          )}
        </Centered>
      );
    }

    return (
      <div>
        <UserInfo
          profile={this.state.profile}
          updateParentProfile={this.updateProfile}
        />

        {this.state.profile.followed_by_me_status === "self" && (
          <UploadPostButton onUpload={this.handleUpload} />
        )}

        {this.state.posts === null ? (
          this.context.isLoggedIn ? (
            <Centered>
              This is closed profile. You have to subscribe it to see the
              content.
            </Centered>
          ) : (
            <Centered>
              This is closed profile. Login to see the content
            </Centered>
          )
        ) : this.state.posts.length === 0 ? (
          <Centered>This user hasn't uploaded any post yet.</Centered>
        ) : (
          <ScrollablePosts
            posts={this.state.posts}
            next={this.state.next}
            updateParent={this.updatePosts}
          />
        )}
      </div>
    );
  }
}

export default UserProfile;
