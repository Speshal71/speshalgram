import React from "react";
import { Spinner } from "react-bootstrap";

import api from "../API";
import AppContext from "../App/AppContext";
import { Centered } from "../Common";
import UserProfile from "./UserProfile";

class MyUserProfile extends React.Component {
  static contextType = AppContext;

  profileStates = {
    LOADING: "loading",
    LOADED: "loaded",
    ERROR: "erorr",
  };

  constructor(props) {
    super(props);
    this.state = {
      profileState: this.profileStates.LOADING,
      username: null,
    };
  }

  async componentDidMount() {
    const response = await api.fetchMyUsername();

    if (response.status === 200) {
      const json = await response.json();
      this.setState({
        profileState: this.profileStates.LOADED,
        username: json.username,
      });
    } else {
      this.setState({ profileState: this.profileStates.ERROR });
    }
  }

  render() {
    return this.state.profileState === this.profileStates.LOADING ? (
      <Centered>
        <Spinner animation="border" />
      </Centered>
    ) : this.state.profileState === this.profileStates.ERROR ? (
      <Centered>Some error occured.</Centered>
    ) : (
      <UserProfile username={this.state.username} />
    );
  }
}

export default MyUserProfile;
