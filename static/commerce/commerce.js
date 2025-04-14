import { chartConfig, fetchData, createChart } from './common.js';

console.log('commerce.js carregado');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado em commerce.js');

    // --------------------------------- Funções utilitárias --------------------------------- //
    // Elementos da UI
    const backToTopButton = document.getElementById('backToTop');
    const customTooltip = document.getElementById('customTooltip');
    const loadingIndicators = document.querySelectorAll('.loading-indicator');

    // Função para mostrar/esconder o botão de voltar ao topo
    function toggleBackToTopButton() {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    }

    // Função para voltar ao topo da página
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    // Função para mostrar tooltip personalizado
    function showTooltip(element, text) {
        const rect = element.getBoundingClientRect();
        customTooltip.textContent = text;
        customTooltip.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
        customTooltip.style.top = `${rect.top + window.scrollY - 30}px`;
        customTooltip.classList.add('visible');
    }

    // Função para esconder tooltip
    function hideTooltip() {
        customTooltip.classList.remove('visible');
    }

    // Função para mostrar/esconder indicador de carregamento
    function toggleLoading(chartId, show) {
        const chartContainer = document.getElementById(chartId).parentElement;
        const loadingIndicator = chartContainer.querySelector('.loading-indicator');
        
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
    }

    // Adicionar event listeners para o botão de voltar ao topo
    window.addEventListener('scroll', toggleBackToTopButton);
    backToTopButton.addEventListener('click', scrollToTop);

    // Adicionar tooltips aos seletores
    const selectors = document.querySelectorAll('.form-select');
    selectors.forEach(selector => {
        selector.addEventListener('mouseenter', function() {
            const label = this.previousElementSibling?.textContent || 'Seletor';
            showTooltip(this, label);
        });
        
        selector.addEventListener('mouseleave', hideTooltip);
    });

    async function populateYearSelector(selectorId, years) {
        console.log(`Populando seletor de anos: ${selectorId} com ${years.length} anos`);
        const selector = document.getElementById(selectorId);
        if (!selector) {
            console.error(`Seletor não encontrado: ${selectorId}`);
            return '';
        }
        
        selector.innerHTML = '';
        
        const allYears = Array.from({length: 15}, (_, i) => (2011 + i).toString());
        
        allYears.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (!years.includes(year)) {
                option.disabled = true;
            }
            selector.appendChild(option);
        });
        
        const defaultYear = years[0] || allYears[0];
        console.log(`Ano padrão selecionado: ${defaultYear}`);
        return defaultYear;
    }

    // Função para mostrar mensagem de carregamento
    function showLoading(chartId) {
        console.log(`Mostrando carregamento para: ${chartId}`);
        toggleLoading(chartId, true);
    }

    // Função para esconder mensagem de carregamento
    function hideLoading(chartId) {
        console.log(`Escondendo carregamento para: ${chartId}`);
        toggleLoading(chartId, false);
    }

    // Função para mostrar mensagem de erro
    function showError(chartId, message) {
        console.error(`Erro no gráfico ${chartId}: ${message}`);
        const chartContainer = document.getElementById(chartId).parentElement;
        
        // Remover mensagens de erro anteriores
        const previousError = chartContainer.querySelector('.error-message');
        if (previousError) {
            previousError.remove();
        }
        
        // Criar e adicionar nova mensagem de erro
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = `Erro ao carregar dados: ${message}`;
        chartContainer.appendChild(errorDiv);
        
        // Esconder indicador de carregamento
        hideLoading(chartId);
    }

    // --------------------------------- Funções de comércio --------------------------------- //
    // Função para carregar todos os gráficos
    async function loadAllCharts() {
        console.log('Iniciando carregamento de todos os gráficos');
        
        try {
        // Volume de Comércio
            console.log('Carregando gráfico de Volume de Comércio');
            showLoading('chartCommerceVolume');
            
        const volumeData = await fetchData('commerce_volume_yearly');
        if (volumeData && volumeData[0] && volumeData[0].data) {
            const data = volumeData[0].data;
            const ctx = document.getElementById('chartCommerceVolume').getContext('2d');
            const years = Object.keys(data).sort();
            
            createChart(ctx, 'line', {
                labels: years,
                datasets: [{
                    label: 'Volume de Comércio',
                    data: years.map(year => data[year]),
                    borderColor: chartConfig.colors.teal,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgb(75, 192, 192)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(75, 192, 192)',
                        fill: true,
                    tension: 0.1
                }]
            }, {
                maintainAspectRatio: false
            });
                console.log('Gráfico de Volume de Comércio carregado com sucesso');
                hideLoading('chartCommerceVolume');
            } else {
                showError('chartCommerceVolume', 'Dados não encontrados ou em formato inválido');
        }

        // Divisão de Comércio
            console.log('Carregando gráfico de Divisão de Comércio');
            showLoading('chartCommerceDivision');
            
        const divisionData = await fetchData('commerce_division');
        if (divisionData && divisionData.length > 0) {
            const ctx = document.getElementById('chartCommerceDivision').getContext('2d');
            const years = divisionData.map(d => d.year);
            const defaultYear = await populateYearSelector('yearSelectorDivision', years);
            
            function updateDivisionChart(year) {
                    console.log(`Atualizando gráfico de Divisão de Comércio para o ano: ${year}`);
                    showLoading('chartCommerceDivision');
                    
                const yearData = divisionData.find(d => d.year === year);
                if (yearData) {
                    const values = [
                        yearData.vehicle_parts_motorcycle || 0,
                        yearData.wholesale_trade || 0,
                        yearData.retail_trade || 0
                    ];
                    
                    createChart(ctx, 'pie', {
                        labels: ['Veículos e Motocicletas', 'Comércio Atacadista', 'Comércio Varejista'],
                        datasets: [{
                            data: values,
                            backgroundColor: [
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)',
                                    'rgba(255, 205, 86, 0.7)'
                                ],
                                borderColor: [
                                    'rgb(255, 99, 132)',
                                    'rgb(54, 162, 235)',
                                    'rgb(255, 205, 86)'
                                ],
                                borderWidth: 1
                        }]
                    }, {
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: `Divisão do Comércio em ${year}`
                            },
                            legend: {
                                position: 'right'
                            }
                        }
                    });
                        console.log('Gráfico de Divisão de Comércio atualizado com sucesso');
                        hideLoading('chartCommerceDivision');
                    } else {
                        showError('chartCommerceDivision', `Dados para o ano ${year} não encontrados`);
                    }
            }

            document.getElementById('yearSelectorDivision').addEventListener('change', function(e) {
                updateDivisionChart(e.target.value);
            });

                // Garantir que o gráfico seja atualizado com o ano padrão
                if (defaultYear) {
            updateDivisionChart(defaultYear);
                } else {
                    showError('chartCommerceDivision', 'Ano padrão não definido');
                }
            } else {
                showError('chartCommerceDivision', 'Dados não encontrados ou em formato inválido');
        }

        // Ranking de Atividades
            console.log('Carregando gráfico de Ranking de Atividades');
            showLoading('chartCommerceRanking');
            
        const rankingData = await fetchData('commerce_ranking');
        if (rankingData && rankingData.length > 0) {
            const ctx = document.getElementById('chartCommerceRanking').getContext('2d');
            const years = rankingData.map(d => d.year);
                const defaultYear = await populateYearSelector('yearSelectorRanking', years);
            
            function updateRankingChart(year) {
                    console.log(`Atualizando gráfico de Ranking de Atividades para o ano: ${year}`);
                    showLoading('chartCommerceRanking');
                    
                const yearData = rankingData.find(d => d.year === year);
                if (yearData) {
                    const divisions = ['vehicle_parts_motorcycle', 'wholesale_trade', 'retail_trade'];
                    const datasets = divisions.map((division, index) => {
                        const divisionData = yearData[division] || [];
                        return {
                            label: division.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                            data: divisionData.map(item => item.count || 0),
                            backgroundColor: [
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)',
                                    'rgba(255, 205, 86, 0.7)'
                                ][index],
                                borderColor: [
                                    'rgb(255, 99, 132)',
                                    'rgb(54, 162, 235)',
                                    'rgb(255, 205, 86)'
                                ][index],
                                borderWidth: 1,
                                hoverBackgroundColor: [
                                    'rgba(255, 99, 132, 0.9)',
                                    'rgba(54, 162, 235, 0.9)',
                                    'rgba(255, 205, 86, 0.9)'
                            ][index]
                        };
                    });

                    const labels = yearData[divisions[0]]?.map(item => item.name) || [];

                    createChart(ctx, 'bar', {
                        labels: labels,
                            datasets: datasets.map((dataset, index) => ({
                                ...dataset,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)',
                                    'rgba(255, 205, 86, 0.7)'
                                ][index],
                                borderColor: [
                                    'rgb(255, 99, 132)',
                                    'rgb(54, 162, 235)',
                                    'rgb(255, 205, 86)'
                                ][index],
                                borderWidth: 1,
                                hoverBackgroundColor: [
                                    'rgba(255, 99, 132, 0.9)',
                                    'rgba(54, 162, 235, 0.9)',
                                    'rgba(255, 205, 86, 0.9)'
                                ][index]
                            }))
                    }, {
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: `Ranking de Atividades em ${year}`
                            }
                        }
                    });
                        console.log('Gráfico de Ranking de Atividades atualizado com sucesso');
                        hideLoading('chartCommerceRanking');
                    } else {
                        showError('chartCommerceRanking', `Dados para o ano ${year} não encontrados`);
                    }
            }

            document.getElementById('yearSelectorRanking').addEventListener('change', function(e) {
                updateRankingChart(e.target.value);
            });

                // Garantir que o gráfico seja atualizado com o ano padrão
                if (defaultYear) {
            updateRankingChart(defaultYear);
                } else {
                    showError('chartCommerceRanking', 'Ano padrão não definido');
                }
            } else {
                showError('chartCommerceRanking', 'Dados não encontrados ou em formato inválido');
        }

        // Receita vs Despesa
            console.log('Carregando gráfico de Receita vs Despesa');
            showLoading('chartRevenueExpense');
            
        const revenueExpenseData = await fetchData('commerce_revenue_expense_yearly');
        if (revenueExpenseData && revenueExpenseData.length > 0) {
            const yearlyData = revenueExpenseData[0];
            const ctx = document.getElementById('chartRevenueExpense').getContext('2d');
            const years = Object.keys(yearlyData.revenue).sort();
            
            createChart(ctx, 'line', {
                labels: years,
                datasets: [
                    {
                        label: 'Receita',
                        data: years.map(year => yearlyData.revenue[year]),
                        borderColor: chartConfig.colors.teal,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderWidth: 2,
                            pointBackgroundColor: 'rgb(75, 192, 192)',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: 'rgb(75, 192, 192)',
                            fill: true,
                        tension: 0.1
                    },
                    {
                        label: 'Despesa',
                        data: years.map(year => yearlyData.expense[year]),
                        borderColor: chartConfig.colors.coral,
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderWidth: 2,
                            pointBackgroundColor: 'rgb(255, 99, 132)',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: 'rgb(255, 99, 132)',
                            fill: true,
                        tension: 0.1
                    }
                ]
            }, {
                maintainAspectRatio: false
            });
                console.log('Gráfico de Receita vs Despesa carregado com sucesso');
                hideLoading('chartRevenueExpense');
            } else {
                showError('chartRevenueExpense', 'Dados não encontrados ou em formato inválido');
        }

        // Receita vs Despesa por Divisão
            console.log('Carregando gráfico de Receita vs Despesa por Divisão');
            showLoading('chartRevenueExpenseGrouped');
            
        const groupedData = await fetchData('commerce_revenue_expense_grouped');
        if (groupedData && groupedData.length > 0) {
            const ctx = document.getElementById('chartRevenueExpenseGrouped').getContext('2d');
            const years = groupedData.map(d => d.year);
                const defaultYear = await populateYearSelector('yearSelectorGrouped', years);

            function updateGroupedChart(year) {
                    console.log(`Atualizando gráfico de Receita vs Despesa por Divisão para o ano: ${year}`);
                    showLoading('chartRevenueExpenseGrouped');
                    
                const yearData = groupedData.find(d => d.year === year);
                if (yearData && yearData.data) {
                    const areas = yearData.data.map(item => item.area);
                    const datasets = [
                        {
                            label: 'Receita',
                            data: yearData.data.map(item => item.revenue || 0),
                                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                                borderColor: 'rgb(75, 192, 192)',
                                borderWidth: 1,
                                hoverBackgroundColor: 'rgba(75, 192, 192, 0.9)'
                        },
                        {
                            label: 'Despesa',
                            data: yearData.data.map(item => item.expense || 0),
                                backgroundColor: 'rgba(255, 99, 132, 0.7)',
                                borderColor: 'rgb(255, 99, 132)',
                                borderWidth: 1,
                                hoverBackgroundColor: 'rgba(255, 99, 132, 0.9)'
                        }
                    ];

                    const labels = areas.map(area => area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));

                    createChart(ctx, 'bar', {
                        labels: labels,
                            datasets: datasets.map((dataset, index) => ({
                                ...dataset,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)',
                                    'rgba(255, 205, 86, 0.7)'
                                ][index],
                                borderColor: [
                                    'rgb(255, 99, 132)',
                                    'rgb(54, 162, 235)',
                                    'rgb(255, 205, 86)'
                                ][index],
                                borderWidth: 1,
                                hoverBackgroundColor: [
                                    'rgba(255, 99, 132, 0.9)',
                                    'rgba(54, 162, 235, 0.9)',
                                    'rgba(255, 205, 86, 0.9)'
                                ][index]
                            }))
                    }, {
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: `Receita vs Despesa por Divisão em ${year}`
                            }
                        }
                    });
                        console.log('Gráfico de Receita vs Despesa por Divisão atualizado com sucesso');
                        hideLoading('chartRevenueExpenseGrouped');
                    } else {
                        showError('chartRevenueExpenseGrouped', `Dados para o ano ${year} não encontrados`);
                    }
            }

            document.getElementById('yearSelectorGrouped').addEventListener('change', function(e) {
                updateGroupedChart(e.target.value);
            });

                // Garantir que o gráfico seja atualizado com o ano padrão
                if (defaultYear) {
            updateGroupedChart(defaultYear);
                } else {
                    showError('chartRevenueExpenseGrouped', 'Ano padrão não definido');
                }
            } else {
                showError('chartRevenueExpenseGrouped', 'Dados não encontrados ou em formato inválido');
            }
            
            console.log('Todos os gráficos carregados com sucesso');
            
            // Adicionar tooltips aos gráficos
            const charts = document.querySelectorAll('canvas');
            charts.forEach(chart => {
                chart.addEventListener('mouseenter', function() {
                    const title = this.closest('.card-body').querySelector('.card-title').textContent;
                    showTooltip(this, title);
                });
                
                chart.addEventListener('mouseleave', hideTooltip);
            });
            
        } catch (error) {
            console.error('Erro ao carregar gráficos:', error);
            
            // Mostrar mensagem de erro geral
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = `Erro ao carregar dados: ${error.message}`;
            document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.container').firstChild);
            
            // Esconder todos os indicadores de carregamento
            loadingIndicators.forEach(indicator => {
                indicator.style.display = 'none';
            });
        }
    }

    // Carregar todos os gráficos quando a página carregar
    loadAllCharts();
}); 