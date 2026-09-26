import { apiRequest } from "./api.js";
import { requireAuth, mountShell } from "./auth.js";

const state = { page: 1, limit: 12, search: "", sort: "created_at", order: "desc" };
let user = null;

const qs = s => document.querySelector(s);

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[ch]));
}

function showToast(title, message, good = true) {
  const stack = qs("#toastStack");
  const item = document.createElement("div");
  item.className = `toast ${good ? "good" : "bad"}`;
  item.innerHTML = `<div class="toast-title">${esc(title)}</div><div class="toast-message">${esc(message)}</div>`;
  stack.appendChild(item);
  setTimeout(() => item.remove(), 3400);
}

function renderPagination(total) {
  const totalPages = Math.max(1, Math.ceil(total / state.limit));
  const info = qs("#paginationInfo");
  info.textContent = `${total} client${total === 1 ? "" : "s"} · page ${state.page} of ${totalPages}`;
  qs("#prevPage").disabled = state.page <= 1;
  qs("#nextPage").disabled = state.page >= totalPages;
}

function renderClients(items) {
  const tbody = qs("#clientRows");
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty"><div class="empty-title">No clients found</div><div>Try another search or clear the filters.</div></div></td></tr>`;
    return;
  }
  tbody.innerHTML = items.map(client => `
    <tr>
      <td><strong>${esc(client.name)}</strong></td>
      <td>${esc(client.phone)}</td>
      <td>${client.email ? esc(client.email) : "<span class='muted'>—</span>"}</td>
      <td class="mono small">#${client.id}</td>
      <td>
        <div class="row-actions">
          <a class="btn btn-sm" href="/app/client.html?id=${client.id}">Open</a>
        </div>
      </td>
    </tr>
  `).join("");
}

async function loadClients() {
  qs("#clientRows").innerHTML = `<tr><td colspan="5"><div class="empty"><div class="skeleton" style="height:22px; width:38%; margin:0 auto 12px"></div><div class="skeleton" style="height:18px; width:55%; margin:auto"></div></div></td></tr>`;
  const params = new URLSearchParams({
    page: state.page,
    limit: state.limit,
    sort: state.sort,
    order: state.order
  });
  if (state.search.trim()) params.set("search", state.search.trim());

  try {
    const data = await apiRequest(`/clients?${params}`);
    renderClients(data.items || []);
    renderPagination(data.total || 0);
  } catch (error) {
    showToast("Could not load clients", error.message, false);
  }
}

async function createClient() {
  const form = qs("#clientForm");
  const payload = {
    name: form.name.value.trim(),
    phone: form.phone.value.trim(),
    email: form.email.value.trim() || null
  };
  try {
    await apiRequest("/clients", { method: "POST", body: JSON.stringify(payload) });
    form.reset();
    qs("#createDialog").close();
    showToast("Client created", `${payload.name} is now in your client list.`);
    await loadClients();
  } catch (error) {
    showToast("Could not create client", error.message, false);
  }
}

async function init() {
  user = await requireAuth();
  mountShell(user);
  if (user.role === "admin") {
    document.querySelectorAll("[data-admin-only]").forEach(
        el => el.hidden = false
    );
}

  qs("#search").addEventListener("input", e => {
    state.search = e.target.value;
    state.page = 1;
    clearTimeout(window.__searchTimer);
    window.__searchTimer = setTimeout(loadClients, 260);
  });
  qs("#sort").addEventListener("change", e => { state.sort = e.target.value; state.page = 1; loadClients(); });
  qs("#order").addEventListener("change", e => { state.order = e.target.value; state.page = 1; loadClients(); });
  qs("#prevPage").addEventListener("click", () => { state.page--; loadClients(); });
  qs("#nextPage").addEventListener("click", () => { state.page++; loadClients(); });
  qs("#clientForm").addEventListener("submit", e => { e.preventDefault(); createClient(); });
  qs("#openCreate").addEventListener("click", () => qs("#createDialog").showModal());
  qs("#closeCreate").addEventListener("click", () => qs("#createDialog").close());
  await loadClients();
}

init().catch(console.error);
