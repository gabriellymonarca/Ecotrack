    // Configurações comuns para todos os gráficos
export const chartConfig = {
    // Cores dos gráficos
    colors: {
        teal: 'rgb(75, 192, 192)',      // verde água
        coral: 'rgb(255, 99, 132)',      // rosa/vermelho
        blue: 'rgb(54, 162, 235)',       // azul
        yellow: 'rgb(255, 205, 86)'      // amarelo
    },
    // Opções comuns para todos os gráficos
    commonOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    boxWidth: 12,
                    padding: 10,
                    font: {
                        size: 11
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 11
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 11
                    }
                }
            }
        }
    }
};

// Função para buscar dados do MongoDB
export async function fetchData(documentName) {
    const response = await fetch(`/api/${documentName}`);
    const data = await response.json();
    console.log(`${documentName} data:`, data);
    return data;
}

// Função para criar um gráfico
export function createChart(ctx, type, data, options) {
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    return new Chart(ctx, {
        type: type,
        data: data,
        options: { ...chartConfig.commonOptions, ...options }
    });
}

// Função para popular o seletor de anos
export async function populateYearSelector(selectorId, years) {
    console.log(`Populando seletor de anos: ${selectorId} com ${years.length} anos`);
    const selector = document.getElementById(selectorId);
    selector.innerHTML = '';
    
    // Usar apenas os anos de 2020 até o ano atual
    const currentYear = new Date().getFullYear();
    const allYears = Array.from({length: currentYear - 2019}, (_, i) => (2020 + i).toString());
    
    allYears.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (years.length > 0 && !years.includes(year)) {
            option.disabled = true;
        }
        selector.appendChild(option);
    });
    
    return years.length > 0 ? years[0] : allYears[0];
}

// Função para popular o seletor de atividades
export async function populateActivitySelector(selectorId, activities) {
    console.log(`Populando seletor de atividades: ${selectorId} com ${activities.length} atividades`);
    const selector = document.getElementById(selectorId);
    selector.innerHTML = '';
    
    activities.forEach(activity => {
        const option = document.createElement('option');
        option.value = activity;
        option.textContent = activity;
        selector.appendChild(option);
    });
    
    return activities.length > 0 ? activities[0] : '';
}

// Função para obter os meses abreviados
export function getAbbreviatedMonths() {
    return [
        'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
        'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ];
}

// Função para obter o nome completo do mês
export function getFullMonthName(abbreviatedMonth) {
    const monthMap = {
        'jan': 'janeiro',
        'fev': 'fevereiro',
        'mar': 'março',
        'abr': 'abril',
        'mai': 'maio',
        'jun': 'junho',
        'jul': 'julho',
        'ago': 'agosto',
        'set': 'setembro',
        'out': 'outubro',
        'nov': 'novembro',
        'dez': 'dezembro'
    };
        return monthMap[abbreviatedMonth] || abbreviatedMonth;
}

// Função para mostrar mensagem de carregamento
export function showLoading(chartId) {
    const canvas = document.getElementById(chartId);
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '16px Arial';
    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    ctx.fillText('Carregando dados...', canvas.width / 2, canvas.height / 2);
}

export function hideLoading(chartId) {
    console.log(`Escondendo carregamento para: ${chartId}`);
    toggleLoading(chartId, false);
}

export function toggleLoading(chartId, show) {
    const chartContainer = document.getElementById(chartId).parentElement;
    const loadingIndicator = chartContainer.querySelector('.loading-indicator');
    
    if (loadingIndicator) {
        loadingIndicator.style.display = show ? 'block' : 'none';
    }
}