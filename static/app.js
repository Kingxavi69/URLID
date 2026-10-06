const form = document.querySelector("#lookup-form");
const targetInput = document.querySelector("#target-input");
const resolveButton = document.querySelector("#resolve-button");
const resultPanel = document.querySelector("#result-panel");
const formError = document.querySelector("#form-error");
const resultStatus = document.querySelector("#result-status");
const statusLabel = document.querySelector("#status-label");
const resultHost = document.querySelector("#result-host");
const resultType = document.querySelector("#result-type");
const ipList = document.querySelector("#ip-list");
const addressCount = document.querySelector("#address-count");
const resultNote = document.querySelector("#result-note");
const sponsorPopup = document.querySelector("#sponsor-popup");
const closePopup = document.querySelector("#close-popup");

function setLoading(loading) {
  resolveButton.disabled = loading;
  resolveButton.querySelector(".button-label").textContent = loading ? "Resolving" : "Resolve";
  targetInput.disabled = loading;
}

function copyButtonFor(value) {
  const button = document.createElement("button");
  button.className = "copy-button";
  button.type = "button";
  button.textContent = "Copy IP";
  button.setAttribute("aria-label", `Copy IP address ${value}`);
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(value);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Copy unavailable";
    }
    window.setTimeout(() => { button.textContent = "Copy IP"; }, 1400);
  });
  return button;
}

function renderResult(data) {
  resultPanel.hidden = false;
  formError.hidden = true;
  const state = data.status || "unresolved";
  resultStatus.dataset.state = state;
  statusLabel.textContent = state === "resolved" ? "Resolved" : state === "invalid" ? "Invalid target" : "No DNS answer";
  resultHost.textContent = data.host || (data.ips?.length ? data.url : "No hostname found");
  resultType.textContent = data.type || "Unknown";
  const addresses = Array.isArray(data.ips) ? data.ips : [];
  addressCount.textContent = String(addresses.length);
  ipList.replaceChildren();

  for (const address of addresses) {
    const row = document.createElement("div");
    row.className = "ip-row";
    const value = document.createElement("span");
    value.className = "ip-value";
    value.textContent = address;
    row.append(value, copyButtonFor(address));
    ipList.append(row);
  }

  if (state === "invalid") {
    resultNote.textContent = "Enter a URL using HTTP or HTTPS, a domain name, or a valid IP address.";
  } else if (state === "unresolved") {
    resultNote.textContent = addresses.length ? "No reverse-DNS hostname was returned for this IP." : "No address records were returned. Check the target and your DNS connection.";
  } else {
    resultNote.textContent = "Host type is inferred from the hostname; it is not a verification of the site's purpose.";
  }
}

async function resolveTarget(value) {
  const target = value.trim();
  formError.hidden = true;
  if (!target) {
    formError.textContent = "Enter a URL, domain, or IP address to continue.";
    formError.hidden = false;
    targetInput.focus();
    return;
  }

  setLoading(true);
  try {
    const response = await fetch("/api/lookup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The lookup request failed.");
    renderResult(data);
  } catch (error) {
    formError.textContent = error instanceof Error ? error.message : "The lookup could not be completed.";
    formError.hidden = false;
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  resolveTarget(targetInput.value);
});

document.querySelectorAll(".example-chip").forEach((button) => {
  button.addEventListener("click", () => {
    targetInput.value = button.dataset.value || "";
    resolveTarget(targetInput.value);
  });
});

function dismissSponsorPopup() {
  if (sponsorPopup.open) sponsorPopup.close();
  try { sessionStorage.setItem("urlid-sponsor-dismissed", "1"); } catch { /* Storage may be disabled. */ }
}

closePopup.addEventListener("click", dismissSponsorPopup);
sponsorPopup.addEventListener("click", (event) => {
  if (event.target === sponsorPopup) dismissSponsorPopup();
});

let sponsorDismissed = false;
try { sponsorDismissed = sessionStorage.getItem("urlid-sponsor-dismissed") === "1"; } catch { sponsorDismissed = true; }
if (!sponsorDismissed) {
  window.setTimeout(() => {
    if (!sponsorPopup.open) sponsorPopup.show();
  }, 6500);
}
