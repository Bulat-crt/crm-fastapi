import { apiRequest } from "./api.js";
import { requireAuth, mountShell } from "./auth.js";

const qs = s => document.querySelector(s);

function renderTaskCards(items) {
  const target = qs("#recentTasks");
  if (!items.length) {
    target.innerHTML = `<div class="empty"><div class="empty-title">No tasks yet</div><div>Create your first task from the Tasks page.</div></div>`;
    return;
  }
  target.innerHTML = items.slice(0, 5).map(task => `
    <a class="card" href="/app/task.html?id=${task.id}" style="display:block">
      <div class="card-title"><strong>${task.title}</strong><span class="badge">${task.status}</span></div>
      <div class="muted small">Due ${new Date(task.deadline).toLocaleString()} · Client #${task.client_id}</div>
    </a>
  `).join("");
}

async function init() {
  const user = await requireAuth();
  mountShell(user);

  try {
    const [clients, tasks] = await Promise.all([
      user.role === "admin" ? apiRequest("/admin/clients?page=1&limit=1") : apiRequest("/clients?page=1&limit=1"),
      user.role === "admin" ? apiRequest("/admin/tasks?page=1&limit=100") : apiRequest("/tasks?page=1&limit=100&sort=deadline&order=asc")
    ]);

    qs("#clientsCount").textContent = clients.total ?? 0;
    qs("#tasksCount").textContent = tasks.total ?? 0;
    const done = (tasks.items || []).filter(task => task.status === "done").length;
    const active = (tasks.items || []).filter(task => task.status !== "done").length;
    qs("#doneCount").textContent = done;
    qs("#activeCount").textContent = active;
    renderTaskCards(tasks.items || []);
  } catch (error) {
    qs("#recentTasks").innerHTML = `<div class="empty"><div class="empty-title">Dashboard data unavailable</div><div>${error.message}</div></div>`;
  }
}

init().catch(console.error);
