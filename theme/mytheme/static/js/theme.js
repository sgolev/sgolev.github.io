(function () {
  var root = document.documentElement;

  function syncGiscus(theme) {
    var iframe = document.querySelector("iframe.giscus-frame");
    if (!iframe) return;
    iframe.contentWindow.postMessage(
      { giscus: { setConfig: { theme: theme === "dark" ? "dark" : "light" } } },
      "https://giscus.app"
    );
  }

  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem("theme", next);
      syncGiscus(next);
    });
  }

  var toTop = document.getElementById("to-top");
  if (toTop) {
    var onScroll = function () {
      toTop.classList.toggle("visible", window.scrollY > 600);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    toTop.addEventListener("click", function () {
      var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
    });
  }

  /* --- Table of contents: disclosure + scroll-spy -------------------------- */
  var toc = document.querySelector(".toc");
  if (toc) {
    var tocBtn = toc.querySelector(".toc-toggle");
    var tocList = toc.querySelector("nav");
    var wide = matchMedia("(min-width: 78rem)");

    /* No data-open means "whatever this screen width defaults to" (see CSS) */
    var isOpen = function () {
      return toc.dataset.open ? toc.dataset.open === "1" : wide.matches;
    };
    var syncBtn = function () {
      tocBtn.setAttribute("aria-expanded", isOpen() ? "true" : "false");
    };

    tocBtn.addEventListener("click", function () {
      toc.dataset.open = isOpen() ? "0" : "1";
      syncBtn();
    });
    wide.addEventListener("change", function () {
      delete toc.dataset.open; /* crossing the breakpoint restores the default */
      syncBtn();
    });
    syncBtn();

    var items = [];
    Array.prototype.forEach.call(toc.querySelectorAll("a[href^='#']"), function (a) {
      var el = document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
      if (el) items.push({ a: a, li: a.parentNode, el: el });
    });

    if (items.length) {
      var active = null;
      var update = function () {
        /* The last heading to have crossed a line 20% down the viewport */
        var line = window.scrollY + window.innerHeight * 0.2;
        var found = items[0];
        for (var i = 0; i < items.length; i++) {
          if (items[i].el.getBoundingClientRect().top + window.scrollY <= line) {
            found = items[i];
          }
        }
        /* At the very bottom the last section may never cross the line */
        if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) {
          found = items[items.length - 1];
        }
        if (found === active) return;
        if (active) {
          active.li.classList.remove("active");
          active.a.removeAttribute("aria-current");
        }
        found.li.classList.add("active");
        found.a.setAttribute("aria-current", "true");
        active = found;
        /* Keep the current entry in view when the list itself scrolls.
           Scrolling .toc instead would carry the "Contents" label off the top. */
        if (tocList && tocList.scrollHeight > tocList.clientHeight) {
          tocList.scrollTop = Math.max(0, found.li.offsetTop - tocList.clientHeight / 2);
        }
      };

      var queued = false;
      var onTocScroll = function () {
        if (queued) return;
        queued = true;
        requestAnimationFrame(function () {
          queued = false;
          update();
        });
      };
      window.addEventListener("scroll", onTocScroll, { passive: true });
      window.addEventListener("resize", onTocScroll);
      update();
    }
  }
})();
