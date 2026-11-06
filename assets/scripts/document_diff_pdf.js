import * as pdfjsLib from 'pdfjs-dist';
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.entry';
import { createDiffNavigator } from './document_diff_navigation';

function createViewer(prefix, url, location) {
    let documentPdf, page = location ? location.page + 1 : 1, rendering = false, pending, ratio = location && location.y_ratio;
    const canvas = document.getElementById(`${prefix}-canvas`);
    const frame = document.getElementById(`${prefix}-canvas-frame`);
    const context = canvas.getContext('2d');
    const render = number => {
        rendering = true;
        documentPdf.getPage(number).then(pdfPage => {
            const base = pdfPage.getViewport({ scale: 1 });
            const viewport = pdfPage.getViewport({ scale: (frame.clientWidth || base.width) / base.width });
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            return pdfPage.render({ canvasContext: context, viewport }).promise;
        }).then(() => {
            rendering = false;
            if (ratio !== null && ratio !== undefined) {
                const holder = document.getElementById('document_diff_holder');
                holder.scrollTo({ top: Math.max(0, holder.scrollTop + canvas.getBoundingClientRect().top - holder.getBoundingClientRect().top + canvas.height * ratio - 100), behavior: 'smooth' });
                ratio = null;
            }
            if (pending) {
                const next = pending;
                pending = null;
                render(next);
            }
        });
        document.getElementById(`${prefix}-page-input`).value = number;
    };
    const show = number => {
        if (rendering) pending = number;
        else render(number);
    };
    const move = delta => {
        const next = page + delta;
        if (documentPdf && next >= 1 && next <= documentPdf.numPages) {
            page = next;
            show(page);
        }
    };
    document.getElementById(`${prefix}-prev-page`).addEventListener('click', () => move(-1));
    document.getElementById(`${prefix}-next-page`).addEventListener('click', () => move(1));
    document.getElementById(`${prefix}-page-input`).addEventListener('change', event => {
        const next = Number(event.target.value);
        if (documentPdf && next >= 1 && next <= documentPdf.numPages) {
            page = next;
            show(page);
        }
    });
    pdfjsLib.getDocument(url).promise.then(pdf => {
        documentPdf = pdf;
        document.getElementById(`${prefix}-page-count`).textContent = pdf.numPages;
        render(page);
    });
    new ResizeObserver(() => documentPdf && show(page)).observe(frame);
    return { goTo: target => {
        if (target) {
            ratio = target.y_ratio || 0;
            page = target.page + 1;
            if (documentPdf) show(page);
        }
    }};
}

export function initPdfComparison(fragments) {
    const firstUrl = document.getElementById('student-pdf-download');
    const secondUrl = document.getElementById('source-pdf-download');
    if (!firstUrl || !secondUrl) return;
    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
    const first = createViewer('student', firstUrl.href, fragments[0] && (fragments[0].doc1 || fragments[0].doc2));
    const second = createViewer('source', secondUrl.href, fragments[0] && (fragments[0].doc2 || fragments[0].doc1));
    createDiffNavigator(fragments, [
        { goTo: item => first.goTo(item.doc1 || item.doc2) },
        { goTo: item => second.goTo(item.doc2 || item.doc1) },
    ]);
}