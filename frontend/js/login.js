import { login } from "./api.js";

const form = document.querySelector("#loginForm");
const errorBox = document.querySelector("#errorBox");

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorBox.hidden = true;
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  button.textContent = "Signing in…";

  try {
    await login(form.email.value.trim(), form.password.value);
    location.href = "/app/dashboard.html";
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = "Enter workspace";
  }
});
