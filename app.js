const viewNames = {
  dashboard: "Dashboard",
  ocr: "Conferência OCR",
  arquivo: "Arquivo de folhas",
  servidores: "Servidores",
  envios: "Fila de envios",
  auditoria: "Auditoria",
  historico: "Histórico",
  usuarios: "Usuários",
  "novo-lote": "Novo lote",
  configuracoes: "Configurações",
  login: "Acesso ao sistema",
};

let queueData = [];
let selectedIndex = 0;
let selectedTimesheetId = null;
let employees = [];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

async function apiFetch(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "Não foi possível concluir a operação.");
  return body;
}

function showToast(message, error = false) {
  const toast = $("#toast");
  $("#toastMessage").textContent = message;
  toast.classList.add("visible");
  toast.querySelector(".toast-icon").textContent = error ? "!" : "✓";
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("visible"), 3600);
}

function showView(view) {
  const isLogin = view === "login";
  $(".app-shell").classList.toggle("hidden", isLogin);
  $("#loginView").classList.toggle("hidden", !isLogin);
  if (isLogin) return;
  $("#dashboardView").classList.toggle("hidden", view !== "dashboard");
  $("#ocrView").classList.toggle("hidden", view !== "ocr");
  $("#placeholderView").classList.toggle("hidden", view === "dashboard" || view === "ocr");
  if (view !== "dashboard" && view !== "ocr") $("#placeholderTitle").textContent = viewNames[view] || "Módulo";
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view));
  $("#breadcrumbCurrent").textContent = viewNames[view] || "Módulo";
  $("#sidebar").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function statusClass(status) {
  return {
    reconhecida: "status-green",
    arquivada: "status-green",
    revisao: "status-yellow",
    pendente: "status-yellow",
    baixa_confianca: "status-red",
    rejeitada: "status-red",
    nao_identificado: "status-gray",
  }[status] || "status-gray";
}

function statusLabel(status) {
  return {
    reconhecida: "Reconhecida",
    arquivada: "Arquivada",
    revisao: "Revisão necessária",
    pendente: "Pendente",
    baixa_confianca: "Baixa confiança",
    rejeitada: "Rejeitada",
    nao_identificado: "Não identificado",
  }[status] || status;
}

async function loadDashboard() {
  const competency = $("#competencySelect").value;
  const data = await apiFetch(`/api/dashboard?competency=${encodeURIComponent(competency)}`);
  const values = [data.total, data.recognized, data.review, data.low_confidence];
  $$(".metric-number").forEach((node, index) => { node.textContent = values[index] ?? 0; });
  const percent = data.recognition_rate || 0;
  $(".progress-summary strong").textContent = `${percent}%`;
  $(".progress-track.large span").style.width = `${percent}%`;
  $(".progress-summary span").textContent = `${data.recognized} de ${data.total} folhas reconhecidas automaticamente`;
  const legendValues = [data.recognized, data.review, data.low_confidence];
  $$(".legend-grid strong").forEach((node, index) => { node.textContent = legendValues[index] ?? 0; });
  const miniValues = $$(".mini-stat-row strong");
  if (miniValues[1]) miniValues[1].textContent = data.archived;
}

function updateEmployeeSelect() {
  const select = $("#employeeSelect");
  select.innerHTML = '<option value="">Selecione um servidor</option>';
  employees.forEach((employee) => {
    const option = document.createElement("option");
    option.value = employee.id;
    option.textContent = `${employee.name} · ${employee.matricula}`;
    select.appendChild(option);
  });
}

function selectQueue(index) {
  const item = queueData[index];
  if (!item) return;
  selectedIndex = index;
  selectedTimesheetId = item.id;
  $$(".queue-item").forEach((queueItem, itemIndex) => queueItem.classList.toggle("selected", itemIndex === index));
  $("#queueProgress").textContent = index + 1;
  $("#reviewTitle").textContent = item.name;
  $("#reviewSubtitle").textContent = `Matrícula ${item.matricula || "não encontrada"} · Referência ${item.competencia}`;
  $("#reviewStatus").textContent = item.status_label || statusLabel(item.status);
  $("#reviewStatus").className = `status-pill ${statusClass(item.status)}`;
  $("#confidenceValue").textContent = `${item.confidence}%`;
  $("#confidenceProgress").style.width = `${item.confidence}%`;
  $("#confidenceProgress").style.background = item.confidence < 70 ? "var(--red)" : "#eab13e";
  $("#confidenceMessage").textContent = item.confidence < 70
    ? "Revise os campos destacados antes de associar."
    : "Alguns campos podem precisar de revisão.";
  $("#matriculaInput").value = item.matricula || "";
  $("#nameInput").value = item.name === "Servidor não identificado" ? "" : item.name;
  $("#employeeSelect").value = item.employee_id ? String(item.employee_id) : "";
  $("#paperMatricula").textContent = item.matricula || "—";
  $("#paperName").textContent = item.name.toUpperCase();
  $("#noteInput").value = item.note || "";
}

async function loadQueue() {
  const rows = await apiFetch(`/api/timesheets?competency=${encodeURIComponent($("#competencySelect").value)}`);
  queueData = rows.filter((row) => !["arquivada", "rejeitada"].includes(row.status));
  const queueItems = $$(".queue-item");
  queueItems.forEach((node, index) => {
    const item = queueData[index];
    node.classList.toggle("hidden", !item);
    if (!item) return;
    node.dataset.timesheetId = item.id;
    node.querySelector(".queue-item-copy strong").textContent = item.name;
    node.querySelector(".queue-item-copy > span").textContent = `Mat. ${item.matricula || "não encontrada"} · ${item.competencia}`;
    const pill = node.querySelector(".status-pill");
    pill.textContent = item.status_label || statusLabel(item.status);
    pill.className = `status-pill ${statusClass(item.status)}`;
    node.querySelector(".queue-confidence").textContent = `${item.confidence}%`;
  });
  $("#queueProgress").textContent = queueData.length ? "1" : "0";
  $(".queue-count").textContent = String(queueData.length).padStart(2, "0");
  const pendingText = $(".ocr-toolbar-copy strong");
  if (pendingText) pendingText.textContent = `${queueData.length} folhas aguardando conferência`;
  if (queueData.length) selectQueue(Math.min(selectedIndex, queueData.length - 1));
}

async function loadData() {
  try {
    [employees] = await Promise.all([
      apiFetch("/api/employees"),
      loadDashboard(),
    ]);
    updateEmployeeSelect();
    await loadQueue();
  } catch (error) {
    showToast(`API indisponível: ${error.message}`, true);
  }
}

async function reviewAction(action) {
  if (!selectedTimesheetId) return showToast("Selecione uma folha para continuar.", true);
  try {
    let result;
    if (action === "confirm") {
      const employeeId = $("#employeeSelect").value ? Number($("#employeeSelect").value) : null;
      result = await apiFetch(`/api/timesheets/${selectedTimesheetId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: $("#nameInput").value.trim() || "Servidor não identificado",
          matricula: $("#matriculaInput").value.trim() || null,
          competencia: "JULHO/2026",
          employee_id: employeeId,
          note: $("#noteInput").value.trim(),
        }),
      });
    } else if (action === "pending") {
      result = await apiFetch(`/api/timesheets/${selectedTimesheetId}/pending?note=${encodeURIComponent($("#noteInput").value.trim())}`, { method: "POST" });
    } else {
      result = await apiFetch(`/api/timesheets/${selectedTimesheetId}/reject`, { method: "POST" });
    }
    showToast(`${result.name} atualizado: ${result.status_label}.`);
    await Promise.all([loadDashboard(), loadQueue()]);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function uploadBatch() {
  const input = $("#batchFileInput");
  const file = input.files[0];
  if (!file) return;
  const form = new FormData();
  form.append("file", file);
  try {
    const result = await apiFetch("/api/batches", { method: "POST", body: form });
    showToast(`Lote processado: ${result.pages} página(s) em modo ${result.mode}.`);
    showView("ocr");
    await Promise.all([loadDashboard(), loadQueue()]);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    input.value = "";
  }
}

$$("[data-view]").forEach((item) => item.addEventListener("click", () => showView(item.dataset.view)));
$$("[data-view-target]").forEach((item) => item.addEventListener("click", () => showView(item.dataset.viewTarget)));
$$(".queue-item").forEach((item) => item.addEventListener("click", () => {
  const index = $$(".queue-item").indexOf(item);
  selectQueue(index);
}));
$("#confirmButton").addEventListener("click", () => reviewAction("confirm"));
$("#pendingButton").addEventListener("click", () => reviewAction("pending"));
$("#rejectButton").addEventListener("click", () => reviewAction("reject"));
$("#mobileMenu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
$("#backToDashboard").addEventListener("click", () => showView("dashboard"));
$("#newBatchButton").addEventListener("click", () => $("#batchFileInput").click());
$("#uploadOcrButton").addEventListener("click", () => $("#batchFileInput").click());
$("#batchFileInput").addEventListener("change", uploadBatch);
$(".notice-close").addEventListener("click", (event) => event.currentTarget.closest(".demo-notice").remove());
$("#competencySelect").addEventListener("change", async (event) => {
  showToast(`Competência alterada para ${event.target.value}.`);
  await Promise.all([loadDashboard(), loadQueue()]);
});
$("#ocrForm").addEventListener("submit", (event) => event.preventDefault());
$("#aboutButton").addEventListener("click", () => $("#aboutModal").classList.remove("hidden"));
$("#aboutClose").addEventListener("click", () => $("#aboutModal").classList.add("hidden"));
$("#aboutModal").addEventListener("click", (event) => {
  if (event.target.id === "aboutModal") $("#aboutModal").classList.add("hidden");
});
$("#logoutButton").addEventListener("click", () => showView("login"));
$("#togglePassword").addEventListener("click", () => {
  const password = $("#loginPassword");
  const visible = password.type === "text";
  password.type = visible ? "password" : "text";
  $("#togglePassword").textContent = visible ? "Mostrar" : "Ocultar";
});
$("#loginForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const user = $("#loginUser").value.trim();
  const password = $("#loginPassword").value.trim();
  if (!user || !password) {
    $("#loginError").classList.remove("hidden");
    return;
  }
  $("#loginError").classList.add("hidden");
  showView("dashboard");
  showToast("Acesso demonstrativo realizado.");
});

document.addEventListener("keydown", (event) => {
  if ($("#ocrView").classList.contains("hidden")) return;
  if (event.key === "ArrowDown") { event.preventDefault(); selectQueue(Math.min(selectedIndex + 1, queueData.length - 1)); }
  if (event.key === "ArrowUp") { event.preventDefault(); selectQueue(Math.max(selectedIndex - 1, 0)); }
});

const initialView = new URLSearchParams(window.location.search).get("view");
if (initialView && Object.prototype.hasOwnProperty.call(viewNames, initialView)) showView(initialView);
loadData();