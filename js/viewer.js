function goToCommand(value, latestPage, firstPage) {

  const v = value.trim().toLowerCase();

  if (!v) return;

  // --------------------------------------------------
  // direct number navigation
  // --------------------------------------------------

  if (/^\d+$/.test(v)) {
    window.location.href = "tegning_nr" + v + ".html";
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
  window.location.href = "/";
  return;
}

  // --------------------------------------------------
  // random command
  // --------------------------------------------------

  if (v === "random") {

    fetch("/archive_report.json")
      .then(r => r.json())
      .then(data => {

        const seq = data.sequence;

        if (!seq || seq.length === 0) return;

        const choice = seq[Math.floor(Math.random() * seq.length)];

        window.location.href = "/drawings/" + choice + ".html";

      })
      .catch(err => {
        console.error("Random navigation failed", err);
      });

    return;
  }

  // --------------------------------------------------
  // normal commands
  // --------------------------------------------------

  const commands = {
    latest: latestPage,
    first: firstPage,
    list: "list.html",
    bio: "bio.html",
    help: "help.html",
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
    latestPage = "tegning_latest.html",
    firstPage = "tegning_nr783.html"
  } = config;

  const commandInput = document.getElementById("command");
  const swipeArea = document.getElementById("swipe-area");

  // --------------------------------------------------
  // console input
  // --------------------------------------------------

  if (commandInput) {

    commandInput.addEventListener("keydown", function (event) {

      if (event.key === "Enter") {

        goToCommand(this.value, latestPage, firstPage);

      }

    });

  }

  // --------------------------------------------------
  // keyboard navigation
  // --------------------------------------------------

  document.addEventListener("keydown", function (event) {

    const activeElement = document.activeElement;
    const activeTag = activeElement ? activeElement.tagName.toLowerCase() : "";
    const typing = activeTag === "input" || activeTag === "textarea";

    if (typing) return;

    if (["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown"].includes(event.key)) {
      event.preventDefault();
    }

    if (event.key === "ArrowRight" && nextPage) {
      window.location.href = nextPage;
    }

    if (event.key === "ArrowLeft" && prevPage) {
      window.location.href = prevPage;
    }

    if (event.key === "ArrowUp") {
      window.location.href = latestPage;
    }

    if (event.key === "ArrowDown") {
      window.location.href = firstPage;
    }

    // open full image

    if (event.key === "f") {

      const img = document.querySelector(".image-area img");

      if (img) {
        window.open(img.src, "_blank");
      }

    }

  });

  // --------------------------------------------------
  // swipe navigation
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

          if (dx < 0 && nextPage) {
            window.location.href = nextPage;
          }

          if (dx > 0 && prevPage) {
            window.location.href = prevPage;
          }

        }

      },
      { passive: true }
    );

  }

}
