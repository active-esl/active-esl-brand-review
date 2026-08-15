(function () {
  "use strict";

  if (!document.documentElement.id) {
    document.documentElement.id = "top";
  }

  // Review host only — live active-esl.com stays clean.
  var host = (window.location && window.location.hostname) || "";
  var isReview =
    host === "review.active-esl.com" ||
    /\.active-esl-website-review\.pages\.dev$/i.test(host) ||
    host.indexOf("active-esl-website-review") !== -1 && /\.workers\.dev$/i.test(host);
  if (isReview && !document.querySelector(".review-banner")) {
    var banner = document.createElement("div");
    banner.className = "review-banner";
    banner.setAttribute("role", "status");
    banner.innerHTML =
      "<strong>Review tip</strong> — not the live site. Production remains " +
      '<a href="https://active-esl.com/">active-esl.com</a>.';
    document.body.insertBefore(banner, document.body.firstChild);
    document.documentElement.classList.add("has-review-banner");
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
