// Modal open/close for follow-up chat and other dialogs
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-modal-open]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-modal-open");
      var modal = document.getElementById(id);
      if (modal) {
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
      }
    });
  });

  document.querySelectorAll("[data-modal-close]").forEach(function (el) {
    el.addEventListener("click", function () {
      var id = el.getAttribute("data-modal-close");
      var modal = document.getElementById(id);
      if (modal) {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
      }
    });
  });
});
