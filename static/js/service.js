// Global Chart.js settings
Chart.defaults.font.family = "'Roboto', sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.color = '#333';
Chart.defaults.borderColor = '#ddd';
Chart.defaults.animation.duration = 800;
Chart.defaults.animation.easing = 'easeInOutQuart';

// Colors for charts
const colors = {
    primary: '#229652',
    secondary: '#f1c40f',
    light: '#e9ecef',
    dark: '#343a40',
    success: '#229652',
    warning: '#f1c40f',
    danger: '#e74c3c',
    info: '#27ae60'
};

// Function to format numbers
function formatNumber(number) {
    return new Intl.NumberFormat('pt-BR').format(number);
}

// Function to display error message
function showError(message, elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i> ${message}
            </div>
        `;
    }
}

// Function to show loading indicator
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
}

// Function to populate year selector
function populateYearSelector(data, selectId) {
    const select = document.getElementById(selectId);
    if (!select) return;

    const years = [...new Set(data.map(item => item._id))].sort().reverse();
    select.innerHTML = years.map(year => `<option value="${year}">${year}</option>`).join('');
}

// Function to populate segment selector
function populateSegmentSelector(data, selectId) {
    const select = document.getElementById(selectId);
    if (!select) return;

    const segments = data.map(item => item._id).sort();
    select.innerHTML = segments.map(segment => {
        // Format segment name for display
        const displayName = segment
            .replace(/_/g, ' ')
            .replace(/\d+\.\s*/, '')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        
        return `<option value="${segment}">${displayName}</option>`;
    }).join('');
}

async function loadVolumeChart() {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;

    showLoading('volumeChart');
    
    try {
        const response = await fetch('/api/service/volume/monthly');
        if (!response.ok) throw new Error('Error loading volume data');
        
        const data = await response.json();
        
        // Populate selectors
        populateSegmentSelector(data, 'volumeSegmentSelect');
        
        const allYears = new Set();
        data.forEach(segment => {
            segment.data.forEach(item => {
                const year = item.date.split('-')[0];
                allYears.add(year);
            });
        });
        
        // Populate year selector
        const yearSelect = document.getElementById('volumeYearSelect');
        if (yearSelect) {
            yearSelect.innerHTML = [...allYears].sort().reverse()
                .map(year => `<option value="${year}">${year}</option>`).join('');
        }
        
        function updateChart() {
            const selectedSegment = document.getElementById('volumeSegmentSelect').value;
            const selectedYear = document.getElementById('volumeYearSelect').value;
            
            const segmentData = data.find(item => item._id === selectedSegment);
            if (!segmentData) return;
            
            // Filter data by selected year
            const filteredData = segmentData.data.filter(item => item.date.startsWith(selectedYear));
            
            if (ctx.chart) {
                ctx.chart.destroy();
            }
            
            ctx.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: filteredData.map(item => {
                        const [year, month] = item.date.split('-');
                        const monthNames = [
                            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                        ];
                        return monthNames[parseInt(month) - 1];
                    }),
                    datasets: [{
                        label: 'Volume de Serviços',
                        data: filteredData.map(item => item.value),
                        borderColor: colors.primary,
                        backgroundColor: colors.primary + '20',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Volume: ${formatNumber(context.raw)}`;
                                }
                            }
                        },
                        legend: {
                            labels: {
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        },
                        x: {
                            ticks: {
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        }
                    }
                }
            });
        }

        // Add event listeners for selectors
        document.getElementById('volumeSegmentSelect').addEventListener('change', updateChart);
        document.getElementById('volumeYearSelect').addEventListener('change', updateChart);
        
        updateChart();
    } catch (error) {
        console.error('Error loading volume chart:', error);
        showError('Could not load volume chart. Please try again later.', 'volumeChart');
    }
}

// Function to load service volume chart by segment
async function loadVolumeRankingChart() {
    const ctx = document.getElementById('volumeRankingChart');
    if (!ctx) return;

    showLoading('volumeRankingChart');
    
    try {
        const response = await fetch('/api/service/volume/ranking');
        if (!response.ok) throw new Error('Error loading volume data by segment');
        
        const data = await response.json();
        populateYearSelector(data, 'volumeRankingYearSelect');
        
        const yearSelect = document.getElementById('volumeRankingYearSelect');
        if (!yearSelect) return;

        function updateChart() {
            const selectedYear = yearSelect.value;
            const yearData = data.find(item => item._id === selectedYear)?.data || [];

            const sortedData = [...yearData].sort((a, b) => b.value - a.value);

            if (ctx.chart) {
                ctx.chart.destroy();
            }

            ctx.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sortedData.map(item => {

                        return item.name
                            .replace(/_/g, ' ')
                            .replace(/\d+\.\s*/, '')
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');
                    }),
                    datasets: [{
                        label: 'Volume de Serviços',
                        data: sortedData.map(item => item.value),
                        backgroundColor: colors.primary,
                        borderColor: colors.primary,
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Volume: ${formatNumber(context.raw)}`;
                                }
                            }
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        },
                        y: {
                            ticks: {
                                callback: function(label) {
                                    const maxLength = 40;
                                    return label.length > maxLength ? label.slice(0, maxLength) + '…' : label;
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }

        // Add event listener for year selector
        yearSelect.addEventListener('change', updateChart);
        
        // Initialize chart
        updateChart();
    } catch (error) {
        console.error('Error loading volume chart by segment:', error);
        showError('Could not load volume chart by segment. Please try again later.', 'volumeRankingChart');
    }
}

// Function to load service revenue chart
async function loadRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    showLoading('revenueChart');
    
    try {
        const response = await fetch('/api/service/revenue/monthly');
        if (!response.ok) throw new Error('Error loading revenue data');
        
        const data = await response.json();
        
        // Populate selectors
        populateSegmentSelector(data, 'revenueSegmentSelect');
        
        const allYears = new Set();
        data.forEach(segment => {
            segment.data.forEach(item => {
                const year = item.date.split('-')[0];
                allYears.add(year);
            });
        });
        
        // Populate year selector
        const yearSelect = document.getElementById('revenueYearSelect');
        if (yearSelect) {
            yearSelect.innerHTML = [...allYears].sort().reverse()
                .map(year => `<option value="${year}">${year}</option>`).join('');
        }
        
        // Function to update chart
        function updateChart() {
            const selectedSegment = document.getElementById('revenueSegmentSelect').value;
            const selectedYear = document.getElementById('revenueYearSelect').value;
            
            const segmentData = data.find(item => item._id === selectedSegment);
            if (!segmentData) return;
            
            // Filter data by selected year
            const filteredData = segmentData.data.filter(item => item.date.startsWith(selectedYear));
            
            if (ctx.chart) {
                ctx.chart.destroy();
            }
            
            ctx.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: filteredData.map(item => {
                        const [year, month] = item.date.split('-');
                        const monthNames = [
                            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                        ];
                        return monthNames[parseInt(month) - 1];
                    }),
                    datasets: [{
                        label: 'Receita de Serviços',
                        data: filteredData.map(item => item.value),
                        borderColor: colors.primary,
                        backgroundColor: colors.primary + '20',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Número-índice com ajuste sazonal: ${context.raw}`;
                                }
                            }
                        },
                        legend: {
                            labels: {
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value;
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        },
                        x: {
                            ticks: {
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        }
                    }
                }
            });
        }

        // Add event listeners for selectors
        document.getElementById('revenueSegmentSelect').addEventListener('change', updateChart);
        document.getElementById('revenueYearSelect').addEventListener('change', updateChart);
        
        // Initialize chart
        updateChart();
    } catch (error) {
        console.error('Error loading revenue chart:', error);
        showError('Could not load revenue chart. Please try again later.', 'revenueChart');
    }
}

// Function to load service revenue chart by segment
async function loadRevenueRankingChart() {
    const ctx = document.getElementById('revenueRankingChart');
    if (!ctx) return;

    showLoading('revenueRankingChart');
    
    try {
        const response = await fetch('/api/service/revenue/ranking');
        if (!response.ok) throw new Error('Error loading revenue data by segment');
        
        const data = await response.json();
        populateYearSelector(data, 'revenueRankingYearSelect');
        
        const yearSelect = document.getElementById('revenueRankingYearSelect');
        if (!yearSelect) return;

        function updateChart() {
            const selectedYear = yearSelect.value;
            const yearData = data.find(item => item._id === selectedYear)?.data || [];
            
            // Sort data by value (descending)
            const sortedData = [...yearData].sort((a, b) => b.value - a.value);
            
            // Destroy existing chart if any
            if (ctx.chart) {
                ctx.chart.destroy();
            }
            
            // Create new chart
            ctx.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sortedData.map(item => {
                        // Format segment name for display
                        return item.name
                            .replace(/_/g, ' ')
                            .replace(/\d+\.\s*/, '')
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');
                    }),
                    datasets: [{
                        label: 'Receita de Serviços',
                        data: sortedData.map(item => item.value),
                        backgroundColor: colors.primary,
                        borderColor: colors.primary,
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Número-índice com ajuste sazonal: ${context.raw}`;
                                }
                            }
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value;
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        },
                        y: {
                            ticks: {
                                callback: function(label) {
                                    const maxLength = 40;
                                    return label.length > maxLength ? label.slice(0, maxLength) + '…' : label;
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }

        // Add event listener for year selector
        yearSelect.addEventListener('change', updateChart);
        
        // Initialize chart
        updateChart();
    } catch (error) {
        console.error('Error loading revenue chart by segment:', error);
        showError('Could not load revenue chart by segment. Please try again later.', 'revenueRankingChart');
    }
}

// Initialize all charts when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadVolumeChart();
    loadVolumeRankingChart();
    loadRevenueChart();
    loadRevenueRankingChart();
});
