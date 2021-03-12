import React from "react";
import { Spinner, Button, Col, Card, Form } from "react-bootstrap";

import api from "../API";
import AppContext from "../App/AppContext";
import { Centered } from "../Common";
import Comment from "./Comment";
import Post from "./Post";

class PostWithComments extends React.Component {
  static contextType = AppContext;

  postStates = {
    LOADING: "loading",
    NOT_LOGGED_IN: "notLoggedIn",
    FORBIDDEN: "forbidden",
    NOT_FOUND: "notFound",
    LOADED: "loaded",
    ERROR: "error",
  };

  constructor(props) {
    super(props);
    this.state = {
      postState: this.postStates.LOADING,
      post: null,
      comments: [],
      next: null,
      newComment: "",
      commentError: null,
    };

    this.loadMoreComments = this.loadMoreComments.bind(this);
    this.handleCommentInput = this.handleCommentInput.bind(this);
    this.addNewComment = this.addNewComment.bind(this);
    this.updatePost = this.updatePost.bind(this);
  }

  async componentDidMount() {
    const [postResp, commentsResp] = await Promise.all([
      api.fetchPost(this.props.postId),
      api.fetchComments(this.props.postId),
    ]);

    if (postResp.status === 200) {
      const postJSON = await postResp.json();
      const commentsJSON = await commentsResp.json();

      this.setState({
        postState: this.postStates.LOADED,
        post: postJSON,
        comments: commentsJSON.results,
        next: commentsJSON.next,
      });
    } else {
      const stateMapping = {
        401: this.postStates.NOT_LOGGED_IN,
        403: this.postStates.FORBIDDEN,
        404: this.postStates.NOT_FOUND,
      };

      this.setState({
        postState: stateMapping[postResp.status] || this.postStates.ERROR,
      });
    }

    this.context.checkLoggedIn();
  }

  async loadMoreComments() {
    if (this.state.next !== null) {
      const response = await api.fetchNext(this.state.next);

      if (response.status === 200) {
        const json = await response.json();

        this.setState({
          comments: this.state.comments.concat(json.results),
          next: json.next,
        });
      }

      this.context.checkLoggedIn();
    }
  }

  handleCommentInput(e) {
    this.setState({ newComment: e.target.value });
  }

  async addNewComment(e) {
    e.preventDefault();

    const response = await api.postComment(
      this.state.post.id,
      this.state.newComment
    );

    if (response.status === 201) {
      const newComment = await response.json();
      this.setState({
        comments: [newComment].concat(this.state.comments),
        newComment: "",
        commentError: null,
      });
    } else if (response.status === 400) {
      const error = await response.json();
      this.setState({ commentError: error.text });
    }

    this.context.checkLoggedIn();
  }

  updatePost(newPost) {
    this.setState({ post: newPost });
  }

  render() {
    if (this.state.postState !== this.postStates.LOADED) {
      return (
        <Centered>
          {this.state.postState === this.postStates.LOADING ? (
            <Spinner animation="border" />
          ) : this.state.postState === this.postStates.NOT_LOGGED_IN ? (
            "This is closed post. You need to log in to see it."
          ) : this.state.postState === this.postStates.FORBIDDEN ? (
            "This is closed post. You have to subscribe the user to see it."
          ) : this.state.postState === this.postStates.NOT_FOUND ? (
            "Such post doesn't exist."
          ) : (
            "Some error occured."
          )}
        </Centered>
      );
    }

    return (
      <>
        <Post data={this.state.post} updateParent={this.updatePost} />

        <Card
          className="m-2"
          style={{
            maxHeight: 400,
            overflow: "auto",
          }}
        >
          <Card.Body className="pt-1 pb-1">
            <div className="mb-3 mt-3">
              {this.state.comments.length === 0 ? (
                <Centered style={{}}>
                  There is no any comment to this post yet
                </Centered>
              ) : (
                <>
                  {this.state.next !== null && (
                    <div className="d-flex justify-content-center">
                      <Button variant="dark" onClick={this.loadMoreComments}>
                        Load More
                      </Button>
                    </div>
                  )}

                  {this.state.comments
                    .slice()
                    .reverse()
                    .map((comment) => (
                      <Comment key={comment.id} data={comment} />
                    ))}
                </>
              )}
            </div>

            {this.context.isLoggedIn && (
              <Form className="mt-2" onSubmit={this.addNewComment}>
                <Form.Row>
                  <Col>
                    <Form.Group className="m-2">
                      <Form.Control
                        required
                        type="text"
                        as="textarea"
                        placeholder="Your comment"
                        name="text"
                        value={this.state.newComment}
                        onChange={this.handleCommentInput}
                      />
                      <Form.Text className="text-danger">
                        {this.state.commentError}
                      </Form.Text>
                    </Form.Group>
                  </Col>

                  <Col xs="auto">
                    <Button variant="dark" type="submit">
                      Submit
                    </Button>
                  </Col>
                </Form.Row>
              </Form>
            )}
          </Card.Body>
        </Card>
      </>
    );
  }
}

export default PostWithComments;
