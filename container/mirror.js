// Mirror build only (Frankfurt standby copy): this host must not receive personal data,
// so every lead form is replaced with a Telegram link.
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form').forEach(function (f) {
    var box = document.createElement('div');
    box.style.cssText = 'padding:24px;border:1px solid currentColor;border-radius:12px;text-align:center;line-height:1.5';
    box.innerHTML = 'Форма заявки временно не работает.<br>Напишите мне в Телеграм: ' +
      '<a href="https://t.me/sergeynasyrov" target="_blank" rel="noopener">@sergeynasyrov</a>';
    f.replaceWith(box);
  });
});
