// Skybit web entry point — boot the canvas-backed App.

import { App } from "./scenes.js";

window.addEventListener("error", (e) => {
  console.error("[skybit] uncaught", e.error || e.message);
});

function boot(): void {
  const canvas = document.getElementById("game") as HTMLCanvasElement | null;
  if (!canvas) throw new Error("game canvas element not found");
  const app = new App(canvas);
  app.start();

  // Wire the loading-overlay tap to the game canvas: forward the pointer
  // down so the overlay's first dismiss tap also serves as the user's
  // first flap (matches the pygbag overlay-dismiss pattern).
  const ov = document.getElementById("skybit-loading");
  if (ov) {
    const dismiss = (e: Event) => {
      e.preventDefault();
      ov.classList.add("skybit-hidden");
      // The window-level pointerdown listener on App will also fire on
      // this same gesture and start the game.
    };
    ov.addEventListener("pointerdown", dismiss, { once: false });
    ov.addEventListener("touchstart", dismiss, { once: false });
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
