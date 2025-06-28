const months = JSON.parse(document.getElementById('months-data').textContent);
const salesData = JSON.parse(document.getElementById('sales-data').textContent);

const ctx = document.getElementById('salesChart').getContext('2d');
const salesChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: months,
        datasets: [{
            label: 'Sales (₹)',
            data: salesData,
            borderColor: '#2A8FF7',
            backgroundColor: '#2A8FF7',
            fill: false,
            tension: 0.3
        }]
    },
    options: {
        scales: {
            y: {
                ticks: {
                    callback: function(value) {
                        return '₹' + value;
                    }
                },
                beginAtZero: true,
                reverse: false  // make sure chart grows bottom to top
            }
        }
    }
});
