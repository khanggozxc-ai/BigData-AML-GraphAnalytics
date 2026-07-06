from pathlib import Path
import ast
import math
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_agraph import agraph, Node, Edge, Config
    HAS_AGRAPH = True
except Exception:
    HAS_AGRAPH = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data/output/suspicious_cycles.csv"

REQUIRED_COLUMNS = [
    "cycle_id",
    "path",
    "total_amount",
    "duration_minutes",
    "risk_score",
    "risk_level",
]

RISK_ORDER = ["Low", "Medium", "High"]
RISK_COLOR_MAP = {
    "High": "#D92D20",
    "Medium": "#F79009",
    "Low": "#12B76A",
    "Unknown": "#98A2B3",
}

st.set_page_config(
    page_title="AML Control Tower | Transaction Monitoring",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 24%),
                linear-gradient(180deg, #070B12 0%, #0B1220 45%, #070B12 100%);
            color: #F9FAFB;
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #050816 0%, #0B1220 48%, #111827 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #E5E7EB;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(16,24,40,0.98), rgba(15,23,42,0.92));
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 18px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 18px 45px rgba(0,0,0,0.24);
        }

        div[data-testid="stMetric"] label {
            color: #94A3B8 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.02em;
        }

        div[data-testid="stMetricValue"] {
            color: #F9FAFB !important;
            font-weight: 800 !important;
        }

        .bank-header {
            padding: 1.15rem 1.35rem;
            border-radius: 20px;
            background:
                linear-gradient(135deg, rgba(15,23,42,0.98), rgba(30,41,59,0.92)),
                linear-gradient(90deg, rgba(212,175,55,0.12), transparent);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 22px 60px rgba(0,0,0,0.28);
            margin-bottom: 1.2rem;
        }

        .bank-header-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.65rem;
        }

        .bank-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .bank-logo-mark {
            width: 46px;
            height: 46px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0B1220, #1D4ED8);
            border: 1px solid rgba(255,255,255,0.16);
            font-size: 1.55rem;
            box-shadow: inset 0 0 20px rgba(255,255,255,0.06);
        }

        .bank-title {
            font-size: 1.85rem;
            font-weight: 850;
            letter-spacing: -0.035em;
            color: #F8FAFC;
            line-height: 1.05;
        }

        .bank-subtitle {
            color: #CBD5E1;
            font-size: 0.92rem;
            margin-top: 0.2rem;
        }

        .env-pill {
            padding: 0.38rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            background: rgba(18,183,106,0.12);
            color: #86EFAC;
            border: 1px solid rgba(18,183,106,0.28);
            white-space: nowrap;
        }

        .bank-status-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 0.8rem;
        }

        .status-tile {
            padding: 0.78rem 0.85rem;
            border-radius: 14px;
            background: rgba(2,6,23,0.38);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .status-label {
            color: #94A3B8;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .status-value {
            color: #F8FAFC;
            font-weight: 750;
            font-size: 0.95rem;
            margin-top: 0.2rem;
        }

        .sidebar-bank-card {
            text-align: left;
            padding: 1rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(30,64,175,0.78));
            border: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 1rem;
            box-shadow: 0 16px 45px rgba(0,0,0,0.25);
        }

        .sidebar-bank-name {
            color: #F8FAFC;
            font-size: 1.05rem;
            font-weight: 850;
            margin-top: 0.4rem;
        }

        .sidebar-bank-caption {
            color: #CBD5E1;
            font-size: 0.78rem;
            margin-top: 0.1rem;
        }

        .compliance-note {
            padding: 0.75rem 0.85rem;
            border-radius: 14px;
            background: rgba(37,99,235,0.12);
            border: 1px solid rgba(59,130,246,0.25);
            color: #BFDBFE;
            font-size: 0.82rem;
            line-height: 1.42;
            margin-top: 0.75rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 800;
            color: #F8FAFC;
            margin-bottom: 0.35rem;
        }

        .section-caption {
            color: #94A3B8;
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
        }

        .risk-badge-high, .risk-badge-medium, .risk-badge-low {
            padding: 0.25rem 0.55rem;
            border-radius: 999px;
            font-weight: 800;
        }

        .risk-badge-high {
            color: #FEE4E2;
            background: rgba(217,45,32,0.18);
            border: 1px solid rgba(217,45,32,0.35);
        }

        .risk-badge-medium {
            color: #FEF0C7;
            background: rgba(247,144,9,0.16);
            border: 1px solid rgba(247,144,9,0.32);
        }

        .risk-badge-low {
            color: #D1FADF;
            background: rgba(18,183,106,0.14);
            border: 1px solid rgba(18,183,106,0.30);
        }

        .stDataFrame {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.08);
        }

        hr {
            border-color: rgba(255,255,255,0.10);
        }

        @media (max-width: 1100px) {
            .bank-status-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_vnd(value: float | int | None) -> str:
    """Định dạng số tiền theo phong cách dashboard tài chính."""
    if value is None or pd.isna(value):
        return "0 VND"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f}B VND"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M VND"

    return f"{value:,.0f} VND"


def parse_cycle_path(path_value: Any) -> list[str]:
    """Chuyển chuỗi path trong CSV thành danh sách tài khoản."""
    if pd.isna(path_value):
        return []

    if isinstance(path_value, list):
        return [str(item).strip() for item in path_value if str(item).strip()]

    text = str(path_value).strip()

    if not text:
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except Exception:
        pass

    if "->" in text:
        return [part.strip().strip("'\"") for part in text.split("->") if part.strip()]

    return [part.strip().strip("'\"[]") for part in text.split(",") if part.strip().strip("'\"[]")]


def calculate_cycle_length(path_value: Any) -> int:
    """Tính độ dài chu trình dựa trên số tài khoản khác nhau."""
    nodes = parse_cycle_path(path_value)

    if not nodes:
        return 0

    if len(nodes) >= 2 and nodes[0] == nodes[-1]:
        return len(nodes) - 1

    return len(nodes)


def extract_affected_accounts(df: pd.DataFrame) -> set[str]:
    """Trích xuất toàn bộ tài khoản xuất hiện trong tập cycle đang lọc."""
    accounts: set[str] = set()

    if df.empty or "path" not in df.columns:
        return accounts

    for path_value in df["path"].dropna():
        for account in parse_cycle_path(path_value):
            accounts.add(account)

    return accounts


def normalize_risk_level(value: Any) -> str:
    """Chuẩn hóa risk_level về Low, Medium, High hoặc Unknown."""
    if pd.isna(value):
        return "Unknown"

    text = str(value).strip().lower()

    if text == "high":
        return "High"

    if text == "medium":
        return "Medium"

    if text == "low":
        return "Low"

    return "Unknown"


def risk_row_style(row: pd.Series) -> list[str]:
    """Tô màu dòng bảng theo risk_level."""
    risk_level = row.get("risk_level", "Unknown")

    if risk_level == "High":
        return ["background-color: rgba(217,45,32,0.18); color: #FEE4E2;" for _ in row]

    if risk_level == "Medium":
        return ["background-color: rgba(247,144,9,0.15); color: #FEF0C7;" for _ in row]

    if risk_level == "Low":
        return ["background-color: rgba(18,183,106,0.12); color: #D1FADF;" for _ in row]

    return ["background-color: rgba(152,162,179,0.10); color: #EAECF0;" for _ in row]


def validate_required_columns(df: pd.DataFrame) -> None:
    """Kiểm tra file CSV có đủ cột bắt buộc."""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(
            "File suspicious_cycles.csv thiếu các cột bắt buộc: " + ", ".join(missing_columns)
        )


def risk_badge_html(level: str) -> str:
    """Tạo HTML badge cho risk level trong phần chi tiết."""
    if level == "High":
        return '<span class="risk-badge-high">HIGH RISK</span>'
    if level == "Medium":
        return '<span class="risk-badge-medium">MEDIUM RISK</span>'
    if level == "Low":
        return '<span class="risk-badge-low">LOW RISK</span>'
    return '<span>UNKNOWN</span>'


@st.cache_data(show_spinner="Loading suspicious transaction cycles...")
def load_suspicious_cycles(csv_path: str) -> pd.DataFrame:
    """Đọc suspicious_cycles.csv và ép kiểu dữ liệu an toàn."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(str(path))

    df = pd.read_csv(path)
    validate_required_columns(df)

    df["cycle_id"] = df["cycle_id"].astype(str)
    df["path"] = df["path"].astype(str)
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce").fillna(0)
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).clip(0, 100)
    df["risk_level"] = df["risk_level"].apply(normalize_risk_level)
    df["cycle_length"] = df["path"].apply(calculate_cycle_length)

    if "amount_variance" in df.columns:
        df["amount_variance"] = pd.to_numeric(df["amount_variance"], errors="coerce").fillna(0)

    if "explanation" not in df.columns:
        df["explanation"] = "No alert narrative available."
    else:
        df["explanation"] = df["explanation"].fillna("No alert narrative available.")

    return df.sort_values(by=["risk_score", "total_amount"], ascending=[False, False]).reset_index(drop=True)


def render_enterprise_header(df: pd.DataFrame) -> None:
    """Vẽ header theo phong cách phần mềm ngân hàng quốc tế."""
    last_refresh = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
    total_cycles = len(df)
    high_count = int((df["risk_level"] == "High").sum()) if not df.empty else 0
    medium_count = int((df["risk_level"] == "Medium").sum()) if not df.empty else 0
    low_count = int((df["risk_level"] == "Low").sum()) if not df.empty else 0

    st.markdown(
        f"""
        <div class="bank-header">
            <div class="bank-header-topline">
                <div class="bank-brand">
                    <div class="bank-logo-mark">🏦</div>
                    <div>
                        <div class="bank-title">Global AML Control Tower</div>
                        <div class="bank-subtitle">
                            Enterprise transaction monitoring console for suspicious circular fund flows
                        </div>
                    </div>
                </div>
                <div class="env-pill">PRODUCTION MONITORING VIEW</div>
            </div>
            <div class="bank-status-grid">
                <div class="status-tile"><div class="status-label">Alert Batch</div><div class="status-value">{total_cycles:,} Cycles</div></div>
                <div class="status-tile"><div class="status-label">Risk Mix</div><div class="status-value">H {high_count} · M {medium_count} · L {low_count}</div></div>
                <div class="status-tile"><div class="status-label">Model</div><div class="status-value">Graph Cycle Analytics</div></div>
                <div class="status-tile"><div class="status-label">Last Refresh</div><div class="status-value">{last_refresh}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(df: pd.DataFrame) -> tuple[float, float, tuple[int, int], list[str]]:
    """Hiển thị sidebar theo phong cách banker-grade compliance console."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-bank-card">
                <div style="font-size: 2rem;">🏦</div>
                <div class="sidebar-bank-name">Global Transaction Surveillance</div>
                <div class="sidebar-bank-caption">AML / CFT · Graph Analytics · Case Triage</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Project Dossier")
        st.caption("Đồ án Big Data — Suspicious Transaction Cycle Detection")
        st.write("**Role A:** Data Engineering / Pipeline")
        st.write("**Role B:** Graph Analytics / Control Tower UI")

        st.markdown(
            """
            <div class="compliance-note">
                <b>Compliance note</b><br/>
                Dashboard này chỉ đánh dấu giao dịch đáng ngờ để hỗ trợ rà soát.
                Không kết luận tài khoản hoặc giao dịch là rửa tiền thật.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("### Surveillance Filters")

        max_amount_value = float(df["total_amount"].max()) if not df.empty else 0.0
        min_score_value = float(df["risk_score"].min()) if not df.empty else 0.0
        min_length_value = int(df["cycle_length"].min()) if not df.empty else 0
        max_length_value = int(df["cycle_length"].max()) if not df.empty else 1

        amount_filter = st.slider(
            "Minimum transaction amount",
            min_value=0.0,
            max_value=max(max_amount_value, 1.0),
            value=0.0,
            step=max(max_amount_value / 100, 1.0),
            format="%.0f",
        )

        risk_score_filter = st.slider(
            "Minimum risk score",
            min_value=0.0,
            max_value=100.0,
            value=max(0.0, min_score_value),
            step=1.0,
        )

        if min_length_value == max_length_value:
            cycle_length_filter = (min_length_value, max_length_value)
            st.info(f"Cycle length in current alert set: {min_length_value}")
        else:
            cycle_length_filter = st.slider(
                "Cycle length",
                min_value=min_length_value,
                max_value=max_length_value,
                value=(min_length_value, max_length_value),
                step=1,
            )

        available_risk_levels = [level for level in RISK_ORDER if level in set(df["risk_level"])]
        selected_risk_levels = st.multiselect(
            "Risk classification",
            options=available_risk_levels,
            default=available_risk_levels,
        )

        st.divider()
        if st.button("Refresh surveillance cache"):
            st.cache_data.clear()
            st.rerun()

    return amount_filter, risk_score_filter, cycle_length_filter, selected_risk_levels


def apply_filters(
    df: pd.DataFrame,
    amount_filter: float,
    risk_score_filter: float,
    cycle_length_filter: tuple[int, int],
    selected_risk_levels: list[str],
) -> pd.DataFrame:
    """Áp dụng filter từ sidebar lên dataframe."""
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df["total_amount"] >= amount_filter]
    filtered_df = filtered_df[filtered_df["risk_score"] >= risk_score_filter]
    filtered_df = filtered_df[filtered_df["cycle_length"].between(cycle_length_filter[0], cycle_length_filter[1])]

    if selected_risk_levels:
        filtered_df = filtered_df[filtered_df["risk_level"].isin(selected_risk_levels)]

    return filtered_df.reset_index(drop=True)


def render_kpi_section(df: pd.DataFrame) -> None:
    """Hiển thị KPI theo phong cách executive risk dashboard."""
    total_cycles = len(df)
    suspicious_amount = df["total_amount"].sum() if not df.empty else 0
    average_risk = df["risk_score"].mean() if not df.empty else 0
    affected_accounts = extract_affected_accounts(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Detected Cycles", f"{total_cycles:,}")
    col2.metric("Suspicious Flow", format_vnd(suspicious_amount))
    col3.metric("Average Risk Score", f"{average_risk:.1f}/100")
    col4.metric("Affected Accounts", f"{len(affected_accounts):,}")


def render_supporting_charts(df: pd.DataFrame) -> None:
    """Vẽ biểu đồ phân bố risk và scatter amount-score."""
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">Number of detected circular flows by risk class.</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("No records available for the current filter.")
        else:
            risk_counts = df["risk_level"].value_counts().reindex(RISK_ORDER).fillna(0).astype(int).reset_index()
            risk_counts.columns = ["risk_level", "count"]

            fig = px.bar(
                risk_counts,
                x="risk_level",
                y="count",
                color="risk_level",
                color_discrete_map=RISK_COLOR_MAP,
                text="count",
                labels={"risk_level": "Risk level", "count": "Alerts"},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=360,
                template="plotly_dark",
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=35, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.markdown('<div class="section-title">Exposure vs Risk Score</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">Relationship between circular amount and computed alert score.</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("No records available for the current filter.")
        else:
            fig = px.scatter(
                df,
                x="total_amount",
                y="risk_score",
                color="risk_level",
                size="cycle_length",
                hover_data=["cycle_id", "cycle_length", "duration_minutes", "total_amount", "risk_score"],
                color_discrete_map=RISK_COLOR_MAP,
                labels={
                    "total_amount": "Total amount",
                    "risk_score": "Risk score",
                    "risk_level": "Risk level",
                    "cycle_length": "Cycle length",
                },
            )
            fig.update_layout(
                height=360,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=35, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)


def render_data_explorer(df: pd.DataFrame) -> None:
    """Hiển thị bảng case triage."""
    st.markdown('<div class="section-title">Alert Case Triage</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Prioritized suspicious cycles for analyst review.</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No suspicious cycles match the current filters.")
        return

    display_columns = [
        "cycle_id",
        "risk_level",
        "risk_score",
        "cycle_length",
        "total_amount",
        "duration_minutes",
        "path",
        "explanation",
    ]

    if "amount_variance" in df.columns:
        display_columns.insert(5, "amount_variance")

    display_df = df[[col for col in display_columns if col in df.columns]].copy()
    styled_df = display_df.style.apply(risk_row_style, axis=1).format(
        {
            "total_amount": "{:,.0f}",
            "duration_minutes": "{:,.0f}",
            "risk_score": "{:.1f}",
            "amount_variance": "{:.4f}",
        }
    )
    st.dataframe(styled_df, use_container_width=True, height=430)


def build_cycle_edges(nodes: list[str]) -> list[tuple[str, str]]:
    """Tạo danh sách cạnh từ path cycle."""
    if len(nodes) < 2:
        return []

    normalized_nodes = nodes.copy()
    if normalized_nodes[0] != normalized_nodes[-1]:
        normalized_nodes.append(normalized_nodes[0])

    return [(normalized_nodes[i], normalized_nodes[i + 1]) for i in range(len(normalized_nodes) - 1)]


def render_graph_with_agraph(nodes: list[str], edges: list[tuple[str, str]]) -> None:
    """Vẽ graph tương tác bằng streamlit-agraph."""
    unique_nodes = list(dict.fromkeys(nodes))
    graph_nodes = [Node(id=node, label=node, size=26) for node in unique_nodes]
    graph_edges = [Edge(source=source, target=target, label="fund flow") for source, target in edges]

    config = Config(
        width="100%",
        height=560,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#D4AF37",
        collapsible=False,
    )
    agraph(nodes=graph_nodes, edges=graph_edges, config=config)


def render_graph_with_plotly(nodes: list[str], edges: list[tuple[str, str]]) -> None:
    """Fallback graph bằng Plotly khi chưa cài streamlit-agraph."""
    unique_nodes = list(dict.fromkeys(nodes))

    if not unique_nodes:
        st.info("No account node available for visualization.")
        return

    node_positions = {}
    radius = 1.0
    total_nodes = len(unique_nodes)

    for index, node in enumerate(unique_nodes):
        angle = 2 * math.pi * index / total_nodes
        node_positions[node] = {"x": radius * math.cos(angle), "y": radius * math.sin(angle)}

    edge_x = []
    edge_y = []
    annotations = []

    for source, target in edges:
        if source not in node_positions or target not in node_positions:
            continue

        x0 = node_positions[source]["x"]
        y0 = node_positions[source]["y"]
        x1 = node_positions[target]["x"]
        y1 = node_positions[target]["y"]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        annotations.append(
            dict(
                ax=x0,
                ay=y0,
                x=x1,
                y=y1,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.25,
                arrowwidth=1.6,
                arrowcolor="#CBD5E1",
            )
        )

    node_x = [node_positions[node]["x"] for node in unique_nodes]
    node_y = [node_positions[node]["y"] for node in unique_nodes]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=2.2, color="#94A3B8"),
            hoverinfo="none",
            name="Fund flow",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=unique_nodes,
            textposition="bottom center",
            marker=dict(size=32, color="#2563EB", line=dict(width=2, color="#D4AF37")),
            hovertext=unique_nodes,
            hoverinfo="text",
            name="Accounts",
        )
    )
    fig.update_layout(
        height=560,
        template="plotly_dark",
        showlegend=False,
        annotations=annotations,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_graph_visualization(df: pd.DataFrame) -> None:
    """Hiển thị bản đồ luân chuyển dòng tiền cho một alert."""
    st.markdown('<div class="section-title">Circular Flow Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Interactive account-to-account movement view for selected alert.</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No suspicious cycle available for graph visualization.")
        return

    cycle_options = [
        f"{row.cycle_id} · {row.risk_level} · score {row.risk_score:.1f} · {format_vnd(row.total_amount)}"
        for row in df.itertuples()
    ]

    selected_label = st.selectbox("Select alert case", options=cycle_options)
    selected_index = cycle_options.index(selected_label)
    selected_row = df.iloc[selected_index]

    nodes = parse_cycle_path(selected_row["path"])
    edges = build_cycle_edges(nodes)

    st.markdown(
        f"""
        <div style="padding:1rem 1.15rem; border-radius:18px; background:rgba(16,24,40,0.78); border:1px solid rgba(255,255,255,0.08); margin-bottom:1rem;">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem;">
                <div>
                    <div style="color:#94A3B8; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em;">Selected Alert</div>
                    <div style="font-size:1.25rem; font-weight:850; color:#F8FAFC;">{selected_row["cycle_id"]}</div>
                </div>
                <div>{risk_badge_html(selected_row["risk_level"])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
    detail_col1.metric("Risk Score", f"{selected_row['risk_score']:.1f}/100")
    detail_col2.metric("Total Amount", format_vnd(selected_row["total_amount"]))
    detail_col3.metric("Duration", f"{selected_row['duration_minutes']:.0f} min")
    detail_col4.metric("Cycle Length", f"{selected_row['cycle_length']} accounts")

    st.markdown("**Fund flow path**")
    st.code(" -> ".join(nodes), language="text")

    st.markdown("**Alert narrative**")
    st.write(selected_row["explanation"])

    if HAS_AGRAPH:
        render_graph_with_agraph(nodes, edges)
    else:
        st.info(
            "streamlit-agraph is not installed. The dashboard is using Plotly fallback. "
            "Install with: pip install streamlit-agraph"
        )
        render_graph_with_plotly(nodes, edges)


def main() -> None:
    """Điều phối toàn bộ dashboard."""
    try:
        df = load_suspicious_cycles(str(DATA_PATH))
    except FileNotFoundError:
        st.info(
            "Missing `data/output/suspicious_cycles.csv`.\n\n"
            "Run the pipeline first:\n\n"
            "`python src/main.py --step clean`\n\n"
            "`python src/main.py --step subgraph`\n\n"
            "`python src/main.py --step detect`"
        )
        st.stop()
    except ValueError as error:
        st.warning(str(error))
        st.stop()
    except Exception as error:
        st.warning("Dashboard could not read the output file. Please verify `data/output/suspicious_cycles.csv`.")
        st.exception(error)
        st.stop()

    if df.empty:
        st.warning("`suspicious_cycles.csv` is empty. The pipeline may have run successfully but detected no cycle.")
        st.stop()

    render_enterprise_header(df)
    amount_filter, risk_score_filter, cycle_length_filter, selected_risk_levels = render_sidebar(df)
    filtered_df = apply_filters(df, amount_filter, risk_score_filter, cycle_length_filter, selected_risk_levels)

    st.markdown("## Executive Surveillance Overview")
    render_kpi_section(filtered_df)

    st.divider()
    st.markdown("## Risk Intelligence")
    render_supporting_charts(filtered_df)

    st.divider()
    st.markdown("## Alert Investigation Workspace")
    render_data_explorer(filtered_df)

    st.divider()
    st.markdown("## Transaction Flow Reconstruction")
    render_graph_visualization(filtered_df)


if __name__ == "__main__":
    main()
