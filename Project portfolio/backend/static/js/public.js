document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('.nav-toggle');
  if (navToggle) {
    navToggle.addEventListener('click', () => {
      document.querySelector('.site-nav')?.classList.toggle('open');
    });
  }
});
