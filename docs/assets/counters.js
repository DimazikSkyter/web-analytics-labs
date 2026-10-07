'use strict';
const counterConfig = JSON.parse(document.getElementById('counter-config').textContent);
const allowedGoals = new Set(['printReport', 'openSource']);

function withSberCounter(action) {
  if (window.top100Counter) action();
  else (window._top100q = window._top100q || []).push(action);
}

document.addEventListener('analyticsgoal', event => {
  const {name, page} = event.detail;
  if (!allowedGoals.has(name)) return;
  if (counterConfig.mytracker) {
    (window._tmr = window._tmr || []).push({
      id: String(counterConfig.mytracker.id), type: 'reachGoal',
      goal: name, params: {page}
    });
  }
  if (counterConfig.sberads) {
    withSberCounter(() => {
      if (typeof window.top100d === 'function') {
        window.top100d(counterConfig.sberads.id, 'reachGoal', name, {page});
      } else {
        window.top100Counter.trackEvent(name, {page});
      }
    });
  }
});

if (counterConfig.sberads) {
  withSberCounter(() => window.top100Counter.drawLogoTo('sber-counter-badge'));
}
