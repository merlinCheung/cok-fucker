/* Mobile-only behavior layered over the shared console without changing APIs. */
(() => {
  if (!window.matchMedia || !window.matchMedia("(max-width: 760px)").matches) return;

  document.documentElement.classList.add("android-mobile");
  // When hosted inside the native shell's "控制台" tab, drop the web page's own
  // bottom tab bar so it never stacks on top of the native bottom navigation.
  if (new URLSearchParams(location.search).get("embed") === "1") {
    document.documentElement.classList.add("cok-embed");
    const dash = document.querySelector("#paneDash");
    const ops = document.querySelector("#paneOps");
    const taskStats = document.querySelector("#cardTaskStats");
    const opsGrid = ops && ops.querySelector(".grid");
    // The native shell hides the web dashboard, so surface its task summary
    // at the top of the embedded console instead of duplicating its state.
    if (taskStats && opsGrid) opsGrid.insertBefore(taskStats, opsGrid.firstChild);
    if (dash) dash.style.display = "none";
    if (ops) ops.style.display = "";
  }
  const tabs = [...document.querySelectorAll(".tab")];
  const labels = { dash: "总览", ops: "操作" };

  for (const tab of tabs) {
    const label = labels[tab.dataset.tab];
    if (!label) continue;
    const textNode = [...tab.childNodes].find(node => node.nodeType === Node.TEXT_NODE);
    if (textNode) textNode.nodeValue = label;
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-label", label);
    tab.addEventListener("click", () => {
      window.setTimeout(() => {
        for (const item of tabs) item.setAttribute("aria-selected", String(item.classList.contains("active")));
      }, 0);
    });
  }

  const tabbar = document.querySelector(".tabbar");
  if (tabbar) {
    tabbar.setAttribute("role", "tablist");
    if (document.documentElement.classList.contains("cok-embed")) tabbar.hidden = true;
  }
})();
