document.addEventListener('DOMContentLoaded', () => {
 console.log('Portfolio initialized.');
 const cards = document.querySelectorAll('.card');
 const sections = document.querySelectorAll('section');
 const observer = new IntersectionObserver((entries) => {
 entries.forEach((entry) => {
 if (entry.isIntersecting) {
 entry.target.classList.add('animate');
 }
 });
 }, {
 threshold: 0.5,
 });
 sections.forEach((section) => {
 observer.observe(section);
 });
});
