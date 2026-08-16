(function () {
  "use strict";

  var backToTopThreshold = Math.min(480, window.innerHeight * 0.75);

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

  document.querySelectorAll(".copy-link[data-copy-url]").forEach(function (copyButton) {
    copyButton.addEventListener("click", function () {
      var url = copyButton.getAttribute("data-copy-url");
      var status = copyButton.closest(".insight-share").querySelector(".copy-link__status");

      function report(success) {
        status.textContent = success ? "Link copied." : "Copy failed — select the address from your browser.";
        if (success) {
          copyButton.textContent = "Copied";
          window.setTimeout(function () {
            copyButton.textContent = "Copy link";
            status.textContent = "";
          }, 2500);
        }
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(
          function () { report(true); },
          function () { report(false); }
        );
        return;
      }

      var fallback = document.createElement("textarea");
      fallback.value = url;
      fallback.setAttribute("readonly", "");
      fallback.style.position = "fixed";
      fallback.style.opacity = "0";
      document.body.appendChild(fallback);
      fallback.select();
      var copied = false;
      try {
        copied = document.execCommand("copy");
      } catch (error) {
        copied = false;
      }
      document.body.removeChild(fallback);
      report(copied);
    });
  });

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
    var show = window.scrollY > backToTopThreshold;
    button.classList.toggle("is-visible", show);
  };

  window.addEventListener("scroll", toggle, { passive: true });
  window.addEventListener("resize", function () {
    backToTopThreshold = Math.min(480, window.innerHeight * 0.75);
    toggle();
  }, { passive: true });
  window.requestAnimationFrame(toggle);
})();
