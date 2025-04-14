import { 
    createChart,
    // Funções relacionadas a dados 
    fetchData, 
    // Funções relacionadas a seletores
    populateYearSelector, 
    populateActivitySelector,
    // Funções de utilidades 
    getAbbreviatedMonths,
    showLoading,
    hideLoading, // Adicionada a importação da função hideLoading
    chartConfig
} from './common.js';
// Função para inicializar os seletores de ano e segmento de serviço
async function initializeSelectors() {
    try {
        // Supondo que populateYearSelector precisa de um id do elemento select
        await populateYearSelector('yearSelectorVolume');
        
        // Inicializar o seletor de segmento de serviço
        const serviceSelector = document.getElementById('serviceVolumeSelector');
        
        // Buscar os segmentos disponíveis da API
        const response = await fetch('/get_service_segments');
        const segments = await response.json();
        
        // Limpar seletor atual
        serviceSelector.innerHTML = '<option value="">Selecione um segmento</option>';
        
        // Adicionar as opções ao seletor
        segments.forEach(segment => {
            const option = document.createElement('option');
            option.value = segment;
            option.textContent = segment;
            serviceSelector.appendChild(option);
        });
        
        console.log('Seletores inicializados com sucesso');
    } catch (error) {
        console.error('Erro ao inicializar os seletores:', error);
    }
}

async function loadAllCharts() {
    console.log('Iniciando carregamento de todos os gráficos');

    try {
        console.log('Carregando gráfico de Volume de Serviço');
        showLoading('chartVolumeMonthly'); // Corrigido para o ID correto do canvas

        const yearSelector = document.getElementById('yearSelectorVolume');
        const serviceSelector = document.getElementById('serviceVolumeSelector');
        
        const monthOrder = [
            'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ];

        function orderByMonth(dataArray) {
            return dataArray.sort((a, b) => {
                const [mesA] = a.date.split(' ');
                const [mesB] = b.date.split(' ');
                return monthOrder.indexOf(mesA.toLowerCase()) - monthOrder.indexOf(mesB.toLowerCase());
            });
        }
        
        async function updateVolumeMonthChart(year, service_segment) {
            showLoading('chartVolumeMonthly'); // Corrigido para o ID correto do canvas

            // Solicitar a criação dos dados no MongoDB
            await fetch('/aggregate_all_service', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ year: year, service_segment: service_segment })
            });

            // Buscar os dados criados
            const response = await fetch(`/get_service_volume_data?year=${year}&segment=${encodeURIComponent(service_segment)}`);
            const data = await response.json();

            if (!data || !data.monthly_data) {
                console.warn('Nenhum dado encontrado para o gráfico Volume de Serviço');
                hideLoading('chartVolumeMonthly'); // Corrigido para o ID correto do canvas
                return;
            }

            const orderedData = orderByMonth(data.monthly_data);
            const labels = orderedData.map(d => d.date);
            const values = orderedData.map(d => d.volume);

            const ctx = document.getElementById('chartVolumeMonthly').getContext('2d'); // Corrigido para o ID correto do canvas

            if (window.serviceVolumeChart) {
                window.serviceVolumeChart.destroy();
            }

            // Utilizando a função createChart importada para criar o gráfico
            window.serviceVolumeChart = createChart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Volume de Serviço',
                        data: values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        fill: false,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });

            hideLoading('chartVolumeMonthly'); // Corrigido para o ID correto do canvas
        }

        // Adicionar event listeners aos seletores
        yearSelector.addEventListener('change', () => {
            const selectedYear = yearSelector.value;
            const selectedSegment = serviceSelector.value;
            if (selectedYear && selectedSegment) {
                updateVolumeMonthChart(selectedYear, selectedSegment);
            }
        });

        serviceSelector.addEventListener('change', () => {
            const selectedYear = yearSelector.value;
            const selectedSegment = serviceSelector.value;
            if (selectedYear && selectedSegment) {
                updateVolumeMonthChart(selectedYear, selectedSegment);
            }
        });
    
    } catch (error) {
        console.error('Erro ao carregar o gráfico de Volume de Serviço', error);
        hideLoading('chartVolumeMonthly'); // Adicionado para garantir que o indicador de carregamento seja removido em caso de erro
    }
}
console.log('service.js carregado');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado em service.js');
    
    // Inicializar os seletores quando o DOM estiver carregado
    initializeSelectors();
    
    // Carregar todos os gráficos
    loadAllCharts();
});

