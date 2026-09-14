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
});