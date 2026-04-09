# DashboardAnaliseCorte
Dashboar de analise, para o setor de corte, da minha atual empresa.

## Execucao

```bash
streamlit run dashboard.py
```

## Observacao sobre deploy Linux

Em alguns ambientes Linux, o Streamlit pode falhar com o erro
`inotify instance limit reached`.

Este projeto ja inclui a configuracao em `.streamlit/config.toml`:

- `fileWatcherType = "none"`
- `runOnSave = false`

Isso evita o uso de inotify e corrige o problema sem depender de ajuste de sistema.
