from pathlib import Path
import ast
import math
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CẤU HÌNH CHUNG
# ============================================================

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

RISK_ORDER = ["Thấp", "Trung bình", "Cao"]
RISK_COLOR_MAP = {
    "Thấp": "#22C55E",
    "Trung bình": "#F59E0B",
    "Cao": "#EF4444",
    "Không xác định": "#94A3B8",
}

STATUS_COLOR_MAP = {
    "Đang theo dõi": "#3B82F6",
    "Đang rà soát": "#F59E0B",
    "Cần chuyển cấp": "#EF4444",
    "Đã đóng": "#22C55E",
}

st.set_page_config(
    page_title="Dashboard giám sát giao dịch AML",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS GIAO DIỆN
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --bg-main: #070B12;
            --bg-card: #0F172A;
            --bg-soft: #111827;
            --bg-soft-2: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --border: rgba(148, 163, 184, 0.18);
            --blue: #3B82F6;
            --green: #22C55E;
            --orange: #F59E0B;
            --red: #EF4444;
            --cyan: #38BDF8;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 28%),
                linear-gradient(180deg, #070B12 0%, #0B1220 52%, #070B12 100%);
            color: var(--text-main);
        }

        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            visibility: hidden !important;
        }

        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1rem !important;
            padding-bottom: 2rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #050816 0%, #0B1220 55%, #0F172A 100%);
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] * {
            color: #E5E7EB;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.92));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.24);
        }

        div[data-testid="stMetric"] label {
            color: var(--text-muted) !important;
            font-size: 0.82rem !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-main) !important;
            font-weight: 850 !important;
        }

        .app-header {
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 58, 138, 0.92) 100%),
                linear-gradient(90deg, rgba(56, 189, 248, 0.14), transparent);
            color: #FFFFFF;
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 22px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 22px 54px rgba(0, 0, 0, 0.34);
        }

        .app-header-title {
            font-size: 1.7rem;
            font-weight: 850;
            letter-spacing: -0.03em;
            margin-bottom: 0.25rem;
        }

        .app-header-caption {
            color: #DBEAFE;
            font-size: 0.95rem;
            line-height: 1.45;
        }

        .section-card {
            background: rgba(15, 23, 42, 0.92);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.22);
        }

        .soft-card {
            background: rgba(17, 24, 39, 0.88);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.75rem;
        }

        .analyst-panel {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.94));
            border: 1px solid rgba(59, 130, 246, 0.30);
            border-left: 4px solid #3B82F6;
            border-radius: 18px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.24);
        }

        .analyst-tag {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.16);
            border: 1px solid rgba(59, 130, 246, 0.36);
            color: #BFDBFE;
            font-size: 0.78rem;
            font-weight: 780;
            margin-bottom: 0.55rem;
        }

        .analyst-title {
            font-size: 1.05rem;
            font-weight: 850;
            color: #F8FAFC;
            margin-bottom: 0.3rem;
        }

        .analyst-caption {
            color: #CBD5E1;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .role-panel {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.94));
            border: 1px solid rgba(59, 130, 246, 0.30);
            border-left: 4px solid #3B82F6;
            border-radius: 18px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.24);
        }

        .role-title {
            font-size: 1.05rem;
            font-weight: 850;
            color: #F8FAFC;
            margin-bottom: 0.3rem;
        }

        .role-caption {
            color: #CBD5E1;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .role-tag {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.16);
            border: 1px solid rgba(59, 130, 246, 0.36);
            color: #BFDBFE;
            font-size: 0.78rem;
            font-weight: 780;
            margin-bottom: 0.55rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 820;
            color: var(--text-main);
            margin-bottom: 0.2rem;
        }

        .section-caption {
            color: var(--text-muted);
            font-size: 0.86rem;
            line-height: 1.45;
            margin-bottom: 0.7rem;
        }

        .explain-box {
            background: rgba(37, 99, 235, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.32);
            border-radius: 18px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
            color: #BFDBFE;
        }

        .insight-box {
            background: rgba(245, 158, 11, 0.13);
            border: 1px solid rgba(245, 158, 11, 0.30);
            border-radius: 18px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
            color: #FDE68A;
        }

        .badge {
            display: inline-block;
            padding: 0.28rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 780;
            border: 1px solid transparent;
            margin-right: 0.25rem;
        }

        .badge-low {
            color: #BBF7D0;
            background: rgba(34, 197, 94, 0.14);
            border-color: rgba(34, 197, 94, 0.30);
        }

        .badge-medium {
            color: #FDE68A;
            background: rgba(245, 158, 11, 0.16);
            border-color: rgba(245, 158, 11, 0.34);
        }

        .badge-high {
            color: #FECACA;
            background: rgba(239, 68, 68, 0.16);
            border-color: rgba(239, 68, 68, 0.34);
        }

        .badge-blue {
            color: #BFDBFE;
            background: rgba(59, 130, 246, 0.15);
            border-color: rgba(59, 130, 246, 0.32);
        }

        .sidebar-title {
            font-size: 1.05rem;
            font-weight: 850;
            color: #F8FAFC;
            margin-bottom: 0.2rem;
        }

        .sidebar-caption {
            color: #94A3B8;
            font-size: 0.85rem;
            line-height: 1.4;
            margin-bottom: 0.8rem;
        }

        .stDataFrame {
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            background: rgba(15, 23, 42, 0.92);
        }

        div[data-testid="stTabs"] button {
            color: #CBD5E1;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #FFFFFF;
        }

        .stSelectbox label,
        .stMultiSelect label,
        .stSlider label,
        .stRadio label,
        .stCheckbox label {
            color: #E5E7EB !important;
        }

        .stCaption, caption {
            color: #94A3B8 !important;
        }

        code {
            color: #DDE7F3 !important;
            background: rgba(15, 23, 42, 0.88) !important;
            border: 1px solid rgba(148, 163, 184, 0.18);
        }

        hr {
            border-color: var(--border);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HÀM TIỆN ÍCH
# ============================================================

def format_vnd(value: float | int | None) -> str:
    """Định dạng tiền VND ngắn gọn."""
    if value is None or pd.isna(value):
        return "0 VND"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f} tỷ VND"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f} triệu VND"

    return f"{value:,.0f} VND"


def parse_cycle_path(path_value: Any) -> list[str]:
    """Chuyển cột path thành danh sách tài khoản."""
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

    return [
        part.strip().strip("'\"[]")
        for part in text.split(",")
        if part.strip().strip("'\"[]")
    ]


def calculate_cycle_length(path_value: Any) -> int:
    """Tính số tài khoản khác nhau trong chu trình."""
    nodes = parse_cycle_path(path_value)
    return len(set(nodes))


def build_cycle_edges(nodes: list[str]) -> list[tuple[str, str]]:
    """Tạo danh sách giao dịch/cạnh từ path."""
    if len(nodes) < 2:
        return []

    normalized_nodes = nodes.copy()

    if normalized_nodes[0] != normalized_nodes[-1]:
        normalized_nodes.append(normalized_nodes[0])

    return [
        (normalized_nodes[i], normalized_nodes[i + 1])
        for i in range(len(normalized_nodes) - 1)
    ]


def normalize_risk_level(value: Any) -> str:
    """Chuẩn hóa risk_level sang tiếng Việt."""
    if pd.isna(value):
        return "Không xác định"

    text = str(value).strip().lower()

    if text in {"high", "cao"}:
        return "Cao"

    if text in {"medium", "trung bình", "trung binh"}:
        return "Trung bình"

    if text in {"low", "thấp", "thap"}:
        return "Thấp"

    return "Không xác định"


def derive_priority(risk_level: str, risk_score: float) -> str:
    """Gán độ ưu tiên xử lý."""
    if risk_level == "Cao" or risk_score >= 70:
        return "P1 - Ưu tiên cao"

    if risk_level == "Trung bình" or risk_score >= 40:
        return "P2 - Cần rà soát"

    return "P3 - Theo dõi"


def derive_status(risk_level: str, risk_score: float) -> str:
    """Gán trạng thái case mô phỏng."""
    if risk_level == "Cao" or risk_score >= 70:
        return "Cần chuyển cấp"

    if risk_level == "Trung bình" or risk_score >= 40:
        return "Đang rà soát"

    return "Đang theo dõi"


def derive_recommended_action(risk_level: str, risk_score: float) -> str:
    """Sinh hành động đề xuất."""
    if risk_level == "Cao" or risk_score >= 70:
        return "Ưu tiên rà soát ngay, kiểm tra chủ tài khoản, lịch sử giao dịch và các bên liên quan."

    if risk_level == "Trung bình" or risk_score >= 40:
        return "Giao cho người rà soát kiểm tra thời gian giao dịch, độ lặp lại và sự tương đồng số tiền."

    return "Tiếp tục theo dõi. Chưa cần chuyển cấp ngay nếu không có dấu hiệu lặp lại."


def badge(label: str) -> str:
    """Tạo badge HTML theo nội dung."""
    if label in {"Cao", "Cần chuyển cấp", "P1 - Ưu tiên cao"}:
        cls = "badge-high"
    elif label in {"Trung bình", "Đang rà soát", "P2 - Cần rà soát"}:
        cls = "badge-medium"
    elif label in {"Thấp", "Đang theo dõi", "P3 - Theo dõi"}:
        cls = "badge-low"
    else:
        cls = "badge-blue"

    return f'<span class="badge {cls}">{label}</span>'


def extract_all_accounts(df: pd.DataFrame) -> list[str]:
    """Lấy danh sách tài khoản xuất hiện trong dataframe."""
    accounts: set[str] = set()

    for path_value in df["path"].dropna():
        accounts.update(parse_cycle_path(path_value))

    return sorted(accounts)


def build_transaction_steps(edges: list[tuple[str, str]]) -> pd.DataFrame:
    """Chuyển cạnh thành bảng giao dịch dễ hiểu."""
    rows = []

    for index, (source, target) in enumerate(edges, start=1):
        rows.append(
            {
                "Giao dịch": f"Giao dịch {index}",
                "Tài khoản gửi": source,
                "Tài khoản nhận": target,
                "Luồng tiền": f"{source} → {target}",
            }
        )

    return pd.DataFrame(rows)


def filter_by_two_accounts(
    df: pd.DataFrame,
    account_a: str | None,
    account_b: str | None,
) -> pd.DataFrame:
    """Lọc các case có đồng thời 2 tài khoản được chọn."""
    if not account_a or not account_b or account_a == account_b:
        return df

    mask = df["path"].apply(
        lambda path_value: account_a in parse_cycle_path(path_value)
        and account_b in parse_cycle_path(path_value)
    )

    return df[mask].reset_index(drop=True)


def direct_edges_between_accounts(
    edges: list[tuple[str, str]],
    account_a: str | None,
    account_b: str | None,
) -> list[tuple[str, str]]:
    """Lấy giao dịch trực tiếp giữa 2 tài khoản nếu có."""
    if not account_a or not account_b or account_a == account_b:
        return []

    return [
        (source, target)
        for source, target in edges
        if {source, target} == {account_a, account_b}
    ]


def risk_label_with_icon(label: str) -> str:
    """Hiển thị mức rủi ro dễ đọc hơn trong bảng."""
    mapping = {
        "Cao": "🔴 Cao",
        "Trung bình": "🟠 Trung bình",
        "Thấp": "🟢 Thấp",
    }
    return mapping.get(label, f"⚪ {label}")


def priority_label_compact(label: str) -> str:
    """Rút gọn độ ưu tiên để bảng đỡ rối mắt."""
    mapping = {
        "P1 - Ưu tiên cao": "P1 · Ưu tiên cao",
        "P2 - Cần rà soát": "P2 · Cần rà soát",
        "P3 - Theo dõi": "P3 · Theo dõi",
    }
    return mapping.get(label, label)


def status_label_with_icon(label: str) -> str:
    """Hiển thị trạng thái với icon trực quan."""
    mapping = {
        "Đang theo dõi": "🟦 Đang theo dõi",
        "Đang rà soát": "🟨 Đang rà soát",
        "Cần chuyển cấp": "🟥 Cần chuyển cấp",
        "Đã đóng": "🟩 Đã đóng",
    }
    return mapping.get(label, label)


def shorten_action(text: str, max_len: int = 72) -> str:
    """Rút ngắn hành động đề xuất để bảng gọn hơn."""
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def explain_case(row: pd.Series) -> str:
    """Diễn giải case bằng ngôn ngữ dễ hiểu."""
    nodes = parse_cycle_path(row["path"])
    readable_path = " → ".join(nodes)
    cycle_length = int(row["cycle_length"])
    total_amount = format_vnd(row["total_amount"])
    duration = float(row["duration_minutes"])
    risk_score = float(row["risk_score"])
    risk_level = row["risk_level_vi"]

    return (
        f"Case này thể hiện dòng tiền đi theo đường: {readable_path}. "
        f"Chu trình có {cycle_length} tài khoản khác nhau, tổng giá trị luân chuyển là {total_amount}, "
        f"hoàn tất trong khoảng {duration:.0f} phút. Hệ thống đánh giá mức rủi ro {risk_level} "
        f"với điểm {risk_score:.1f}/100. Đây là cảnh báo cần rà soát, không phải kết luận rửa tiền."
    )


def style_table(row: pd.Series) -> list[str]:
    """Tô màu bảng theo mức rủi ro, phù hợp nền tối."""
    risk_level = row.get("Mức rủi ro", "Không xác định")

    if risk_level == "Cao":
        return [
            "background-color: rgba(239, 68, 68, 0.18); color: #FECACA; font-weight: 650;"
            for _ in row
        ]

    if risk_level == "Trung bình":
        return [
            "background-color: rgba(245, 158, 11, 0.18); color: #FDE68A; font-weight: 650;"
            for _ in row
        ]

    if risk_level == "Thấp":
        return [
            "background-color: rgba(34, 197, 94, 0.15); color: #BBF7D0; font-weight: 650;"
            for _ in row
        ]

    return [
        "background-color: rgba(15, 23, 42, 0.92); color: #E5E7EB;"
        for _ in row
    ]


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(show_spinner="Đang đọc dữ liệu cảnh báo...")
def load_data(csv_path: str) -> pd.DataFrame:
    """Đọc file suspicious_cycles.csv và chuẩn hóa dữ liệu."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(csv_path)

    df = pd.read_csv(path)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError("Thiếu cột bắt buộc: " + ", ".join(missing_columns))

    df["cycle_id"] = df["cycle_id"].astype(str)
    df["path"] = df["path"].astype(str)
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce").fillna(0)
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).clip(0, 100)

    df["risk_level_vi"] = df["risk_level"].apply(normalize_risk_level)
    df["cycle_length"] = df["path"].apply(calculate_cycle_length)
    df["priority"] = df.apply(
        lambda row: derive_priority(row["risk_level_vi"], float(row["risk_score"])),
        axis=1,
    )
    df["case_status"] = df.apply(
        lambda row: derive_status(row["risk_level_vi"], float(row["risk_score"])),
        axis=1,
    )
    df["recommended_action"] = df.apply(
        lambda row: derive_recommended_action(row["risk_level_vi"], float(row["risk_score"])),
        axis=1,
    )

    df["case_explanation"] = df.apply(explain_case, axis=1)

    priority_order = {
        "P1 - Ưu tiên cao": 1,
        "P2 - Cần rà soát": 2,
        "P3 - Theo dõi": 3,
    }

    df["_priority_order"] = df["priority"].map(priority_order).fillna(9)

    df = df.sort_values(
        by=["_priority_order", "risk_score", "total_amount"],
        ascending=[True, False, False],
    ).drop(columns=["_priority_order"]).reset_index(drop=True)

    return df


# ============================================================
# RENDER COMPONENTS
# ============================================================

def render_header(df: pd.DataFrame) -> None:
    """Header chính."""
    total_cases = len(df)
    two_account_cases = int((df["cycle_length"] == 2).sum())
    three_account_cases = int((df["cycle_length"] == 3).sum())

    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-header-title">Bàn làm việc chuyên viên rà soát AML</div>
            <div class="app-header-caption">
                Hệ thống biểu diễn giao dịch dưới dạng đồ thị, phát hiện các vòng dòng tiền khép kín
                và hỗ trợ rà soát theo mức rủi ro. Tổng dữ liệu hiện có: <b>{total_cases}</b> case,
                gồm <b>{two_account_cases}</b> vòng 2 tài khoản và <b>{three_account_cases}</b> vòng 3 tài khoản.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Sidebar filter."""
    st.sidebar.markdown('<div class="sidebar-title">Bộ lọc dữ liệu</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="sidebar-caption">Điều chỉnh các bộ lọc để xem nhóm cảnh báo phù hợp.</div>',
        unsafe_allow_html=True,
    )

    amount_min = st.sidebar.slider(
        "Số tiền tối thiểu",
        min_value=0.0,
        max_value=max(float(df["total_amount"].max()), 1.0),
        value=0.0,
        step=max(float(df["total_amount"].max()) / 100, 1.0),
        format="%.0f",
    )

    score_min = st.sidebar.slider(
        "Điểm rủi ro tối thiểu",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0,
    )

    min_len = int(df["cycle_length"].min())
    max_len = int(df["cycle_length"].max())

    if min_len == max_len:
        length_range = (min_len, max_len)
        st.sidebar.info(f"Dữ liệu hiện chỉ có chu trình độ dài {min_len}.")
    else:
        length_range = st.sidebar.slider(
            "Độ dài chu trình",
            min_value=min_len,
            max_value=max_len,
            value=(min_len, max_len),
            step=1,
        )

    risk_options = [risk for risk in RISK_ORDER if risk in set(df["risk_level_vi"])]
    selected_risks = st.sidebar.multiselect(
        "Mức rủi ro",
        options=risk_options,
        default=risk_options,
    )

    priority_options = sorted(df["priority"].unique().tolist())
    selected_priorities = st.sidebar.multiselect(
        "Độ ưu tiên",
        options=priority_options,
        default=priority_options,
    )

    status_options = sorted(df["case_status"].unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "Trạng thái",
        options=status_options,
        default=status_options,
    )

    if st.sidebar.button("Làm mới dashboard"):
        st.cache_data.clear()
        st.rerun()

    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df["total_amount"] >= amount_min]
    filtered_df = filtered_df[filtered_df["risk_score"] >= score_min]
    filtered_df = filtered_df[filtered_df["cycle_length"].between(length_range[0], length_range[1])]

    if selected_risks:
        filtered_df = filtered_df[filtered_df["risk_level_vi"].isin(selected_risks)]

    if selected_priorities:
        filtered_df = filtered_df[filtered_df["priority"].isin(selected_priorities)]

    if selected_statuses:
        filtered_df = filtered_df[filtered_df["case_status"].isin(selected_statuses)]

    filter_state = {
        "amount_min": amount_min,
        "score_min": score_min,
        "length_range": length_range,
        "selected_risks": selected_risks,
        "selected_priorities": selected_priorities,
        "selected_statuses": selected_statuses,
    }

    return filtered_df.reset_index(drop=True), filter_state



def render_analyst_context() -> None:
    """Dashboard cố định cho vai trò Chuyên viên rà soát."""
    st.markdown(
        """
        <div class="analyst-panel">
            <div class="analyst-tag">Vai trò cố định: Chuyên viên rà soát</div>
            <div class="analyst-title">Bàn làm việc rà soát case giao dịch đáng ngờ</div>
            <div class="analyst-caption">
                Dashboard này tập trung vào công việc của chuyên viên: xem hàng đợi case,
                chọn case cần kiểm tra, phân tích đường đi dòng tiền, xem các giao dịch tạo thành chu trình
                và dùng checklist để rà soát. Cảnh báo chỉ là dấu hiệu hỗ trợ điều tra,
                không phải kết luận rửa tiền.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_phase2_notes() -> None:
    """Phần giải thích Phase 2 để xử lý góp ý Big Data và lưu graph."""
    st.markdown('<div class="section-title">Phase 2 - Hướng nâng cấp xử lý góp ý</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-card">
            <b>1. PySpark cho dữ liệu lớn</b><br>
            NetworkX phù hợp cho MVP và graph nhỏ-vừa. Khi dữ liệu tăng lên lớn hơn,
            hệ thống nên nâng cấp sang PySpark hoặc GraphFrames để xử lý phân tán.
        </div>
        <div class="section-card">
            <b>2. Neo4j cho lưu trữ graph</b><br>
            Ở MVP, graph được dựng tạm từ CSV. Phase 2 đề xuất Neo4j để lưu tài khoản và giao dịch
            theo mô hình graph tự nhiên, hỗ trợ truy vấn quan hệ và trực quan hóa tốt hơn.
        </div>
        <div class="section-card">
            <b>3. Dashboard theo vai trò xử lý</b><br>
            Dashboard được tập trung vào vai trò Chuyên viên rà soát để bám sát người trực tiếp xử lý cảnh báo AML.
            Giao diện hỗ trợ quy trình xem hàng đợi case, chọn case, điều tra dòng tiền và ghi nhận định hướng xử lý.
        </div>
        <div class="section-card">
            <b>4. Backend và case management</b><br>
            Phase 2 có thể bổ sung FastAPI làm API backend và database riêng để lưu người phụ trách,
            trạng thái case, lịch sử xử lý và audit log.
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_overview(df: pd.DataFrame) -> None:
    """Tab tổng quan."""
    st.markdown(
        """
        <div class="explain-box">
            <b>Cách đọc dashboard:</b><br>
            Mỗi tài khoản là một điểm trong đồ thị. Mỗi giao dịch là một mũi tên có hướng.
            Một vòng giao dịch xảy ra khi dòng tiền đi qua các tài khoản rồi quay lại điểm ban đầu.
            Ví dụ A → B → A là vòng 2 tài khoản, còn A → B → C → A là vòng 3 tài khoản.
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_cases = len(df)
    total_amount = df["total_amount"].sum() if not df.empty else 0
    avg_score = df["risk_score"].mean() if not df.empty else 0
    affected_accounts = len(extract_all_accounts(df)) if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Số vòng giao dịch", f"{total_cases:,}")
    col2.metric("Tổng dòng tiền", format_vnd(total_amount))
    col3.metric("Điểm rủi ro trung bình", f"{avg_score:.1f}/100")
    col4.metric("Số tài khoản liên quan", f"{affected_accounts:,}")

    high_count = int((df["risk_level_vi"] == "Cao").sum()) if not df.empty else 0
    medium_count = int((df["risk_level_vi"] == "Trung bình").sum()) if not df.empty else 0
    low_count = int((df["risk_level_vi"] == "Thấp").sum()) if not df.empty else 0
    two_count = int((df["cycle_length"] == 2).sum()) if not df.empty else 0
    three_count = int((df["cycle_length"] == 3).sum()) if not df.empty else 0

    st.markdown(
        f"""
        <div class="insight-box">
            <b>Kết luận nhanh:</b><br>
            Dashboard đang hiển thị <b>{total_cases}</b> vòng giao dịch đáng ngờ,
            gồm <b>{two_count}</b> vòng 2 tài khoản và <b>{three_count}</b> vòng 3 tài khoản.
            Mức rủi ro gồm <b>{high_count}</b> cao, <b>{medium_count}</b> trung bình
            và <b>{low_count}</b> thấp.
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="section-title">Phân bố mức rủi ro</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("Không có dữ liệu để hiển thị.")
        else:
            risk_counts = (
                df["risk_level_vi"]
                .value_counts()
                .reindex(RISK_ORDER)
                .fillna(0)
                .astype(int)
                .reset_index()
            )
            risk_counts.columns = ["Mức rủi ro", "Số case"]

            fig = px.bar(
                risk_counts,
                x="Mức rủi ro",
                y="Số case",
                text="Số case",
                color="Mức rủi ro",
                color_discrete_map=RISK_COLOR_MAP,
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=340,
                template="plotly_dark",
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.25)",
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.markdown('<div class="section-title">Phân bố độ dài chu trình</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("Không có dữ liệu để hiển thị.")
        else:
            length_counts = (
                df["cycle_length"]
                .value_counts()
                .sort_index()
                .reset_index()
            )
            length_counts.columns = ["Số tài khoản trong vòng", "Số case"]

            fig = px.bar(
                length_counts,
                x="Số tài khoản trong vòng",
                y="Số case",
                text="Số case",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=340,
                template="plotly_dark",
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.25)",
            )
            st.plotly_chart(fig, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown('<div class="section-title">Tương quan số tiền và điểm rủi ro</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("Không có dữ liệu để hiển thị.")
        else:
            fig = px.scatter(
                df,
                x="total_amount",
                y="risk_score",
                size="cycle_length",
                color="risk_level_vi",
                hover_data=["cycle_id", "cycle_length", "priority", "case_status"],
                labels={
                    "total_amount": "Tổng tiền",
                    "risk_score": "Điểm rủi ro",
                    "risk_level_vi": "Mức rủi ro",
                    "cycle_length": "Độ dài chu trình",
                },
                color_discrete_map=RISK_COLOR_MAP,
            )
            fig.update_layout(
                height=360,
                template="plotly_dark",
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.25)",
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col4:
        st.markdown('<div class="section-title">Trạng thái xử lý case</div>', unsafe_allow_html=True)

        if df.empty:
            st.info("Không có dữ liệu để hiển thị.")
        else:
            status_counts = df["case_status"].value_counts().reset_index()
            status_counts.columns = ["Trạng thái", "Số case"]

            fig = px.pie(
                status_counts,
                names="Trạng thái",
                values="Số case",
                hole=0.55,
                color="Trạng thái",
                color_discrete_map=STATUS_COLOR_MAP,
            )
            fig.update_layout(
                height=360,
                template="plotly_dark",
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)


def render_case_table(df: pd.DataFrame) -> None:
    """Tab danh sách cảnh báo."""
    st.markdown('<div class="section-title">Danh sách cảnh báo</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Bảng này hiển thị các vòng giao dịch đáng ngờ sau khi áp dụng bộ lọc.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="soft-card">
            <b>Gợi ý cách đọc bảng:</b>
            🟢 Thấp · 🟠 Trung bình · 🔴 Cao &nbsp;&nbsp;|&nbsp;&nbsp;
            P1 là ưu tiên cao nhất, P3 là mức theo dõi.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Không có case nào phù hợp với bộ lọc hiện tại.")
        return

    display_df = df[
        [
            "cycle_id",
            "priority",
            "case_status",
            "risk_level_vi",
            "risk_score",
            "cycle_length",
            "total_amount",
            "duration_minutes",
            "recommended_action",
        ]
    ].copy()

    display_df["priority"] = display_df["priority"].apply(priority_label_compact)
    display_df["case_status"] = display_df["case_status"].apply(status_label_with_icon)
    display_df["risk_level_vi"] = display_df["risk_level_vi"].apply(risk_label_with_icon)
    display_df["risk_score"] = display_df["risk_score"].map(lambda x: f"{x:.1f}")
    display_df["total_amount"] = display_df["total_amount"].map(format_vnd)
    display_df["duration_minutes"] = display_df["duration_minutes"].map(lambda x: f"{x:,.0f} phút")
    display_df["recommended_action"] = display_df["recommended_action"].apply(shorten_action)

    display_df = display_df.rename(
        columns={
            "cycle_id": "Mã case",
            "priority": "Độ ưu tiên",
            "case_status": "Trạng thái",
            "risk_level_vi": "Mức rủi ro",
            "risk_score": "Điểm rủi ro",
            "cycle_length": "Số tài khoản",
            "total_amount": "Tổng tiền",
            "duration_minutes": "Thời gian hoàn tất",
            "recommended_action": "Hành động đề xuất",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "Mã case": st.column_config.TextColumn(width="small"),
            "Độ ưu tiên": st.column_config.TextColumn(width="medium"),
            "Trạng thái": st.column_config.TextColumn(width="medium"),
            "Mức rủi ro": st.column_config.TextColumn(width="small"),
            "Điểm rủi ro": st.column_config.TextColumn(width="small"),
            "Số tài khoản": st.column_config.NumberColumn(width="small"),
            "Tổng tiền": st.column_config.TextColumn(width="small"),
            "Thời gian hoàn tất": st.column_config.TextColumn(width="small"),
            "Hành động đề xuất": st.column_config.TextColumn(width="large"),
        },
    )

    with st.expander("Xem diễn giải chi tiết từng case"):
        detail_df = df[
            ["cycle_id", "path", "case_explanation", "recommended_action"]
        ].copy()
        detail_df = detail_df.rename(
            columns={
                "cycle_id": "Mã case",
                "path": "Đường đi",
                "case_explanation": "Diễn giải",
                "recommended_action": "Khuyến nghị",
            }
        )
        st.dataframe(detail_df, use_container_width=True, hide_index=True, height=420)

    st.download_button(
        label="Tải danh sách case CSV",
        data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="suspicious_cycles_filtered.csv",
        mime="text/csv",
        type="primary",
    )


def render_plotly_graph(nodes: list[str], edges: list[tuple[str, str]]) -> None:
    """Vẽ graph bằng Plotly, tránh lỗi khối trắng của streamlit-agraph."""
    unique_nodes = list(dict.fromkeys(nodes))

    if not unique_nodes:
        st.info("Không có tài khoản để vẽ.")
        return

    positions = {}
    radius = 1.0

    for index, node in enumerate(unique_nodes):
        angle = 2 * math.pi * index / len(unique_nodes)
        positions[node] = {
            "x": radius * math.cos(angle),
            "y": radius * math.sin(angle),
        }

    edge_x = []
    edge_y = []
    annotations = []

    for source, target in edges:
        if source not in positions or target not in positions:
            continue

        x0, y0 = positions[source]["x"], positions[source]["y"]
        x1, y1 = positions[target]["x"], positions[target]["y"]

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
                arrowsize=1.2,
                arrowwidth=1.8,
                arrowcolor="#CBD5E1",
            )
        )

    node_x = [positions[node]["x"] for node in unique_nodes]
    node_y = [positions[node]["y"] for node in unique_nodes]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=2.5, color="#CBD5E1"),
            hoverinfo="none",
            name="Dòng tiền",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=unique_nodes,
            textposition="bottom center",
            marker=dict(
                size=36,
                color="#3B82F6",
                line=dict(width=2, color="#93C5FD"),
            ),
            hovertext=unique_nodes,
            hoverinfo="text",
            name="Tài khoản",
        )
    )

    fig.update_layout(
        height=500,
        template="plotly_dark",
        showlegend=False,
        annotations=annotations,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_flow_view(df: pd.DataFrame) -> None:
    """Tab xem dòng tiền."""
    st.markdown('<div class="section-title">Xem dòng tiền theo chu trình</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Có thể xem vòng 2 tài khoản, vòng 3 tài khoản hoặc lọc theo 2 tài khoản cụ thể.</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Không có dữ liệu để hiển thị.")
        return

    mode = st.radio(
        "Chế độ hiển thị",
        options=[
            "Hiển thị cả vòng 2 và 3 tài khoản",
            "Chỉ vòng 2 tài khoản",
            "Chỉ vòng 3 tài khoản",
            "Hiển thị tất cả",
        ],
        index=0,
        horizontal=True,
    )

    display_df = df.copy()

    if mode == "Hiển thị cả vòng 2 và 3 tài khoản":
        display_df = display_df[display_df["cycle_length"].isin([2, 3])]
    elif mode == "Chỉ vòng 2 tài khoản":
        display_df = display_df[display_df["cycle_length"] == 2]
    elif mode == "Chỉ vòng 3 tài khoản":
        display_df = display_df[display_df["cycle_length"] == 3]

    display_df = display_df.reset_index(drop=True)

    if display_df.empty:
        st.warning("Không có case phù hợp với chế độ đang chọn.")
        return

    all_accounts = extract_all_accounts(display_df)
    no_filter = "Không chọn"

    st.markdown("**Lọc theo 2 tài khoản cụ thể**")
    account_col1, account_col2 = st.columns(2)

    with account_col1:
        account_a = st.selectbox(
            "Tài khoản thứ nhất",
            options=[no_filter] + all_accounts,
            index=0,
        )

    with account_col2:
        account_b = st.selectbox(
            "Tài khoản thứ hai",
            options=[no_filter] + all_accounts,
            index=0,
        )

    account_a = None if account_a == no_filter else account_a
    account_b = None if account_b == no_filter else account_b

    if account_a and account_b and account_a == account_b:
        st.warning("Vui lòng chọn 2 tài khoản khác nhau.")
        return

    filtered_by_accounts = filter_by_two_accounts(display_df, account_a, account_b)

    if filtered_by_accounts.empty:
        st.warning("Không tìm thấy case nào chứa đồng thời 2 tài khoản đã chọn.")
        return

    case_options = [
        (
            f"{row.cycle_id} · {row.cycle_length} tài khoản · "
            f"{row.risk_level_vi} · điểm {row.risk_score:.1f} · {format_vnd(row.total_amount)}"
        )
        for row in filtered_by_accounts.itertuples()
    ]

    selected_case = st.selectbox("Chọn case để xem chi tiết", options=case_options)
    selected_index = case_options.index(selected_case)
    selected_row = filtered_by_accounts.iloc[selected_index]

    nodes = parse_cycle_path(selected_row["path"])
    edges = build_cycle_edges(nodes)

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">Case {selected_row["cycle_id"]}</div>
            <div style="margin-top:0.5rem;">
                {badge(selected_row["priority"])}
                {badge(selected_row["case_status"])}
                {badge(selected_row["risk_level_vi"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Số tài khoản", f"{selected_row['cycle_length']}")
    metric_col2.metric("Số giao dịch", f"{len(edges)}")
    metric_col3.metric("Tổng tiền", format_vnd(selected_row["total_amount"]))
    metric_col4.metric("Điểm rủi ro", f"{selected_row['risk_score']:.1f}/100")

    left_col, right_col = st.columns([1.35, 1])

    with left_col:
        st.markdown("**Đường đi dòng tiền**")
        st.code(" → ".join(nodes), language="text")

        transaction_df = build_transaction_steps(edges)
        st.markdown("**Các giao dịch tạo thành chu trình**")
        st.dataframe(
            transaction_df,
            use_container_width=True,
            hide_index=True,
            height=min(320, 105 + 46 * len(transaction_df)),
        )

        if account_a and account_b:
            direct_edges = direct_edges_between_accounts(edges, account_a, account_b)

            st.markdown("**Dòng tiền trực tiếp giữa 2 tài khoản đã chọn**")

            if direct_edges:
                st.dataframe(
                    build_transaction_steps(direct_edges),
                    use_container_width=True,
                    hide_index=True,
                    height=min(240, 105 + 46 * len(direct_edges)),
                )
            else:
                st.info(
                    "Case này có chứa cả 2 tài khoản đã chọn, nhưng hai tài khoản không giao dịch trực tiếp. "
                    "Dòng tiền đi qua tài khoản trung gian."
                )

        render_plotly_graph(nodes, edges)

    with right_col:
        st.markdown("**Diễn giải dễ hiểu**")
        st.write(selected_row["case_explanation"])

        st.markdown("**Hành động đề xuất**")
        st.write(selected_row["recommended_action"])

        st.markdown("**Checklist rà soát**")
        st.checkbox("Kiểm tra chủ sở hữu tài khoản", value=False)
        st.checkbox("Kiểm tra các giao dịch lặp lại", value=False)
        st.checkbox("Kiểm tra thời gian chuyển tiền", value=False)
        st.checkbox("Kiểm tra độ tương đồng của số tiền", value=False)
        st.checkbox("Chuyển cấp nếu mẫu giao dịch tiếp tục xuất hiện", value=False)


def render_model_notes(df: pd.DataFrame) -> None:
    """Tab giải thích hệ thống."""
    st.markdown('<div class="section-title">Giải thích hệ thống</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <b>1. Hệ thống phát hiện gì?</b><br>
            Hệ thống phát hiện các vòng giao dịch khép kín trong dữ liệu. Ví dụ A → B → A là vòng 2 tài khoản,
            còn A → B → C → A là vòng 3 tài khoản.
        </div>
        <div class="section-card">
            <b>2. Vì sao dùng đồ thị?</b><br>
            Vì giao dịch ngân hàng có dạng mạng lưới. Tài khoản là điểm, giao dịch là mũi tên.
            Đồ thị giúp nhìn thấy các mẫu luân chuyển tiền mà bảng dữ liệu thông thường khó thể hiện.
        </div>
        <div class="section-card">
            <b>3. Điểm rủi ro có ý nghĩa gì?</b><br>
            Điểm rủi ro dùng để ưu tiên rà soát. Điểm càng cao thì case càng nên được kiểm tra trước.
        </div>
        <div class="section-card">
            <b>4. Cách hiểu trạng thái</b><br>
            "Đang theo dõi" là case rủi ro thấp, chưa cần xử lý gấp nhưng vẫn được lưu lại để quan sát.
            "Đang rà soát" là case rủi ro trung bình, cần kiểm tra chi tiết hơn.
            "Cần chuyển cấp" là case rủi ro cao, cần ưu tiên xử lý.
        </div>
        <div class="section-card">
            <b>5. Giới hạn quan trọng</b><br>
            Dashboard không kết luận giao dịch là rửa tiền. Nó chỉ đánh dấu dấu hiệu đáng ngờ để hỗ trợ rà soát.
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_df = pd.DataFrame(
        [
            {"Thông tin": "Tổng số case", "Giá trị": len(df)},
            {"Thông tin": "Vòng 2 tài khoản", "Giá trị": int((df["cycle_length"] == 2).sum()) if not df.empty else 0},
            {"Thông tin": "Vòng 3 tài khoản", "Giá trị": int((df["cycle_length"] == 3).sum()) if not df.empty else 0},
            {"Thông tin": "Tổng dòng tiền", "Giá trị": format_vnd(df["total_amount"].sum() if not df.empty else 0)},
        ]
    )

    st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Hàm chạy dashboard."""
    try:
        df = load_data(str(DATA_PATH))
    except FileNotFoundError:
        st.error(
            "Không tìm thấy file `data/output/suspicious_cycles.csv`. "
            "Hãy chạy pipeline trước: `python src/main.py --step detect --min-cycle-length 2`."
        )
        st.stop()
    except ValueError as error:
        st.error(str(error))
        st.stop()
    except Exception as error:
        st.error("Dashboard không đọc được dữ liệu đầu vào.")
        st.exception(error)
        st.stop()

    if df.empty:
        st.warning("File kết quả đang rỗng. Pipeline có thể chưa phát hiện được chu trình nào.")
        st.stop()

    render_header(df)
    render_analyst_context()
    filtered_df, _ = render_sidebar(df)

    case_tab, flow_tab, overview_tab, notes_tab = st.tabs(
        [
            "Hàng đợi rà soát",
            "Điều tra dòng tiền",
            "Tổng quan hỗ trợ",
            "Ghi chú hệ thống",
        ]
    )

    with case_tab:
        render_case_table(filtered_df)

    with flow_tab:
        render_flow_view(filtered_df)

    with overview_tab:
        render_overview(filtered_df)

    with notes_tab:
        render_model_notes(filtered_df)
        render_phase2_notes()


if __name__ == "__main__":
    main()
