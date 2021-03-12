import React from "react";
import { Card, Row, Col } from "react-bootstrap";
import { Link, Redirect } from "react-router-dom";

import api from "../API";
import AppContext from "../App/AppContext";
import { ScrollableProfileListModal } from "../Common";
import { Heart, FilledHeart } from "../Common/SVG";
import { ShortUserProfile } from "../UserProfile";
import Comment from "./Comment";

function Separator(props) {
  return (
    <div>
      <Row>
        <Col className="pr-0">
          <hr />
        </Col>
        <Col
          xs="auto"
          className="pl-1 pr-1 d-flex align-items-center text-muted"
          style={{ fontSize: 14 }}
        >
          {props.text}
        </Col>
        <Col className="pl-0">
          <hr />
        </Col>
      </Row>
    </div>
  );
}

class Post extends React.Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      showLikes: false,
      redirectToLogin: false,
    };

    this.likePost = this.likePost.bind(this);
    this.toggleModal = this.toggleModal.bind(this);
    this.loadLikes = this.loadLikes.bind(this);
  }

  async likePost() {
    if (!this.context.isLoggedIn) {
      this.setState({ redirectToLogin: true });
      return;
    }

    const apiAction = this.props.data.is_liked_by_me
      ? api.deleteLike
      : api.putLike;

    const response = await apiAction.call(api, this.props.data.id);

    if (response.status === 200) {
      this.props.data.is_liked_by_me = !this.props.data.is_liked_by_me;
      this.props.data.nlikes = (await response.json()).nlikes;

      this.props.updateParent(this.props.data);
    }

    this.context.checkLoggedIn();
  }

  toggleModal() {
    this.setState({ showLikes: !this.state.showLikes });
  }

  loadLikes() {
    return api.fetchLikes(this.props.data.id);
  }

  render() {
    if (this.state.redirectToLogin) {
      return <Redirect to={`/login?redirect=${window.location.pathname}`} />;
    }

    const data = this.props.data;

    return (
      <Card className="m-2">
        <Card.Header id="post-header" className="p-1">
          <ShortUserProfile
            className="m-1"
            profile={data.owner}
            useName={false}
          />
        </Card.Header>

        <div className="m-1 ml-2 mr-2">
          <Card.Img
            variant="top"
            src={data.picture}
            onDoubleClick={this.likePost}
          />
        </div>

        <Card.Body>
          <div
            className="mb-2"
            style={{ cursor: "pointer" }}
            onClick={this.toggleModal}
          >
            <span>{data.is_liked_by_me ? <FilledHeart /> : <Heart />}</span>
            <span> {data.nlikes} likes </span>
          </div>

          {data.description && (
            <Comment data={{ owner: data.owner, text: data.description }} />
          )}

          {data.hasOwnProperty("preview_comments") && (
            <>
              {data.preview_comments.length > 0 && (
                <Separator text="Last comments" />
              )}
              {data.preview_comments.map((comment) => (
                <Comment key={comment.id} data={comment} />
              ))}
              <Link
                className="plain-text text-muted"
                style={{ fontSize: 14 }}
                to={`/posts/${data.id}`}
              >
                View all / Leave a comment
              </Link>
            </>
          )}
        </Card.Body>

        <ScrollableProfileListModal
          title="Post likes"
          emptyResultMsg="Noboby has liked this post yet"
          show={this.state.showLikes}
          toggleModal={this.toggleModal}
          fetchInitialProfiles={this.loadLikes}
        />
      </Card>
    );
  }
}

export default Post;
