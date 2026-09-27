export function createDiffNavigator(items, viewers) {
    const previous = document.getElementById('previous-difference');
    const next = document.getElementById('next-difference');
    const info = document.getElementById('difference-info');
    if (!previous || !next || !info) return;

    let index = 0;
    const show = () => {
        if (!items.length) {
            info.textContent = 'Различий не обнаружено';
            previous.disabled = true;
            next.disabled = true;
            return;
        }
        info.textContent = `Отличие ${index + 1} из ${items.length}`;
        previous.disabled = index === 0;
        next.disabled = index === items.length - 1;
        viewers.forEach(viewer => viewer.goTo(items[index]));
    };

    previous.addEventListener('click', () => {
        if (index) {
            index -= 1;
            show();
        }
    });
    next.addEventListener('click', () => {
        if (index < items.length - 1) {
            index += 1;
            show();
        }
    });

    show();
}