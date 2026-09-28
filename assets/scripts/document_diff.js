import '../styles/document_diff.css';
import { initPdfComparison } from './document_diff_pdf';
import { initPresentationViewer } from './document_diff_presentation';
import { initDocumentSelection } from './document_diff_selection';

$(function () {
    const form = document.getElementById('document-diff-form');
    if (form) {
        initDocumentSelection(form);
    } else if (window.diffData && window.diffData.format === 'pptx') {
        initPresentationViewer(window.diffData.mapping || []);
    } else {
        initPdfComparison(window.diffData ? window.diffData.fragments || [] : []);
    }
});