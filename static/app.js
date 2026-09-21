/**
 * BCSFE Web Edition - Frontend Application Logic
 */

// State
let currentSaveData = null;
let currentSaveBase64 = null;

// DOM Elements
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const saveStatusBar = document.getElementById("saveStatusBar");
const saveStatusDot = document.getElementById("saveStatusDot");
const saveStatusText = document.getElementById("saveStatusText");
const saveStatusPills = document.getElementById("saveStatusPills");
const pillRegion = document.getElementById("pillRegion");
const pillVersion = document.getElementById("pillVersion");
const pillUR = document.getElementById("pillUR");

// Quick Stats
const quickStatCatfood = document.getElementById("quickStatCatfood");
const quickStatXp = document.getElementById("quickStatXp");
const quickStatLeadership = document.getElementById("quickStatLeadership");
const quickStatRareTickets = document.getElementById("quickStatRareTickets");
const quickStatCats = document.getElementById("quickStatCats");

// Tab Navigation
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");

tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const targetTab = btn.getAttribute("data-tab");
    tabButtons.forEach(b => b.classList.remove("active"));
    tabPanels.forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    const panel = document.getElementById(targetTab);
    if (panel) panel.classList.add("active");
  });
});

// Toast System
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  const icon = type === "success" ? "✅" : type === "error" ? "❌" : "⚠️";
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Helper Functions for Presets
function setVal(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val;
}

function addVal(id, delta) {
  const el = document.getElementById(id);
  if (el) el.value = (parseInt(el.value) || 0) + delta;
}

function setAllCatfruit(val) {
  document.querySelectorAll(".catfruit-input").forEach(input => input.value = val);
}

function setAllCatseyes(val) {
  document.querySelectorAll(".catseye-input").forEach(input => input.value = val);
}

function setAllCatamins(val) {
  document.querySelectorAll(".catamin-input").forEach(input => input.value = val);
}

// Fetch and Update Status
async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.success && data.data) {
      updateUI(data.data);
    }
  } catch (err) {
    console.error("Failed to fetch status:", err);
  }
}

// Update UI with Save Data
function updateUI(data) {
  currentSaveData = data;
  if (data.save_data) {
    currentSaveBase64 = data.save_data;
  }

  if (!data.loaded) {
    saveStatusDot.classList.remove("active");
    saveStatusText.textContent = "未載入存檔 (請上傳或建立測試存檔)";
    saveStatusPills.style.display = "none";
    quickStatCatfood.textContent = "--";
    quickStatXp.textContent = "--";
    quickStatLeadership.textContent = "--";
    quickStatRareTickets.textContent = "--";
    quickStatCats.textContent = "--";
    return;
  }

  // Active state
  saveStatusDot.classList.add("active");
  saveStatusText.textContent = "存檔已載入";
  saveStatusPills.style.display = "flex";
  pillRegion.textContent = (data.cc || "TW").toUpperCase();
  pillVersion.textContent = `v${data.game_version || "14.2.0"}`;
  pillUR.textContent = `UR: ${data.user_rank || 0}`;

  // Quick stats
  quickStatCatfood.textContent = (data.catfood || 0).toLocaleString();
  quickStatXp.textContent = (data.xp || 0).toLocaleString();
  quickStatLeadership.textContent = (data.leadership || 0).toLocaleString();
  quickStatRareTickets.textContent = (data.rare_tickets || 0).toLocaleString();
  quickStatCats.textContent = `${data.cats_unlocked || 0} / ${data.cats_total || 0}`;

  // Tab Save Info
  const infoCc = document.getElementById("infoCc");
  const infoGv = document.getElementById("infoGv");
  const infoInquiry = document.getElementById("infoInquiry");
  const infoUR = document.getElementById("infoUR");
  const infoCats = document.getElementById("infoCats");
  const infoPlaytime = document.getElementById("infoPlaytime");

  if (infoCc) infoCc.textContent = (data.cc || "TW").toUpperCase();
  if (infoGv) infoGv.textContent = data.game_version || "--";
  if (infoInquiry) infoInquiry.textContent = data.inquiry_code || "--";
  if (infoUR) infoUR.textContent = (data.user_rank || 0).toLocaleString();
  if (infoCats) infoCats.textContent = `${data.cats_unlocked || 0} / ${data.cats_total || 0}`;
  if (infoPlaytime) infoPlaytime.textContent = `${data.playtime_hours || 0} 小時`;

  // Currencies Inputs
  setVal("inputCatfood", data.catfood || 0);
  setVal("inputXp", data.xp || 0);
  setVal("inputLeadership", data.leadership || 0);
  setVal("inputNp", data.np || 0);
  setVal("inputNormalTickets", data.normal_tickets || 0);
  setVal("inputRareTickets", data.rare_tickets || 0);
  setVal("inputPlatTickets", data.platinum_tickets || 0);
  setVal("inputLegendTickets", data.legend_tickets || 0);
  setVal("inputPlatShards", data.platinum_shards || 0);
  setVal("input100mTicket", data.hundred_million_ticket || 0);
  setVal("inputGoldenCpu", data.golden_cpu_count || 0);
  setVal("inputPlaytimeHours", data.playtime_hours || 0);

  // Render Battle Items
  renderBattleItems(data.battle_items || []);

  // Render Catfruit
  renderCatfruit(data.catfruit || []);

  // Render Catseyes
  renderCatseyes(data.catseyes || []);

  // Render Catamins
  renderCatamins(data.catamins || []);
}

// Render Battle Items
function renderBattleItems(items) {
  const container = document.getElementById("battleItemsContainer");
  if (!container) return;
  container.innerHTML = "";

  const defaultNames = ["速度加快", "寶物雷達", "土豪貓", "貓咪電腦", "洞悉先機", "狙擊手"];

  for (let i = 0; i < 6; i++) {
    const item = items[i] || { id: i, name: defaultNames[i], amount: 0 };
    const div = document.createElement("div");
    div.className = "form-group";
    div.innerHTML = `
      <label class="form-label">${item.name || defaultNames[i]}</label>
      <div class="input-with-actions">
        <input type="number" class="form-input battle-item-input" data-id="${i}" value="${item.amount || 0}">
        <button class="btn btn-secondary btn-sm" onclick="this.previousElementSibling.value = 999">999</button>
      </div>
    `;
    container.appendChild(div);
  }
}

// Render Catfruit
function renderCatfruit(items) {
  const container = document.getElementById("catfruitContainer");
  if (!container) return;
  container.innerHTML = "";

  if (items.length === 0) {
    const defaultFruitNames = [
      "紫種子", "紅種子", "藍種子", "綠種子", "黃種子",
      "紫果實", "紅果實", "藍果實", "綠果實", "黃果實",
      "彩虹種子", "彩虹果實", "古代種子", "古代果實",
      "黃金種子", "黃金果實", "惡魔種子", "惡魔果實",
      "紫獸石", "紅獸石", "藍獸石", "綠獸石", "黃獸石",
      "紫獸玉", "紅獸玉", "藍獸玉", "綠獸玉", "黃獸玉", "虹獸玉"
    ];
    items = defaultFruitNames.map((name, i) => ({ id: i, name, amount: 0 }));
  }

  items.forEach(item => {
    const div = document.createElement("div");
    div.className = "form-group";
    div.innerHTML = `
      <label class="form-label" style="font-size: 0.8rem;">${item.name}</label>
      <input type="number" class="form-input catfruit-input" data-id="${item.id}" value="${item.amount || 0}">
    `;
    container.appendChild(div);
  });
}

// Render Catseyes
function renderCatseyes(items) {
  const container = document.getElementById("catseyesContainer");
  if (!container) return;
  container.innerHTML = "";

  const defaultNames = ["EX貓目石", "稀有貓目石", "激稀有貓目石", "超激稀有貓目石", "傳說貓目石", "暗黑貓目石"];

  for (let i = 0; i < 6; i++) {
    const item = items[i] || { id: i, name: defaultNames[i], amount: 0 };
    const div = document.createElement("div");
    div.className = "form-group";
    div.innerHTML = `
      <label class="form-label">${item.name || defaultNames[i]}</label>
      <div class="input-with-actions">
        <input type="number" class="form-input catseye-input" data-id="${i}" value="${item.amount || 0}">
        <button class="btn btn-secondary btn-sm" onclick="this.previousElementSibling.value = 99">99</button>
      </div>
    `;
    container.appendChild(div);
  }
}

// Render Catamins
function renderCatamins(items) {
  const container = document.getElementById("cataminsContainer");
  if (!container) return;
  container.innerHTML = "";

  const defaultNames = ["喵力達 A", "喵力達 B", "喵力達 C"];

  for (let i = 0; i < 3; i++) {
    const item = items[i] || { id: i, name: defaultNames[i], amount: 0 };
    const div = document.createElement("div");
    div.className = "form-group";
    div.innerHTML = `
      <label class="form-label">${item.name || defaultNames[i]}</label>
      <div class="input-with-actions">
        <input type="number" class="form-input catamin-input" data-id="${i}" value="${item.amount || 0}">
        <button class="btn btn-secondary btn-sm" onclick="this.previousElementSibling.value = 999">999</button>
      </div>
    `;
    container.appendChild(div);
  }
}

// Dropzone Events
if (dropzone) {
  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });
}

if (fileInput) {
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  });
}

// Upload File
async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const cc = document.getElementById("uploadCcSelect").value;
  if (cc) formData.append("cc", cc);

  showToast("正在載入存檔...", "warning");
  try {
    const res = await fetch("/api/save/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || "存檔載入成功！", "success");
      updateUI(data.data);
    } else {
      showToast(data.error || "存檔載入失敗", "error");
    }
  } catch (err) {
    showToast(`網路或伺服器錯誤: ${err.message}`, "error");
  }
}

// Create Test Save
document.getElementById("btnCreateTestSave").addEventListener("click", async () => {
  showToast("正在建立測試存檔...", "warning");
  try {
    const res = await fetch("/api/save/new_test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cc: "tw", gv: "14.2.0" }),
    });
    const data = await res.json();
    if (data.success) {
      showToast("測試存檔建立成功！", "success");
      updateUI(data.data);
    } else {
      showToast(data.error || "建立失敗", "error");
    }
  } catch (err) {
    showToast(`建立失敗: ${err.message}`, "error");
  }
});

// Download from PONOS Server
document.getElementById("btnDownloadServer").addEventListener("click", async () => {
  const transfer_code = document.getElementById("inputTransferCode").value.trim();
  const confirmation_code = document.getElementById("inputConfirmCode").value.trim();
  const cc = document.getElementById("downloadCcSelect").value;
  const gv = document.getElementById("downloadGvInput").value.trim();

  if (!transfer_code || !confirmation_code) {
    showToast("請輸入引繼碼與認證碼", "error");
    return;
  }

  showToast("正在從官方伺服器下載存檔...", "warning");
  try {
    const res = await fetch("/api/save/download_transfer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transfer_code, confirmation_code, cc, gv }),
    });
    const data = await res.json();
    if (data.success) {
      showToast("伺服器存檔下載成功！", "success");
      updateUI(data.data);
    } else {
      showToast(data.error || "下載失敗", "error");
    }
  } catch (err) {
    showToast(`下載失敗: ${err.message}`, "error");
  }
});

// Upload to PONOS Server
document.getElementById("btnUploadServer").addEventListener("click", async () => {
  showToast("正在上傳存檔至伺服器...", "warning");
  try {
    const res = await fetch("/api/save/upload_transfer", { method: "POST" });
    const data = await res.json();
    if (data.success && data.data) {
      showToast("存檔已成功上傳至官方伺服器！", "success");
      document.getElementById("uploadResultBox").style.display = "block";
      document.getElementById("resTransferCode").textContent = data.data.transfer_code;
      document.getElementById("resConfirmCode").textContent = data.data.confirmation_code;
    } else {
      showToast(data.error || "上傳失敗", "error");
    }
  } catch (err) {
    showToast(`上傳失敗: ${err.message}`, "error");
  }
});

// Copy Codes
document.getElementById("btnCopyCodes").addEventListener("click", () => {
  const tCode = document.getElementById("resTransferCode").textContent;
  const cCode = document.getElementById("resConfirmCode").textContent;
  const text = `引繼碼: ${tCode}\n認證碼: ${cCode}`;
  navigator.clipboard.writeText(text).then(() => {
    showToast("引繼碼與認證碼已複製到剪貼簿！", "success");
  }).catch(() => {
    showToast("請手動複製代碼", "warning");
  });
});

// Export Save
document.getElementById("btnExportSave").addEventListener("click", () => {
  if (!currentSaveData || !currentSaveData.loaded) {
    showToast("尚未載入存檔，無法匯出", "error");
    return;
  }
  if (currentSaveBase64) {
    try {
      const binaryString = atob(currentSaveBase64);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "application/octet-stream" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "SAVE_DATA";
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast("存檔已成功下載 (SAVE_DATA)！", "success");
      return;
    } catch (e) {
      console.warn("Client-side export failed, falling back to server:", e);
    }
  }
  window.location.href = "/api/save/export";
});

// Save Currencies
document.getElementById("btnSaveCurrencies").addEventListener("click", async () => {
  const payload = {
    catfood: parseInt(document.getElementById("inputCatfood").value) || 0,
    xp: parseInt(document.getElementById("inputXp").value) || 0,
    leadership: parseInt(document.getElementById("inputLeadership").value) || 0,
    np: parseInt(document.getElementById("inputNp").value) || 0,
  };
  await sendPost("/api/edit/currencies", payload, "貨幣設定儲存成功！");
});

// Save Tickets
document.getElementById("btnSaveTickets").addEventListener("click", async () => {
  const payload = {
    normal_tickets: parseInt(document.getElementById("inputNormalTickets").value) || 0,
    rare_tickets: parseInt(document.getElementById("inputRareTickets").value) || 0,
    platinum_tickets: parseInt(document.getElementById("inputPlatTickets").value) || 0,
    legend_tickets: parseInt(document.getElementById("inputLegendTickets").value) || 0,
    platinum_shards: parseInt(document.getElementById("inputPlatShards").value) || 0,
    hundred_million_ticket: parseInt(document.getElementById("input100mTicket").value) || 0,
  };
  await sendPost("/api/edit/currencies", payload, "抽獎券設定儲存成功！");
});

// Save Battle Items
document.getElementById("btnSaveBattleItems").addEventListener("click", async () => {
  const items = [];
  document.querySelectorAll(".battle-item-input").forEach(input => {
    items.push({
      id: parseInt(input.getAttribute("data-id")),
      amount: parseInt(input.value) || 0,
    });
  });
  const golden_cpu_count = parseInt(document.getElementById("inputGoldenCpu").value) || 0;
  await sendPost("/api/edit/battle_items", { items, golden_cpu_count }, "戰鬥道具設定儲存成功！");
});

// Quick Max Battle Items
document.getElementById("btnQuickMaxBattleItems").addEventListener("click", () => {
  document.querySelectorAll(".battle-item-input").forEach(input => input.value = 999);
  document.getElementById("inputGoldenCpu").value = 99;
  showToast("已將所有戰鬥道具數值填入 999", "success");
});

// Save Catfruit
document.getElementById("btnSaveCatfruit").addEventListener("click", async () => {
  const items = [];
  document.querySelectorAll(".catfruit-input").forEach(input => {
    items.push({
      id: parseInt(input.getAttribute("data-id")),
      amount: parseInt(input.value) || 0,
    });
  });
  await sendPost("/api/edit/catfruit", { items }, "貓薄荷設定儲存成功！");
});

// Save Catseyes
document.getElementById("btnSaveCatseyes").addEventListener("click", async () => {
  const items = [];
  document.querySelectorAll(".catseye-input").forEach(input => {
    items.push({
      id: parseInt(input.getAttribute("data-id")),
      amount: parseInt(input.value) || 0,
    });
  });
  await sendPost("/api/edit/catseyes", { items }, "貓目石設定儲存成功！");
});

// Save Catamins
document.getElementById("btnSaveCatamins").addEventListener("click", async () => {
  const items = [];
  document.querySelectorAll(".catamin-input").forEach(input => {
    items.push({
      id: parseInt(input.getAttribute("data-id")),
      amount: parseInt(input.value) || 0,
    });
  });
  await sendPost("/api/edit/catamins", { items }, "喵力達設定儲存成功！");
});

// Apply Cats Edits
document.getElementById("btnApplyCatEdits").addEventListener("click", async () => {
  const unlock_all = document.getElementById("chkUnlockAllCats").checked;
  let rarities = null;
  if (!unlock_all) {
    rarities = [];
    document.querySelectorAll(".chk-rarity:checked").forEach(chk => {
      rarities.push(parseInt(chk.value));
    });
  }

  const payload = {
    unlock_all,
    rarities,
    upgrade_level: {
      base: parseInt(document.getElementById("inputCatBaseLevel").value) || 50,
      plus: parseInt(document.getElementById("inputCatPlusLevel").value) || 90,
    },
    unlock_true_form: document.getElementById("chkUnlockTrueForm").checked,
    unlock_fourth_form: document.getElementById("chkUnlockFourthForm").checked,
    max_talents: document.getElementById("chkMaxTalents").checked,
    unlock_guide: document.getElementById("chkUnlockCatGuide").checked,
  };
  await sendPost("/api/edit/cats", payload, "貓咪全功能修改完成！");
});

// Apply Stages Edits
document.getElementById("btnApplyStages").addEventListener("click", async () => {
  const payload = {
    clear_story: document.getElementById("chkClearStory").checked,
    all_gold_treasures: document.getElementById("chkAllGoldTreasures").checked,
    max_timed_scores: document.getElementById("chkMaxTimedScores").checked,
    clear_outbreaks: document.getElementById("chkClearOutbreaks").checked,
    unlock_aku: true,
    clear_aku: document.getElementById("chkClearAku").checked,
    clear_sol: document.getElementById("chkClearSol").checked,
    clear_ul: document.getElementById("chkClearUl").checked,
    clear_zl: document.getElementById("chkClearZl").checked,
    clear_towers: document.getElementById("chkClearTowers").checked,
  };
  await sendPost("/api/edit/stages", payload, "關卡與寶物進度修改完成！");
});

// Apply Base & Gamatoto Edits
document.getElementById("btnApplyBase").addEventListener("click", async () => {
  const payload = {
    max_gamatoto: document.getElementById("chkMaxGamatoto").checked,
    legendary_helpers: document.getElementById("chkLegendaryHelpers").checked,
    base_materials_amount: parseInt(document.getElementById("inputBaseMaterials").value) || 9999,
    max_engineers: document.getElementById("chkMaxEngineers").checked,
    unlock_max_cannons: document.getElementById("chkMaxCannons").checked,
    max_cat_shrine: document.getElementById("chkMaxShrine").checked,
    max_special_skills: document.getElementById("chkMaxSpecialSkills").checked,
  };
  await sendPost("/api/edit/gamatoto_base", payload, "加碼多多與基地設定修改完成！");
});

// Apply Fixes & Extras
document.getElementById("btnApplyFixes").addEventListener("click", async () => {
  const payload = {
    fix_time: document.getElementById("chkFixTime").checked,
    fix_gamatoto: document.getElementById("chkFixGamatoto").checked,
    fix_ototo: document.getElementById("chkFixOtoto").checked,
    fix_officer_pass: document.getElementById("chkFixOfficerPass").checked,
    unlock_lineups: document.getElementById("chkUnlockLineups").checked,
    unlock_medals: document.getElementById("chkUnlockMedals").checked,
    clear_missions: document.getElementById("chkClearMissions").checked,
    unlock_enemy_guide: document.getElementById("chkUnlockEnemyGuide").checked,
    unlock_gold_pass: document.getElementById("chkUnlockGoldPass").checked,
    reset_gambling: document.getElementById("chkResetGambling").checked,
    unban_account: document.getElementById("chkUnbanAccount").checked,
    playtime_hours: parseFloat(document.getElementById("inputPlaytimeHours").value) || 120,
  };
  await sendPost("/api/edit/fixes_extras", payload, "修復與特殊項目修改完成！");
});

// One-Click God Mode (Extreme)
document.getElementById("btnGodMode").addEventListener("click", async () => {
  if (!confirm("確定要執行【一鍵極致畢業】嗎？\n這將會解鎖全部貓咪、滿級50+90、滿本能、全關卡通關、全金寶、加碼多多滿級與大量資源！")) {
    return;
  }
  showToast("正在執行一鍵極致畢業修改...", "warning");
  await sendPost("/api/edit/one_click", { safe_mode: false }, "🎉 一鍵極致畢業完成！存檔已達到全滿神的境界！");
});

// One-Click Safe Max
document.getElementById("btnSafeMaxAll").addEventListener("click", async () => {
  if (!confirm("確定要執行【一鍵安全全滿 (防封)】嗎？\n所有數值將維持在官方安全上限內 (罐頭 19,999、金券 99 等)，確保連線安全！")) {
    return;
  }
  showToast("正在執行安全全滿修改...", "warning");
  await sendPost("/api/edit/one_click", { safe_mode: true }, "🛡️ 一鍵安全全滿完成！各項資源已設定為防封安全上限！");
});

// Generic Post Helper
async function sendPost(url, payload, successMsg) {
  if (!currentSaveData || !currentSaveData.loaded) {
    showToast("尚未載入存檔，請先建立測試存檔或上傳存檔", "error");
    return;
  }
  if (currentSaveBase64 && !payload.save_data) {
    payload.save_data = currentSaveBase64;
  }
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.success) {
      showToast(successMsg, "success");
      updateUI(data.data);
    } else {
      showToast(data.error || "操作失敗", "error");
    }
  } catch (err) {
    showToast(`網路或伺服器錯誤: ${err.message}`, "error");
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  fetchStatus();
});
