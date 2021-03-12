import React from "react";
import { Spinner } from "react-bootstrap";
import InfiniteScroll from "react-infinite-scroll-component";

import api from "../API";
import AppContext from "../App/AppContext";
import Post from "./Post";

class ScrolledPosts extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.loadMorePosts = this.loadMorePosts.bind(this);
  }

  async loadMorePosts() {
    if (this.props.next !== null) {
      const responce = await api.fetchNext(this.props.next);

      if (responce.status === 200) {
        const json = await responce.json();

        this.props.updateParent(
          this.props.posts.concat(json.results),
          json.next
        );
      }

      this.context.checkLoggedIn();
    }
  }

  updatePost(i, updatedPost) {
    this.props.updateParent(
      this.props.posts.map((post, j) => (j === i ? updatedPost : post)),
      this.props.next
    );
  }

  render() {
    return (
      <InfiniteScroll
        dataLength={this.props.posts.length}
        next={this.loadMorePosts}
        hasMore={this.props.next !== null}
        loader={
          <p className="d-flex justify-content-center">
            <Spinner animation="border" />
          </p>
        }
        scrollThreshold={0.95}
      >
        {this.props.posts.map((post, i) => (
          <Post
            key={post.id}
            data={post}
            updateParent={this.updatePost.bind(this, i)}
          />
        ))}
      </InfiniteScroll>
    );
  }
}

export default ScrolledPosts;
