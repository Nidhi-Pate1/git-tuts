import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Battery Simulation Dashboard", layout="wide")

# --- Style ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f4ff;
        color: #1c1c1c;
            [theme]
        base="light"

    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.title("🔧 Configuration")
mode = st.sidebar.radio("Mode", ["Charging", "Discharging"])

if "cell_count" not in st.session_state:
    st.session_state.cell_count = 8

add_cell = st.sidebar.button("Add Cell")
remove_cell = st.sidebar.button("Remove Cell")

if add_cell:
    st.session_state.cell_count += 1
if remove_cell and st.session_state.cell_count > 1:
    st.session_state.cell_count -= 1

cell_count = st.session_state.cell_count

# --- Cell Types Input ---
cell_types = []
for i in range(cell_count):
    cell_types.append(st.sidebar.selectbox(f"Cell {i+1} Type", ["lfp", "nmc"], key=f"cell_type_{i}"))

# --- Battery Simulation Logic ---
cells_data = {}

def simulate_cell(cell_type, mode):
    base_voltage = 3.2 if cell_type == "lfp" else 3.6
    min_v = 2.8 if cell_type == "lfp" else 3.2
    max_v = 3.6 if cell_type == "lfp" else 4.0
    delta = round(random.uniform(0.01, 0.05), 2)
    voltage = base_voltage + delta if mode == "Charging" else base_voltage - delta
    voltage = min(max(voltage, min_v), max_v)
    temp = round(random.uniform(25, 40), 1)
    current = round(random.uniform(0.5, 1.5), 2)
    capacity = round(voltage * current, 2)
    return voltage, current, temp, capacity, min_v, max_v

for i, cell_type in enumerate(cell_types):
    voltage, current, temp, capacity, min_v, max_v = simulate_cell(cell_type, mode)
    cells_data[f"Cell {i+1} ({cell_type.upper()})"] = {
        "Voltage (V)": voltage,
        "Current (A)": current,
        "Temperature (C)": temp,
        "Capacity (Wh)": capacity,
        "Min V": min_v,
        "Max V": max_v
    }

# --- Dashboard ---
st.title("🔋 Battery Simulation Dashboard")
st.subheader(f"Live {mode} Mode")

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
total_voltage = sum([v['Voltage (V)'] for v in cells_data.values()])
avg_temp = round(sum([v['Temperature (C)'] for v in cells_data.values()]) / cell_count, 2)
total_capacity = sum([v['Capacity (Wh)'] for v in cells_data.values()])
avg_voltage = round(total_voltage / cell_count, 2)

summary_col1.metric("Total Cells", cell_count)
summary_col2.metric("Average Voltage", f"{avg_voltage:.2f} V")
summary_col3.metric("Average Temperature", f"{avg_temp:.1f} C")
summary_col4.metric("Total Capacity", f"{total_capacity:.2f} Wh")

# --- Graph Selector ---
st.subheader("📊 Graphs")
graph_option = st.selectbox("Choose Graph", ["Voltage", "Current", "Temperature", "Capacity", "Scatter Voltage vs Temp", "Scatter Capacity vs Current"])

labels = list(cells_data.keys())
df = pd.DataFrame.from_dict(cells_data, orient='index')

if graph_option in ["Voltage", "Current", "Temperature", "Capacity"]:
    column_map = {
        "Voltage": "Voltage (V)",
        "Current": "Current (A)",
        "Temperature": "Temperature (C)",
        "Capacity": "Capacity (Wh)"
    }
    data = df[column_map[graph_option]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=data, marker_color="#7a5ecc"))
    fig.update_layout(title=f"{graph_option} per Cell", xaxis_title="Cell", yaxis_title=graph_option)
    st.plotly_chart(fig, use_container_width=True)
elif graph_option == "Scatter Voltage vs Temp":
    fig = px.scatter(df, x="Voltage (V)", y="Temperature (C)", color=df.index, title="Voltage vs Temperature")
    st.plotly_chart(fig, use_container_width=True)
elif graph_option == "Scatter Capacity vs Current":
    fig = px.scatter(df, x="Capacity (Wh)", y="Current (A)", color=df.index, title="Capacity vs Current")
    st.plotly_chart(fig, use_container_width=True)

# --- Data Table ---
st.dataframe(df.style.format("{:.2f}"))
