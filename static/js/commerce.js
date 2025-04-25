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

// Function to populate year selector
function populateYearSelector(data, selectId) {
    const select = document.getElementById(selectId);
    if (!select) return;

    const date = [...new Set(data.map(item => item._id))].sort().reverse();
    select.innerHTML = date.map(date => `<option value="${date}">${date}</option>`).join('');
}

// Function to load volume chart
async function loadVolumeChart() {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;

    showLoading('volumeChart');
    
    try {
        const response = await fetch('/api/commerce/volume/series');
        if (!response.ok) throw new Error('Error loading volume data');
        
        const data = await response.json();
        
        if (ctx.chart) {
            ctx.chart.destroy();
        }
        
        ctx.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date),
                datasets: [{
                    label: 'Quantidade de Empresas',
                    data: data.map(item => item.value),
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
                                return `Empresas: ${formatNumber(context.raw)}`;
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
    } catch (error) {
        console.error('Error loading volume chart:', error);
        showError('Could not load volume chart. Please try again later.', 'volumeChart');
    }
}

// Function to load division chart
async function loadDivisionChart() {
    const ctx = document.getElementById('divisionChart');
    if (!ctx) return;

    showLoading('divisionChart');
    
    try {
        const response = await fetch('/api/commerce/division');
        if (!response.ok) throw new Error('Error loading division data');
        
        const data = await response.json();
        populateYearSelector(data, 'divisionDateSelect');
        
        const dateSelect = document.getElementById('divisionDateSelect');
        if (!dateSelect) return;

        const divisionLabelsMap = {
            vehicle_parts_motorcycle: 'Veículos e Peças',
            wholesale_trade: 'Comércio Atacadista',
            retail_trade: 'Comércio Varejista'
        };

        function updateChart() {
            const selectedDate = dateSelect.value;
            const dateData = data.find(item => item._id === selectedDate)?.data || [];
            
            if (ctx.chart) {
                ctx.chart.destroy();
            }

            ctx.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: dateData.map(item => divisionLabelsMap[item.name] || item.name),
                    datasets: [{
                        data: dateData.map(item => item.value),
                        backgroundColor: [
                            colors.blue,
                            colors.secondary,
                            colors.info
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${context.label}: ${formatNumber(value)} (${percentage}%)`;
                                }
                            }
                        },
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    size: 16
                                },
                                padding: 20,
                                color: function(context) {
                                    return getComputedStyle(document.body).color;
                                }
                            }
                        }
                    }
                }
            });
        }

        dateSelect.addEventListener('change', updateChart);
        updateChart();
    } catch (error) {
        console.error('Error loading division chart:', error);
        showError('Could not load division chart. Please try again later.', 'divisionChart');
    }
}

// Function to load ranking charts
async function loadRankingCharts() {
    const ctx1 = document.getElementById('rankingChart1');
    const ctx2 = document.getElementById('rankingChart2');
    const ctx3 = document.getElementById('rankingChart3');
    
    if (!ctx1 || !ctx2 || !ctx3) return;

    showLoading('rankingChart1');
    showLoading('rankingChart2');
    showLoading('rankingChart3');
    
    try {
        const response = await fetch('/api/commerce/ranking');
        if (!response.ok) throw new Error('Error loading ranking data');
        
        const data = await response.json();
        populateYearSelector(data, 'rankingDateSelect');
        
        const dateSelect = document.getElementById('rankingDateSelect');
        if (!dateSelect) return;

        function updateCharts() {
            const selectedDate = dateSelect.value;
            const dateData = data.find(item => item._id === selectedDate)?.data || [];
            
            const prefixes = ['4.', '3.', '2.'];
            const labels = ['Comércio Varejista', 'Comércio Atacadista', 'Comércio de Veículos'];

            const datasets = prefixes.map(prefix => {
                const nameData = dateData
                    .filter(item => item.name.startsWith(prefix))
                    .sort((a, b) => b.value - a.value)
                    .slice(0, 10);
                
                return {
                    labels: nameData.map(item => item.name),
                    data: nameData.map(item => item.value)
                };
            });

            [ctx1, ctx2, ctx3].forEach((ctx, index) => {
                if (ctx.chart) {
                    ctx.chart.destroy();
                }
                
                ctx.chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: datasets[index].labels,
                        datasets: [{
                            label: labels[index],
                            data: datasets[index].data,
                            backgroundColor: colors.primary
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `Empresas: ${formatNumber(context.raw)}`;
                                    }
                                }
                            },
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    font: {
                                        size: 16,
                                        weight: 'bold'
                                    },
                                    color: function(context) {
                                        return getComputedStyle(document.body).color;
                                    }
                                }
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
                                    color: getGridColor()
                                }
                            },
                            y: {
                                ticks: {
                                    callback: function(value) {
                                        const maxLenght = 40;
                                        return value.length > maxLenght ? value.slice(0, maxLenght) + '...': value;
                                    },
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
            });
        }

        dateSelect.addEventListener('change', updateCharts);
        updateCharts();
    } catch (error) {
        console.error('Error loading ranking charts:', error);
        showError('Could not load ranking charts. Please try again later.', 'rankingChart1');
        showError('Could not load ranking charts. Please try again later.', 'rankingChart2');
        showError('Could not load ranking charts. Please try again later.', 'rankingChart3');
    }
}

// Function to load revenue and expense chart
async function loadRevenueExpenseChart() {
    const ctx = document.getElementById('revenueExpenseChart');
    if (!ctx) return;

    showLoading('revenueExpenseChart');
    
    try {
        const response = await fetch('/api/commerce/revenue-expense/series');
        if (!response.ok) throw new Error('Error loading revenue and expense data');
        
        const rawData = await response.json();

        const formattedData = rawData.map(item => {
            const result = { date: item._id };
            item.data.forEach(entry => {
                result[entry.name] = entry.value;
            });
            return result;
        });
        
        if (ctx.chart) {
            ctx.chart.destroy();
        }
        
        ctx.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: formattedData.map(item => item.date),
                datasets: [
                    {
                        label: 'Receita',
                        data: formattedData.map(item => item.revenue),
                        borderColor: colors.success,
                        backgroundColor: colors.success + '20',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Despesa',
                        data: formattedData.map(item => item.expense),
                        borderColor: colors.warning,
                        backgroundColor: colors.warning + '20',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
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
                                return `R$ ${value.toFixed(0).replace('.', ',')} mi` ;
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
    } catch (error) {
        console.error('Error loading revenue and expense chart:', error);
        showError('Could not load revenue and expense chart. Please try again later.', 'revenueExpenseChart');
    }
}

// Function to load revenue and expense charts by division
async function loadRevenueExpenseDivisionCharts() {
    const ctx1 = document.getElementById('revenueExpenseChart1');
    const ctx2 = document.getElementById('revenueExpenseChart2');
    const ctx3 = document.getElementById('revenueExpenseChart3');
    
    if (!ctx1 || !ctx2 || !ctx3) return;

    showLoading('revenueExpenseChart1');
    showLoading('revenueExpenseChart2');
    showLoading('revenueExpenseChart3');
    
    try {
        const response = await fetch('/api/commerce/revenue-expense/grouped');
        if (!response.ok) throw new Error('Error loading revenue and expense data by division');
        
        const rawData = await response.json();
        populateYearSelector(rawData, 'revenueExpenseYearSelect');
        
        const yearSelect = document.getElementById('revenueExpenseYearSelect');
        if (!yearSelect) return;

        function updateCharts() {
            const selectedYear = yearSelect.value;
            const selectedDoc = rawData.find(item => item._id === selectedYear);
            if (!selectedDoc) return;

            const data = selectedDoc.data;

            const grouped = {
                vehicle_parts_motorcycle: { revenue: 0, expense: 0 },
                wholesale_trade: { revenue: 0, expense: 0 },
                retail_trade: { revenue: 0, expense: 0 }
            };

            data.forEach(item => {
                if (grouped[item.type]) {
                    grouped[item.type][item.name] = item.value;
                }
            });

            const chartData = [
                {
                    ctx: ctx1,
                    label: 'Comércio de Veículos',
                    values: grouped.vehicle_parts_motorcycle
                },
                {
                    ctx: ctx2,
                    label: 'Comércio Atacadista',
                    values: grouped.wholesale_trade
                },
                {
                    ctx: ctx3,
                    label: 'Comércio Varejista',
                    values: grouped.retail_trade
                }
            ];

            chartData.forEach(({ ctx, label, values }) => {
                if (ctx.chart) ctx.chart.destroy();

                ctx.chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Receita', 'Despesa'],
                        datasets: [{
                            label,
                            data: [values.revenue || 0, values.expense || 0],
                            backgroundColor: [colors.success, colors.warning]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `${context.label}: ${formatCurrency(context.raw)}`;
                                    }
                                }
                            },
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    font: {
                                        size: 16,
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
                                        return `R$ ${value.toFixed(0).replace('.', ',')} mi`;
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
            });
        }

        yearSelect.addEventListener('change', updateCharts);
        updateCharts();
    } catch (error) {
        console.error('Error loading revenue and expense charts by division:', error);
        ['revenueExpenseChart1', 'revenueExpenseChart2', 'revenueExpenseChart3'].forEach(id =>
            showError('Could not load chart. Please try again later.', id)
        );
    }
}

// Load all charts when the page is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadVolumeChart();
    loadDivisionChart();
    loadRankingCharts();
    loadRevenueExpenseChart();
    loadRevenueExpenseDivisionCharts();
});