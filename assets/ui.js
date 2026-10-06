'use strict';
// Counter adapters listen for these semantic actions after their real IDs are configured.
function emitGoal(name) {
  document.dispatchEvent(new CustomEvent('analyticsgoal', {
    detail: {name, page: location.pathname}
  }));
}
document.querySelectorAll('[data-print-report]').forEach(button => {
  button.addEventListener('click', () => { emitGoal('printReport'); window.print(); });
});
document.querySelectorAll('.sources a').forEach(link => {
  link.addEventListener('click', () => emitGoal('openSource'));
});
