# 📊 Dashboard Controle de Corte - Multi-Empresa

Sistema de Dashboard para análise de produção de corte de mantas com suporte para múltiplas empresas e cidades.

## 🏗️ Arquitetura

### Estrutura de Pastas

```
DashboardAnaliseCorte/
├── app.py                    # 🏠 Página inicial (seletor cidade/empresa)
├── config.py                 # ⚙️ Configuração de empresas e metas
├── pages/
│   └── dashboard.py          # 📊 Dashboard dinâmico (reutilizável)
├── requirements.txt          # 📦 Dependências Python
└── README.md                 # 📝 Este arquivo
```

### Como Funciona

1. **app.py** - Página inicial com seletor de cidade/empresa
   - Usuário escolhe a CIDADE (ex: Arealva, Iacanga)
   - Usuário escolhe a EMPRESA (ex: Zanattex, Zannata)
   - Armazena configuração no `st.session_state`
   - Navega para o dashboard

2. **config.py** - Configuração centralizada
   - Define as empresas disponíveis por cidade
   - Armazena links das planilhas Google Sheets
   - Define metas padrão

3. **pages/dashboard.py** - Dashboard dinâmico
   - Lê a configuração da empresa selecionada
   - Carrega dados da planilha específica
   - Renderiza as mesmas análises para qualquer empresa

## 🚀 Como Adicionar Uma Nova EMPRESA

### Passo 1: Obter o Link da Planilha Google Sheets

Copie o ID e GID da sua planilha Google Sheets:

```
https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}#gid={GID}
```

Exemplo:
- **SHEET_ID**: `14OFOAxrV_DkyrwG6KG8NZT-PeXUV4jezPrPO90rh1DU`
- **GID**: `1362699684`

### Passo 2: Adicionar no `config.py`

Edite o arquivo `config.py` e adicione a nova empresa:

```python
EMPRESAS = {
    'Arealva': {
        'Zanattex': {
            'sheet_id': '1i52aEX3f5ACe9hzu68FUk8HALtn_NZUTxbhiJckxYmc',
            'gid': '1548681035',
            'nome_display': 'Zanattex - Arealva',
            'emoji': '🏭'
        }
    },
    'Iacanga': {
        'Zannata': {
            'sheet_id': '14OFOAxrV_DkyrwG6KG8NZT-PeXUV4jezPrPO90rh1DU',
            'gid': '1362699684',
            'nome_display': 'Zannata - Iacanga',
            'emoji': '🏢'
        },
        'NOVA_EMPRESA': {  # 👈 Adicione aqui
            'sheet_id': 'NOVO_ID_AQUI',
            'gid': 'NOVO_GID_AQUI',
            'nome_display': 'Nova Empresa - Iacanga',
            'emoji': '✨'
        }
    }
}
```

### Passo 3: Estrutura da Planilha

Sua planilha **DEVE** conter estas colunas (em qualquer ordem):

| DATA | OP | COR | QUANTIDADE | ESTAÇÃO DE CORTE | PRODUTO |
|------|----|----|------------|------------------|---------|
| 03/02/25 | 242673 | PRETO | 100 | MAQUINA | MICROFIBRA |
| 03/02/25 | 242688 | AZUL | 200 | MESA 1 | OUTLET |

- **DATA**: Formato DD/MM/YY ou DD/MM/YYYY
- **OP**: Número da Ordem de Produção
- **COR**: Cor da manta
- **QUANTIDADE**: Número de peças
- **ESTAÇÃO DE CORTE**: Máquina ou mesa (ex: MAQUINA, MESA 1, MESA 2)
- **PRODUTO**: Tipo de produto

### Passo 4: Compartilhar a Planilha

1. Abra a planilha no Google Sheets
2. Clique em **"Compartilhar"**
3. Selecione **"Qualquer pessoa com o link"**
4. Defina permissão como **"Visualizador"**

Pronto! O dashboard detectará automaticamente.

## 🎯 Adicionar uma Nova CIDADE

Edite `config.py` e adicione uma nova chave:

```python
EMPRESAS = {
    # ... empresas existentes ...
    'Sorocaba': {  # 👈 Nova cidade
        'Empresa1': {
            'sheet_id': 'ID_AQUI',
            'gid': 'GID_AQUI',
            'nome_display': 'Empresa1 - Sorocaba',
            'emoji': '🏗️'
        }
    }
}
```

## 📊 Análises Disponíveis

### Tab 1 - Visão Geral
- KPIs: Total de peças, OPs, cores, dias trabalhados
- Produção diária com linha de tendência (5 dias)
- Distribuição por estação (gráfico de pizza)
- Top produtos e cores

### Tab 2 - Acompanhamento por OP
- Resumo de todas as OPs
- Detalhes de cada OP (cores, quantidade, períodos)
- Histórico de cortes

### Tab 3 - Produção por Estação
- Progresso vs meta de cada estação
- Produção diária por estação
- Análise detalhada (estatísticas, box-plots)
- Comparativo semanal

## 🔧 Configurar Metas

As metas são definidas em `config.py`:

```python
METAS_PADRAO = {
    'MAQUINA': 8000,    # 8 mil peças/dia
    'MESA 1': 4000,     # 4 mil peças/dia
    'MESA 2': 3000      # 3 mil peças/dia
}
```

**Futuro**: Criar aba "METAS" em cada planilha para metas específicas por empresa.

## 🚀 Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o dashboard
```bash
streamlit run app.py
```

### 3. Abrir no navegador
```
http://localhost:8501
```

## 📱 Interface

### Página Inicial
- Seletor de cidade (dropdown)
- Seletor de empresa (dropdown dinâmico baseado na cidade)
- Botão para acessar o dashboard

### Dashboard
- Sidebar com filtros (OP, Estação, Produto, Datas)
- Botão "Limpar Cache" para forçar atualização
- Botão "Voltar" para retornar ao seletor

## 🔄 Fluxo de Dados

```
Google Sheets
      ↓
  config.py
      ↓
  app.py (seletor)
      ↓
  session_state
      ↓
  pages/dashboard.py (dashboard dinâmico)
      ↓
  Análises & Visualizações
```

## 📝 Notas Importantes

- ✅ Cada empresa tem sua própria planilha
- ✅ Estações são detectadas automaticamente da coluna "ESTAÇÃO DE CORTE"
- ✅ Zero necessidade de editar código para adicionar novas empresas
- ✅ Dashboard reutiliza o mesmo código para todas as empresas
- ⚠️ A planilha DEVE estar compartilhada como "Qualquer pessoa com o link"
- ⚠️ Colunas obrigatórias: DATA, OP, COR, QUANTIDADE, ESTAÇÃO DE CORTE, PRODUTO

## 🐛 Troubleshooting

### "Nenhuma empresa selecionada"
- Certifique-se de iniciar em **app.py** (não em pages/dashboard.py)

### "Erro ao carregar a planilha"
- Verifique se a planilha está compartilhada corretamente
- Confirme que a conexão de internet está ativa
- Teste o link da planilha no navegador

### "Colunas obrigatórias faltando"
- Verifique se as colunas existem na planilha
- Os nomes devem ser exatos (maiúsculas/minúsculas)

## 📦 Dependências

Veja `requirements.txt` para a lista completa.

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
```

---

**Desenvolvido com ❤️ para análise de produção de corte de mantas**
