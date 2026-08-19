// Highlight the active sidebar link based on current path.
(function () {
  var path = window.location.pathname;
  document.querySelectorAll(".sidebar .nav-link").forEach(function (link) {
    var href = link.getAttribute("href");
    if (href && href !== "#" && path.startsWith(href)) {
      link.classList.add("active");
    }
  });
})();

// Generic "add another row" helper for repeatable sub-forms (children, etc.).
function cloneRow(templateId, containerId) {
  var tpl = document.getElementById(templateId);
  var container = document.getElementById(containerId);
  if (!tpl || !container) return;
  var idx = container.children.length;
  var html = tpl.innerHTML.replace(/__INDEX__/g, idx);
  var wrapper = document.createElement("div");
  wrapper.innerHTML = html;
  container.appendChild(wrapper.firstElementChild);
}

function removeRow(btn) {
  var row = btn.closest("[data-repeat-row]");
  if (row) row.remove();
}
