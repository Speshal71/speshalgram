import React from "react";
import { Spinner } from "react-bootstrap";

import api from "../API";
import AppContext from "../App/AppContext";
import { Centered } from "../Common";
import ScrolledPosts from "./ScrollablePosts";

class Feed extends React.Component {
  static contextType = AppContext;

  feedStates = {
    LOADING: "loading",
    LOADED: "loaded",
    ERROR: "error",
  };

  constructor(props) {
    super(props);
    this.state = {
      feedState: this.feedStates.LOADING,
      posts: [],
      next: null,
    };

    this.updatePosts = this.updatePosts.bind(this);
  }

  async componentDidMount() {
    const responce = await api.fetchFeed();

    if (responce.status === 200) {
      const json = await responce.json();
      this.setState({
        feedState: this.feedStates.LOADED,
        posts: json.results,
        next: json.next,
      });
    } else {
      this.setState({ feedState: this.feedStates.ERROR });
    }

    this.context.checkLoggedIn();
  }

  updatePosts(newPosts, next) {
    this.setState({
      posts: newPosts,
      next: next,
    });
  }

  render() {
    if (this.state.feedState !== this.feedStates.LOADED) {
      return (
        <Centered>
          {this.state.feedState === this.feedStates.LOADING ? (
            <Spinner animation="border" />
          ) : (
            "Some error occured."
          )}
        </Centered>
      );
    }

    return (
      <div>
        {this.state.posts.length > 0 ? (
          <ScrolledPosts
            posts={this.state.posts}
            next={this.state.next}
            updateParent={this.updatePosts}
          />
        ) : (
          <Centered>Your friends haven't uploaded any posts yet.</Centered>
        )}
      </div>
    );
  }
}

export default Feed;
