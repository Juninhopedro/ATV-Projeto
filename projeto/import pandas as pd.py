import pandas as pd
import numpy as np

np.random.seed(42)

# Simulação de 180 dias (outono + inverno) em 5 viveiros
dias = 180
viveiros = ['Viveiro_01', 'Viveiro_02', 'Viveiro_03', 'Viveiro_04', 'Viveiro_05']

dados = []
data_inicio = pd.to_datetime('2025-04-01')

for viveiro in viveiros:
    # Cada viveiro tem uma estratégia diferente
    if viveiro == 'Viveiro_01':
        estrategia = 'Sem Proteção'
        temp_base = 18
    elif viveiro == 'Viveiro_02':
        estrategia = 'Estufa Plástica'
        temp_base = 25
    elif viveiro == 'Viveiro_03':
        estrategia = 'Aquecedor'
        temp_base = 28
    elif viveiro == 'Viveiro_04':
        estrategia = 'Bioflocos + Estufa'
        temp_base = 29
    else:
        estrategia = 'Sem Proteção'
        temp_base = 19

    populacao = 100000  # camarões iniciais
    
    for d in range(dias):
        data = data_inicio + pd.Timedelta(days=d)
        # Simula queda de temperatura no inverno (jun-ago)
        mes = data.month
        if mes in [6, 7, 8]:
            ajuste_inverno = -4
        elif mes in [5, 9]:
            ajuste_inverno = -2
        else:
            ajuste_inverno = 0
        
        temperatura = temp_base + ajuste_inverno + np.random.normal(0, 1.5)
        oxigenio = np.random.normal(6, 0.8)  # mg/L
        ph = np.random.normal(7.8, 0.3)
        salinidade = np.random.normal(25, 2)
        
        # Mortalidade baseada na temperatura (regra científica)
        if temperatura < 18:
            taxa_mort = np.random.uniform(0.015, 0.035)
        elif temperatura < 22:
            taxa_mort = np.random.uniform(0.005, 0.015)
        elif temperatura < 28:
            taxa_mort = np.random.uniform(0.001, 0.005)
        else:
            taxa_mort = np.random.uniform(0.0005, 0.002)
        
        mortos = int(populacao * taxa_mort)
        populacao = max(0, populacao - mortos)
        
        dados.append({
            'data': data,
            'viveiro': viveiro,
            'estrategia': estrategia,
            'temperatura_C': round(temperatura, 2),
            'oxigenio_mgL': round(oxigenio, 2),
            'pH': round(ph, 2),
            'salinidade_ppt': round(salinidade, 2),
            'camaroes_vivos': populacao,
            'camaroes_mortos_dia': mortos
        })

df = pd.DataFrame(dados)
df.to_csv('dados_camarao.csv', index=False)
print("✅ Arquivo 'dados_camarao.csv' criado com sucesso!")
print(f"Total de registros: {len(df)}")
