'use strict';

function emitGoal(name) {
  document.dispatchEvent(new CustomEvent('analyticsgoal', {
    detail: {name, page: location.pathname}
  }));
}

document.querySelectorAll('[data-print-report]').forEach(button => {
  button.addEventListener('click', () => { emitGoal('printReport'); window.print(); });
});
document.querySelectorAll('.sources a, .source-note a').forEach(link => {
  link.addEventListener('click', () => emitGoal('openSource'));
});

function normalizeSearch(text) {
  return text.toLocaleLowerCase('ru').replaceAll('ё', 'е').trim();
}

function matchesPhone(searchText, categories, query, selectedFilter) {
  const stopWords = new Set(['смартфон', 'смартфоны', 'телефон', 'телефоны', 'для', 'с', 'хочу', 'ищу', 'хорошей', 'хорошая', 'хороший', 'мне', 'и', 'под']);
  const synonyms = {игр: 'игры', игровой: 'игры', игровые: 'игры', игрового: 'игры', камерой: 'камера', камеры: 'камера', камеру: 'камера', фотографий: 'фото', компактного: 'компактный', компактные: 'компактный', маленький: 'компактный'};
  const tokens = normalizeSearch(query).replace(/[^\p{L}\p{N}-]+/gu, ' ').split(/\s+/)
    .filter(token => token && !stopWords.has(token)).map(token => synonyms[token] || token);
  const haystack = normalizeSearch(searchText);
  return (selectedFilter === 'all' || categories.split(' ').includes(selectedFilter))
    && tokens.every(token => haystack.includes(token) || haystack.replace(/\s+/g, '').includes(token));
}

const searchInput = document.getElementById('phone-search');
if (searchInput) {
  const cards = [...document.querySelectorAll('#catalog [data-phone-card]')];
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const counter = document.querySelector('[data-result-count]');
  const empty = document.querySelector('[data-empty-state]');
  let selectedFilter = 'all';

  function applyFilter() {
    let visible = 0;
    cards.forEach(card => {
      const match = matchesPhone(card.dataset.search, card.dataset.categories, searchInput.value, selectedFilter);
      card.hidden = !match;
      if (match) visible++;
    });
    counter.textContent = 'Показано моделей: ' + visible;
    empty.hidden = visible !== 0;
    filterButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selectedFilter)));
  }

  function resetFilter() {
    searchInput.value = '';
    selectedFilter = 'all';
    applyFilter();
    searchInput.focus();
  }

  searchInput.addEventListener('input', applyFilter);
  filterButtons.forEach(button => button.addEventListener('click', () => {
    selectedFilter = button.dataset.filter;
    applyFilter();
  }));
  document.querySelector('[data-clear-search]').addEventListener('click', resetFilter);
  document.querySelector('[data-reset-search]').addEventListener('click', resetFilter);
  const initialQuery = new URLSearchParams(location.search).get('q');
  if (initialQuery) searchInput.value = initialQuery;
  applyFilter();
}
