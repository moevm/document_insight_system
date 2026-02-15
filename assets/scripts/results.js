import '../styles/results.css';
import * as pdfjsLib from 'pdfjs-dist';
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";

$(function(){
        if($("#stats_table").length > 0){
            let pdfDoc,
                pageNum,
                pageIsRendering,
                pageNumIsPending,
                scale,
                canvas,
                ctx,
                currentPage;
            
            pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
            
            const renderPage = num => {
                pageIsRendering = true;
            
                pdfDoc.getPage(num).then(page => {
                    const viewport = page.getViewport({ scale });
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
            
                    $('#page-num')[0].textContent = num;
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
            
            const toggleAllVerdicts = () => {
                $('.accordian-body').collapse('toggle');
            };
            
            if ($("#pdf_download").length !== 0) {
                var href = $("#pdf_download").attr('href');
                pdfDoc = null;
                pageNum = 1;
                pageIsRendering = false,
                    pageNumIsPending = null;
                scale = 1.1;
                canvas = $("#the-canvas")[0];
                ctx = canvas.getContext("2d");
                var href = $("#pdf_download").attr('href');
                pdfDoc = null;
                pageNum = 1;
                pageIsRendering = false,
                    pageNumIsPending = null;
                scale = 1.1;
            
                canvas = document.getElementById('the-canvas');
                ctx = canvas.getContext('2d');
            
                pdfjsLib
                    .getDocument(href)
                    .promise.then(pdfDoc_ => {
                        pdfDoc = pdfDoc_;
            
                        $('#page-count')[0].textContent = pdfDoc.numPages;
                        renderPage(pageNum);
                    });
            
                $('#prev-page').click(showPrevPage);
                $('#next-page').click(showNextPage);
            }
            
            $('#showAllVerdicts').click(toggleAllVerdicts);
        
        // function for automatic reload page after checking:
        let reloaded = true
        
        function checkStatus(end_check_function){
            let request = new XMLHttpRequest();
                const check_id = window.location.pathname.substr(window.location.pathname.lastIndexOf('/') + 1);
                request.open('GET', '/api/results/ready/' + check_id, true);
                request.onreadystatechange = function () {
                    if (request.readyState === XMLHttpRequest.DONE) {
                        if (request.status === 200) {
                            let response = JSON.parse(request.responseText);
                            console.log(response.is_ended)
                            if (response.is_ended && reloaded) {
                                end_check_function();
                                return;
                            } else {
                                reloaded = false
                                if (response.is_ended) {
                                    window.location.href = '/results/' + check_id;
                                }
                            }
                        } else {
                            console.error('Request failed:', request.status);
                            end_check_function();
                        }
                    }
                };
                request.send();
        }

        function recheckStatus() {
            const intervalId = setInterval(() => {
                checkStatus(() => {clearInterval(intervalId)});
            }, 10000);
        }
        
        checkStatus(() => {});
        recheckStatus()
    }
});

document.querySelectorAll('.toggleresult').forEach(item => {
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

const toggleButtonResult = document.getElementById('toggleButtonResult');
if (toggleButtonResult) {
    toggleButtonResult.addEventListener('click', () => {
        const button = document.getElementById('toggleButtonResult');
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
