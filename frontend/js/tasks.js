import { apiRequest } from "./api.js";
import { requireAuth, mountShell } from "./auth.js";

const state = { page: 1, limit: 12, search: "", status: "", sort: "created_at", order: "desc" };
const qs = s => document.querySelector(s);

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;"," >":"&gt;","\"":"&quot;","'":"&#039;"}[ch]) || ch);
}

function toast(title, message, good = true) {
  const stack = qs("#toastStack");
  const item = document.createElement("div");
  item.className = `toast ${good ? "good" : "bad"}`;
  item.innerHTML = `<div class="toast-title">${esc(title)}</div><div class="toast-message">${esc(message)}</div>`;
  stack.appendChild(item);
  setTimeout(() => item.remove(), 3400);
}

function statusBadge(status) {
  const map = { new: ["badge-new", "New"], in_progress: ["badge-progress", "In progress"], done: ["badge-done", "Done"] };
  const [cls, label] = map[status] || ["", status];
  return `<span class="badge ${cls}">${esc(label)}</span>`;
}

function render(items) {
  const tbody = qs("#taskRows");
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty"><div class="empty-title">No tasks found</div><div>Try another search or clear your filters.</div></div></td></tr>`;
    return;
  }
  tbody.innerHTML = items.map(task => `
    <tr>
      <td><strong>${esc(task.title)}</strong><div class="muted small">${esc(task.description)}</div></td>
      <td>#${task.client_id}</td>
      <td>${statusBadge(task.status)}</td>
      <td>${new Date(task.deadline).toLocaleString()}</td>
      <td class="mono small">#${task.id}</td>
      <td><a class="btn btn-sm" href="/app/task.html?id=${task.id}">Open</a></td>
    </tr>
  `).join("");
}

function renderPagination(data) {
  const totalPages = Math.max(1, Math.ceil((data.total || 0) / state.limit));
  qs("#paginationInfo").textContent = `${data.total || 0} task${(data.total || 0) === 1 ? "" : "s"} · page ${state.page} of ${totalPages}`;
  qs("#prevPage").disabled = state.page <= 1;
  qs("#nextPage").disabled = state.page >= totalPages;
}

async function load() {
  const params = new URLSearchParams({ page: state.page, limit: state.limit, sort: state.sort, order: state.order });
  if (state.status) params.set("status", state.status);
  if (state.search.trim()) params.set("search", state.search.trim());
  try {
    const data = await apiRequest(`/tasks?${params}`);
    render(data.items || []);
    renderPagination(data);
  } catch (error) {
    toast("Could not load tasks", error.message, false);
  }
}

async function loadClientsForForm() {
  const data = await apiRequest("/clients?page=1&limit=100&sort=created_at&order=desc");
  const select = qs("#client_id");
  select.innerHTML = (data.items || []).map(client => `<option value="${client.id}">${esc(client.name)} · #${client.id}</option>`).join("");
}

async function createTask() {
  const form = qs("#taskForm");
  const payload = {
    client_id: Number(form.client_id.value),
    title: form.title.value.trim(),
    description: form.description.value.trim(),
    deadline: new Date(form.deadline.value).toISOString(),
    status: form.status.value
  };
  try {
    await apiRequest("/tasks", { method: "POST", body: JSON.stringify(payload) });
    form.reset();
    qs("#createDialog").close();
    toast("Task created", payload.title);
    await load();
  } catch (error) {
    toast("Could not create task", error.message, false);
  }
}

async function init() {
  const user = await requireAuth();
  mountShell(user);

  qs("#search").addEventListener("input", e => { state.search = e.target.value; state.page = 1; clearTimeout(window.__taskTimer); window.__taskTimer = setTimeout(load, 260); });
  qs("#status").addEventListener("change", e => { state.status = e.target.value; state.page = 1; load(); });
  qs("#sort").addEventListener("change", e => { state.sort = e.target.value; state.page = 1; load(); });
  qs("#order").addEventListener("change", e => { state.order = e.target.value; state.page = 1; load(); });
  qs("#prevPage").addEventListener("click", () => { state.page--; load(); });
  qs("#nextPage").addEventListener("click", () => { state.page++; load(); });
  qs("#openCreate").addEventListener("click", async () => { try { await loadClientsForForm(); qs("#createDialog").showModal(); } catch (e) { toast("Clients unavailable", e.message, false); } });
  qs("#closeCreate").addEventListener("click", () => qs("#createDialog").close());
  qs("#taskForm").addEventListener("submit", e => { e.preventDefault(); createTask(); });
  await load();
}

init().catch(console.error);
