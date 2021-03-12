import React from "react";
import { Container } from "react-bootstrap";
import { Switch, Route, Redirect } from "react-router-dom";

import api from "../API";
import { Centered, Login, SignUp } from "../Common";
import { Feed, PostWithComments } from "../Post";
import { MyUserProfile, UserProfile, IncomingRequests } from "../UserProfile";
import AppContext from "./AppContext";
import CheckLoggedInRoute from "./CheckLoggedInRoute";
import Header from "./Header";
import ProtectedRoute from "./ProtectedRoute";
import Navigation from "./Navigation";

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoggedIn: api.isLoggedIn(),
    };

    this.checkLoggedIn = this.checkLoggedIn.bind(this);
  }

  checkLoggedIn() {
    if (this.state.isLoggedIn !== api.isLoggedIn()) {
      this.setState({ isLoggedIn: !this.state.isLoggedIn });
    }
  }

  render() {
    const context = {
      isLoggedIn: this.state.isLoggedIn,
      checkLoggedIn: this.checkLoggedIn,
    };

    return (
      <AppContext.Provider value={context}>
        <div className="App">
          <Header />
          {this.state.isLoggedIn && <Navigation />}

          <Container as="main" style={{ maxWidth: 700 }}>
            <Switch>
              <Route exact path="/" render={() => <Redirect to="/profile" />} />

              <ProtectedRoute exact path="/profile" component={MyUserProfile} />

              <CheckLoggedInRoute
                path="/profiles/:username"
                render={(props) => (
                  <UserProfile username={props.match.params.username} />
                )}
              />

              <ProtectedRoute path="/feed" component={Feed} />

              <ProtectedRoute path="/incoming" component={IncomingRequests} />

              <CheckLoggedInRoute
                path="/posts/:postId"
                render={(props) => (
                  <PostWithComments postId={props.match.params.postId} />
                )}
              />

              <Route path="/login" component={Login} />

              <Route path="/signup" component={SignUp} />

              <Route>
                <Centered>Requested resource is not found :(</Centered>
              </Route>
            </Switch>
          </Container>
        </div>
      </AppContext.Provider>
    );
  }
}

export default App;
