import React from "react";
import { Route, Redirect } from "react-router-dom";

import AppContext from "./AppContext";

function ProtectedRoute({ path, component, ...rest }) {
  let Component = component;
  return (
    <AppContext.Consumer>
      {({ isLoggedIn, checkLoggedIn }) => (
        <Route
          path={path}
          render={() =>
            isLoggedIn ? (
              <Component />
            ) : (
              <Redirect to={`/login?redirect=${path}`} />
            )
          }
          {...rest}
        />
      )}
    </AppContext.Consumer>
  );
}

export default ProtectedRoute;
