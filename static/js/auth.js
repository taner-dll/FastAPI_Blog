document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const pathname = window.location.pathname;

  const setNavState = () => {
    const authLink = document.getElementById("auth-link");
    const profileLink = document.getElementById("profile-link");
    const logoutLink = document.getElementById("logout-link");
    const createPostLink = document.getElementById("create-post-link");

    if (token) {
      if (authLink) authLink.style.display = "none";
      if (profileLink) profileLink.style.display = "inline-block";
      if (logoutLink) logoutLink.style.display = "inline-block";
      if (createPostLink) createPostLink.style.display = "inline-block";
    } else {
      if (authLink) authLink.style.display = "inline-block";
      if (profileLink) profileLink.style.display = "none";
      if (logoutLink) logoutLink.style.display = "none";
      if (createPostLink) createPostLink.style.display = "none";
    }
  };

  const bindAuthForms = () => {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");

    loginForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(loginForm).entries());

      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      const result = await res.json();
      if (res.ok) {
        localStorage.setItem("token", result.access_token);
        window.location.href = "/";
      } else {
        alert(result.detail || "Giriş başarısız");
      }
    });

    registerForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(registerForm).entries());

      const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      const result = await res.json();
      if (res.ok) {
        localStorage.setItem("token", result.access_token);
        window.location.href = "/";
      } else {
        alert(result.detail || "Kayıt başarısız");
      }
    });
  };

  const bindLogout = () => {
    document.querySelectorAll("[id='logout-link'], #logout-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.replace("/auth");
      });
    });
  };

  const protectPage = () => {
    if ((pathname === "/profile-page" || pathname === "/posts/create") && !token) {
      alert("Giriş yapmanız gerekiyor.");
      window.location.replace("/auth");
      return;
    }

    if (pathname === "/profile-page" && token) {
      fetch("/profile", {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then((res) => res.json())
        .then((data) => {
          const usernameEl = document.getElementById("profile-username");
          const emailEl = document.getElementById("profile-email");
          if (usernameEl) usernameEl.textContent = data.username;
          if (emailEl) emailEl.textContent = data.email;
        });
    }
  };

  const bindPostActions = () => {
    const editForm = document.getElementById("edit-post-form");
    const deleteButton = document.getElementById("delete-post-btn");
    const postActions = document.getElementById("post-actions");

    if (!editForm || !deleteButton || !postActions) {
      return;
    }

    if (!token) {
      postActions.style.display = "none";
      return;
    }

    const postId = window.location.pathname.split("/").pop();

    editForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const data = Object.fromEntries(new FormData(editForm).entries());

      const response = await fetch(`/posts/${postId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        alert("Yazı güncellendi.");
        window.location.reload();
      } else {
        alert(result.detail || "Yazı güncellenemedi.");
      }
    });

    deleteButton.addEventListener("click", async () => {
      const confirmed = confirm("Bu yazıyı silmek istediğinize emin misiniz?");

      if (!confirmed) {
        return;
      }

      const response = await fetch(`/posts/${postId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      const result = await response.json();

      if (response.ok) {
        alert("Yazı silindi.");
        window.location.replace("/blog");
      } else {
        alert(result.detail || "Yazı silinemedi.");
      }
    });
  };

  setNavState();
  bindAuthForms();
  bindLogout();
  protectPage();
  bindPostActions();
});