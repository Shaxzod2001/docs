// ---------- Yordamchilar ----------
async function api(path, opts = {}) {
    const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...opts,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Xato" }));
        throw new Error(err.detail || res.statusText);
    }
    return res.json();
}

function toast(msg, type = "ok") {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = `toast show ${type}`;
    setTimeout(() => (t.className = "toast"), 3500);
}

function esc(s) {
    return (s || "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

// ---------- Tab navigatsiya ----------
document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
        document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
        item.classList.add("active");
        const tab = item.dataset.tab;
        document.getElementById(tab).classList.add("active");
        if (tab === "dashboard") loadDashboard();
        if (tab === "posts") loadPosts();
        if (tab === "subscribers") loadSubs();
    });
});

// ---------- Holat ----------
async function loadStatus() {
    try {
        const s = await api("/api/status");
        const el = document.getElementById("tg-status");
        const modeLabel = s.mode === "user" ? "to'liq rejim" : (s.mode === "bot" ? "bot rejimi" : "sozlanmagan");
        if (s.telegram_authorized) {
            el.textContent = "🟢 Telegram ulangan";
            el.className = "status-pill ok";
        } else {
            const hint = s.mode === "user" ? "sessiya yo'q (login.py)" : "token tekshiring (.env)";
            el.textContent = "🔴 Ulanmagan — " + hint;
            el.className = "status-pill bad";
        }
        document.getElementById("auto-times").innerHTML =
            "<b>Rejim:</b> " + modeLabel + "<br><b>Avtomatik post vaqtlari:</b> " +
            (s.auto_post_times.join(", ") || "yo'q");
    } catch (e) { /* ignore */ }
}

// ---------- Dashboard ----------
let growthChart = null;
async function loadDashboard() {
    try {
        const d = await api("/api/dashboard");
        document.getElementById("stat-subs").textContent = d.subscriber_count ?? "—";
        document.getElementById("stat-views").textContent = d.total_views ?? 0;
        document.getElementById("stat-reactions").textContent = d.total_reactions ?? 0;
        document.getElementById("stat-scheduled").textContent = d.scheduled_count ?? 0;

        const labels = d.snapshots.map(s => new Date(s.timestamp).toLocaleDateString("uz"));
        const data = d.snapshots.map(s => s.subscriber_count);
        const ctx = document.getElementById("growthChart");
        if (growthChart) growthChart.destroy();
        growthChart = new Chart(ctx, {
            type: "line",
            data: { labels, datasets: [{
                label: "Obunachilar", data,
                borderColor: "#3b82f6", backgroundColor: "rgba(59,130,246,0.1)",
                fill: true, tension: 0.3,
            }]},
            options: {
                plugins: { legend: { labels: { color: "#8a97a6" } } },
                scales: {
                    x: { ticks: { color: "#8a97a6" }, grid: { color: "#2c3744" } },
                    y: { ticks: { color: "#8a97a6" }, grid: { color: "#2c3744" } },
                },
            },
        });

        const tp = document.getElementById("top-posts");
        if (!d.top_posts.length) {
            tp.innerHTML = '<div class="empty">Hali statistika yo\'q. "Yangilash" tugmasini bosing.</div>';
        } else {
            tp.innerHTML = d.top_posts.map(p => `
                <div class="list-item">
                    <div class="preview">${esc(p.content.slice(0, 120))}...</div>
                    <div class="meta"><span>👁 ${p.views}</span><span>❤️ ${p.reactions}</span></div>
                </div>`).join("");
        }
    } catch (e) { toast(e.message, "err"); }
}

async function syncStats() {
    toast("⏳ Statistika yangilanmoqda...");
    try {
        const r = await api("/api/sync", { method: "POST" });
        toast(`✅ Yangilandi: ${r.subscriber_count} obunachi`);
        loadDashboard();
    } catch (e) { toast(e.message, "err"); }
}

// ---------- Postlar ----------
let currentImageUrl = null;
let currentImagePrompt = null;

function showImage(url) {
    currentImageUrl = url;
    const wrap = document.getElementById("image-wrap");
    const img = document.getElementById("post-image");
    if (url) {
        wrap.style.display = "block";
        img.style.opacity = "0.4";
        img.onload = () => { img.style.opacity = "1"; };
        img.onerror = () => { toast("Rasm yuklanmadi, '🔄 Boshqa rasm' ni bosing", "err"); };
        img.src = url;
    } else {
        wrap.style.display = "none";
    }
}

function removeImage() { showImage(null); currentImagePrompt = null; toast("Rasm olib tashlandi"); }

function regenImage() {
    if (!currentImageUrl) return toast("Avval post yarating", "err");
    const seed = Math.floor(Math.random() * 1000000);
    // Mavjud URL dagi seed ni almashtirish (uslub bir xil qoladi)
    const url = currentImageUrl.replace(/seed=\d+/, "seed=" + seed);
    showImage(url);
    toast("🔄 Yangi rasm yuklanmoqda...");
}

async function generatePost() {
    const topic = document.getElementById("topic-input").value.trim();
    const withImage = document.getElementById("with-image").checked;
    toast("🤖 AI post yaratmoqda...");
    try {
        const r = await api("/api/posts/generate", {
            method: "POST", body: JSON.stringify({ topic: topic || null, with_image: withImage }),
        });
        document.getElementById("post-content").value = r.content;
        currentImagePrompt = r.image_prompt || null;
        showImage(r.image_url || null);
        toast("✅ Post tayyor!");
    } catch (e) { toast(e.message, "err"); }
}

async function loadIdeas() {
    document.getElementById("ideas-box").innerHTML = '<p class="muted">⏳ G\'oyalar yuklanmoqda...</p>';
    try {
        const r = await api("/api/posts/ideas");
        document.getElementById("ideas-box").innerHTML =
            `<div class="list-item"><div class="preview">${esc(r.ideas)}</div></div>`;
    } catch (e) { toast(e.message, "err"); }
}

async function sendNow() {
    const content = document.getElementById("post-content").value.trim();
    if (!content) return toast("Post matni bo'sh!", "err");
    toast("🚀 Yuborilmoqda...");
    try {
        await api("/api/posts", { method: "POST", body: JSON.stringify({ content, image_url: currentImageUrl, send_now: true }) });
        toast("✅ Post kanalga yuborildi!");
        document.getElementById("post-content").value = "";
        showImage(null);
        loadPosts();
    } catch (e) { toast(e.message, "err"); }
}

async function schedulePost() {
    const content = document.getElementById("post-content").value.trim();
    const dt = document.getElementById("schedule-time").value;
    if (!content) return toast("Post matni bo'sh!", "err");
    if (!dt) return toast("Vaqtni tanlang!", "err");
    const scheduled_time = dt.replace("T", " ").slice(0, 16);
    try {
        await api("/api/posts", { method: "POST", body: JSON.stringify({ content, image_url: currentImageUrl, scheduled_time }) });
        toast("✅ Post rejalashtirildi!");
        document.getElementById("post-content").value = "";
        showImage(null);
        loadPosts();
    } catch (e) { toast(e.message, "err"); }
}

async function loadPosts() {
    try {
        const r = await api("/api/posts");
        const el = document.getElementById("posts-list");
        if (!r.posts.length) {
            el.innerHTML = '<div class="empty">Hali post yo\'q.</div>';
            return;
        }
        el.innerHTML = r.posts.map(p => {
            const time = p.scheduled_time || p.sent_time || p.created_at || "";
            return `<div class="list-item">
                ${p.image_url ? `<img class="post-image" src="${esc(p.image_url)}" alt="">` : ""}
                <div class="preview">${esc(p.content.slice(0, 200))}${p.content.length > 200 ? "..." : ""}</div>
                <div class="meta">
                    <span class="badge ${p.status}">${p.status}</span>
                    <span>🕐 ${time.slice(0, 16).replace("T", " ")}</span>
                    ${p.status === "sent" ? `<span>👁 ${p.views} ❤️ ${p.reactions}</span>` : ""}
                </div>
                <div class="item-actions">
                    ${p.status !== "sent" ? `<button class="btn primary" onclick="sendPost(${p.id})">🚀 Yuborish</button>` : ""}
                    <button class="btn" onclick="deletePost(${p.id})">🗑 O'chirish</button>
                </div>
            </div>`;
        }).join("");
    } catch (e) { toast(e.message, "err"); }
}

async function sendPost(id) {
    try { await api(`/api/posts/${id}/send`, { method: "POST" }); toast("✅ Yuborildi!"); loadPosts(); }
    catch (e) { toast(e.message, "err"); }
}
async function deletePost(id) {
    if (!confirm("O'chirilsinmi?")) return;
    try { await api(`/api/posts/${id}`, { method: "DELETE" }); toast("🗑 O'chirildi"); loadPosts(); }
    catch (e) { toast(e.message, "err"); }
}

// ---------- Obunachilar ----------
async function loadSubs() {
    try {
        const r = await api("/api/subscribers");
        const el = document.getElementById("subs-list");
        if (!r.subscribers.length) {
            el.innerHTML = '<div class="empty">Obunachilar yuklanmagan. "Ro\'yxatni yangilash" ni bosing.</div>';
            return;
        }
        el.innerHTML = r.subscribers.map(s => `
            <div class="sub-row">
                <div>
                    <div class="sub-name">${esc(s.first_name || "—")} ${s.is_bot ? "🤖" : ""}</div>
                    <div class="sub-handle">${s.username ? "@" + esc(s.username) : "id: " + s.user_id}</div>
                </div>
                <div class="sub-interests">${esc(s.interests || "")}</div>
            </div>`).join("");
    } catch (e) { toast(e.message, "err"); }
}

async function syncSubs() {
    toast("⏳ Obunachilar yuklanmoqda...");
    try { const r = await api("/api/subscribers/sync", { method: "POST" }); toast(`✅ ${r.synced} obunachi`); loadSubs(); }
    catch (e) { toast(e.message, "err"); }
}

async function analyzeInterests() {
    toast("🎯 Qiziqishlar aniqlanmoqda (biroz vaqt oladi)...");
    try {
        const r = await api("/api/subscribers/analyze", { method: "POST" });
        toast(`✅ ${r.analyzed} obunachi tahlil qilindi`);
        loadSubs();
    } catch (e) { toast(e.message, "err"); }
}

async function loadInsights() {
    document.getElementById("insights-box").textContent = "⏳ Tahlil qilinmoqda...";
    try {
        const r = await api("/api/subscribers/insights");
        document.getElementById("insights-box").textContent = r.analysis;
    } catch (e) { toast(e.message, "err"); }
}

// ---------- Boshlash ----------
loadStatus();
loadDashboard();
setInterval(loadStatus, 30000);
