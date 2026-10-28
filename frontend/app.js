// Клиентская часть: карточки туров, бронирование, вход администратора.
// Все запросы идут на тот же адрес (/api/...), их направляет контейнер proxy.

const $ = (id) => document.getElementById(id);
// Экранирование: имя клиента вводит пользователь, его нельзя вставлять в HTML как есть
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let selectedTour = null;
let adminPassword = null;   // хранится только в памяти страницы

// ---- Карточки туров ----
async function loadTours() {
  const tours = await (await fetch("/api/tours")).json();
  $("tours").innerHTML = tours.map((t) => `
    <div class="card">
      <div class="art">${esc(t.emoji)}</div>
      <div class="body">
        <h3>${esc(t.title)}</h3>
        <p>${esc(t.description)}</p>
        <div class="row">
          <span class="price">${Number(t.price).toLocaleString("ru-RU")} ₽</span>
          <button data-id="${t.id}" data-title="${esc(t.title)}">Забронировать</button>
        </div>
      </div>
    </div>`).join("");
  document.querySelectorAll("#tours button").forEach((b) =>
    b.addEventListener("click", () => {
      selectedTour = b.dataset.id;
      $("booking-title").textContent = b.dataset.title;
      $("booking-error").hidden = true;
      $("booking-dialog").showModal();
    }));
}

// ---- Бронирование ----
$("booking-cancel").onclick = () => $("booking-dialog").close();
$("booking-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const res = await fetch("/api/bookings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tour_id: Number(selectedTour), customer_name: f.get("customer_name"), people: Number(f.get("people")) }),
  });
  if (!res.ok) {
    $("booking-error").textContent = "Не удалось забронировать";
    $("booking-error").hidden = false;
    return;
  }
  $("booking-dialog").close();
  e.target.reset();
  alert("Бронирование принято!");
  if (adminPassword) loadBookings();
});

// ---- Администратор ----
async function loadBookings() {
  const res = await fetch("/api/bookings", { headers: { "X-Admin-Password": adminPassword } });
  if (!res.ok) return false;
  const rows = await res.json();
  $("bookings").innerHTML = rows.map((r) =>
    `<tr><td>${r.id}</td><td>${esc(r.title)}</td><td>${esc(r.customer_name)}</td><td>${r.people}</td></tr>`).join("");
  $("admin").hidden = false;
  return true;
}

$("admin-btn").onclick = () => { $("admin-error").hidden = true; $("admin-dialog").showModal(); };
$("admin-cancel").onclick = () => $("admin-dialog").close();
$("admin-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  adminPassword = new FormData(e.target).get("password");
  if (await loadBookings()) {
    $("admin-dialog").close();
    e.target.reset();
  } else {
    adminPassword = null;
    $("admin-error").textContent = "Неверный пароль";
    $("admin-error").hidden = false;
  }
});

loadTours();
