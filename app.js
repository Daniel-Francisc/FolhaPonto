const viewNames = {
  dashboard: "Dashboard",
  ocr: "Conferência OCR",
  arquivo: "Arquivo de folhas",
  servidores: "Servidores",
  envios: "Fila de envios",
  auditoria: "Auditoria",
  configuracoes: "Configurações",
};

const queueData = [
  { name: "Alexandre Nata Vicente", matricula: "17289106", confidence: 78, status: "Revisão necessária", statusClass: "status-yellow", message: "Alguns campos podem precisar de revisão." },
  { name: "Ana Ribeiro", matricula: "16234018", confidence: 62, status: "Baixa confiança", statusClass: "status-red", message: "Revise os campos destacados antes de associar." },
  { name: "Caio Ferreira", matricula: "17450291", confidence: 78, status: "Revisão necessária", statusClass: "status-yellow", message: "Alguns campos podem precisar de revisão." },
  { name: "Servidor não identificado", matricula: "Não encontrada", confidence: 41, status: "Não identificado", statusClass: "status-gray", message: "A matrícula não foi localizada no cadastro." },
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function showToast(message) {
  const toast = $("#toast");
  $("#toastMessage").textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("visible"), 3200);
}

function showView(view) {
  const dashboard = $("#dashboardView");
  const ocr = $("#ocrView");
  const placeholder = $("#placeholderView");
  dashboard.classList.toggle("hidden", view !== "dashboard");
  ocr.classList.toggle("hidden", view !== "ocr");
  placeholder.classList.toggle("hidden", view === "dashboard" || view === "ocr");
  if (view !== "dashboard" && view !== "ocr") $("#placeholderTitle").textContent = viewNames[view] || "Módulo";
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view));
  $("#breadcrumbCurrent").textContent = viewNames[view] || "Módulo";
  $("#sidebar").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function selectQueue(index) {
  const item = queueData[index];
  if (!item) return;
  $$(".queue-item").forEach((queueItem, itemIndex) => queueItem.classList.toggle("selected", itemIndex === index));
  $("#queueProgress").textContent = index + 1;
  $("#reviewTitle").textContent = item.name;
  $("#reviewSubtitle").textContent = `Matrícula ${item.matricula} · Referência JULHO/2026`;
  $("#reviewStatus").textContent = item.status;
  $("#reviewStatus").className = `status-pill ${item.statusClass}`;
  $("#confidenceValue").textContent = `${item.confidence}%`;
  $("#confidenceProgress").style.width = `${item.confidence}%`;
  $("#confidenceProgress").style.background = item.confidence < 70 ? "var(--red)" : "#eab13e";
  $("#confidenceMessage").textContent = item.message;
  $("#matriculaInput").value = item.matricula === "Não encontrada" ? "" : item.matricula;
  $("#nameInput").value = item.name === "Servidor não identificado" ? "" : item.name;
  $("#paperMatricula").textContent = item.matricula;
  $("#paperName").textContent = item.name.toUpperCase();
  $("#employeeSelect").value = item.name === "Alexandre Nata Vicente" ? "Alexandre Nata Vicente · 17289106" : "";
}

function handleAction(action) {
  const name = $("#reviewTitle").textContent;
  if (action === "confirm") showToast(`${name} foi confirmado e arquivado.`);
  if (action === "pending") showToast(`${name} foi encaminhado para pendência.`);
  if (action === "reject") showToast(`Processamento de ${name} rejeitado.`);
}

$$("[data-view]").forEach((item) => item.addEventListener("click", () => showView(item.dataset.view)));
$$("[data-view-target]").forEach((item) => item.addEventListener("click", () => showView(item.dataset.viewTarget)));
$$(".queue-item").forEach((item) => item.addEventListener("click", () => selectQueue(Number(item.dataset.queueIndex))));
$("#confirmButton").addEventListener("click", () => handleAction("confirm"));
$("#pendingButton").addEventListener("click", () => handleAction("pending"));
$("#rejectButton").addEventListener("click", () => handleAction("reject"));
$("#mobileMenu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
$("#backToDashboard").addEventListener("click", () => showView("dashboard"));
$("#newBatchButton").addEventListener("click", () => showToast("Novo lote: fluxo de upload será conectado na próxima etapa."));
$("#uploadOcrButton").addEventListener("click", () => showToast("O upload em lote será conectado na próxima etapa."));
$(".notice-close").addEventListener("click", (event) => event.currentTarget.closest(".demo-notice").remove());
$("#competencySelect").addEventListener("change", (event) => showToast(`Competência alterada para ${event.target.value}.`));
$("#ocrForm").addEventListener("submit", (event) => event.preventDefault());

document.addEventListener("keydown", (event) => {
  if ($("#ocrView").classList.contains("hidden")) return;
  const current = $$(".queue-item").findIndex((item) => item.classList.contains("selected"));
  if (event.key === "ArrowDown") { event.preventDefault(); selectQueue(Math.min(current + 1, queueData.length - 1)); }
  if (event.key === "ArrowUp") { event.preventDefault(); selectQueue(Math.max(current - 1, 0)); }
});

const initialView = new URLSearchParams(window.location.search).get("view");
if (initialView && Object.prototype.hasOwnProperty.call(viewNames, initialView)) showView(initialView);