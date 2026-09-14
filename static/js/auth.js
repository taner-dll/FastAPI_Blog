document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab-btn");
    const forms = document.querySelectorAll(".auth-form");

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((btn) => btn.classList.remove("active"));
            forms.forEach((form) => form.classList.remove("active"));

            tab.classList.add("active");
            document.getElementById(`${tab.dataset.tab}-form-box`).classList.add("active");
        });
    });

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
            alert("Giriş başarılı");
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
            alert("Kayıt başarılı");
            localStorage.setItem("token", result.access_token);
            window.location.href = "/";
        } else {
            alert(result.detail || "Kayıt başarısız");
        }
    });

    const token = localStorage.getItem("token");

    if (token && window.location.pathname === "/profile-page") {
        fetch("/profile", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("profile-username").textContent = data.username;
            document.getElementById("profile-email").textContent = data.email;
        });
    }

    document.getElementById("logout-btn")?.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/auth";
    });

    const authLink = document.getElementById("auth-link");
    const profileLink = document.getElementById("profile-link");
    const logoutLink = document.getElementById("logout-link");

    if (token) {
        authLink.style.display = "none";
        profileLink.style.display = "inline-block";
        logoutLink.style.display = "inline-block";
    } else {
        authLink.style.display = "inline-block";
        profileLink.style.display = "none";
        logoutLink.style.display = "none";
    }

    logoutLink?.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/auth";
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");

    if (window.location.pathname === "/profile-page") {
        if (!token) {
            alert("Giriş yapmanız gerekiyor.");
            window.location.href = "/auth";
            return;
        }

        fetch("/profile", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Unauthorized");
            }
            return res.json();
        })
        .then(data => {
            document.getElementById("profile-username").textContent = data.username;
            document.getElementById("profile-email").textContent = data.email;
        })
        .catch(() => {
            alert("Oturum süresi doldu veya giriş yapılmadı.");
            localStorage.removeItem("token");
            window.location.href = "/auth";
        });
    }
});