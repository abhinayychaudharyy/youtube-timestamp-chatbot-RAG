chrome.action.onClicked.addListener((tab) => {
  if (tab.url && tab.url.includes("youtube.com/watch")) {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const panel = document.getElementById("yt-rag-panel");
        if (panel) {
          const isVisible = panel.style.display !== "none";
          panel.style.display = isVisible ? "none" : "flex";
        }
      }
    });
  }
});
