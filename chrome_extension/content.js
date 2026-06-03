(() => {
  const BACKEND_URL = "https://youtube-timestamp-chatbot-rag-jqh0.onrender.com/chat";
  const PANEL_ID = "yt-rag-panel";

  let currentVideoId = null;

  function getVideoId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("v");
  }

  async function fetchTranscriptFromPage() {
    return new Promise((resolve) => {
      const script = document.createElement("script");
      script.id = "yt-rag-extractor";
      script.textContent = `
        (function() {
          try {
            const data = window.ytInitialPlayerResponse;
            document.dispatchEvent(new CustomEvent("yt-rag-player-data", {
              detail: data ? JSON.stringify(data) : null
            }));
          } catch(e) {
            document.dispatchEvent(new CustomEvent("yt-rag-player-data", { detail: null }));
          }
        })();
      `;

      document.addEventListener("yt-rag-player-data", async (e) => {
        const existing = document.getElementById("yt-rag-extractor");
        if (existing) existing.remove();

        if (!e.detail) { resolve(null); return; }

        try {
          const playerResponse = JSON.parse(e.detail);
          const captionTracks =
            playerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks;

          if (!captionTracks || captionTracks.length === 0) { resolve(null); return; }

          const track =
            captionTracks.find((t) => t.languageCode === "en") ||
            captionTracks.find((t) => t.languageCode?.startsWith("en")) ||
            captionTracks[0];

          const url = track.baseUrl + "&fmt=json3";
          const res = await fetch(url);
          const data = await res.json();

          const transcript = (data.events || [])
            .filter((ev) => ev.segs)
            .map((ev) => ({
              text: ev.segs.map((s) => s.utf8 || "").join("").replace(/\n/g, " ").trim(),
              start: (ev.tStartMs || 0) / 1000,
              duration: (ev.dDurationMs || 0) / 1000,
            }))
            .filter((ev) => ev.text.trim().length > 0);

          resolve(transcript.length > 0 ? transcript : null);
        } catch (err) {
          console.error("[YT-RAG] Transcript parse error:", err);
          resolve(null);
        }
      }, { once: true });

      document.head.appendChild(script);
    });
  }

  function buildPanel() {
    const panel = document.createElement("div");
    panel.id = PANEL_ID;
    panel.innerHTML = `
      <div id="yt-rag-header">
        <div id="yt-rag-header-left">
          <div id="yt-rag-logo">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          <div>
            <div id="yt-rag-title">RAG Chatbot</div>
            <div id="yt-rag-subtitle">Powered by Groq + LLaMA</div>
          </div>
        </div>
        <button id="yt-rag-close-btn" title="Close">✕</button>
      </div>

      <div id="yt-rag-video-bar">
        <div id="yt-rag-video-dot"></div>
        <div id="yt-rag-video-id-text">Loading video ID...</div>
      </div>

      <div id="yt-rag-messages">
        <div id="yt-rag-welcome">
          <div id="yt-rag-welcome-icon">🎬</div>
          <h3>Ask anything about this video</h3>
          <p>I'll read the transcript and give you a detailed answer based on what was said in this video.</p>
        </div>
      </div>

      <div id="yt-rag-input-area">
        <textarea
          id="yt-rag-input"
          rows="1"
          placeholder="Ask a question about this video..."
        ></textarea>
        <button id="yt-rag-send-btn" title="Send">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    `;

    document.body.appendChild(panel);
    panel.style.display = "flex";

    document.getElementById("yt-rag-close-btn").addEventListener("click", () => {
      panel.style.display = "none";
    });

    document.getElementById("yt-rag-send-btn").addEventListener("click", handleSend);

    document.getElementById("yt-rag-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    document.getElementById("yt-rag-input").addEventListener("input", autoResizeTextarea);

    return panel;
  }

  function autoResizeTextarea() {
    const ta = document.getElementById("yt-rag-input");
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 100) + "px";
  }

  function updateVideoBar(videoId) {
    const bar = document.getElementById("yt-rag-video-id-text");
    if (bar) {
      bar.textContent = videoId ? `Video: ${videoId}` : "No video detected";
    }
  }

  function appendUserMessage(text) {
    const welcome = document.getElementById("yt-rag-welcome");
    if (welcome) welcome.remove();

    const messages = document.getElementById("yt-rag-messages");
    const row = document.createElement("div");
    row.className = "yt-rag-msg-row yt-rag-msg-user";
    row.innerHTML = `<div class="yt-rag-bubble yt-rag-bubble-user">${escapeHtml(text)}</div>`;
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
  }

  function appendThinking() {
    const messages = document.getElementById("yt-rag-messages");
    const row = document.createElement("div");
    row.className = "yt-rag-msg-row yt-rag-msg-ai";
    row.id = "yt-rag-thinking-row";
    row.innerHTML = `
      <div class="yt-rag-thinking">
        <span></span><span></span><span></span>
      </div>
    `;
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeThinking() {
    const row = document.getElementById("yt-rag-thinking-row");
    if (row) row.remove();
  }

  function appendAIMessage(answer, timestamp, ytLink) {
    const messages = document.getElementById("yt-rag-messages");
    const row = document.createElement("div");
    row.className = "yt-rag-msg-row yt-rag-msg-ai";

    const formattedAnswer = answer
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");

    row.innerHTML = `
      <div class="yt-rag-bubble yt-rag-bubble-ai">
        ${formattedAnswer}
        ${timestamp ? `
          <br>
          <a class="yt-rag-timestamp-link" href="${ytLink}" target="_blank">
            ▶ Jump to ${timestamp}
          </a>
        ` : ""}
      </div>
    `;
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
  }

  function appendErrorMessage(text) {
    const messages = document.getElementById("yt-rag-messages");
    const row = document.createElement("div");
    row.className = "yt-rag-msg-row yt-rag-msg-ai";
    row.innerHTML = `<div class="yt-rag-bubble yt-rag-bubble-error">⚠️ ${escapeHtml(text)}</div>`;
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function handleSend() {
    const input = document.getElementById("yt-rag-input");
    const sendBtn = document.getElementById("yt-rag-send-btn");
    const question = input.value.trim();

    if (!question) return;

    const videoId = getVideoId();
    if (!videoId) {
      appendErrorMessage("No YouTube video detected. Please navigate to a YouTube video first.");
      return;
    }

    input.value = "";
    input.style.height = "auto";
    sendBtn.disabled = true;

    appendUserMessage(question);
    appendThinking();

    try {
      const transcript = await fetchTranscriptFromPage();

      if (!transcript) {
        removeThinking();
        appendErrorMessage(
          "Could not extract transcript from this video. Make sure the video has captions/subtitles enabled."
        );
        sendBtn.disabled = false;
        input.focus();
        return;
      }

      const response = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_url: `https://www.youtube.com/watch?v=${videoId}`,
          question: question,
          transcript: transcript,
        }),
      });

      removeThinking();

      if (response.ok) {
        const data = await response.json();
        appendAIMessage(data.answer, data.timestamp, data.youtube_link);
      } else {
        let detail = `Server error (${response.status})`;
        try {
          const err = await response.json();
          detail = err.detail || detail;
        } catch (_) { }
        appendErrorMessage(detail);
      }
    } catch (err) {
      removeThinking();
      appendErrorMessage(`Error: ${err.message}`);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  function initPanel() {
    let panel = document.getElementById(PANEL_ID);
    if (!panel) {
      panel = buildPanel();
    }

    const videoId = getVideoId();
    currentVideoId = videoId;
    updateVideoBar(videoId);

    return panel;
  }

  function handleNavigation() {
    const videoId = getVideoId();
    if (videoId && videoId !== currentVideoId) {
      currentVideoId = videoId;
      updateVideoBar(videoId);

      const messages = document.getElementById("yt-rag-messages");
      if (messages) {
        messages.innerHTML = `
          <div id="yt-rag-welcome">
            <div id="yt-rag-welcome-icon">🎬</div>
            <h3>New video detected!</h3>
            <p>Ask me anything about this video. I'll analyze the transcript and answer in detail.</p>
          </div>
        `;
      }
    }
  }

  function init() {
    initPanel();

    const observer = new MutationObserver(() => {
      handleNavigation();
    });

    observer.observe(document.querySelector("title") || document.head, {
      subtree: true,
      characterData: true,
      childList: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
