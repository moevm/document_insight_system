import '../styles/admin_criterions.css';

document.querySelectorAll('.toggle').forEach(item => {
    item.addEventListener('click', event => {
        const nextRow = item.parentNode.nextElementSibling;
        if (nextRow.classList.contains('hidden')) {
            nextRow.classList.remove('hidden');
            nextRow.classList.add('visible');
        } else {
            nextRow.classList.add('hidden');
            nextRow.classList.remove('visible');
        }
    });
});

const toggleButton = document.getElementById('toggleButton');
if (toggleButton) {
    toggleButton.addEventListener('click', () => {
        const button = document.getElementById('toggleButton');
        if (button.innerHTML.trim() === '<i class="bi bi-chevron-double-down"></i>') {
            button.innerHTML = '<i class="bi bi-chevron-double-up"></i>';
            document.querySelectorAll('.hidden').forEach(row => {
                row.classList.remove('hidden');
                row.classList.add('visible');
            });
        } else {
            button.innerHTML = '<i class="bi bi-chevron-double-down"></i>';
            document.querySelectorAll('.visible').forEach(row => {
                row.classList.remove('visible');
                row.classList.add('hidden');
            });
        }
    });
}
