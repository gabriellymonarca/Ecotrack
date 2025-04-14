import { 
    createChart,
    // Funções relacionadas a dados 
    fetchData, 
    // Funções relacionadas a seletores
    populateYearSelector, 
    populateActivitySelector,
    // Funções de utilidades 
    getAbbreviatedMonths,
    showLoading
} from './common.js';

console.log('industry.js carregado');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado em industry.js');

    // Função para gerar dados de produção industrial
    async function generateProductionData(activity, year, month) {
        console.log(`Gerando dados de produção para atividade: ${activity}, ano: ${year}, mês: ${month}`);
        try {
            // Formatar a data para o formato esperado pelo backend (ex: "abril 2020")
            const monthNames = [
                'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
            ];
            const monthIndex = parseInt(month) - 1;
            const formattedDate = `${monthNames[monthIndex]} ${year}`;
            
            console.log(`Data formatada: ${formattedDate}`);
            
            const response = await fetch('/api/generate_industrial_production', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    activity: activity,
                    date: formattedDate
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`Erro na resposta: ${response.status} - ${errorText}`);
                throw new Error(`Erro ao gerar dados: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('Dados gerados:', data);
            
            // Verificar se os dados têm a estrutura esperada
            if (!data || !data.total_production) {
                console.error('Dados retornados não têm a estrutura esperada:', data);
                throw new Error('Dados retornados não têm a estrutura esperada');
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao gerar dados de produção:', error);
            throw error;
        }
    }

    // Função para gerar dados de receita industrial
    async function generateRevenueData(activity) {
        console.log(`Iniciando geração de dados de receita para atividade: ${activity}`);
        try {
            const response = await fetch('/api/generate_industrial_revenue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    activity: activity
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`Erro na resposta do servidor: Status ${response.status} - ${errorText}`);
                throw new Error(`Falha ao gerar dados de receita: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('Dados de receita recebidos:', data);
            
            // Verificar se os dados têm a estrutura esperada
            if (!data || !data.data || Object.keys(data.data).length === 0) {
                console.error('Dados de receita retornados estão vazios ou em formato inválido:', data);
                throw new Error('Dados de receita retornados estão vazios ou em formato inválido');
            }

            console.log('Dados de receita gerados com sucesso:', data);
            return data;
        } catch (error) {
            console.error('Erro ao gerar dados de receita:', error);
            throw error;
        }
    }

    // Função para carregar todos os gráficos
    async function loadAllCharts() {
        console.log('Iniciando carregamento dos gráficos industriais');
        
        try {
            // Buscar atividades das tabelas PostgreSQL
            console.log('Buscando atividades da tabela industrial_activity...');
            const productionActivities = await fetchData('industrial_activity');
            if (!productionActivities || productionActivities.length === 0) {
                throw new Error('Nenhuma atividade de produção encontrada');
            }
            console.log('Atividades de produção encontradas:', productionActivities);
            
            console.log('Buscando atividades da tabela industrial_activity_cnae...');
            const revenueActivities = await fetchData('industrial_activity_cnae');
            if (!revenueActivities || revenueActivities.length === 0) {
                throw new Error('Nenhuma atividade de receita encontrada');
            }
            console.log('Atividades de receita encontradas:', revenueActivities);
            
            // Popular seletor de atividades de produção
            const defaultProductionActivity = await populateActivitySelector('activitySelectorProduction', productionActivities);
            console.log('Atividade de produção padrão:', defaultProductionActivity);
            
            // Popular seletor de anos
            const defaultYear = await populateYearSelector('yearSelectorProduction', []);
            console.log('Ano padrão:', defaultYear);
            
            // Popular seletor de atividades de receita
            const defaultRevenueActivity = await populateActivitySelector('activitySelectorRevenue', revenueActivities);
            console.log('Atividade de receita padrão:', defaultRevenueActivity);
            
            // Função para atualizar o gráfico de produção
            async function updateProductionChart(activity, year) {
                console.log(`Atualizando gráfico de produção para atividade: ${activity}, ano: ${year}`);
                const ctx = document.getElementById('chartIndustrialProduction');
                
                // Remover mensagens de erro anteriores
                const previousError = ctx.parentNode.querySelector('.alert-danger');
                if (previousError) {
                    previousError.remove();
                }
                
                // Restaurar a visibilidade do canvas
                ctx.style.display = 'block';
                
                try {
                    // Mostrar mensagem de carregamento
                    showLoading('chartIndustrialProduction');
                    
                    // Gerar dados para todos os meses
                    const months = getAbbreviatedMonths();
                    const allData = [];
                    
                    for (let i = 0; i < months.length; i++) {
                        try {
                            const monthData = await generateProductionData(activity, year, (i + 1).toString());
                            if (monthData && monthData.total_production !== undefined) {
                                allData.push({
                                    month: months[i],
                                    value: monthData.total_production
                                });
                            }
                        } catch (error) {
                            console.error(`Erro ao gerar dados para o mês ${months[i]}:`, error);
                        }
                    }
                    
                    if (allData.length === 0) {
                        throw new Error('Nenhum dado foi gerado com sucesso');
                    }
                    
                    // Criar o gráfico
                    createChart(ctx, 'line', {
                        labels: allData.map(d => d.month),
                        datasets: [{
                            label: 'Produção Industrial',
                            data: allData.map(d => d.value),
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderWidth: 2,
                            pointBackgroundColor: 'rgb(75, 192, 192)',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: 'rgb(75, 192, 192)',
                            fill: true
                        }]
                    }, {
                        plugins: {
                            title: {
                                display: true,
                                text: `Produção Industrial - ${activity} (${year})`
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Produção'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Mês'
                                }
                            }
                        }
                    });
                    
                } catch (error) {
                    console.error('Erro ao atualizar gráfico de produção:', error);
                    ctx.style.display = 'none';
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = `Erro ao carregar dados: ${error.message}`;
                    ctx.parentNode.appendChild(errorDiv);
                }
            }
            
            // Função para atualizar o gráfico de receita
            async function updateRevenueChart(activity) {
                console.log(`Iniciando atualização do gráfico de receita para atividade: ${activity}`);
                const ctx = document.getElementById('chartIndustrialRevenue');
                
                if (!ctx) {
                    console.error('Elemento canvas não encontrado: chartIndustrialRevenue');
                    return;
                }
                
                // Remover mensagens de erro anteriores
                const previousError = ctx.parentNode.querySelector('.alert-danger');
                if (previousError) {
                    previousError.remove();
                }
                
                // Remover gráfico anterior se existir
                if (window.revenueChart) {
                    console.log('Destruindo gráfico anterior');
                    window.revenueChart.destroy();
                }
                
                // Restaurar a visibilidade do canvas
                ctx.style.display = 'block';
                
                try {
                    // Mostrar mensagem de carregamento
                    showLoading('chartIndustrialRevenue');
                    
                    // Gerar dados de receita
                    const revenueData = await generateRevenueData(activity);
                    
                    if (!revenueData || !revenueData.data || Object.keys(revenueData.data).length === 0) {
                        throw new Error('Nenhum dado de receita foi encontrado para esta atividade');
                    }

                    // Ordenar os anos em ordem crescente
                    const years = Object.keys(revenueData.data).sort();
                    const values = years.map(year => revenueData.data[year]);
                    
                    console.log('Anos ordenados:', years);
                    console.log('Valores correspondentes:', values);

                    // Criar o gráfico
                    console.log('Criando gráfico de barras...');
                    window.revenueChart = createChart(ctx, 'bar', {
                        labels: years,
                        datasets: [{
                            label: 'Receita Industrial',
                            data: values,
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                            borderColor: 'rgb(255, 99, 132)',
                            borderWidth: 1,
                            hoverBackgroundColor: 'rgba(255, 99, 132, 0.9)',
                            hoverBorderColor: 'rgb(255, 99, 132)'
                        }]
                    }, {
                        plugins: {
                            title: {
                                display: true,
                                text: `Receita Industrial - ${activity}`
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Receita (R$)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Ano'
                                }
                            }
                        }
                    });
                    
                    console.log('Gráfico de receita criado com sucesso');
                    
                } catch (error) {
                    console.error('Erro ao atualizar gráfico de receita:', error);
                    ctx.style.display = 'none';
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = `Erro ao carregar dados: ${error.message}`;
                    ctx.parentNode.appendChild(errorDiv);
                }
            }
            
            // Configurar event listeners
            document.getElementById('activitySelectorProduction').addEventListener('change', function(e) {
                const year = document.getElementById('yearSelectorProduction').value;
                updateProductionChart(e.target.value, year);
            });
            
            document.getElementById('yearSelectorProduction').addEventListener('change', function(e) {
                const activity = document.getElementById('activitySelectorProduction').value;
                updateProductionChart(activity, e.target.value);
            });
            
            document.getElementById('activitySelectorRevenue').addEventListener('change', function(e) {
                updateRevenueChart(e.target.value);
            });
            
            // Inicializar os gráficos com valores padrão
            console.log('Inicializando gráfico de produção...');
            await updateProductionChart(defaultProductionActivity, defaultYear);
            
            console.log('Inicializando gráfico de receita...');
            await updateRevenueChart(defaultRevenueActivity);
            
            console.log('Carregamento dos gráficos concluído com sucesso');
        } catch (error) {
            console.error('Erro ao carregar gráficos:', error);
            // Exibir mensagem de erro na interface
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger';
            errorDiv.textContent = `Erro ao carregar gráficos: ${error.message}`;
            document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.container').firstChild);
        }
    }
    
    // Carregar todos os gráficos quando a página carregar
    loadAllCharts();
});

