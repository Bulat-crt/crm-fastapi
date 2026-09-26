import { apiRequest } from "./api.js";

export function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[ch]));
}

export async function loadComments(taskId, container) {
  try {
    const items = await apiRequest(`/tasks/${taskId}/comments`);
    if (!items.length) {
      container.innerHTML = `<div class="empty"><div class="empty-title">No comments yet</div><div>Start the conversation around this task.</div></div>`;
      return items;
    }
    container.innerHTML = items.map(comment => `
      <article class="comment">
        <div class="comment-head">
          <div><strong>Member #${comment.user_id}</strong><div class="muted small">${new Date(comment.created_at).toLocaleString()}</div></div>
          <button class="btn btn-sm btn-danger" data-delete-comment="${comment.id}">Delete</button>
        </div>
        <div class="comment-text">${esc(comment.text_comment)}</div>
      </article>
    `).join("");

    container.querySelectorAll("[data-delete-comment]").forEach(button => {
      button.addEventListener("click", async () => {
        if (!confirm("Delete this comment?")) return;
        try {
          await apiRequest(`/comments/${button.dataset.deleteComment}`, { method: "DELETE" });
          await loadComments(taskId, container);
        } catch (error) {
          alert(error.message);
        }
      });
    });
    return items;
  } catch (error) {
    container.innerHTML = `<div class="empty"><div class="empty-title">Comments unavailable</div><div>${esc(error.message)}</div></div>`;
    return [];
  }
}

export async function addComment(taskId, text) {
  return apiRequest(`/tasks/${taskId}/comments`, {
    method: "POST",
    body: JSON.stringify({ text })
  });
}
