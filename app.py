import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sports Analytics Programs",
    page_icon="📊",
    layout="wide",
)

# ── Load data ────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("ncaa_programs.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Rename long columns to shorter keys
    df = df.rename(columns={
        "Sports Analytics or Sports Science": "Focus",
        "Program type (dropdown)": "Program Type",
        "Private/Public": "Institution Type",
        "Undergrad program": "Has UG",
        "Graduate program": "Has Grad",
        "Degree of Experiental Learning (0-5)": "Experiential Learning",
        "Technical vs Applied (0-5)": "Technical vs Applied",
        "Department/College housed in (ex: Business, Education, Economics, etc)": "Department",
        "Sports analytics focus (business, tech, human phys, etc)": "Analytics Focus",
        "External partners (Athletics, community)": "External Partners",
        "Required internship or capstone (if applicable)": "Internship/Capstone",
        "Credit Hours Undergraduate  (or N/A)": "UG Credit Hours",
        "Credit Hours Graduate (or N/A)": "Grad Credit Hours",
        "Technical Aspects: (Computer Science, Data Engineering, Algorithms, Machine Learning, Other, N/A)": "Technical Aspects",
        "Applied Aspects: (Marketing, Sports Management, Finance, Kinesiology, Human Physology, Other, N/A": "Applied Aspects",
    })

    # Drop rows with no university name
    df = df.dropna(subset=["University Name"])

    # Normalize text fields
    df["Focus"] = df["Focus"].str.strip().str.title()
    df["Focus"] = df["Focus"].replace({"2": None})
    df["Institution Type"] = df["Institution Type"].str.strip()
    df["Program Type"] = df["Program Type"].str.strip()
    df["Has UG"] = df["Has UG"].str.strip()
    df["Has Grad"] = df["Has Grad"].str.strip()
    df["State"] = df["State"].str.strip()

    # Parse tuition to numeric
    for col in ["In-State Tuition", "Out-of-State Tuition"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[\$,\s]", "", regex=True)
            .replace({"N/A": None, "nan": None, "": None})
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Numeric scales
    df["Experiential Learning"] = pd.to_numeric(df["Experiential Learning"], errors="coerce")
    df["Technical vs Applied"] = pd.to_numeric(df["Technical vs Applied"], errors="coerce")
    df["Year Established"] = pd.to_numeric(df["Year Established"], errors="coerce")

    # Credit hour columns
    ch_cols = [
        "Credit hours in business",
        "Credit hours in human physiology",
        "Credit hours in kinesiology",
        "Credit hours in sports management",
        "Credit hours in computer science",
        "Credit hours in data analytics",
    ]
    for c in ch_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df, ch_cols


df_all, CH_COLS = load_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🏟️ Filter Programs")

    # Focus filter
    focus_options = sorted(df_all["Focus"].dropna().unique())
    focus_sel = st.multiselect("Focus", focus_options, default=focus_options)

    # Institution type
    inst_options = sorted(df_all["Institution Type"].dropna().unique())
    inst_sel = st.multiselect("Institution Type", inst_options, default=inst_options)

    # Program type
    pt_options = sorted(df_all["Program Type"].dropna().unique())
    pt_sel = st.multiselect("Program Type", pt_options, default=pt_options)

    # Level (UG / Grad)
    level_sel = st.multiselect(
        "Degree Level",
        ["Undergraduate", "Graduate"],
        default=["Undergraduate", "Graduate"],
    )

    # State
    state_options = sorted(df_all["State"].dropna().unique())
    state_sel = st.multiselect("State", state_options, default=state_options)

    st.divider()

    # Scales
    exp_range = st.slider("Experiential Learning (0–5)", 0, 5, (0, 5))
    tech_range = st.slider("Technical vs Applied (0–5)", 0, 5, (0, 5))

# ── Apply filters ────────────────────────────────────────────────────────────

df = df_all.copy()
if focus_sel:
    df = df[df["Focus"].isin(focus_sel) | df["Focus"].isna()]
    df = df[df["Focus"].isin(focus_sel)]
if inst_sel:
    df = df[df["Institution Type"].isin(inst_sel)]
if pt_sel:
    df = df[df["Program Type"].isin(pt_sel)]
if state_sel:
    df = df[df["State"].isin(state_sel)]

# Level filter
if "Undergraduate" in level_sel and "Graduate" not in level_sel:
    df = df[df["Has UG"] == "Yes"]
elif "Graduate" in level_sel and "Undergraduate" not in level_sel:
    df = df[df["Has Grad"] == "Yes"]

# Scale filters
df = df[
    (df["Experiential Learning"].isna() | df["Experiential Learning"].between(exp_range[0], exp_range[1]))
    & (df["Technical vs Applied"].isna() | df["Technical vs Applied"].between(tech_range[0], tech_range[1]))
]

# ── Header ───────────────────────────────────────────────────────────────────

st.title("Sports Analytics & Science Programs")
st.caption(f"Showing {len(df)} of {len(df_all)} programs")

# ── KPI row ──────────────────────────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Programs", len(df))
k2.metric("States", df["State"].nunique())
k3.metric("With UG", (df["Has UG"] == "Yes").sum())
k4.metric("With Grad", (df["Has Grad"] == "Yes").sum())
k5.metric("Avg Year Est.", int(df["Year Established"].dropna().mean()) if df["Year Established"].notna().any() else "—")

st.divider()

# ── Row 1: Map + Program type breakdown ─────────────────────────────────────

col_map, col_type = st.columns([2, 1])

with col_map:
    st.subheader("Programs by State")
    state_counts = df.groupby("State").size().reset_index(name="count")
    fig_map = px.choropleth(
        state_counts,
        locations="State",
        locationmode="USA-states",
        color="count",
        scope="usa",
        color_continuous_scale="Blues",
        labels={"count": "Programs"},
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig_map, use_container_width=True)

with col_type:
    st.subheader("By Program Type")
    pt_counts = df["Program Type"].value_counts().reset_index()
    pt_counts.columns = ["Type", "Count"]
    fig_pt = px.bar(pt_counts, x="Count", y="Type", orientation="h", color="Count",
                    color_continuous_scale="Blues")
    fig_pt.update_layout(showlegend=False, coloraxis_showscale=False,
                         margin=dict(l=0, r=0, t=10, b=0), height=350,
                         yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_pt, use_container_width=True)

# ── Row 2: Technical vs Applied scatter ─────────────────────────────────────

st.subheader("Technical vs. Applied Orientation")
scatter_df = df.dropna(subset=["Technical vs Applied", "Experiential Learning"])

if not scatter_df.empty:
    fig_scatter = px.scatter(
        scatter_df,
        x="Technical vs Applied",
        y="Experiential Learning",
        color="Institution Type",
        symbol="Focus",
        hover_name="University Name",
        hover_data={
            "Program Type": True,
            "State": True,
            "Technical vs Applied": True,
            "Experiential Learning": True,
        },
        labels={
            "Technical vs Applied": "← Applied (0)  —  Technical (5) →",
            "Experiential Learning": "Experiential Learning (0–5)",
        },
        height=420,
    )
    fig_scatter.update_traces(marker=dict(size=12))
    fig_scatter.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No programs with both scale values in current filter.")

# ── Row 3: Credit hours breakdown + Tuition ─────────────────────────────────

col_ch, col_tuit = st.columns([3, 2])

with col_ch:
    st.subheader("Credit Hours by Subject Area")
    ch_labels = {
        "Credit hours in business": "Business",
        "Credit hours in human physiology": "Human Physiology",
        "Credit hours in kinesiology": "Kinesiology",
        "Credit hours in sports management": "Sports Management",
        "Credit hours in computer science": "Computer Science",
        "Credit hours in data analytics": "Data Analytics",
    }
    ch_totals = df[CH_COLS].sum().rename(ch_labels)
    ch_totals = ch_totals[ch_totals > 0].sort_values(ascending=True)
    if not ch_totals.empty:
        fig_ch = px.bar(
            ch_totals.reset_index(),
            x=0,
            y="index",
            orientation="h",
            labels={"index": "", 0: "Total Credit Hours (all programs)"},
            color=0,
            color_continuous_scale="Teal",
        )
        fig_ch.update_layout(showlegend=False, coloraxis_showscale=False,
                             margin=dict(l=0, r=0, t=10, b=0), height=320)
        st.plotly_chart(fig_ch, use_container_width=True)
    else:
        st.info("No credit hour data in current filter.")

with col_tuit:
    st.subheader("Tuition Comparison")
    tuit_df = df[["University Name", "In-State Tuition", "Out-of-State Tuition", "Institution Type"]].dropna(
        subset=["In-State Tuition", "Out-of-State Tuition"]
    ).sort_values("In-State Tuition")
    if not tuit_df.empty:
        fig_tuit = go.Figure()
        fig_tuit.add_trace(go.Bar(
            name="In-State",
            x=tuit_df["University Name"],
            y=tuit_df["In-State Tuition"],
            marker_color="#1f77b4",
        ))
        fig_tuit.add_trace(go.Bar(
            name="Out-of-State",
            x=tuit_df["University Name"],
            y=tuit_df["Out-of-State Tuition"],
            marker_color="#aec7e8",
        ))
        fig_tuit.update_layout(
            barmode="group",
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(tickprefix="$", tickformat=",.0f"),
            margin=dict(l=0, r=0, t=10, b=80),
            height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_tuit, use_container_width=True)
    else:
        st.info("No tuition data in current filter.")

# ── Row 4: Year established histogram ───────────────────────────────────────

year_df = df.dropna(subset=["Year Established"])
if not year_df.empty:
    st.subheader("When Programs Were Established")
    fig_year = px.histogram(
        year_df,
        x="Year Established",
        nbins=20,
        color="Program Type",
        labels={"Year Established": "Year"},
        height=300,
    )
    fig_year.update_layout(margin=dict(l=0, r=0, t=10, b=0), bargap=0.1)
    st.plotly_chart(fig_year, use_container_width=True)

# ── Program detail table ─────────────────────────────────────────────────────

st.divider()
st.subheader("Program Detail Table")

display_cols = [
    "University Name", "State", "Institution Type", "Program Type",
    "Focus", "Has UG", "Has Grad",
    "Technical vs Applied", "Experiential Learning",
    "In-State Tuition", "Department", "Analytics Focus",
    "External Partners", "Internship/Capstone",
]
display_cols = [c for c in display_cols if c in df.columns]

st.dataframe(
    df[display_cols].reset_index(drop=True),
    use_container_width=True,
    height=400,
    column_config={
        "In-State Tuition": st.column_config.NumberColumn(format="$%,.0f"),
        "Technical vs Applied": st.column_config.NumberColumn(format="%.0f / 5"),
        "Experiential Learning": st.column_config.NumberColumn(format="%.0f / 5"),
    },
)

# ── Program detail expander ──────────────────────────────────────────────────

st.divider()
st.subheader("Program Deep Dive")

selected_uni = st.selectbox(
    "Select a program to view details",
    options=sorted(df["University Name"].unique()),
)

row = df[df["University Name"] == selected_uni].iloc[0]

d1, d2, d3 = st.columns(3)
d1.metric("Program Type", row.get("Program Type", "—") or "—")
d2.metric("Technical vs Applied", f"{int(row['Technical vs Applied'])}/5" if pd.notna(row.get("Technical vs Applied")) else "—")
d3.metric("Experiential Learning", f"{int(row['Experiential Learning'])}/5" if pd.notna(row.get("Experiential Learning")) else "—")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"**Program Name:** {row.get('Program Name', '—')}")
    st.markdown(f"**Department:** {row.get('Department', '—')}")
    st.markdown(f"**Analytics Focus:** {row.get('Analytics Focus', '—')}")
    st.markdown(f"**Year Established:** {int(row['Year Established']) if pd.notna(row.get('Year Established')) else '—'}")
    st.markdown(f"**External Partners:** {row.get('External Partners', '—')}")
    st.markdown(f"**Internship/Capstone:** {row.get('Internship/Capstone', '—')}")
with col_b:
    st.markdown(f"**Technical Aspects:** {row.get('Technical Aspects', '—')}")
    st.markdown(f"**Applied Aspects:** {row.get('Applied Aspects', '—')}")
    if pd.notna(row.get("In-State Tuition")):
        st.markdown(f"**In-State Tuition:** ${row['In-State Tuition']:,.0f}")
    if pd.notna(row.get("Out-of-State Tuition")):
        st.markdown(f"**Out-of-State Tuition:** ${row['Out-of-State Tuition']:,.0f}")

if pd.notna(row.get("Mission Statement")):
    with st.expander("Mission Statement"):
        st.write(row["Mission Statement"])
if pd.notna(row.get("Problem They're solving")):
    with st.expander("Problem They're Solving"):
        st.write(row["Problem They're solving"])

# Credit hours breakdown for this program
ch_row = {ch_labels.get(c, c): row[c] for c in CH_COLS if pd.notna(row.get(c)) and row[c] > 0}
if ch_row:
    with st.expander("Credit Hour Breakdown"):
        ch_series = pd.Series(ch_row).sort_values(ascending=False)
        fig_indiv = px.bar(ch_series.reset_index(), x="index", y=0,
                           labels={"index": "Subject", 0: "Credit Hours"},
                           color=0, color_continuous_scale="Blues")
        fig_indiv.update_layout(showlegend=False, coloraxis_showscale=False,
                                margin=dict(l=0, r=0, t=10, b=0), height=250)
        st.plotly_chart(fig_indiv, use_container_width=True)
