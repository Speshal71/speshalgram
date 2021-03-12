import React from "react";
import { Route } from "react-router-dom";

import AppContext from "./AppContext";

function CheckLoggedInRoute(props) {
  return (
    <AppContext.Consumer>
      {({ isLoggedIn, checkLoggedIn }) => <Route key={isLoggedIn} {...props} />}
    </AppContext.Consumer>
  );
}

export default CheckLoggedInRoute;
