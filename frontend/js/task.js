import { apiRequest } from "./api.js";
import { requireAuth, mountShell } from "./auth.js";
import { loadComments, addComment, esc } from "./comments.js";

const id = new URLSearchParams(location.search).get("id");
const isAdmin = new URLSearchParams(location.search).get("admin") === "1";
const qs = s => document.querySelector(s);

function statusBadge(status) {
  const label = status === "in_progress" ? "In progress" : status;
  return `<span class="badge">${esc(label)}</span>`;
}

function fill(task) {
  qs("#taskTitle").textContent = task.title;
  qs("#taskMeta").textContent = `Task #${task.id} · Client #${task.client_id}`;
  qs("#title").value = task.title;
  qs("#description").value = task.description;
  qs("#deadline").value = new Date(task.deadline).toISOString().slice(0,16);
  qs("#status").value = task.status;
  qs("#manager").textContent = `#${task.manager_id}`;
  qs("#client").textContent = `#${task.client_id}`;
  qs("#created").textContent = new Date(task.created_at).toLocaleString();
  qs("#statusView").innerHTML = statusBadge(task.status);
}

async function init() {
  const user = await requireAuth();
  mountShell(user);
  if (!id) { location.href = "/app/tasks.html"; return; }

  const task = await apiRequest(isAdmin ? `/admin/tasks/${id}` : `/tasks/${id}`);
  fill(task);
  await loadComments(id, qs("#comments"));

  qs("#editForm").addEventListener("submit", async e => {
    e.preventDefault();
    if (isAdmin) return;
    const payload = {
      title: qs("#title").value.trim(),
      description: qs("#description").value.trim(),
      status: qs("#status").value,
      deadline: new Date(qs("#deadline").value).toISOString()
    };
    try { await apiRequest(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(payload) }); alert("Task updated."); }
    catch (error) { alert(error.message); }
  });

  qs("#commentForm").addEventListener("submit", async e => {
    e.preventDefault();
    const text = qs("#commentText").value.trim();
    if (!text) return;
    try { await addComment(id, text); qs("#commentText").value = ""; await loadComments(id, qs("#comments")); }
    catch (error) { alert(error.message); }
  });

  qs("#deleteTask").addEventListener("click", async () => {
    if (isAdmin || !confirm("Delete this task?")) return;
    try { await apiRequest(`/tasks/${id}`, { method: "DELETE" }); location.href = "/app/tasks.html"; }
    catch (error) { alert(error.message); }
  });

  if (isAdmin) {
    qs("#deleteTask").hidden = true;
    qs("#editForm").querySelectorAll("input,select,textarea,button").forEach(el => el.disabled = true);
    qs("#commentForm").hidden = true;
  }
}

init().catch(error => { alert(error.message); console.error(error); });
