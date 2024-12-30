import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(
    page_title="VIX Price Charts",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': 'VIX Price Analysis Dashboard'}
)

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
    }
    h1, h2, h3 {
        color: white !important;
    }
    .plot-container {
        background-color: #0E1117 !important;
    }
</style>
""", unsafe_allow_html=True)

def load_existing_data(filename='VIX_History.csv'):
    try:
        df_existing = pd.read_csv(filename)
        df_existing['DATE'] = pd.to_datetime(df_existing['DATE'])
        for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
            df_existing[col] = df_existing[col].round(2)
        return df_existing
    except Exception as e:
        st.error(f"Error loading existing data: {str(e)}")
        return None

def get_new_data():
    try:
        vix = yf.download('^VIX')
        df_new = vix.reset_index()
        df_new = df_new[['Date', 'Open', 'High', 'Low', 'Close']]
        df_new.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']
        for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
            df_new[col] = df_new[col].round(2)
        return df_new
    except Exception as e:
        st.error(f"Error getting new data: {str(e)}")
        return None

def update_vix_data():
    with st.spinner('Updating data...'):
        df_existing = load_existing_data()
        if df_existing is None:
            return None
        df_new = get_new_data()
        if df_new is None:
            return df_existing
        latest_date = df_existing['DATE'].max()
        df_new_filtered = df_new[df_new['DATE'] > latest_date]
        if len(df_new_filtered) > 0:
            df_combined = pd.concat([df_existing, df_new_filtered])
            df_combined = df_combined.sort_values('DATE')
            df_combined = df_combined.drop_duplicates(subset=['DATE'], keep='last')
            df_combined.to_csv('VIX_History.csv', index=False, float_format='%.2f')
            st.success(f"Added {len(df_new_filtered)} new records to VIX_History.csv")
            return df_combined
        else:
            st.info("No new data to add")
            return df_existing

def create_figure(data, column, title, color):
    min_val = data[column].min()
    max_val = data[column].max()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data['DATE'],
            y=data[column],
            mode='lines',
            name=column,
            line=dict(color=color, width=1.5),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}',
        )
    )
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24, color='white'),
            x=0.5,
            y=0.95
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.95)',
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.8)',
            tickfont=dict(size=12, color='black'),
            title_font=dict(color='black'),
            rangeslider=dict(visible=True),
            type='date',
            fixedrange=False
        ),
        yaxis=dict(
            title=f"{column} Price",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.8)',
            tickfont=dict(size=12, color='black'),
            title_font=dict(color='black'),
            fixedrange=False,
            autorange=True
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial",
            font_color="black"
        ),
        dragmode='zoom'
    )
    return fig

st.title('📈 VIX Index Price Chart')
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

if st.button('🔄 Refresh Data'):
    df = update_vix_data()
else:
    df = load_existing_data()

if df is not None:
    latest_date = df['DATE'].max().strftime('%Y-%m-%d')
    st.markdown(f"### Latest data: {latest_date}")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            create_figure(df, 'OPEN', 'Opening Price Trends', '#1f77b4'),
            use_container_width=True
        )
        st.plotly_chart(
            create_figure(df, 'HIGH', 'Daily High Values', '#2ca02c'),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            create_figure(df, 'LOW', 'Daily Low Values', '#d62728'),
            use_container_width=True
        )
        st.plotly_chart(
            create_figure(df, 'CLOSE', 'Closing Price Trends', '#9467bd'),
            use_container_width=True
        )
