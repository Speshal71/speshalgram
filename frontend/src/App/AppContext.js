import React from "react";

const AppContext = React.createContext({
  isLoggedIn: false,
  checkLoggedIn: undefined,
});

export default AppContext;
