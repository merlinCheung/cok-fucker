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
     原生底部导航是「状态 / 操作 / 账号 / 更多 / 高级控制台」，页面自己那两条
     一级导航会叠在上面 —— 所以隐藏页面导航，只留原生那套。
     代价是原生导航里没有「看板」，看板内容就看不到了。这里把看板里
     「功能页没有的块」整段搬进功能页，然后藏掉看板本体。
     搬运是可逆的（搬之前记下原位），切页时先还原再搬，不会越搬越少。 */
  const MOVED = [];

  function moveInto(from, to, pred) {
    for (const el of Array.from(from.children)) {
      if (!pred(el)) continue;
      MOVED.push({ el: el, parent: from, next: el.nextElementSibling });
      to.appendChild(el);
    }
  }

  function restore() {
    while (MOVED.length) {
      const it = MOVED.pop();
      if (it.next && it.next.parentNode === it.parent) it.parent.insertBefore(it.el, it.next);
      else it.parent.appendChild(it.el);
    }
  }

  function rebuildEmbedded() {
    const dash = $("paneDash"), ops = $("paneOps");
    if (!dash || !ops) return;
    const host = ops.querySelector(".grid");
    if (!host) return;

    restore();

    /* 看板的分节标题（概览/监控/事件）搬到功能页会变成空标题 —— 留在看板里，
       而看板已经隐藏，等于丢掉，所以这里直接连标题一起搬。
       「今日待办」和「任务统计」在看板的 .grid 里，单独摘出来放到功能页顶部
       （它们是概览，不是操作）；概览条/监控卡/事件流则整段接到功能页卡片后面。 */
    const dashGrid = dash.querySelector(".grid");
    const picks = [];
    if (dashGrid) {
      for (const id of ["cardTaskStats", "cardTodo"]) {
        const el = $(id);
        if (el && el.parentElement === dashGrid) picks.push(el);
      }
    }
    moveInto(dash, host, (el) => picks.indexOf(el) >= 0);
    moveInto(dash, host, (el) =>
      el.classList.contains("ovbar") ||
      el.classList.contains("logbar") ||
      el.id === "cards" ||
      el.id === "logs");

    dash.style.display = "none";
    ops.style.display = "";
    for (const item of document.querySelectorAll(".navItem")) {
      item.classList.toggle("active", item.dataset.tab === "ops");
    }
  }

  if (embed) {
    root.classList.add("cok-embed");
    const nav = document.querySelector(".nav");
    if (nav) nav.style.display = "none";

    const apply = () => {
      const ops = $("paneOps"), dash = $("paneDash");
      if (!ops || !dash) return;
      /* 页面会记住上次的 Tab（localStorage），可能一进来就是「看板」——
         而看板在内嵌模式下是隐藏的，所以每次都要拽回功能页。 */
      if (dash.style.display !== "none" || ops.style.display === "none") {
        if (typeof window.switchTab === "function") window.switchTab("ops");
        else {
          dash.style.display = "none";
          ops.style.display = "";
        }
      }
      rebuildEmbedded();
    };
    apply();
    /* 页面启动是异步的（/api/me → /api/state → 渲染监控卡），
       搬完还会冒出新的节点，所以头几秒要反复对齐。 */
    const iv = setInterval(apply, 800);
    setTimeout(() => clearInterval(iv), 8000);
    window.addEventListener("resize", apply);
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