document.getElementById("year").textContent = new Date().getFullYear();

// ---- Visitor counter (Python backend) ----
(async function visitorCounter() {
  const el = document.getElementById("visit-count");
  try {
    // count each browser session once
    let counted = false;
    try { counted = sessionStorage.getItem("visited") === "1"; } catch (e) {}
    const res = await fetch("/api/visit", { method: counted ? "GET" : "POST" });
    const data = await res.json();
    el.textContent = data.visits;
    try { sessionStorage.setItem("visited", "1"); } catch (e) {}
  } catch (e) {
    el.textContent = "--";
  }
})();

// ---- Contact form (Python backend) ----
const form = document.getElementById("contact-form");
const statusEl = document.getElementById("form-status");
const btn = document.getElementById("send-btn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.className = "status";
  statusEl.textContent = "";

  const payload = {
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    message: form.message.value.trim(),
  };
  if (payload.name.length < 2 || payload.message.length < 5 || !payload.email) {
    statusEl.classList.add("err");
    statusEl.textContent = "Please fill in your name, a valid email and a short message.";
    return;
  }

  btn.disabled = true;
  btn.textContent = "Sending...";
  try {
    const res = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok) {
      statusEl.classList.add("ok");
      statusEl.textContent = data.detail;
      form.reset();
    } else {
      statusEl.classList.add("err");
      statusEl.textContent = typeof data.detail === "string"
        ? data.detail
        : "Please check your details and try again.";
    }
  } catch (err) {
    statusEl.classList.add("err");
    statusEl.textContent = "Could not reach the server. Please try again.";
  } finally {
    btn.disabled = false;
    btn.textContent = "Send message";
  }
});
