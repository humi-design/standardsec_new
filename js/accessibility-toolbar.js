const toggleBtn = document.getElementById("accessibilityToggle");
const panel = document.getElementById("accessibilityPanel");

toggleBtn.addEventListener("click", () => {
  const expanded = toggleBtn.getAttribute("aria-expanded") === "true";
  toggleBtn.setAttribute("aria-expanded", !expanded);
  panel.hidden = expanded;
});

// Font resize
function changeFontSize(delta) {
  let body = document.body;
  let currentSize = parseFloat(window.getComputedStyle(body, null).getPropertyValue('font-size'));
  body.style.fontSize = (currentSize + delta) + 'px';
}

// Dark mode toggle
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

// Text-to-speech
function readContent() {
  let content = document.querySelector("main") || document.body;
  let text = content.innerText;
  let speech = new SpeechSynthesisUtterance(text);
  speech.lang = "en-IN"; 
  window.speechSynthesis.speak(speech);
}
