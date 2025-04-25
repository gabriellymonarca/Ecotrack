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
    success: '#2ecc71',
    warning: '#f1c40f',
    danger: '#f1c40f',
    info: '#27ae60',
    blue: '#2E6F9E'
};

// Function to get grid color based on current theme
function getGridColor() {
    const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
}

// Function to format numbers
function formatNumber(number) {
    return new Intl.NumberFormat('pt-BR').format(number);
}

// Function to format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
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

// Function to extract year from a date in YYYY-MM format
function getYearFromDate(date) {
    return date.split('-')[0];
}

// Function to load industrial production chart
async function loadProductionChart() {
    const ctx = document.getElementById('productionChart');
    if (!ctx) return;

    showLoading('productionChart');
    
    try {
        const response = await fetch('/api/industry/production/series');
        if (!response.ok) throw new Error('Error loading production data');
        
        const data = await response.json();
        
        // Populate activity selector
        const activitySelect = document.getElementById('activitySelect');
        const activities = data.map(item => ({
            id: item._id,
            name: item._id.replace(/_/g, ' ').toUpperCase()
        }));
        
        activitySelect.innerHTML = activities.map(activity => 
            `<option value="${activity.id}">${activity.name}</option>`
        ).join('');
        
        // Populate year selector
        const productionYearSelect = document.getElementById('productionYearSelect');
        const allYears = new Set();
        data.forEach(activity => {
            activity.data.forEach(item => {
                const year = item.date.split('-')[0];
                allYears.add(year);
            });
        });
                
        productionYearSelect.innerHTML = [...allYears].sort().map(year => 
            `<option value="${year}">${year}</option>`
        ).join('');
        
        function updateChart() {
            const selectedActivity = activitySelect.value;
            const selectedYear = productionYearSelect.value;
            
            const activityData = data.find(item => item._id === selectedActivity);
            if (!activityData) return;
            
            const filteredData = activityData.data
            .filter(item => getYearFromDate(item.date) === selectedYear)
            .sort((a, b) => a.date.localeCompare(b.date));
        
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
                        label: 'Índice de Produção',
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
                                    return `Índice: ${formatNumber(context.raw)}`;
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
                                color: getGridColor()
                            }
                        },
                        x: {
                            ticks: {
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: getGridColor()
                            }
                        }
                    }
                }
            });
        }
        
        // Update chart when selectors change
        activitySelect.addEventListener('change', updateChart);
        productionYearSelect.addEventListener('change', updateChart);
        
        // Load initial chart
        updateChart();
        
    } catch (error) {
        console.error('Error loading production chart:', error);
        showError('Could not load industrial production data.', 'productionChart');
    }
}

// Function to load revenue chart
async function loadRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    showLoading('revenueChart');
    
    try {
        const response = await fetch('/api/industry/revenue/yearly');
        if (!response.ok) throw new Error('Error loading revenue data');
        
        const data = await response.json();
        
        // Populate CNAE selector
        const cnaeSelect = document.getElementById('cnaeSelect');
        const cnaeActivities = data.map(item => ({
            id: item._id,
            name: item._id.replace(/_/g, ' ').toUpperCase()
        }));
        
        cnaeSelect.innerHTML = cnaeActivities.map(activity => 
            `<option value="${activity.id}">${activity.name}</option>`
        ).join('');
        
        function updateChart() {
            const selectedCnae = cnaeSelect.value;
            const cnaeData = data.find(item => item._id === selectedCnae);
            if (!cnaeData) return;
            
            // Destroy existing chart if any
            if (ctx.chart) {
                ctx.chart.destroy();
            }
            
            // Create new chart
            ctx.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: cnaeData.data.map(item => item.date),
                    datasets: [{
                        label: 'Receita',
                        data: cnaeData.data.map(item => item.value),
                        backgroundColor: colors.primary
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Receita: ${formatCurrency(context.raw)}`;
                                }
                            }
                        },
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
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
                                    return formatCurrency(value);
                                },
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: getGridColor()
                            }
                        },
                        x: {
                            ticks: {
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            },
                            grid: {
                                color: getGridColor()
                            }
                        }
                    }
                }
            });
        }
        
        // Update chart when selector changes
        cnaeSelect.addEventListener('change', updateChart);
        
        // Load initial chart
        updateChart();
        
    } catch (error) {
        console.error('Error loading revenue chart:', error);
        showError('Could not load revenue data.', 'revenueChart');
    }
}

// Load all charts when the page is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadProductionChart();
    loadRevenueChart();
});
