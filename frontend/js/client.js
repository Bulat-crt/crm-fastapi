import { apiRequest } from "./api.js";
import { requireAuth, mountShell } from "./auth.js";

const id = new URLSearchParams(location.search).get("id");
const qs = s => document.querySelector(s);

function esc(value) { return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[ch])); }

function fill(client) {
  qs("#clientTitle").textContent = client.name;
  qs("#clientMeta").textContent = `Client #${client.id}`;
  qs("#name").value = client.name;
  qs("#phone").value = client.phone;
  qs("#email").value = client.email || "";
  qs("#manager").textContent = `#${client.manager_id}`;
  qs("#created").textContent = new Date(client.created_at).toLocaleString();
}

async function init() {
  const user = await requireAuth();
  mountShell(user);
  if (!id) { location.href = "/app/clients.html"; return; }

  const isAdmin = new URLSearchParams(location.search).get("admin") === "1";
  const client = await apiRequest(isAdmin ? `/admin/clients/${id}` : `/clients/${id}`);
  fill(client);

  qs("#editForm").addEventListener("submit", async e => {
    e.preventDefault();
    try {
      await apiRequest(`/clients/${id}`, { method: "PUT", body: JSON.stringify({ name: qs("#name").value.trim(), phone: qs("#phone").value.trim(), email: qs("#email").value.trim() || null }) });
      alert("Client updated.");
    } catch (error) { alert(error.message); }
  });

  if (!isAdmin) {
    qs("#deleteClient").addEventListener("click", async () => {
      if (!confirm("Delete this client?")) return;
      try { await apiRequest(`/clients/${id}`, { method: "DELETE" }); location.href = "/app/clients.html"; }
      catch (error) { alert(error.message); }
    });
  } else {
    qs("#deleteClient").hidden = true;
    qs("#editForm").querySelectorAll("input,button").forEach(el => { if (el.id !== "deleteClient") el.disabled = true; });
  }
}

init().catch(error => { alert(error.message); console.error(error); });
