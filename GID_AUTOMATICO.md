# 🔧 Detecção Automática de GID - Guia de Uso

## O Problema

Quando a planilha Google Sheets era atualizada com novos dados, o **GID (Grid ID) mudava**, forçando você a atualizar manualmente o código a cada vez. Isso tornava o dashboard instável.

## A Solução

Implementei uma **detecção automática e inteligente de GID** que:

✅ **Detecta automaticamente** qual aba usar da planilha  
✅ **Funciona sem GID fixo** - sempre carrega a primeira aba por padrão  
✅ **Implementa fallback** caso algo mude na estrutura  
✅ **Cache inteligente** para evitar requisições desnecessárias

---

## Como Funciona?

### 1️⃣ **Modo Padrão (RECOMENDADO)**

O dashboard agora funciona **sem GID hardcoded**. Ele carrega automaticamente a **primeira aba** da planilha Google Sheets.

```python
# Não precisa mais especificar o GID!
GOOGLE_SHEETS_ID = "1iGj4-vknwzepbrHdRz1PwisZU2foU7aW"
# GID é detectado automaticamente
```

### 2️⃣ **Se Precisar Customizar**

Abra o arquivo `config.py` e mude:

```python
# Para detecção automática (padrão):
GOOGLE_SHEETS_GID = None

# Ou especifique um GID fixo se necessário:
GOOGLE_SHEETS_GID = "206085601"
```

### 3️⃣ **Detectar GID Manualmente**

Se a planilha tiver mudanças estruturais, execute:

```bash
python gid_detector.py
```

Este script irá:

- Detectar automaticamente o GID correto
- Testar múltiplas GIDs conhecidas
- Sugerir qual usar

---

## Arquivos Novos/Modificados

| Arquivo             | O que faz                                            |
| ------------------- | ---------------------------------------------------- |
| **config.py**       | Configuração centralizada (ID, GID, METAS, CACHE)    |
| **gid_detector.py** | Ferramenta para detectar GID automaticamente         |
| **dashboard.py**    | Atualizado para usar config.py e detecção automática |

---

## Benefícios

| Antes                              | Depois                         |
| ---------------------------------- | ------------------------------ |
| ❌ GID hardcoded                   | ✅ Detecção automática         |
| ❌ Quebrava quando planilha mudava | ✅ Funciona mesmo com mudanças |
| ❌ Manutenção manual               | ✅ Automático e resiliente     |
| ❌ Uma URL para cada GID           | ✅ URLs dinâmicas e eficientes |

---

## Próximas Vezes

**Você não precisa fazer mais nada!** 🎉

- A planilha pode mudar
- Novos dados podem chegar
- O dashboard continuará funcionando automaticamente

Se por algum motivo o dashboard parar de funcionar:

1. Execute `python gid_detector.py`
2. Veja qual GID foi detectado
3. Atualize `config.py` se necessário

---

## ⚡ Quick Start

```bash
# 1. Rodar o dashboard (normal)
streamlit run dashboard.py

# 2. Se precisar detectar GID (raro)
python gid_detector.py

# 3. Customizar (opcional)
# Edite config.py
```

---

**Seu dashboard agora é estável e automático! 🚀**
