import { getToken, removeToken, me } from "./api.js";

export function initials(name = "U") {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0].toUpperCase())
    .join("");
}

export async function requireAuth() {
  if (!getToken()) {
    location.href = "/app/login.html";
    throw new Error("Not authenticated");
  }
  return me();
}

export function logout() {
  removeToken();
  location.href = "/app/login.html";
}

export function setupLogout() {
  document.querySelectorAll("[data-logout]").forEach(button => {
    button.addEventListener("click", logout);
  });
}

export function markActiveNav() {
  const current = location.pathname.split("/").pop() || "dashboard.html";
  document.querySelectorAll("[data-nav]").forEach(link => {
    if (link.getAttribute("href") === current) link.classList.add("active");
  });
}

export function mountShell(user) {
  const role = user.role;
  const roleBadge = document.querySelector("[data-role]");
  if (roleBadge) {
    roleBadge.textContent = role;
    roleBadge.classList.add(role === "admin" ? "badge-admin" : "badge-manager");
  }

  const name = document.querySelector("[data-user-name]");
  if (name) name.textContent = user.name;
  const email = document.querySelector("[data-user-email]");
  if (email) email.textContent = user.email;
  const avatar = document.querySelector("[data-avatar]");
  if (avatar) avatar.textContent = initials(user.name);

  document.querySelectorAll("[data-admin-only]").forEach(el => {
    el.hidden = role !== "admin";
  });

  setupLogout();
  markActiveNav();
}
