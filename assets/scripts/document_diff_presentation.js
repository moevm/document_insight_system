import { createDiffNavigator } from './document_diff_navigation';

function slidesForSide(mapping, side) {
    return mapping.filter(item => item[`image_${side}`]);
}

function createSlideViewer(side, mapping) {
    const image = document.getElementById(`slide-img-${side}`);
    const empty = document.getElementById(`slide-empty-${side}`);
    const previous = document.getElementById(`slide-${side}-prev`);
    const next = document.getElementById(`slide-${side}-next`);
    const pageInput = document.getElementById(`slide-${side}-page-input`);
    const pageCount = document.getElementById(`slide-${side}-page-count`);
    const slides = slidesForSide(mapping, side);
    const total = slides.length;
    let index = 0;

    const paint = (item, { canPrev, canNext } = {}) => {
        if (!item || !item[`image_${side}`]) {
            image.classList.add('d-none');
            empty.classList.remove('d-none');
            empty.textContent = total ? 'Слайда нет' : 'Нет слайдов для отображения';
            pageInput.value = '';
            pageInput.disabled = true;
            pageCount.textContent = total;
            previous.disabled = canPrev === undefined ? true : !canPrev;
            next.disabled = canNext === undefined ? true : !canNext;
            return;
        }
        image.src = item[`image_${side}`];
        image.classList.remove('d-none');
        empty.classList.add('d-none');
        pageInput.disabled = false;
        pageInput.max = total;
        pageInput.value = item[`slide_${side}`] + 1;
        pageCount.textContent = total;
        previous.disabled = canPrev === undefined ? index === 0 : !canPrev;
        next.disabled = canNext === undefined ? index === slides.length - 1 : !canNext;
    };

    const render = () => {
        if (!slides.length) {
            paint(null);
            return;
        }
        paint(slides[index]);
    };

    const goToSlideNumber = num => {
        const targetIndex = slides.findIndex(item => item[`slide_${side}`] + 1 === num);
        if (targetIndex !== -1) {
            index = targetIndex;
            render();
        } else if (slides[index]) {
            pageInput.value = slides[index][`slide_${side}`] + 1;
        }
    };

    const neighborsInMapping = item => {
        const position = mapping.indexOf(item);
        let previousIndex = -1;
        let nextIndex = -1;
        slides.forEach((slide, slideIndex) => {
            const slidePosition = mapping.indexOf(slide);
            if (slidePosition < position) {
                previousIndex = slideIndex;
            } else if (slidePosition > position && nextIndex === -1) {
                nextIndex = slideIndex;
            }
        });
        return { previousIndex, nextIndex };
    };

    const goTo = item => {
        const withinCurrent = slides.indexOf(item);
        if (withinCurrent !== -1) {
            index = withinCurrent;
            render();
            return;
        }
        const { previousIndex, nextIndex } = neighborsInMapping(item);
        index = previousIndex;
        paint(item[`image_${side}`] ? item : null, {
            canPrev: previousIndex !== -1,
            canNext: nextIndex !== -1,
        });
    };

    previous.addEventListener('click', () => {
        if (index > 0) {
            index -= 1;
            render();
        }
    });
    next.addEventListener('click', () => {
        if (index < slides.length - 1) {
            index += 1;
            render();
        }
    });
    pageInput.addEventListener('change', () => {
        const num = parseInt(pageInput.value, 10);
        if (!Number.isNaN(num)) {
            goToSlideNumber(num);
        }
    });
    pageInput.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            pageInput.blur();
        }
    });

    return { render, goTo };
}

export function initPresentationViewer(mapping) {
    const viewers = ['a', 'b'].map(side => createSlideViewer(side, mapping));
    viewers.forEach(viewer => viewer.render());

    const diffs = mapping.filter(item => item.status_label !== 'unchanged');
    createDiffNavigator(diffs, viewers);
}