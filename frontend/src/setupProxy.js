const createProxyMiddleware = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    ["/api", "/media"],
    createProxyMiddleware({
      target: `http://${process.env.REACT_APP_PROXY_HOST}:${process.env.REACT_APP_PROXY_PORT}/`,
    })
  );
};
