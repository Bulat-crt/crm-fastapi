import { apiRequest } from "./api.js";
import { requireAuth, mountShell } from "./auth.js";

const qs = s => document.querySelector(s);
const state = { section: "users", page: 1, limit: 12 };

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[ch]));
}

function toast(title, message, good = true) {
  const stack = qs("#toastStack");
  const item = document.createElement("div");
  item.className = `toast ${good ? "good" : "bad"}`;
  item.innerHTML = `<div class="toast-title">${esc(title)}</div><div class="toast-message">${esc(message)}</div>`;
  stack.appendChild(item);
  setTimeout(() => item.remove(), 3400);
}

function pagination(data) {
  const totalPages = Math.max(1, Math.ceil((data.total || 0) / state.limit));
  qs("#paginationInfo").textContent = `${data.total || 0} records · page ${state.page} of ${totalPages}`;
  qs("#prevPage").disabled = state.page <= 1;
  qs("#nextPage").disabled = state.page >= totalPages;
}

function renderTable(data) {
  const head = qs("#adminHead");
  const body = qs("#adminRows");
  const items = data.items || [];

  if (state.section === "users") {
    head.innerHTML = `<tr><th>Name</th><th>Email</th><th>Role</th><th>ID</th><th></th></tr>`;
    body.innerHTML = items.length ? items.map(user => `
      <tr>
        <td><strong>${esc(user.name)}</strong></td>
        <td>${esc(user.email)}</td>
        <td><span class="badge ${user.role === "admin" ? "badge-admin" : "badge-manager"}">${esc(user.role)}</span></td>
        <td class="mono small">#${user.id}</td>
        <td><button class="btn btn-sm" data-role-user="${user.id}" data-current-role="${user.role}">Change role</button></td>
      </tr>
    `).join("") : `<tr><td colspan="5"><div class="empty"><div class="empty-title">No users</div></div></td></tr>`;

    body.querySelectorAll("[data-role-user]").forEach(button => {
      button.addEventListener("click", async () => {
        const next = button.dataset.currentRole === "admin" ? "manager" : "admin";
        try {
          await apiRequest(`/admin/users/${button.dataset.roleUser}`, { method: "PUT", body: JSON.stringify({ role: next }) });
          toast("Role updated", `User #${button.dataset.roleUser} is now ${next}.`);
          await load();
        } catch (error) {
          toast("Could not change role", error.message, false);
        }
      });
    });
  }

  if (state.section === "clients") {
    head.innerHTML = `<tr><th>Name</th><th>Phone</th><th>Email</th><th>Manager</th><th>ID</th><th></th></tr>`;
    body.innerHTML = items.length ? items.map(client => `
      <tr>
        <td><strong>${esc(client.name)}</strong></td><td>${esc(client.phone)}</td><td>${client.email ? esc(client.email) : "—"}</td>
        <td>#${client.manager_id}</td><td>#${client.id}</td><td><a class="btn btn-sm" href="/app/client.html?id=${client.id}&admin=1">Open</a></td>
      </tr>
    `).join("") : `<tr><td colspan="6"><div class="empty"><div class="empty-title">No clients</div></div></td></tr>`;
  }

  if (state.section === "tasks") {
    head.innerHTML = `<tr><th>Task</th><th>Client</th><th>Manager</th><th>Status</th><th>Deadline</th><th></th></tr>`;
    body.innerHTML = items.length ? items.map(task => `
      <tr>
        <td><strong>${esc(task.title)}</strong><div class="muted small">#${task.id}</div></td><td>#${task.client_id}</td><td>#${task.manager_id}</td>
        <td>${esc(task.status)}</td><td>${new Date(task.deadline).toLocaleString()}</td><td><a class="btn btn-sm" href="/app/task.html?id=${task.id}&admin=1">Open</a></td>
      </tr>
    `).join("") : `<tr><td colspan="6"><div class="empty"><div class="empty-title">No tasks</div></div></td></tr>`;
  }
}

async function loadManagerTasks(managerId) {
  const page = Number(qs("#managerTaskPage").value || 1);
  const limit = Number(qs("#managerTaskLimit").value || 10);
  const data = await apiRequest(`/admin/users/${managerId}/tasks?page=${page}&limit=${limit}`);
  qs("#managerTaskOutput").innerHTML = (data.items || []).map(task => `
    <article class="card" style="margin-bottom:10px">
      <div class="card-title"><strong>${esc(task.title)}</strong><span class="badge">${esc(task.status)}</span></div>
      <div class="muted small">Task #${task.id} · Client #${task.client_id} · ${new Date(task.deadline).toLocaleString()}</div>
    </article>
  `).join("") || `<div class="empty">No tasks for this manager.</div>`;
}

async function load() {
  try {
    const data = await apiRequest(`/admin/${state.section === "users" ? "users" : state.section}?page=${state.page}&limit=${state.limit}`);
    renderTable(data);
    pagination(data);
  } catch (error) {
    toast("Could not load admin data", error.message, false);
  }
}

async function init() {
  const user = await requireAuth();
  if (user.role !== "admin") {
    location.href = "/app/dashboard.html";
    return;
  }
  mountShell(user);

  document.querySelectorAll("[data-admin-section]").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-admin-section]").forEach(b => b.classList.remove("active"));
      button.classList.add("active");
      state.section = button.dataset.adminSection;
      state.page = 1;
      qs("#adminSectionTitle").textContent = button.textContent.trim();
      load();
    });
  });

  qs("#prevPage").addEventListener("click", () => { state.page--; load(); });
  qs("#nextPage").addEventListener("click", () => { state.page++; load(); });
  qs("#loadManagerTasks").addEventListener("click", async () => {
    try { await loadManagerTasks(Number(qs("#managerId").value)); }
    catch (error) { toast("Could not load manager tasks", error.message, false); }
  });

  await load();
}

init().catch(console.error);
