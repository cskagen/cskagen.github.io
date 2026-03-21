function goToRandom(archiveSequence) {
  if (!archiveSequence || archiveSequence.length === 0) return;

  const choice = archiveSequence[Math.floor(Math.random() * archiveSequence.length)];
  window.location.href = "/drawings/" + choice + ".html";
}

function goToCommand(value, config) {

  const v = value.trim().toLowerCase();

  if (!v) return;

  const {
    latestPage,
    firstPage,
    homePage = "/",
    archiveSequence = []
  } = config;

  // --------------------------------------------------
  // direct number navigation
  // --------------------------------------------------

  if (/^\d+$/.test(v)) {
    window.location.href = "/drawings/tegning_nr" + v + ".html";
    return;
  }

  // --------------------------------------------------
  // print command
  // --------------------------------------------------

  if (v === "print") {
    window.print();
    return;
  }

  // --------------------------------------------------
  // home command
  // --------------------------------------------------

  if (v === "home") {
    window.location.href = homePage;
    return;
  }

  // --------------------------------------------------
  // random command
  // --------------------------------------------------

  if (v === "random") {
    goToRandom(archiveSequence);
    return;
  }

  // --------------------------------------------------
  // normal commands
  // --------------------------------------------------

  const commands = {
    latest: latestPage,
    first: firstPage,
    archive: "/archive.html",
    report: "/archive_report.txt"
  };

  if (commands[v]) {
    window.location.href = commands[v];
  }
}

function setupViewer(config) {

  const {
    nextPage = null,
    prevPage = null,
    latestPage: latestPageInput = "tegning_latest.html",
    firstPage: firstPageInput = null,
    homePage = "/",
    archiveReportPath = "/archive_report.json",
    useArchiveReport = false
  } = config;

  const commandInput = document.getElementById("command");
  const swipeArea = document.getElementById("swipe-area");

  let latestPage = latestPageInput;
  let firstPage = firstPageInput;
  let archiveSequence = [];

  function runSetup() {

    // --------------------------------------------------
    // console input
    // --------------------------------------------------

    if (commandInput) {
      commandInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          goToCommand(this.value, {
            latestPage,
            firstPage,
            homePage,
            archiveSequence
          });
        }
      });
    }

    // --------------------------------------------------
    // keyboard navigation
    // drawing pages:
    //   right = next
    //   left = prev
    // homepage:
    //   right = latest
    //   left = first
    //   R = random
    // --------------------------------------------------

    document.addEventListener("keydown", function (event) {

      const activeElement = document.activeElement;
      const activeTag = activeElement ? activeElement.tagName.toLowerCase() : "";
      const typing = activeTag === "input" || activeTag === "textarea";

      if (typing) return;

      // let browser/system shortcuts pass through
      // examples: Cmd+R, Ctrl+R, Cmd+P, Cmd+F
      if (event.metaKey || event.ctrlKey || event.altKey) return;

      if (["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "r", "R", "f", "F"].includes(event.key)) {
        event.preventDefault();
      }

      if (event.key === "ArrowRight") {
        if (nextPage) {
          window.location.href = nextPage;
        } else if (latestPage) {
          window.location.href = latestPage;
        }
      }

      if (event.key === "ArrowLeft") {
        if (prevPage) {
          window.location.href = prevPage;
        } else if (firstPage) {
          window.location.href = firstPage;
        }
      }

      if (event.key === "ArrowUp" && latestPage) {
        window.location.href = latestPage;
      }

      if (event.key === "ArrowDown" && firstPage) {
        window.location.href = firstPage;
      }

      // --------------------------------------------------
      // random shortcut (R)
      // --------------------------------------------------

      if (event.key === "r" || event.key === "R") {
        goToRandom(archiveSequence);
      }

      // --------------------------------------------------
      // open full image
      // only works on drawing pages with an image
      // --------------------------------------------------

      if (event.key === "f" || event.key === "F") {
        const img = document.querySelector(".image-area img");

        if (img) {
          window.open(img.src, "_blank");
        }
      }
    });

    // --------------------------------------------------
    // swipe navigation
    // drawing pages:
    //   swipe left = next
    //   swipe right = prev
    // homepage:
    //   swipe left = latest
    //   swipe right = first
    // --------------------------------------------------

    if (swipeArea) {

      let touchStartX = 0;
      let touchStartY = 0;
      let touchEndX = 0;
      let touchEndY = 0;

      swipeArea.addEventListener(
        "touchstart",
        function (event) {
          const touch = event.changedTouches[0];
          touchStartX = touch.screenX;
          touchStartY = touch.screenY;
        },
        { passive: true }
      );

      swipeArea.addEventListener(
        "touchend",
        function (event) {
          const touch = event.changedTouches[0];

          touchEndX = touch.screenX;
          touchEndY = touch.screenY;

          const dx = touchEndX - touchStartX;
          const dy = touchEndY - touchStartY;

          if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {

            if (dx < 0) {
              if (nextPage) {
                window.location.href = nextPage;
              } else if (latestPage) {
                window.location.href = latestPage;
              }
            }

            if (dx > 0) {
              if (prevPage) {
                window.location.href = prevPage;
              } else if (firstPage) {
                window.location.href = firstPage;
              }
            }
          }
        },
        { passive: true }
      );
    }
  }

  // --------------------------------------------------
  // optional archive report loading
  // homepage uses this to discover first/latest/sequence
  // drawing pages still use fixed next/prev plus sequence
  // --------------------------------------------------

  if (useArchiveReport) {

    fetch(archiveReportPath)
      .then(r => r.json())
      .then(data => {

        if (data.latest) {
          latestPage = "/drawings/" + data.latest + ".html";
        }

        if (data.first) {
          firstPage = "/drawings/" + data.first + ".html";
        }

        if (Array.isArray(data.sequence)) {
          archiveSequence = data.sequence;
        }

        runSetup();
      })
      .catch(err => {
        console.error("Archive report load failed", err);
        runSetup();
      });

  } else {

    fetch(archiveReportPath)
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data.sequence)) {
          archiveSequence = data.sequence;
        }
      })
      .catch(err => {
        console.error("Archive report load failed", err);
      })
      .finally(() => {
        runSetup();
      });
  }
}