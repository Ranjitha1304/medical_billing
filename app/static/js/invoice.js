function printInvoice() {
    window.print();
}

function downloadPDF() {
    const element = document.getElementById('invoice-box');
    import('https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js')
        .then(() => {
            const opt = {
                margin:       0.3,
                filename:     'invoice.pdf',
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2 },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        });
}
