/* 手机端行为层：只补桌面 UI 在窄屏上「看得见但用不了」的那几处。
   不复制页面逻辑，不改任何接口调用。 */
(() => {
  if (!window.matchMedia || !window.matchMedia("(max-width: 760px)").matches) return;

  const root = document.documentElement;
  root.classList.add("android-mobile");

  const params = new URLSearchParams(location.search);
  const embed = params.get("embed") === "1";
  const $ = (id) => document.getElementById(id);
  const PANES = { dash: "paneDash", ops: "paneOps" };

  /* ---------------- 内嵌模式（原生 App 的「高级控制台」页） ----------------
     原生底部导航只有「高级控制台」一个入口，而页面本身是「看板 / 功能」两套。
     这里在顶栏下补一条两段切换条（.embedSeg），切谁显示谁 —— **不做搬运**。

     ⚠️ 早先是把看板的块搬进功能页再藏起看板，问题很大：
        (1) 看板一显示就是空的（内容全在功能页里），来回切等于丢内容；
        (2) 搬移和切页的 display 互相打架，会出现「点了看板又跳回功能」。
        现在两套各自待在原地，只切 display，天然可逆、可来回切。 */

  if (embed) {
    root.classList.add("cok-embed");
    const nav = document.querySelector(".nav");
    if (nav) nav.style.display = "none";

    const seg = document.createElement("div");
    seg.className = "nav embedSeg";
    seg.setAttribute("role", "tablist");
    seg.setAttribute("aria-label", "页面切换");
    const items = [["dash", "看板"], ["ops", "功能"]];
    seg.innerHTML = items.map(([k, t]) =>
      '<button type="button" class="navItem" role="tab" data-tab="' + k + '">' + t + "</button>"
    ).join("");
    // 挂在主区顶部（sticky 在顶栏下面）—— 挂进 .sidebar 的话它是 fixed 底栏，
    // 会把两段切换条甩到屏幕最下面、脱离顶栏。
    const mount = document.querySelector(".main") || document.body;
    const topbar = document.querySelector(".topbar");
    if (topbar && topbar.parentElement === mount) mount.insertBefore(seg, topbar.nextSibling);
    else mount.insertBefore(seg, mount.firstChild);

    const syncSeg = () => {
      const onOps = getComputedStyle($("paneOps")).display !== "none";
      seg.querySelectorAll(".navItem").forEach(b => {
        const on = (b.dataset.tab === "ops") === onOps;
        b.classList.toggle("active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });
    };
    seg.addEventListener("click", (e) => {
      const b = e.target.closest && e.target.closest(".navItem");
      if (!b) return;
      if (typeof window.switchTab === "function") window.switchTab(b.dataset.tab);
      else {
        $("paneDash").style.display = b.dataset.tab === "dash" ? "" : "none";
        $("paneOps").style.display = b.dataset.tab === "ops" ? "" : "none";
      }
      syncSeg();
    });
    syncSeg();
    setInterval(syncSeg, 800);

    /* 首屏：页面会记住上次的 Tab（localStorage），可能一进来就是「看板」。
       只在前 2.5 秒里做一次「落在功能页」的修正，之后完全交给用户 ——
       早先写成"每次轮询都拽回功能页"，结果用户切到看板后 600ms 就被覆盖。 */
    let forceOps = true;
    const apply = () => {
      const ops = $("paneOps"), dash = $("paneDash");
      if (!ops || !dash) return;
      if (forceOps && (dash.style.display !== "none" || ops.style.display === "none")) {
        if (typeof window.switchTab === "function") window.switchTab("ops");
        else {
          dash.style.display = "none";
          ops.style.display = "";
        }
      }
    };
    apply();
    const iv = setInterval(apply, 800);
    setTimeout(() => { clearInterval(iv); forceOps = false; }, 2500);
  } else {
    /* 独立打开（手机浏览器 / 桌面窄窗）：页面自己管导航，
       顺手把 aria 补全 —— 底部导航是图标 + 文字，读屏需要明确标签。 */
    const nav = document.querySelector(".nav");
    if (nav) {
      nav.setAttribute("role", "tablist");
      for (const item of nav.querySelectorAll(".navItem")) {
        const key = item.dataset.tab;
        if (!PANES[key]) continue;
        item.setAttribute("role", "tab");
        const label = item.querySelector("span:not(.cnt)");
        if (label) item.setAttribute("aria-label", label.textContent.trim());
      }
    }
  }

  /* 连接状态胶囊被 fixed 到顶栏右边，长文本会挤掉标题 —— 完整内容放进 title */
  const connText = $("connText");
  if (connText) {
    const full = connText.textContent.trim();
    if (full.length > 6) connText.title = full;
  }
})();