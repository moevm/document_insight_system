import '../styles/anti_plagiarism.css';
import * as pdfjsLib from 'pdfjs-dist';
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";

$(function(){
    if ($("#student-pdf-download").length === 0 || $("#source-pdf-download").length === 0) {
        return;
    }

    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;

    function initPdfViewer(canvasId, canvasFrameId, prevBtnId, nextBtnId, pageNumId, pageCountId, pdfUrl) {
        let pdfDoc = null;
        let pageNum = 1;
        let pageIsRendering = false;
        let pageNumIsPending = null;

        const canvas = document.getElementById(canvasId);
        const canvasFrame = document.getElementById(canvasFrameId);
        const ctx = canvas.getContext('2d');

        const renderPage = num => {
            pageIsRendering = true;

            pdfDoc.getPage(num).then(page => {
                const baseViewport = page.getViewport({scale: 1});
                const targetWidth = canvasFrame.clientWidth || baseViewport.width;
                const scale = targetWidth / baseViewport.width;
                const viewport = page.getViewport({scale: scale});

                canvas.height = viewport.height;
                canvas.width = viewport.width;

                const renderCtx = {
                    canvasContext: ctx,
                    viewport
                };

                page.render(renderCtx).promise.then(() => {
                    pageIsRendering = false;

                    if (pageNumIsPending !== null) {
                        renderPage(pageNumIsPending);
                        pageNumIsPending = null;
                    }
                });

                document.getElementById(pageNumId).textContent = num;
            });
        };

        const queueRenderPage = num => {
            if (pageIsRendering) {
                pageNumIsPending = num;
            } else {
                renderPage(num);
            }
        };

        const showPrevPage = () => {
            if (pageNum <= 1) {
                return;
            }
            pageNum--;
            queueRenderPage(pageNum);
        };

        const showNextPage = () => {
            if (pageNum >= pdfDoc.numPages) {
                return;
            }
            pageNum++;
            queueRenderPage(pageNum);
        };

        const handleResize = () => {
            if (!pdfDoc) {
                return;
            }
            queueRenderPage(pageNum);
        };

        pdfjsLib
            .getDocument(pdfUrl)
            .promise.then(pdfDoc_ => {
                pdfDoc = pdfDoc_;
                document.getElementById(pageCountId).textContent = pdfDoc.numPages;
                renderPage(pageNum);
            });

        $('#' + prevBtnId).click(showPrevPage);
        $('#' + nextBtnId).click(showNextPage);
        window.addEventListener('resize', handleResize);

        if (window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(handleResize);
            resizeObserver.observe(canvasFrame);
        }
    }

    const studentPdfUrl = $("#student-pdf-download").attr('href');
    const sourcePdfUrl = $("#source-pdf-download").attr('href');

    initPdfViewer(
        'student-canvas',
        'student-canvas-frame',
        'student-prev-page',
        'student-next-page',
        'student-page-num',
        'student-page-count',
        studentPdfUrl
    );

    initPdfViewer(
        'source-canvas',
        'source-canvas-frame',
        'source-prev-page',
        'source-next-page',
        'source-page-num',
        'source-page-count',
        sourcePdfUrl
    );
});
