function goToRandom(archiveSequence) {
  if (!archiveSequence || archiveSequence.length === 0) return;

  const choice = archiveSequence[Math.floor(Math.random() * archiveSequence.length)];
  window.location.href = "/drawings/" + choice + ".html";
}

function getDrawingNumberFromPath() {
  const match = window.location.pathname.match(/tegning_nr(\d+)/);
  return match ? match[1] : null;
}

function isIOSDevice() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

function openReplicaPageForNumber(nr) {
  if (!nr) return;

  let url = "/replica/tegning_nr" + nr + ".html";

  if (isIOSDevice()) {
    url += "?clean=1";
  }

  window.open(url, "_blank");
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

  if (v === "about") {
    window.location.href = "/about.html";
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

  function navigateNext() {
    if (nextPage) {
      window.location.href = nextPage;
    } else if (latestPage) {
      window.location.href = latestPage;
    }
  }

  function navigatePrev() {
    if (prevPage) {
      window.location.href = prevPage;
    } else if (firstPage) {
      window.location.href = firstPage;
    }
  }

  function setupZoomableImage() {
    if (!swipeArea) return null;

    const img = swipeArea.querySelector("img");
    if (!img) return null;

    swipeArea.classList.add("zoom-enabled");

    let zoomShell = swipeArea.querySelector(".zoom-shell");
    if (!zoomShell) {
      zoomShell = document.createElement("div");
      zoomShell.className = "zoom-shell";
      img.parentNode.insertBefore(zoomShell, img);
      zoomShell.appendChild(img);
    }

    let scale = 1;
    let translateX = 0;
    let translateY = 0;

    const MIN_SCALE = 1;
    const MAX_SCALE = 4;

    function clamp(value, min, max) {
      return Math.min(max, Math.max(min, value));
    }

    function getPanLimits() {
      const rect = swipeArea.getBoundingClientRect();
      const maxX = Math.max(0, ((rect.width * scale) - rect.width) / 2);
      const maxY = Math.max(0, ((rect.height * scale) - rect.height) / 2);
      return { maxX, maxY };
    }

    function clampPan() {
      const { maxX, maxY } = getPanLimits();
      translateX = clamp(translateX, -maxX, maxX);
      translateY = clamp(translateY, -maxY, maxY);
    }

    function applyTransform() {
    img.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }

    function resetZoom() {
      scale = 1;
      translateX = 0;
      translateY = 0;
      applyTransform();
    }

    function isZoomed() {
      return scale > 1.01;
    }

    applyTransform();

    window.addEventListener("resize", function () {
      clampPan();
      applyTransform();
    });

    return {
      getScale: () => scale,
      isZoomed,
      resetZoom,
      panBy(dx, dy) {
        translateX += dx;
        translateY += dy;
        clampPan();
        applyTransform();
      },
      zoomAround(centerX, centerY, newScale) {
        const rect = swipeArea.getBoundingClientRect();
        const oldScale = scale;
        const nextScale = clamp(newScale, MIN_SCALE, MAX_SCALE);

        if (nextScale === oldScale) return;

        const viewportCenterX = rect.width / 2;
        const viewportCenterY = rect.height / 2;

        const offsetX = centerX - rect.left - viewportCenterX - translateX;
        const offsetY = centerY - rect.top - viewportCenterY - translateY;

        const scaleRatio = nextScale / oldScale;

        translateX -= offsetX * (scaleRatio - 1);
        translateY -= offsetY * (scaleRatio - 1);
        scale = nextScale;

        if (scale <= 1.01) {
          resetZoom();
          return;
        }

        clampPan();
        applyTransform();
      }
    };
  }

  function runSetup() {
    const zoomState = setupZoomableImage();
    const hasZoom = !!zoomState;

    if (commandInput) {
  commandInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {

      const value = this.value.trim();

      // Empty return → home
      if (value === "") {
        window.location.href = homePage;
        return;
      }

      goToCommand(value, {
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

if (event.key === "Enter") {
  event.preventDefault();
  window.location.href = homePage;
  return;
}

      if (["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "r", "R", "f", "F", "Escape"].includes(event.key)) {
        event.preventDefault();
      }

      if (event.key === "Escape" && hasZoom && zoomState.isZoomed()) {
        zoomState.resetZoom();
        return;
      }

      if (event.key === "ArrowRight") {
        if (!(hasZoom && zoomState.isZoomed())) {
          navigateNext();
        }
        return;
      }

      if (event.key === "ArrowLeft") {
        if (!(hasZoom && zoomState.isZoomed())) {
          navigatePrev();
        }
        return;
      }

      if (event.key === "ArrowUp") {
        if (!(hasZoom && zoomState.isZoomed()) && latestPage) {
          window.location.href = latestPage;
        }
        return;
      }

      if (event.key === "ArrowDown") {
        if (!(hasZoom && zoomState.isZoomed()) && firstPage) {
          window.location.href = firstPage;
        }
        return;
      }

      if (event.key === "r" || event.key === "R") {
        if (!(hasZoom && zoomState.isZoomed())) {
          goToRandom(archiveSequence);
        }
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

      let holdTimer = null;
      let holdTriggered = false;

      let mode = "idle"; // idle | swipe | pan | pinch
      let lastPanX = 0;
      let lastPanY = 0;

      let pinchStartDistance = 0;
      let pinchStartScale = 1;

      const SWIPE_THRESHOLD = 50;
      const TAP_MOVE_THRESHOLD = 12;
      const HOLD_DELAY = 280;

      function clearHoldTimer() {
        if (holdTimer) {
          clearTimeout(holdTimer);
          holdTimer = null;
        }
      }

      function markHoldTriggered() {
        holdTriggered = true;

        try {
          if (navigator.vibrate) {
            navigator.vibrate(10);
          }
        } catch (err) {
          // ignore
        }
      }

      function distanceBetweenTouches(t1, t2) {
        const dx = t2.clientX - t1.clientX;
        const dy = t2.clientY - t1.clientY;
        return Math.hypot(dx, dy);
      }

      function centerBetweenTouches(t1, t2) {
        return {
          x: (t1.clientX + t2.clientX) / 2,
          y: (t1.clientY + t2.clientY) / 2
        };
      }

      swipeArea.addEventListener(
        "touchstart",
        function (event) {
          if (hasZoom && event.touches.length === 2) {
            clearHoldTimer();
            holdTriggered = false;
            mode = "pinch";

            const t1 = event.touches[0];
            const t2 = event.touches[1];
            pinchStartDistance = distanceBetweenTouches(t1, t2);
            pinchStartScale = zoomState.getScale();
            return;
          }

          if (event.touches.length !== 1) return;

          const touch = event.touches[0];
          touchStartX = touch.screenX;
          touchStartY = touch.screenY;
          touchEndX = touchStartX;
          touchEndY = touchStartY;
          holdTriggered = false;

          lastPanX = touch.clientX;
          lastPanY = touch.clientY;

          if (hasZoom && zoomState.isZoomed()) {
            mode = "pan";
            clearHoldTimer();
          } else {
            mode = "swipe";
            clearHoldTimer();
            holdTimer = setTimeout(function () {
              if (!(hasZoom && zoomState.isZoomed()) && mode === "swipe") {
                markHoldTriggered();
              }
            }, HOLD_DELAY);
          }
        },
        { passive: true }
      );

      swipeArea.addEventListener(
        "touchmove",
        function (event) {
          if (hasZoom && event.touches.length === 2) {
            event.preventDefault();
            clearHoldTimer();
            holdTriggered = false;
            mode = "pinch";

            const t1 = event.touches[0];
            const t2 = event.touches[1];

            const currentDistance = distanceBetweenTouches(t1, t2);
            if (!pinchStartDistance) {
              pinchStartDistance = currentDistance;
              pinchStartScale = zoomState.getScale();
            }

            const center = centerBetweenTouches(t1, t2);
            const nextScale = pinchStartScale * (currentDistance / pinchStartDistance);
            zoomState.zoomAround(center.x, center.y, nextScale);
            return;
          }

          if (event.touches.length !== 1) return;

          const touch = event.touches[0];
          const dx = touch.screenX - touchStartX;
          const dy = touch.screenY - touchStartY;

          if (hasZoom && (zoomState.isZoomed() || mode === "pan")) {
            event.preventDefault();
            clearHoldTimer();

            const moveX = touch.clientX - lastPanX;
            const moveY = touch.clientY - lastPanY;
            zoomState.panBy(moveX, moveY);

            lastPanX = touch.clientX;
            lastPanY = touch.clientY;
            mode = "pan";
            return;
          }

          if (Math.abs(dx) > TAP_MOVE_THRESHOLD || Math.abs(dy) > TAP_MOVE_THRESHOLD) {
            clearHoldTimer();
          }
        },
        { passive: false }
      );

      swipeArea.addEventListener(
        "touchend",
        function (event) {
          clearHoldTimer();

          if (mode === "pinch") {
            if (hasZoom && event.touches.length === 1) {
              const touch = event.touches[0];
              lastPanX = touch.clientX;
              lastPanY = touch.clientY;
              mode = zoomState.isZoomed() ? "pan" : "idle";
            } else {
              mode = "idle";
            }

            pinchStartDistance = 0;
            holdTriggered = false;
            return;
          }

          const touch = event.changedTouches[0];
          if (!touch) {
            mode = "idle";
            holdTriggered = false;
            return;
          }

          touchEndX = touch.screenX;
          touchEndY = touch.screenY;

          const dx = touchEndX - touchStartX;
          const dy = touchEndY - touchStartY;

          const absDx = Math.abs(dx);
          const absDy = Math.abs(dy);

          if (hasZoom && (zoomState.isZoomed() || mode === "pan")) {
            mode = "idle";
            holdTriggered = false;
            return;
          }

          if (holdTriggered && absDx <= TAP_MOVE_THRESHOLD && absDy <= TAP_MOVE_THRESHOLD) {
            holdTriggered = false;
            mode = "idle";
            goToRandom(archiveSequence);
            return;
          }

          holdTriggered = false;

          if (absDx > SWIPE_THRESHOLD && absDx > absDy) {
            mode = "idle";

            if (dx < 0) {
              navigateNext();
            } else if (dx > 0) {
              navigatePrev();
            }

            return;
          }

          mode = "idle";
        },
        { passive: true }
      );

      swipeArea.addEventListener(
        "touchcancel",
        function () {
          clearHoldTimer();
          holdTriggered = false;
          mode = "idle";
          pinchStartDistance = 0;
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