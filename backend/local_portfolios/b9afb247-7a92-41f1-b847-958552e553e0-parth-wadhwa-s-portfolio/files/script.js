document.addEventListener('DOMContentLoaded', () => {
 console.log('Portfolio initialized.');
 const projectCards = document.querySelectorAll('.project-card');
 const skillCategories = document.querySelectorAll('.skill-category');

 projectCards.forEach((card) => {
 card.addEventListener('mouseover', () => {
 card.style.transform = 'translateY(-10px)';
 card.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.3)';
 });

 card.addEventListener('mouseout', () => {
 card.style.transform = 'translateY(0)';
 card.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
 });
 });

 skillCategories.forEach((category) => {
 category.addEventListener('mouseover', () => {
 category.style.backgroundColor = '#333333';
 });

 category.addEventListener('mouseout', () => {
 category.style.backgroundColor = '#2b2b2b';
 });
 });
});
