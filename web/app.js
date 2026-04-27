// Tabs
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.tab-panel');
tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.tab;
    tabs.forEach((t) => t.classList.toggle('active', t === tab));
    panels.forEach((p) => p.classList.toggle('active', p.dataset.panel === target));
  });
});

// Copy install command
const copyText = async (text, button) => {
  try {
    await navigator.clipboard.writeText(text);
    const originalText = button.querySelector('span:last-child')?.textContent;
    button.classList.add('copied');
    if (originalText) {
      button.querySelector('span:last-child').textContent = 'Copied!';
      setTimeout(() => {
        button.classList.remove('copied');
        button.querySelector('span:last-child').textContent = originalText;
      }, 1600);
    }
  } catch (err) {
    console.error('clipboard failed', err);
  }
};

document.querySelectorAll('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const targetId = btn.dataset.copy;
    const code = document.getElementById(targetId)?.querySelector('code')?.textContent;
    if (code) copyText(code, btn);
  });
});

// Click on the command box itself to copy it
const cmdBox = document.querySelector('#curl-cmd');
if (cmdBox) {
  cmdBox.addEventListener('click', () => {
    const code = cmdBox.querySelector('code')?.textContent;
    const btn = document.querySelector('[data-copy="curl-cmd"]');
    if (code && btn) copyText(code, btn);
  });
}
