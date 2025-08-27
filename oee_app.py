import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ===== Page Config =====
st.set_page_config(page_title="Ceramic OEE Dashboard", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://images.unsplash.com/photo-1605120158860-c4a6f8456cf0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .st-bk {
        background-color: rgba(255,255,255,0.85) !important;
        padding:10px;
        border-radius:10px;
    }
    </style>
    """, unsafe_allow_html=True
)
st.title("🏭 Ceramic Production OEE Dashboard – PAY Method")

# ===== Steps =====
steps = [
    "Step 1: Batching", "Step 2: Mixing & Grinding", "Step 3: Colour Mixing",
    "Step 4: Spray Drying", "Step 5: Creating the Tile", "Step 6: Drying",
    "Step 7: Print & Glaze", "Step 8: Firing", "Step 9: Polishing & Squaring",
    "Step 10: Selection & Packing"
]

# ===== Initialize Data =====
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame({
        'Step': steps,
        'PlannedRunTime':[480]*10,
        'ActualRunTime':[450,430,470,460,440,430,450,470,460,480],
        'IdealOutput':[1000]*10,
        'ActualOutput':[950,900,970,940,960,930,950,970,960,980],
        'TotalOutput':[960,920,980,950,970,940,960,980,970,990],
        'GoodOutput':[940,880,960,930,950,920,940,960,950,980],
        'VA':[200,180,190,210,220,200,205,215,210,225],
        'NVA':[50,60,45,55,50,48,52,55,50,60],
        'NNVA':[20,30,25,22,20,25,23,22,21,25]
    })
data = st.session_state['data']

# ===== Sidebar Inputs =====
st.sidebar.header("Input Data per Step")
selected_step = st.sidebar.selectbox("Select Step", steps)
step_idx = data.index[data['Step']==selected_step][0]

with st.sidebar.expander("Run Time (Production Dept)"):
    data.loc[step_idx,'PlannedRunTime'] = st.number_input("Planned Run Time (min)", min_value=1, value=int(data.loc[step_idx,'PlannedRunTime']))
    data.loc[step_idx,'ActualRunTime'] = st.number_input("Actual Run Time (min)", min_value=0, value=int(data.loc[step_idx,'ActualRunTime']))

with st.sidebar.expander("Output / Yield (QC Dept)"):
    data.loc[step_idx,'IdealOutput'] = st.number_input("Ideal Output", min_value=1, value=int(data.loc[step_idx,'IdealOutput']))
    data.loc[step_idx,'ActualOutput'] = st.number_input("Actual Output", min_value=0, value=int(data.loc[step_idx,'ActualOutput']))
    data.loc[step_idx,'TotalOutput'] = st.number_input("Total Output", min_value=1, value=int(data.loc[step_idx,'TotalOutput']))
    data.loc[step_idx,'GoodOutput'] = st.number_input("Good Output", min_value=0, value=int(data.loc[step_idx,'GoodOutput']))

with st.sidebar.expander("Value Added Analysis (Engineering)"):
    data.loc[step_idx,'VA'] = st.number_input("VA (min)", min_value=0, value=int(data.loc[step_idx,'VA']))
    data.loc[step_idx,'NVA'] = st.number_input("NVA (min)", min_value=0, value=int(data.loc[step_idx,'NVA']))
    data.loc[step_idx,'NNVA'] = st.number_input("NNVA (min)", min_value=0, value=int(data.loc[step_idx,'NNVA']))

# ===== Calculate OEE =====
data['Availability'] = data['ActualRunTime']/data['PlannedRunTime']*100
data['Performance'] = data['ActualOutput']/data['IdealOutput']*100
data['Quality'] = data['GoodOutput']/data['TotalOutput']*100
data['OEE'] = data['Availability']*data['Performance']*data['Quality']/10000

# ===== KPI Cards =====
st.subheader("Overall KPIs", anchor=None)
avg_avail = data['Availability'].mean()
avg_perf = data['Performance'].mean()
avg_quality = data['Quality'].mean()
avg_oee = data['OEE'].mean()
k1,k2,k3,k4 = st.columns(4)
k1.metric("Avg Availability", f"{avg_avail:.2f}%")
k2.metric("Avg Performance", f"{avg_perf:.2f}%")
k3.metric("Avg Quality", f"{avg_quality:.2f}%")
k4.metric("Avg OEE", f"{avg_oee:.2f}%", delta=f"{avg_oee-85:.2f}% vs Target")

# ===== Gauges =====
col1,col2,col3 = st.columns([2,2,2])
with col1:
    fig_total_oee = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_oee,
        delta={'reference':85,'position':'top','increasing':{'color':'green'},'decreasing':{'color':'red'}},
        title={'text':"Total OEE (%)"},
        gauge={'axis':{'range':[0,100]},
               'bar':{'color':'blue'},
               'steps':[{'range':[0,70],'color':'red'},
                        {'range':[70,85],'color':'orange'},
                        {'range':[85,100],'color':'green'}]}
    ))
    st.plotly_chart(fig_total_oee,use_container_width=True,height=200)

with col2:
    fig_avail = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data.loc[step_idx,'Availability'],
        title={'text':"Availability (%)"},
        gauge={'axis':{'range':[0,100]},'bar':{'color':'green'}}
    ))
    st.plotly_chart(fig_avail,use_container_width=True,height=200)

with col3:
    fig_perf = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data.loc[step_idx,'Performance'],
        title={'text':"Performance (%)"},
        gauge={'axis':{'range':[0,100]},'bar':{'color':'orange'}}
    ))
    st.plotly_chart(fig_perf,use_container_width=True,height=200)

# ===== Pie + VA/NVA/NNVA =====
col1,col2 = st.columns(2)
with col1:
    fig_quality = go.Figure(go.Pie(
        values=[data.loc[step_idx,'Quality'],100-data.loc[step_idx,'Quality']],
        labels=['Good','Reject'],
        hole=0.4
    ))
    fig_quality.update_layout(title_text=f"Product Quality - {selected_step}")
    st.plotly_chart(fig_quality,use_container_width=True,height=250)

with col2:
    fig_va = go.Figure(data=[
        go.Bar(name='VA',x=data['Step'],y=data['VA'],text=data['VA'],textposition='auto'),
        go.Bar(name='NVA',x=data['Step'],y=data['NVA'],text=data['NVA'],textposition='auto'),
        go.Bar(name='NNVA',x=data['Step'],y=data['NNVA'],text=data['NNVA'],textposition='auto')
    ])
    fig_va.update_layout(barmode='stack',yaxis_title="Minutes",title_text="Value-Added Analysis per Step")
    st.plotly_chart(fig_va,use_container_width=True,height=250)

# ===== Performance Table =====
st.subheader("📋 Step Performance Table")
def color_oee(val):
    if val<70:
        return 'background-color:red;color:white'
    elif val<85:
        return 'background-color:orange;color:black'
    else:
        return 'background-color:green;color:white'
st.dataframe(data.style.applymap(color_oee, subset=['OEE']))
