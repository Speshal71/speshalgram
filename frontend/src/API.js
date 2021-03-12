import config from "./Config";

class APIClient {
  getFullEnpoint(endpoint, absolute = false) {
    if (absolute) {
      return endpoint;
    }

    return `${config.APIHost}${endpoint}`;
  }

  async fetch(
    endpoint,
    requestConfig = {},
    { forceRequestConfig = false, isAbsolute = false } = {}
  ) {
    const accessToken = localStorage.getItem(config.accessToken);
    const refreshToken = localStorage.getItem(config.refreshToken);

    if (!forceRequestConfig) {
      requestConfig = {
        method: "GET",
        headers: {
          "Content-type": "application/json",
          Accept: "application/json",
        },
        ...requestConfig,
      };
    }

    let response;

    if (accessToken) {
      requestConfig.headers.Authorization = `Bearer ${accessToken}`;

      response = await fetch(
        this.getFullEnpoint(endpoint, isAbsolute),
        requestConfig
      );

      if (response.status !== 401) {
        return response;
      }

      if (refreshToken) {
        delete requestConfig.headers.Authorization;

        response = await fetch(this.getFullEnpoint("/api/token/refresh/"), {
          method: "POST",
          headers: {
            "Content-type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            refresh: refreshToken,
          }),
        });

        if (response.status === 200) {
          const newAccessToken = (await response.json())["access"];
          localStorage.setItem(config.accessToken, newAccessToken);

          requestConfig.headers.Authorization = `Bearer ${newAccessToken}`;

          response = await fetch(
            this.getFullEnpoint(endpoint, isAbsolute),
            requestConfig
          );

          return response;
        } else {
          this.logout();
        }
      }
    }

    response = await fetch(
      this.getFullEnpoint(endpoint, isAbsolute),
      requestConfig
    );

    return response;
  }

  isLoggedIn() {
    return Boolean(
      localStorage.getItem(config.accessToken) &&
        localStorage.getItem(config.refreshToken)
    );
  }

  logout() {
    localStorage.removeItem(config.accessToken);
    localStorage.removeItem(config.refreshToken);
  }

  async fetchTokens(username, password) {
    const response = await this.fetch("/api/token/", {
      method: "POST",
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    return response;
  }

  async registerUser(username, password) {
    const response = await this.fetch("/api/users/", {
      method: "POST",
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    return response;
  }

  async fetchProfile(username) {
    const response = await this.fetch(`/api/users/${username}`);
    return response;
  }

  async fetchPosts(username) {
    const response = await this.fetch(`/api/posts/?username=${username}`);
    return response;
  }

  async fetchNext(nextURL) {
    if (nextURL !== null) {
      const response = await this.fetch(nextURL, {}, { isAbsolute: true });
      return response;
    }
    return null;
  }

  async fetchFeed() {
    const response = await this.fetch("/api/posts/feed/");
    return response;
  }

  async fetchMyUsername() {
    const response = await this.fetch("/api/users/me/");
    return response;
  }

  async fetchSuggestedUsers(username) {
    const response = await this.fetch(`/api/users/?search=${username}`);
    return response;
  }

  async uploadPost(picture, description) {
    let formData = new FormData();
    if (picture !== null) {
      formData.append("picture", picture);
    }
    if (description !== null) {
      formData.append("description", description);
    }

    const response = await this.fetch(
      "/api/posts/",
      { method: "POST", body: formData, headers: {} },
      { forceRequestConfig: true }
    );

    return response;
  }

  async putLike(postId) {
    const response = await this.fetch(`/api/likes/?post_id=${postId}`, {
      method: "PUT",
    });
    return response;
  }

  async deleteLike(postId) {
    const response = await this.fetch(`/api/likes/?post_id=${postId}`, {
      method: "DELETE",
    });
    return response;
  }

  async fetchPost(postId) {
    const response = await this.fetch(`/api/posts/${postId}/`);
    return response;
  }

  async fetchComments(postId) {
    const response = await this.fetch(`/api/comments/?post_id=${postId}`);
    return response;
  }

  async postComment(postId, newComment) {
    const response = await this.fetch(`/api/comments/?post_id=${postId}`, {
      method: "POST",
      body: JSON.stringify({ text: newComment }),
    });
    return response;
  }

  async fetchLikes(postId) {
    const response = await this.fetch(`/api/likes/?post_id=${postId}`);
    return response;
  }

  async fetchFollowers(username) {
    const response = await this.fetch(`/api/users/${username}/followers/`);
    return response;
  }

  async fetchFollowings(username) {
    const response = await this.fetch(`/api/users/${username}/follows/`);
    return response;
  }

  async patchMyProfile(newProfile) {
    let formData = new FormData();

    for (let formFieldName of [
      "avatar",
      "username",
      "first_name",
      "last_name",
      "description",
      "is_opened",
    ]) {
      if (newProfile[formFieldName] !== null) {
        formData.append(formFieldName, newProfile[formFieldName]);
      }
    }

    const response = await this.fetch(
      "/api/users/me/",
      { method: "PATCH", body: formData, headers: {} },
      { forceRequestConfig: true }
    );

    return response;
  }

  async subscribeUser(username) {
    const response = await this.fetch(`/api/users/${username}/subscribe/`, {
      method: "PUT",
    });
    return response;
  }

  async cancelSubscription(username) {
    const response = await this.fetch(`/api/users/${username}/subscribe/`, {
      method: "DELETE",
    });
    return response;
  }

  async fetchPendingProfiles() {
    const response = await this.fetch(`/api/users/pending_followers/`);
    return response;
  }

  async acceptRequest(username) {
    const response = await this.fetch(`/api/users/${username}/accept/`, {
      method: "PUT",
    });
    return response;
  }

  async rejectRequest(username) {
    const response = await this.fetch(`/api/users/${username}/accept/`, {
      method: "DELETE",
    });
    return response;
  }
}

const api = new APIClient();

export default api;
