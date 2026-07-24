(function () {
  "use strict";

  if (!document.documentElement.id) {
    document.documentElement.id = "top";
  }

  var existing = document.querySelector(".back-to-top");
  var button = existing;
  if (!button) {
    button = document.createElement("a");
    button.className = "back-to-top";
    button.href = "#top";
    button.setAttribute("aria-label", "Back to top");
    button.textContent = "Top";
    document.body.appendChild(button);
  }

  var toggle = function () {
    var show = window.scrollY > Math.min(480, window.innerHeight * 0.75);
    button.classList.toggle("is-visible", show);
  };

  window.addEventListener("scroll", toggle, { passive: true });
  window.addEventListener("resize", toggle, { passive: true });
  toggle();
})();
