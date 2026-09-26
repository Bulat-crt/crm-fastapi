import { apiRequest } from "./api.js";

const form = document.querySelector("#registerForm");
const errorBox = document.querySelector("#errorBox");

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorBox.hidden = true;
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  button.textContent = "Creating…";

  const payload = {
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    password: form.password.value
  };

  try {
    await apiRequest("/auth/register", { method: "POST", body: JSON.stringify(payload) });
    location.href = "/app/login.html";
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = "Create account";
  }
});
