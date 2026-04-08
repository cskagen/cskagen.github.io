function goToRandom(archiveSequence) {
  if (!archiveSequence || archiveSequence.length === 0) return;

  const choice = archiveSequence[Math.floor(Math.random() * archiveSequence.length)];
  window.location.href = "/drawings/" + choice + ".html";
}

function getDrawingNumberFromPath() {
  const match = window.location.pathname.match(/tegning_nr(\d+)/);
  return match ? match[1] : null;
}

function openReplicaPageForNumber(nr) {
  if (!nr) return;
  window.open("/replica/tegning_nr" + nr + ".html", "_blank");
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

  if (/^\d+$/.test(v)) {
    window.location.href = "/drawings/tegning_nr" + v + ".html";
    return;
  }

  if (v === "print") {
    window.print();
    return;
  }

  if (v === "replica") {
    const nr = getDrawingNumberFromPath();
    if (nr) {
      openReplicaPageForNumber(nr);
    }
    return;
  }

  if (/^replica\s+\d+$/.test(v)) {
    const nr = v.split(/\s+/)[1];
    openReplicaPageForNumber(nr);
    return;
  }

  if (v === "replica list") {
    window.location.href = "/replica.html";
    return;
  }

  if (v === "home") {
    window.location.href = homePage;
    return;
  }

  if (v === "random") {
    goToRandom(archiveSequence);
    return;
  }

  const commands = {
    latest: latestPage,
    first: firstPage,
    archive: "/archive.html",
    report: "/archive_report.html"
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

    document.addEventListener("keydown", function (event) {
      const activeElement = document.activeElement;
      const activeTag = activeElement ? activeElement.tagName.toLowerCase() : "";
      const typing = activeTag === "input" || activeTag === "textarea";

      if (typing) return;
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
        return;
      }

      if (event.key === "ArrowLeft") {
        if (prevPage) {
          window.location.href = prevPage;
        } else if (firstPage) {
          window.location.href = firstPage;
        }
        return;
      }

      if (event.key === "ArrowUp") {
        if (latestPage) {
          window.location.href = latestPage;
        }
        return;
      }

      if (event.key === "ArrowDown") {
        if (firstPage) {
          window.location.href = firstPage;
        }
        return;
      }

      if (event.key === "r" || event.key === "R") {
        goToRandom(archiveSequence);
        return;
      }

      if (event.key === "f" || event.key === "F") {
        const img = document.querySelector(".image-area img");
        if (img) {
          window.open(img.src, "_blank");
        }
      }
    });

    if (swipeArea) {
      let touchStartX = 0;
      let touchStartY = 0;
      let touchEndX = 0;
      let touchEndY = 0;

      const SWIPE_THRESHOLD = 50;
      const TAP_MOVE_THRESHOLD = 12;

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

          const absDx = Math.abs(dx);
          const absDy = Math.abs(dy);

          if (absDx > SWIPE_THRESHOLD && absDx > absDy) {
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

            return;
          }

          if (absDx <= TAP_MOVE_THRESHOLD && absDy <= TAP_MOVE_THRESHOLD) {
            goToRandom(archiveSequence);
          }
        },
        { passive: true }
      );
    }
  }

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