# 🚀 Guia de Execução - Dashboard de Carcinicultura

## 📌 Passos Rápidos para Iniciar

### 1️⃣ Primeira Execução (Geração de Dados)

Abra o terminal na pasta do projeto e execute:

```bash
# Instalar dependências
pip install -r requirements.txt

# Gerar dados simulados
python gerar_dados.py

# Executar o dashboard
streamlit run app.py
```

O dashboard abrirá automaticamente em seu navegador em `http://localhost:8501`

---

## 📊 O que Você Vai Ver

### **Página Principal - Dashboard**

#### 🦐 Galeria de Camarões
Imagens ilustrativas com informações sobre:
- Camarão Adulto (15-20cm)
- Pós-larva (0,8-1cm)
- Temperatura Ideal (28-32°C)
- Viveiro Protegido (Estufa)

#### 📈 Indicadores Chave (KPIs)
- **🌡️ Temperatura Média:** Valor atual da temperatura
- **💀 Total de Mortes:** Somatório em 180 dias
- **🦐 Sobreviventes:** População final de camarões
- **✅ Taxa de Sobrevivência:** Percentual de sucesso

#### 📉 Gráficos Interativos
1. **Temperatura ao Longo do Tempo**
   - Mostra zona crítica (<20°C) e zona ideal (28°C)
   - Destaca o período de inverno (Jun-Ago)

2. **Mortalidade Diária por Viveiro**
   - Evolução da quantidade de mortes
   - Comparação entre diferentes estratégias

3. **População de Camarões**
   - Declínio populacional ao longo do tempo
   - Diferença entre estratégias protegidas e desprotegidas

---

### **Aba 2 - Análise Período Chuvoso ☔**

Análise especializada de **junho a agosto** (período crítico):

#### Indicadores Específicos:
- **Temperatura Média (Chuvoso):** Redução em relação aos outros períodos
- **Mortes no Período Chuvoso:** Comparação com período seco
- **Índice de Chuva Médio:** Intensidade de precipitação
- **Dias Críticos:** Quantos dias com T < 20°C

#### Gráficos Avançados:
1. **Temperatura vs Chuva:** Visualiza a correlação
2. **Relação Chuva x Mortalidade:** Scatter plot com linha de tendência
3. **Efetividade de Estratégias:** Qual reduz mais mortalidade no período chuvoso

---

### **Aba 3 - Comparação de Estratégias 🛡️**

Análise comparativa de todas as 5 estratégias:

| Estratégia | Mortes | Sobrevivência | Temperatura | Eficiência |
|------------|--------|---------------|-------------|-----------|
| Sem Proteção | Alto | Baixa | 18-19°C | Controle |
| Estufa Plástica | Médio | Média | 25°C | 50% redução |
| Aquecedor | Baixo | Alta | 28°C | 60% redução |
| Bioflocos + Estufa | Muito Baixo | Muito Alta | 29°C | 75% redução |

#### Análise de Custo-Benefício:
- Investimento Inicial
- Manutenção Mensal
- Redução de Mortalidade (%)

---

### **Aba 4 - Dados Detalhados 📋**

Tabela completa com:
- Data do monitoramento
- Viveiro (ID)
- Estratégia aplicada
- Temperatura (°C)
- Camarões vivos
- Camarões mortos/dia
- Índice de chuva

**Funcionalidades:**
- Filtrar número de linhas
- Ordenar por diferentes colunas
- **Download em CSV** para análise externa

---

## 🔍 Filtros na Barra Lateral

Na esquerda você pode filtrar por:
- **Viveiros:** Selecione quais viveiros analisar
- **Estratégias:** Escolha quais estratégias de manejo visualizar

*Os gráficos se atualizam automaticamente!*

---

## 💡 Insights Que Você Encontrará

### 🔴 Problema Crítico
- Período chuvoso (junho-agosto) causa queda de temperatura de até 4°C
- Quando T < 20°C, mortalidade pode chegar a 90%
- Viveiros sem proteção perdem até 70% da população

### 🟢 Solução Mais Efetiva
- **Bioflocos + Estufa Plástica** reduz mortalidade em 75%
- Mantém temperatura acima de 28°C mesmo no inverno
- Melhor retorno sobre investimento

### 📊 Dados Científicos
- Temperatura ideal: 28-32°C
- Taxa de mortalidade crítica: T < 20°C
- Período crítico: junho a agosto
- Índice de chuva amplifica mortalidade em até 30%

---

## ⚙️ Personalizações Possíveis

Você pode editar `app.py` para:

### Adicionar mais viveiros
```python
viveiros = ['Andre', 'Vitoria', 'Messalas', 'Lula', 'Kennedy', ...mais]
```

### Alterar cores dos gráficos
```python
fig = px.line(..., color_discrete_map={'Estratégia A': '#FF5733'})
```

### Modificar período analisado
```python
df_chuvoso = df_filtrado[df_filtrado['mes'].isin([6, 7, 8])]  # Altere os meses
```

### Adicionar novos KPIs
```python
st.metric("Nova Métrica", valor, delta)
```

---

## 🆘 Troubleshooting

### Erro: "FileNotFoundError: dados_camarao.csv"
**Solução:** Execute `python gerar_dados.py` antes de rodar o app

### Erro: "ModuleNotFoundError: No module named 'streamlit'"
**Solução:** Execute `pip install -r requirements.txt`

### Gráficos em branco
**Solução:** Verifique se os dados foram gerados corretamente

### Aplicação lenta
**Solução:** Reduza o número de registros ou use filtros na sidebar

---

## 📱 Dicas de Uso

✅ **Use os filtros** para focar em estratégias específicas
✅ **Passe o mouse** nos gráficos para ver valores exatos
✅ **Clique nas legendas** para mostrar/ocultar dados
✅ **Baixe o CSV** para fazer análises adicionais

---

## 🎯 Próximas Melhorias Sugeridas

- Adicionar upload de dados reais
- Implementar predição de mortalidade
- Adicionar recomendações automáticas
- Conectar a banco de dados
- Criar alertas para condições críticas

---

**Aproveite sua análise! 🦐📊**
