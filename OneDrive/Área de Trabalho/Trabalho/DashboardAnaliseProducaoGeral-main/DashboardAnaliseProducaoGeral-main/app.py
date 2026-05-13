import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import re
import io
import numpy as np

# ──────────────────────────────────────────────
# CONFIGURACAO DA PAGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Produção - Empresas",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CSS CUSTOMIZADO
# ──────────────────────────────────────────────
st.markdown("""
<style>
    footer {visibility: hidden;}
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1C1C22 0%, #28282E 100%);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #FFFFFF !important; font-size: 0.8rem !important;
        font-weight: 600 !important; text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important; font-weight: 700 !important; font-size: 1.8rem !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1C1C22, #28282E) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #FFFFFF !important; border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        border-color: #4ECDC4 !important;
        box-shadow: 0 0 15px rgba(78,205,196,0.3) !important;
        color: #4ECDC4 !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111115 0%, #191920 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    section[data-testid="stSidebar"] * { color: #E0E0E0 !important; }
    .main-title {
        text-align: center; color: #FFFFFF; font-size: 2.6rem;
        font-weight: 800; margin-bottom: 0; letter-spacing: 0.5px;
    }
    .sub-title {
        text-align: center; color: #A0A0A0; font-size: 1.15rem;
        margin-top: 4px; margin-bottom: 20px;
    }
    .section-title {
        text-align: center; color: #FFFFFF; font-size: 1.4rem;
        font-weight: 700; margin: 24px 0 12px 0;
    }
    hr { border: none; border-top: 1px solid rgba(255,255,255,0.12); margin: 20px 0; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stProgress > div > div > div { background-color: #4ECDC4 !important; }
    span[data-baseweb="tag"] {
        background-color: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #FFFFFF !important;
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────
SPREADSHEET_ID = "15s_ZttYG4UkSprgp4V_9gUBSgg7p8JRTiSQZL4xBi6Y"

CORES_EMPRESAS = {
    "Burdays": "#FF6B6B",
    "Camesa": "#4ECDC4",
    "Niazitex": "#45B7D1",
    "Cortex": "#FFA726",
    "Sultan": "#AB47BC",
    "Decor": "#26C6DA",
    "Marcelino": "#FFD54F",
}

DARK_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#CBD5E0"),
    xaxis=dict(gridcolor="#2D3748", zerolinecolor="#2D3748"),
    yaxis=dict(gridcolor="#2D3748", zerolinecolor="#2D3748"),
    separators=",.",
)

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

MESES_NOME = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

NOMES_DIAS = {
    "Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
    "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom",
}

ORDEM_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# ──────────────────────────────────────────────
# UTILITÁRIOS
# ──────────────────────────────────────────────
def fmt_br(v, decimals=0):
    txt = f"{v:,.{decimals}f}"
    return txt.replace(",", "X").replace(".", ",").replace("X", ".")


def dias_uteis(datas):
    d = pd.to_datetime(datas).dropna().dt.normalize().drop_duplicates()
    return int((d.dt.weekday <= 4).sum())


def dias_para_media(df):
    """
    Calcula dias de trabalho para a média, considerando lógica especial para sábados.
    
    Regra:
    - Dias úteis (seg-sex): TODOS os dias contam, mesmo com produção zerada
    - Sábado: apenas dias com produção > 0 contam
    
    Args:
        df: DataFrame com colunas 'Data', 'Quantidade' e 'DiaSemana'
    
    Returns:
        Número de dias a considerar no cálculo da média
    """
    if df.empty:
        return 0
    
    # Copia o dataframe
    df_temp = df[["Data", "Quantidade", "DiaSemana"]].copy()
    df_temp["Data"] = df_temp["Data"].dt.normalize()
    
    # Agrupa por data
    datas_unicas = df_temp.groupby("Data").agg({
        "Quantidade": "sum",
        "DiaSemana": "first"
    }).reset_index()
    
    # Conta dias
    dias_contados = 0
    for _, row in datas_unicas.iterrows():
        dia_semana = row['DiaSemana']
        qtd = row['Quantidade']
        eh_sabado = dia_semana == "Saturday"
        tem_producao = qtd > 0
        
        if eh_sabado:
            if tem_producao:
                dias_contados += 1
        else:
            dias_contados += 1
    
    return dias_contados


def _calc_meta(df_f: pd.DataFrame, sel_facs: list) -> tuple:
    """
    Calcula a meta do período considerando que cada mês pode ter
    uma meta diária diferente por facção/produto.
    """
    df_sel = df_f[df_f["Faccao"].isin(sel_facs)].copy()

    meta_mensal = (
        df_sel
        .drop_duplicates(subset=["Faccao", "Produto", "Ano", "Mes"])
        .groupby(["Faccao", "Ano", "Mes"], as_index=False)
        .agg({
            "Meta Diaria": "first"  # Pega apenas uma meta por (Faccao, Mes) - não duplica
        })
    )
    meta_mensal["Meta Diaria"] = meta_mensal["Meta Diaria"].fillna(0)

    if meta_mensal["Meta Diaria"].sum() == 0:
        empty = pd.DataFrame(columns=["Faccao", "Meta Periodo", "Meta Dia Min", "Meta Dia Max"])
        return 0.0, pd.Series(dtype=float), empty

    dias_mes = (
        df_sel.groupby(["Ano", "Mes"])["Data"]
        .apply(dias_uteis)
        .reset_index()
        .rename(columns={"Data": "DiasUteis"})
    )

    meta_mensal = meta_mensal.merge(dias_mes, on=["Ano", "Mes"], how="left")
    meta_mensal["DiasUteis"] = meta_mensal["DiasUteis"].fillna(0)
    meta_mensal["Meta Periodo Mes"] = meta_mensal["Meta Diaria"] * meta_mensal["DiasUteis"]

    meta_periodo = float(meta_mensal["Meta Periodo Mes"].sum())

    meta_por_anomes = (
        meta_mensal.groupby(["Ano", "Mes"], as_index=False)["Meta Diaria"].sum()
    )
    datas_unicas = df_sel[["Data", "Ano", "Mes"]].drop_duplicates()
    meta_por_data = (
        datas_unicas
        .merge(meta_por_anomes, on=["Ano", "Mes"], how="left")
        .sort_values("Data")
        .set_index("Data")["Meta Diaria"]
        .fillna(0)
    )
    meta_por_data = meta_por_data[~meta_por_data.index.duplicated(keep="first")]

    meta_por_faccao = (
        meta_mensal
        .groupby("Faccao")
        .agg(
            Meta_Periodo=("Meta Periodo Mes", "sum"),
            Meta_Dia_Min=("Meta Diaria", "min"),
            Meta_Dia_Max=("Meta Diaria", "max"),
        )
        .reset_index()
        .rename(columns={
            "Meta_Periodo": "Meta Periodo",
            "Meta_Dia_Min": "Meta Dia Min",
            "Meta_Dia_Max": "Meta Dia Max",
        })
    )

    return meta_periodo, meta_por_data, meta_por_faccao


def _calc_meta_por_produto(df_f: pd.DataFrame, sel_facs: list) -> pd.DataFrame:
    """
    Calcula meta por (Faccao, Produto) para a tabela expandida.
    """
    df_sel = df_f[df_f["Faccao"].isin(sel_facs)].copy()

    meta_mensal = (
        df_sel
        .drop_duplicates(subset=["Faccao", "Produto", "Ano", "Mes"])
        [["Faccao", "Produto", "Ano", "Mes", "Meta Diaria"]]
        .copy()
    )
    meta_mensal["Meta Diaria"] = meta_mensal["Meta Diaria"].fillna(0)

    dias_mes = (
        df_sel.groupby(["Ano", "Mes"])["Data"]
        .apply(dias_uteis)
        .reset_index()
        .rename(columns={"Data": "DiasUteis"})
    )

    meta_mensal = meta_mensal.merge(dias_mes, on=["Ano", "Mes"], how="left")
    meta_mensal["DiasUteis"] = meta_mensal["DiasUteis"].fillna(0)
    meta_mensal["Meta Periodo Mes"] = meta_mensal["Meta Diaria"] * meta_mensal["DiasUteis"]

    result = (
        meta_mensal
        .groupby(["Faccao", "Produto"])
        .agg(
            Meta_Periodo=("Meta Periodo Mes", "sum"),
            Meta_Dia_Min=("Meta Diaria", "min"),
            Meta_Dia_Max=("Meta Diaria", "max"),
        )
        .reset_index()
        .rename(columns={
            "Meta_Periodo": "Meta Periodo",
            "Meta_Dia_Min": "Meta Dia Min",
            "Meta_Dia_Max": "Meta Dia Max",
        })
    )
    return result


# ──────────────────────────────────────────────
# PARSING DE DATAS
# ──────────────────────────────────────────────
_SKIP_KEYWORDS = frozenset([
    "faccao", "produto", "meta", "qtde", "falta",
    "column", "cliente", "responsavel", "%", " tr",
])

_PT_MONTHS = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4,
    "mai": 5, "jun": 6, "jul": 7, "ago": 8,
    "set": 9, "out": 10, "nov": 11, "dez": 12,
}


def _remove_accents(text):
    replacements = {
        "\u00e7": "c", "\u00c7": "C", "\u00e3": "a", "\u00c3": "A",
        "\u00e1": "a", "\u00c1": "A", "\u00e9": "e", "\u00c9": "E",
        "\u00ed": "i", "\u00cd": "I", "\u00f3": "o", "\u00d3": "O",
        "\u00fa": "u", "\u00da": "U", "\u00e2": "a", "\u00ea": "e", "\u00f4": "o",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


def _infer_year(month: int, day: int, base_year: int | None) -> int:
    """
    Infere o ano para cabeçalhos sem ano explícito escolhendo o mais próximo
    da data atual dentro da janela [base_year-1, base_year, base_year+1].
    """
    today = datetime.now().date()
    if base_year is None:
        base_year = today.year

    candidatos: list[tuple[int, int]] = []
    for year in (base_year - 1, base_year, base_year + 1):
        try:
            dt = date(year, month, day)
        except ValueError:
            continue
        candidatos.append((abs((today - dt).days), year))

    if not candidatos:
        return base_year

    return min(candidatos, key=lambda x: x[0])[1]


def parse_date_header(h, base_year=None):
    if base_year is None:
        base_year = datetime.now().year

    if h is None:
        return None
    if isinstance(h, datetime):
        return h.date()
    if isinstance(h, date):
        return h

    h_str = str(h).strip()
    if not h_str or h_str.lower() == "nan":
        return None

    skip_check = _remove_accents(h_str.lower())
    if any(kw in skip_check for kw in _SKIP_KEYWORDS):
        return None

    h_norm = h_str.replace("-", "/")

    try:
        return datetime.strptime(h_norm, "%d/%m/%Y").date()
    except ValueError:
        pass

    try:
        return datetime.strptime(h_norm, "%d/%m/%y").date()
    except ValueError:
        pass

    parts = h_norm.split("/")
    if len(parts) in (2, 3):
        try:
            day = int(parts[0])
            month = int(parts[1])
            if len(parts) == 3:
                year = int(parts[2])
                year = year + 2000 if year < 100 else year
            else:
                year = _infer_year(month, day, base_year)
            return date(year, month, day)
        except (ValueError, TypeError):
            pass

    for abbr, month_num in _PT_MONTHS.items():
        if abbr in h_str.lower():
            match = re.search(r"(\d+)", h_str)
            if match:
                day = int(match.group(1))
                year = _infer_year(month_num, day, base_year)
                try:
                    return date(year, month_num, day)
                except ValueError:
                    pass

    return None


# ──────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ──────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_all_data():
    import requests as req

    xlsx_data = None
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
        r = req.get(url, timeout=30)
        r.raise_for_status()
        xlsx_data = io.BytesIO(r.content)
    except Exception as e:
        st.warning(f"Não foi possível carregar do Google Sheets: {e}. Tentando arquivo local...")
        xlsx_data = "planilha_producao.xlsx"

    all_data: dict[str, pd.DataFrame] = {}
    xls = pd.ExcelFile(xlsx_data, engine="openpyxl")

    for sheet in xls.sheet_names:
        if sheet.lower() == "diversos":
            continue
        try:
            raw = pd.read_excel(xlsx_data, sheet_name=sheet, header=None, engine="openpyxl")
            parsed = _parse_sheet(raw, sheet)
            if parsed is not None and len(parsed) > 0:
                all_data[sheet] = parsed
        except Exception as e:
            st.warning(f"Erro ao processar aba '{sheet}': {e}")

    return all_data


# ──────────────────────────────────────────────
# PARSING DE ABAS
# ──────────────────────────────────────────────
_HEADER_LABELS = frozenset([
    "FACCAO", "PRODUTO", "META DIARIA", "META MENSAL",
    "QTDE PRODUZIDA", "FALTA", "CLIENTE",
])


def _is_header_row(row_series) -> bool:
    vals = row_series.astype(str).str.upper().tolist()
    for v in vals:
        v = str(v).strip()
        v_clean = _remove_accents(v)
        if "FACCAO" in v_clean or v == "PRODUTO":
            return True
    return False


def _find_all_header_rows(raw) -> list[int]:
    header_rows = []
    for i in range(len(raw)):
        if _is_header_row(raw.iloc[i]):
            header_rows.append(i)
    return header_rows


def _parse_block(raw_block: pd.DataFrame, headers: list, sheet_name: str) -> list[dict]:
    col_idx: dict[str, int] = {}
    for idx, h in enumerate(headers):
        if h is None or str(h) == "nan":
            continue
        hu = str(h).upper().strip()
        hu_clean = _remove_accents(hu)

        if "FACCAO" in hu_clean and "faccao" not in col_idx:
            col_idx["faccao"] = idx
        elif hu == "PRODUTO" and "produto" not in col_idx:
            col_idx["produto"] = idx
        elif hu == "CLIENTE" and "faccao" not in col_idx:
            col_idx["faccao"] = idx
        elif ("META" in hu and ("DIARI" in hu_clean or "DIARIA" in hu_clean)
              and "meta_diaria" not in col_idx):
            col_idx["meta_diaria"] = idx

    date_cols: dict[int, date] = {}
    for idx, h in enumerate(headers):
        d = parse_date_header(h)
        if d is not None:
            date_cols[idx] = d

    if not date_cols or "produto" not in col_idx:
        return []

    records = []
    for _, row in raw_block.iterrows():
        if "faccao" in col_idx:
            fv = row.iloc[col_idx["faccao"]]
            if pd.isna(fv) or str(fv).strip() in ("", "nan", "None"):
                continue
            faccao = str(fv).strip().upper()
            if _remove_accents(faccao) in _HEADER_LABELS or faccao in _HEADER_LABELS:
                continue
        else:
            faccao = sheet_name.upper()

        pv = row.iloc[col_idx["produto"]]
        if pd.isna(pv) or str(pv).strip() in ("", "nan", "None"):
            continue
        produto = str(pv).strip().upper()
        if _remove_accents(produto) in _HEADER_LABELS or produto in _HEADER_LABELS:
            continue

        meta_d = None
        if "meta_diaria" in col_idx:
            mv = row.iloc[col_idx["meta_diaria"]]
            try:
                meta_d = float(mv) if pd.notna(mv) else None
            except (ValueError, TypeError):
                meta_d = None

        for ci, dt in date_cols.items():
            try:
                v = row.iloc[ci]
                qty = float(v) if (pd.notna(v) and str(v).strip() not in ("-", "")) else 0.0
            except (ValueError, TypeError, IndexError):
                qty = 0.0

            records.append({
                "Faccao": faccao,
                "Produto": produto,
                "Data": dt,
                "Quantidade": qty,
                "Meta Diaria": meta_d,
            })

    return records


def _parse_sheet(raw: pd.DataFrame, sheet_name: str) -> pd.DataFrame | None:
    header_rows = _find_all_header_rows(raw)

    if not header_rows:
        return None

    all_records: list[dict] = []

    for block_num, header_idx in enumerate(header_rows):
        next_header = header_rows[block_num + 1] if block_num + 1 < len(header_rows) else len(raw)
        headers = raw.iloc[header_idx].tolist()
        block_data = raw.iloc[header_idx + 1 : next_header].reset_index(drop=True)
        block_data = block_data.dropna(how="all").reset_index(drop=True)

        if block_data.empty:
            continue

        records = _parse_block(block_data, headers, sheet_name)
        all_records.extend(records)

    if not all_records:
        return None

    df = pd.DataFrame(all_records)
    df["Data"] = pd.to_datetime(df["Data"])

    # Regra de negócio: tratar toda a produção como de um único vendedor.
    df["Faccao"] = "VENDEDOR UNICO"

    df = (
        df.groupby(["Faccao", "Produto", "Data"], as_index=False)
        .agg({"Quantidade": "sum", "Meta Diaria": "first"})
    )

    df["Ano"]       = df["Data"].dt.year
    df["Mes"]       = df["Data"].dt.month
    df["Mes Nome"]  = df["Mes"].map(MESES_PT)
    df["Dia"]       = df["Data"].dt.day
    df["Semana"]    = df["Data"].dt.isocalendar().week.astype(int)
    df["DiaSemana"] = df["Data"].dt.day_name()

    return df


# ──────────────────────────────────────────────
# Callbacks de filtro
# ──────────────────────────────────────────────
def _on_home_ano_change():
    for k in ("home_mes", "home_dia", "home_ini", "home_fim"):
        st.session_state.pop(k, None)


def _on_home_mes_change():
    for k in ("home_dia", "home_ini", "home_fim"):
        st.session_state.pop(k, None)


# ──────────────────────────────────────────────
# BOTÃO FILTROS (HTML)
# ──────────────────────────────────────────────
_FILTROS_BTN_HTML = """
<button onclick="
    var doc = window.parent.document;
    var selectors = [
        '[data-testid=stSidebarCollapsedControl] button',
        '[data-testid=stSidebarCollapsedControl]',
        'button[data-testid=stBaseButton-headerNoPadding]',
        '[data-testid=collapsedControl] button'
    ];
    var clicked = false;
    for (var i = 0; i < selectors.length; i++) {
        var el = doc.querySelector(selectors[i]);
        if (el) { el.click(); clicked = true; break; }
    }
    if (!clicked) {
        var btns = doc.querySelectorAll('button');
        for (var j = 0; j < btns.length; j++) {
            var b = btns[j];
            var r = b.getBoundingClientRect();
            if (r.left < 60 && r.top < 60 && r.width < 60 && b.querySelector('svg')) {
                b.click(); break;
            }
        }
    }
" style="
    width:100%;cursor:pointer;text-align:center;
    background:linear-gradient(135deg,#1A1F2E,#252B3B);
    border:1px solid #2D3748;border-radius:10px;
    color:#E2E8F0;padding:8px 16px;
    font-size:0.9rem;font-family:sans-serif;transition:all 0.3s ease;
" onmouseover="this.style.borderColor='#4ECDC4';this.style.color='#4ECDC4';"
   onmouseout="this.style.borderColor='#2D3748';this.style.color='#E2E8F0';">Filtros</button>
"""


# ──────────────────────────────────────────────
# TELA INICIAL (HOME)
# ──────────────────────────────────────────────
def render_home(all_data):
    with st.sidebar:
        st.markdown("### Filtros")

        all_anos = sorted(set(a for df in all_data.values() for a in df["Ano"].unique()))
        if "home_ano" not in st.session_state:
            st.session_state["home_ano"] = list(all_anos)
        sel_anos = st.multiselect("Ano", all_anos, key="home_ano", on_change=_on_home_ano_change)
        if not sel_anos:
            sel_anos = all_anos

        all_meses = sorted(set(
            m for df in all_data.values()
            for m in df[df["Ano"].isin(sel_anos)]["Mes"].unique()
        ))
        if "home_mes" not in st.session_state:
            st.session_state["home_mes"] = list(all_meses)
        else:
            valid_set = set(all_meses)
            st.session_state["home_mes"] = [m for m in st.session_state["home_mes"] if m in valid_set]
        sel_meses = st.multiselect(
            "Mês", all_meses, format_func=lambda m: MESES_NOME[m],
            key="home_mes", on_change=_on_home_mes_change,
        )
        if not sel_meses:
            sel_meses = all_meses

        st.markdown("### Filtro de Dias")
        modo = st.radio("Tipo de filtro", ["Período", "Um dia"], horizontal=True, key="home_modo")

        all_datas = pd.concat([df["Data"] for df in all_data.values()])
        filtered_datas = all_datas[
            all_datas.dt.year.isin(sel_anos) & all_datas.dt.month.isin(sel_meses)
        ]
        if not filtered_datas.empty:
            d_min = filtered_datas.min().date()
            d_max = filtered_datas.max().date()
        else:
            d_min = all_datas.min().date()
            d_max = all_datas.max().date()

        for _k, _def in [("home_dia", d_max), ("home_ini", d_min), ("home_fim", d_max)]:
            if _k not in st.session_state:
                st.session_state[_k] = _def
            else:
                _v = st.session_state[_k]
                if _v < d_min:
                    st.session_state[_k] = d_min
                elif _v > d_max:
                    st.session_state[_k] = d_max

        if modo == "Um dia":
            dia_sel = st.date_input("Dia", min_value=d_min, max_value=d_max,
                                    format="DD/MM/YYYY", key="home_dia")
            date_filter = lambda df: df[
                df["Ano"].isin(sel_anos) & df["Mes"].isin(sel_meses) &
                (df["Data"].dt.date == dia_sel)
            ]
        else:
            d_ini = st.date_input("Início", min_value=d_min, max_value=d_max,
                                  format="DD/MM/YYYY", key="home_ini")
            d_fim = st.date_input("Fim", min_value=d_min, max_value=d_max,
                                  format="DD/MM/YYYY", key="home_fim")
            ini, fim = min(d_ini, d_fim), max(d_ini, d_fim)
            date_filter = lambda df: df[
                df["Ano"].isin(sel_anos) & df["Mes"].isin(sel_meses) &
                (df["Data"].dt.date.between(ini, fim))
            ]

        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.sidebar.divider()
        st.sidebar.caption("Dados atualizados a cada 10 min.")

    filtered_data = {emp: date_filter(df) for emp, df in all_data.items()}
    filtered_data = {emp: df for emp, df in filtered_data.items() if not df.empty}
    excluidas = sorted(set(all_data.keys()) - set(filtered_data.keys()))

    if not filtered_data:
        st.markdown('<p class="main-title">🏭 Dashboard de Produção — Todas as Empresas</p>', unsafe_allow_html=True)
        st.markdown("---")
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        components.html(_FILTROS_BTN_HTML, height=45)

    st.markdown('<p class="main-title">🏭 Dashboard de Produção — Todas as Empresas</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Visão Geral de Todas as Empresas</p>', unsafe_allow_html=True)
    st.markdown("---")

    total_geral = sum(df["Quantidade"].sum() for df in filtered_data.values())
    n_empresas = len(filtered_data)
    dias_total = max((df[df["Quantidade"] > 0]["Data"].nunique() for df in filtered_data.values()), default=0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Empresas Ativas", n_empresas)
    m2.metric("Produção Total", f"{total_geral:,.0f}".replace(",", "."))
    m3.metric("Média por Empresa", f"{total_geral / n_empresas:,.0f}".replace(",", ".") if n_empresas else "0")
    m4.metric("Dias com Registros", dias_total)

    if excluidas:
        st.info(f"Empresas sem dados no período filtrado: **{', '.join(excluidas)}**")

    st.markdown("---")

    col_chart, col_select = st.columns([3, 2])
    company_totals = [{"Empresa": emp, "Total": df["Quantidade"].sum()} for emp, df in filtered_data.items()]
    df_totals = pd.DataFrame(company_totals).sort_values("Total", ascending=True)

    with col_chart:
        st.markdown('<p class="section-title">Produção Total por Empresa</p>', unsafe_allow_html=True)
        fig = px.bar(df_totals, x="Total", y="Empresa", orientation="h",
                     color="Empresa", color_discrete_map=CORES_EMPRESAS, text="Total")
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont=dict(color="#CBD5E0"))
        fig.update_layout(showlegend=False, height=max(300, n_empresas * 55),
                          margin=dict(l=0, r=80, t=10, b=0),
                          xaxis_title="Quantidade Produzida", yaxis_title="", **DARK_LAYOUT)
        st.plotly_chart(fig, width="stretch")

    with col_select:
        st.markdown('<p class="section-title">Selecione uma Empresa</p>', unsafe_allow_html=True)
        for emp in sorted(filtered_data.keys()):
            total_emp = df_totals.loc[df_totals["Empresa"] == emp, "Total"].values[0]
            if st.button(f"  {emp}  -  {total_emp:,.0f} un.".replace(",", "."),
                         key=f"btn_{emp}", use_container_width=True):
                st.query_params["empresa"] = emp
                st.rerun()

    st.markdown("---")

    st.markdown('<p class="section-title">Evolução Mensal da Produção</p>', unsafe_allow_html=True)
    monthly_frames = []
    for emp, df in filtered_data.items():
        grp = df.groupby(["Ano", "Mes"])["Quantidade"].sum().reset_index()
        grp["Empresa"] = emp
        grp["Periodo"] = grp.apply(lambda r: f"{int(r['Ano'])}-{int(r['Mes']):02d}", axis=1)
        monthly_frames.append(grp)

    if monthly_frames:
        df_monthly = pd.concat(monthly_frames, ignore_index=True)
        fig2 = px.line(df_monthly, x="Periodo", y="Quantidade", color="Empresa",
                       color_discrete_map=CORES_EMPRESAS, markers=True)
        fig2.update_layout(height=420, xaxis_title="Período", yaxis_title="Quantidade Produzida",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                           **DARK_LAYOUT)
        st.plotly_chart(fig2, width="stretch")

    st.markdown("---")
    st.markdown('<p class="section-title">Produção Total por Produto</p>', unsafe_allow_html=True)

    prod_frames = []
    for emp, df in filtered_data.items():
        grp = df.groupby("Produto")["Quantidade"].sum().reset_index()
        grp["Empresa"] = emp
        prod_frames.append(grp)

    if prod_frames:
        df_prod_full = pd.concat(prod_frames, ignore_index=True)
        df_prod_full = df_prod_full[df_prod_full["Quantidade"] > 0]

        empresas_disp = sorted(df_prod_full["Empresa"].unique())
        produtos_disp_all = sorted(df_prod_full["Produto"].unique())

        st.markdown("""
        <style>
        .filtro-treemap-card {
            background: linear-gradient(135deg, #16161C 0%, #1E1E26 100%);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 14px;
            padding: 14px 20px 6px 20px;
            margin-bottom: 16px;
        }
        .filtro-treemap-header {
            display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
            color: #FFFFFF; font-size: 0.78rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 1px;
        }
        .filtro-treemap-header span {
            display: inline-block; width: 18px; height: 2px;
            background: #FFFFFF; border-radius: 2px;
        }
        .filtro-treemap-card label {
            color: #8899AA !important; font-size: 0.72rem !important;
            font-weight: 600 !important; text-transform: uppercase !important;
            letter-spacing: 0.6px !important;
        }
        span[data-baseweb="tag"] {
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #FFFFFF !important; border-radius: 6px !important;
            font-size: 0.9rem !important;
        }
        span[data-baseweb="tag"] span { color: #FFFFFF !important; font-size: 0.9rem !important; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="filtro-treemap-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="filtro-treemap-header"><span></span> Filtros do Gráfico <span></span></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.pop("_tree_reset", False):
            st.session_state["tree_empresas"] = []
            st.session_state["tree_produtos"] = []

        col_fe, col_fp, col_clear = st.columns([3, 5, 1])

        with col_fe:
            sel_emp_tree = st.multiselect(
                "🏭  Empresas", empresas_disp, key="tree_empresas",
                placeholder="Selecione empresas...",
            )

        with col_fp:
            base_emp = sel_emp_tree if sel_emp_tree else empresas_disp
            produtos_disp = sorted(
                df_prod_full[df_prod_full["Empresa"].isin(base_emp)]["Produto"].unique()
            )
            sel_prod_tree = st.multiselect(
                "📦  Produtos", produtos_disp, key="tree_produtos",
                placeholder="Selecione produtos...",
            )

        with col_clear:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            if st.button("✕ Limpar", key="tree_clear", help="Resetar filtros do gráfico", use_container_width=True):
                st.session_state["_tree_reset"] = True
                st.rerun()

        emp_ativas  = sel_emp_tree  if sel_emp_tree  else empresas_disp
        prod_ativos = sel_prod_tree if sel_prod_tree else produtos_disp

        n_emp = len(emp_ativas); n_prod = len(prod_ativos)
        total_emp = len(empresas_disp); total_prod = len(produtos_disp_all)
        filtro_msg = (
            "Sem filtro ativo — exibindo tudo"
            if not sel_emp_tree and not sel_prod_tree
            else f'Exibindo <b style="color:#FFFFFF">{n_emp}</b>/{total_emp} empresas '
                 f'· <b style="color:#FFFFFF">{n_prod}</b>/{total_prod} produtos'
        )
        st.markdown(
            f'<p style="color:#555E6E;font-size:0.72rem;margin:4px 0 0 2px;">{filtro_msg}</p>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        df_prod = df_prod_full[
            df_prod_full["Empresa"].isin(emp_ativas) &
            df_prod_full["Produto"].isin(prod_ativos)
        ].copy()

        df_prod["Qtd_fmt"] = df_prod["Quantidade"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        fig3 = px.treemap(df_prod, path=["Produto", "Empresa"], values="Quantidade",
                          color="Empresa", color_discrete_map=CORES_EMPRESAS, custom_data=["Qtd_fmt"])
        fig3.update_traces(
            textinfo="label+value",
            texttemplate="<b>%{label}</b><br>%{customdata[0]} un.",
            textfont=dict(size=13, color="#FFFFFF"),
            hovertemplate="<b>%{label}</b><br>Quantidade: %{customdata[0]}<extra></extra>",
        )
        fig3.update_layout(height=550, margin=dict(l=0, r=0, t=30, b=0), **DARK_LAYOUT)
        st.plotly_chart(fig3, width="stretch")

    st.markdown('<p class="section-title">Resumo por Empresa</p>', unsafe_allow_html=True)
    resumo_rows = []
    for emp, df in filtered_data.items():
        total = df["Quantidade"].sum()
        dias = dias_para_media(df)
        media = total / dias if dias > 0 else 0
        resumo_rows.append({
            "Empresa": emp, "Total Produzido": int(total),
            "Dias Trabalhados": dias, "Média Diária": int(media),
            "Produtos": df["Produto"].nunique(),
        })
    df_resumo = pd.DataFrame(resumo_rows).sort_values("Total Produzido", ascending=False)
    _fmt_int = lambda v: f"{v:,.0f}".replace(",", ".")
    st.dataframe(df_resumo.style.format({"Total Produzido": _fmt_int, "Média Diária": _fmt_int}),
                 width="stretch", hide_index=True)


# ──────────────────────────────────────────────
# PAGINA DA EMPRESA (ANALISE DETALHADA)
# ──────────────────────────────────────────────
def render_company(empresa, df, all_data):
    cor = CORES_EMPRESAS.get(empresa, "#1E3A5F")

    with st.sidebar:
        if st.button("< Voltar para Visão Geral", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        st.markdown("---")
        st.markdown(f"### {empresa}")
        st.sidebar.markdown("### Filtros")

        anos = sorted(df["Ano"].unique())
        sel_anos = st.multiselect("Ano", anos, default=anos)
        if not sel_anos:
            sel_anos = anos

        meses_disp = sorted(df[df["Ano"].isin(sel_anos)]["Mes"].unique())
        sel_meses = st.multiselect("Mês", meses_disp, default=meses_disp,
                                   format_func=lambda m: MESES_NOME[m])
        if not sel_meses:
            sel_meses = meses_disp

        df_f = df[(df["Ano"].isin(sel_anos)) & (df["Mes"].isin(sel_meses))]

        st.markdown("### Filtro de Dias")
        modo = st.radio("Tipo de filtro", ["Período", "Um dia"], horizontal=True)

        if not df_f.empty:
            d_min = df_f["Data"].min().date()
            d_max = df_f["Data"].max().date()

            if modo == "Um dia":
                dia_sel = st.date_input("Dia", value=d_max, min_value=d_min,
                                        max_value=d_max, format="DD/MM/YYYY")
                df_f = df_f[df_f["Data"].dt.date == dia_sel]
            else:
                d_ini = st.date_input("Início", value=d_min, min_value=d_min,
                                      max_value=d_max, format="DD/MM/YYYY")
                d_fim = st.date_input("Fim", value=d_max, min_value=d_min,
                                      max_value=d_max, format="DD/MM/YYYY")
                ini, fim = min(d_ini, d_fim), max(d_ini, d_fim)
                df_f = df_f[df_f["Data"].dt.date.between(ini, fim)]

        prods = sorted(df_f["Produto"].unique()) if not df_f.empty else []
        sel_prods = st.multiselect("Produto", prods, default=prods)
        if not sel_prods:
            sel_prods = prods

        if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_atualizar_empresa"):
            st.cache_data.clear()
            st.rerun()

        st.sidebar.divider()
        st.sidebar.caption("Dados atualizados a cada 10 min.")

    df_f = df_f[df_f["Produto"].isin(sel_prods)]

    sel_facs = sorted(df_f["Faccao"].unique())

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        components.html(_FILTROS_BTN_HTML, height=45)
    st.markdown(f'<p class="main-title">🏭 Dashboard de Produção Diária — {empresa.upper()}</p>', unsafe_allow_html=True)
    st.markdown("---")

    if df_f.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return

    prod_total = df_f["Quantidade"].sum()
    d_uteis = dias_uteis(df_f["Data"])
    d_para_media = dias_para_media(df_f)
    media_dia = prod_total / d_para_media if d_para_media else 0

    meta_periodo, meta_por_data, meta_por_faccao = _calc_meta(df_f, sel_facs)
    tem_meta = meta_periodo > 0
    saldo = prod_total - meta_periodo if tem_meta else 0
    ating = (prod_total / meta_periodo) if (tem_meta and meta_periodo > 0) else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Produzido", fmt_br(prod_total))
    k2.metric("Meta do Período", fmt_br(meta_periodo) if tem_meta else "Sem meta")
    k3.metric("Saldo", fmt_br(saldo) if tem_meta else "-",
              delta=fmt_br(saldo) if tem_meta else None,
              delta_color="normal" if tem_meta else "off")
    k4.metric("Atingimento", f"{ating*100:.1f}%" if tem_meta else "-",
              delta=f"{(ating-1)*100:+.1f} pp" if tem_meta else None)
    k5.metric("Média / Dia", fmt_br(media_dia))
    k6.metric("Dias Úteis", str(d_uteis))

    if not tem_meta:
        st.info("Esta empresa ainda não possui meta cadastrada. "
                "Ao preencher a coluna 'Meta Diária', os gráficos de meta serão exibidos automaticamente.")

    st.markdown("")
    _fmt_int = lambda v: f"{v:,.0f}".replace(",", ".")

    tab_vis, tab_prod, tab_rank, tab_dados = st.tabs(
        ["Visão Geral", "Por Produto", "Ranking & Alertas", "Dados"]
    )

    # ─── Tab 1 ────────────────────────────────────────────────────
    with tab_vis:
        serie = df_f.groupby("Data", as_index=False)["Quantidade"].sum().sort_values("Data")
        serie["Meta Dia"] = serie["Data"].map(meta_por_data).fillna(0)
        serie["Acum. Produzido"] = serie["Quantidade"].cumsum()
        serie["Acum. Meta"] = serie["Meta Dia"].cumsum()

        fig1 = go.Figure()
        cores_barras = (
            ["#22c55e" if p >= m else "#ef4444" for p, m in zip(serie["Quantidade"], serie["Meta Dia"])]
            if tem_meta else [cor] * len(serie)
        )
        fig1.add_bar(x=serie["Data"], y=serie["Quantidade"], name="Produzido", marker_color=cores_barras)
        if tem_meta:
            fig1.add_scatter(x=serie["Data"], y=serie["Meta Dia"], mode="lines",
                             name="Meta Diária", line=dict(color="#facc15", width=2, dash="dash"))
        fig1.update_layout(title="Produção Diária x Meta", xaxis_title="Data", yaxis_title="Peças",
                           template="plotly_dark", separators=",.",
                           xaxis=dict(tickformat="%d/%m/%Y"),
                           legend=dict(orientation="h", y=-0.15), margin=dict(t=50, b=60))
        st.plotly_chart(fig1, width="stretch")

        col_a, col_b = st.columns(2)
        with col_a:
            fig_acum = go.Figure()
            fig_acum.add_scatter(x=serie["Data"], y=serie["Acum. Produzido"],
                                 mode="lines+markers", name="Produzido Acumulado",
                                 line=dict(color="#3b82f6", width=3))
            if tem_meta:
                fig_acum.add_scatter(x=serie["Data"], y=serie["Acum. Meta"],
                                     mode="lines", name="Meta Acumulada",
                                     line=dict(color="#facc15", width=2, dash="dot"))
            fig_acum.update_layout(title="Acumulado: Produção x Meta", template="plotly_dark",
                                   separators=",.", xaxis=dict(tickformat="%d/%m/%Y"),
                                   legend=dict(orientation="h", y=-0.18), margin=dict(t=50, b=60))
            st.plotly_chart(fig_acum, width="stretch")

        with col_b:
            dia_df = df_f.groupby(["Data", "DiaSemana"], as_index=False)["Quantidade"].sum()
            dia_df["DiaSemana"] = pd.Categorical(dia_df["DiaSemana"], categories=ORDEM_DIAS, ordered=True)
            dia_df = dia_df.dropna(subset=["DiaSemana"]).sort_values("DiaSemana")
            dia_df["Dia"] = dia_df["DiaSemana"].map(NOMES_DIAS)
            fig_box = px.box(dia_df, x="Dia", y="Quantidade", color="Dia",
                             title="Distribuição por Dia da Semana", template="plotly_dark")
            fig_box.update_layout(showlegend=False, separators=",.", margin=dict(t=50, b=40))
            st.plotly_chart(fig_box, width="stretch")

        mensal = df_f.groupby(["Ano", "Mes"], as_index=False)["Quantidade"].sum()
        mensal["MesNome"] = mensal["Mes"].map(MESES_NOME)
        mensal["Ano"] = mensal["Ano"].astype(str)
        fig_mes = px.bar(mensal, x="MesNome", y="Quantidade", color="Ano", barmode="group",
                         text_auto=True, title="Produção Mensal", template="plotly_dark")
        fig_mes.update_layout(xaxis_title="Mês", yaxis_title="Peças",
                              separators=",.", margin=dict(t=50, b=40))
        st.plotly_chart(fig_mes, width="stretch")

    # ─── Tab 2 ────────────────────────────────────────────────────
    with tab_prod:
        st.markdown("### Resumo por Produto")

        # Calcula dias de trabalho por produto considerando a lógica de sábado
        tbl_prod = df_f.groupby("Produto", as_index=False).agg(
            Produzido=("Quantidade", "sum"),
        )
        
        # Calcula dias para média por produto usando a função especial para sábados
        dias_por_produto = []
        for _, row in tbl_prod.iterrows():
            produto = row["Produto"]
            df_produto = df_f[df_f["Produto"] == produto]
            dias = dias_para_media(df_produto)
            dias_por_produto.append(dias)
        
        tbl_prod["Dias"] = dias_por_produto

        meta_prod = (
            df_f.drop_duplicates(subset=["Produto", "Ano", "Mes"])
            [["Produto", "Ano", "Mes", "Meta Diaria"]]
            .copy()
        )
        dias_mes = (
            df_f.groupby(["Ano", "Mes"])["Data"]
            .apply(dias_uteis)
            .reset_index()
            .rename(columns={"Data": "DiasUteis"})
        )
        meta_prod = meta_prod.merge(dias_mes, on=["Ano", "Mes"], how="left")
        meta_prod["Meta Diaria"] = meta_prod["Meta Diaria"].fillna(0)
        meta_prod["DiasUteis"] = meta_prod["DiasUteis"].fillna(0)
        meta_prod["Meta Periodo Mes"] = meta_prod["Meta Diaria"] * meta_prod["DiasUteis"]
        meta_prod = meta_prod.groupby("Produto", as_index=False)["Meta Periodo Mes"].sum()
        meta_prod = meta_prod.rename(columns={"Meta Periodo Mes": "Meta Periodo"})

        tbl_prod = tbl_prod.merge(meta_prod, on="Produto", how="left")
        tbl_prod["Meta Periodo"] = tbl_prod["Meta Periodo"].fillna(0)
        tbl_prod["Ating. %"] = np.where(
            tbl_prod["Meta Periodo"] > 0,
            tbl_prod["Produzido"] / tbl_prod["Meta Periodo"] * 100,
            0,
        )
        tbl_prod["Saldo"] = tbl_prod["Produzido"] - tbl_prod["Meta Periodo"]
        tbl_prod["Média/Dia"] = np.where(tbl_prod["Dias"] > 0, tbl_prod["Produzido"] / tbl_prod["Dias"], 0)
        tbl_prod = tbl_prod.sort_values("Produzido", ascending=False)

        st.dataframe(
            tbl_prod.style.format({
                "Produzido": _fmt_int,
                "Meta Periodo": _fmt_int,
                "Saldo": _fmt_int,
                "Ating. %": "{:.1f}%",
                "Média/Dia": _fmt_int,
            }),
            width="stretch",
            hide_index=True,
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_prod = px.bar(
                tbl_prod.sort_values("Produzido", ascending=True),
                y="Produto", x="Produzido", orientation="h", text="Produzido",
                color_discrete_sequence=[cor],
                title="Volume Produzido por Produto",
                template="plotly_dark",
            )
            fig_prod.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_prod.update_layout(separators=",.", margin=dict(t=50, l=80, r=40, b=40))
            st.plotly_chart(fig_prod, width="stretch")

        with col_p2:
            serie_prod = (
                df_f.groupby(["Data", "Produto"], as_index=False)["Quantidade"]
                .sum().sort_values("Data")
            )
            fig_linha_prod = px.line(
                serie_prod,
                x="Data",
                y="Quantidade",
                color="Produto",
                markers=True,
                title="Evolução Diária por Produto",
                template="plotly_dark",
            )
            fig_linha_prod.update_layout(
                xaxis=dict(tickformat="%d/%m/%Y"),
                separators=",.",
                legend=dict(orientation="h", y=-0.2),
                margin=dict(t=50, b=80),
            )
            st.plotly_chart(fig_linha_prod, width="stretch")

    # ─── Tab 3 ────────────────────────────────────────────────────
    with tab_rank:
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.markdown("### Top 5 Dias Mais Produtivos")
            top5 = df_f.groupby("Data", as_index=False)["Quantidade"].sum().nlargest(5, "Quantidade")
            top5["DataFmt"] = top5["Data"].dt.strftime("%d/%m/%Y")
            for i, row in enumerate(top5.itertuples(), 1):
                medal = ["1.", "2.", "3."][i - 1] if i <= 3 else f"  {i}."
                st.markdown(f"**{medal} {row.DataFmt}** - {fmt_br(row.Quantidade)} peças")

        with col_r2:
            st.markdown("### Top 5 Dias Menos Produtivos")
            bot5 = df_f.groupby("Data", as_index=False)["Quantidade"].sum().nsmallest(5, "Quantidade")
            bot5["DataFmt"] = bot5["Data"].dt.strftime("%d/%m/%Y")
            for i, row in enumerate(bot5.itertuples(), 1):
                st.markdown(f"**{i}. {row.DataFmt}** - {fmt_br(row.Quantidade)} peças")

        st.markdown("---")
        st.markdown("### Dias Abaixo de 70% da Meta Diária")
        if tem_meta:
            alerta_dia = df_f.groupby("Data", as_index=False)["Quantidade"].sum()
            alerta_dia["Meta Dia"] = alerta_dia["Data"].map(meta_por_data).fillna(0)
            alerta_dia = alerta_dia[alerta_dia["Meta Dia"] > 0].copy()
            alerta_dia["Ating. %"] = alerta_dia["Quantidade"] / alerta_dia["Meta Dia"] * 100
            alerta_dia["Saldo"] = alerta_dia["Quantidade"] - alerta_dia["Meta Dia"]
            alerta_dia = alerta_dia[alerta_dia["Ating. %"] < 70].sort_values("Data")

            if alerta_dia.empty:
                st.success("Nenhum dia abaixo de 70% da meta no período selecionado!")
            else:
                alerta_dia["Data"] = alerta_dia["Data"].dt.strftime("%d/%m/%Y")
                st.dataframe(
                    alerta_dia.style.format({
                        "Quantidade": _fmt_int,
                        "Meta Dia": _fmt_int,
                        "Ating. %": "{:.1f}%",
                        "Saldo": _fmt_int,
                    }).map(lambda _: "color: #ef4444", subset=["Ating. %"]),
                    width="stretch",
                    hide_index=True,
                )
        else:
            st.info("Alertas de meta serão exibidos quando a meta for cadastrada na planilha.")

    # ─── Tab 4 ────────────────────────────────────────────────────
    with tab_dados:
        st.markdown("### Base Filtrada")
        df_view = df_f[["Data", "Produto", "Quantidade", "Meta Diaria"]].copy()
        df_view = df_view.sort_values(["Data", "Produto"], ascending=[False, True])
        df_view["Data"] = df_view["Data"].dt.strftime("%d/%m/%Y")
        df_view = df_view.rename(columns={"Meta Diaria": "Meta Diária"})
        _fmt_int = lambda v: f"{v:,.0f}".replace(",", ".") if pd.notna(v) and v is not None else "-"
        st.dataframe(
            df_view.reset_index(drop=True).style.format({
                "Quantidade": _fmt_int, "Meta Diária": _fmt_int,
            }),
            width="stretch", height=500,
        )
        csv = df_f.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Baixar CSV filtrado", csv,
            file_name=f"producao_{empresa.lower()}_filtrada.csv",
            mime="text/csv",
        )


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    all_data = load_all_data()

    if not all_data:
        st.error("Não foi possível carregar os dados da planilha.")
        st.info("Verifique se o arquivo 'planilha_producao.xlsx' está disponível "
                "ou se a planilha do Google Sheets está acessível.")
        return

    empresa = st.query_params.get("empresa", None)

    if empresa and empresa in all_data:
        render_company(empresa, all_data[empresa], all_data)
    else:
        render_home(all_data)


if __name__ == "__main__":
    main()