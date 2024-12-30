import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(
    page_title="VIX Price Charts",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': 'VIX Price Analysis Dashboard'}
)

def load_existing_data(filename='VIX_History.csv'):
    try:
        df_existing = pd.read_csv(filename)
        df_existing['DATE'] = pd.to_datetime(df_existing['DATE'])
        for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
            df_existing[col] = df_existing[col].round(2)
        return df_existing
    except FileNotFoundError:
        df_new = get_new_data()
        if df_new is not None:
            df_new.to_csv(filename, index=False)
            return df_new
        return None
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
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,17,17,0.8)',
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24, color='white'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.8)',
            tickfont=dict(size=12, color='white'),
            title_font=dict(color='white'),
            rangeslider=dict(
                visible=True,
                bgcolor='rgba(17,17,17,0.8)',
                bordercolor='rgba(128,128,128,0.2)'
            ),
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
            tickfont=dict(size=12, color='white'),
            title_font=dict(color='white'),
            fixedrange=False,
            autorange=True
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(17,17,17,0.8)',
            font_size=12,
            font_family="Arial",
            font_color="white"
        ),
        dragmode='zoom'
    )
    return fig

st.markdown("""
<style>
    .stApp {
        background: rgb(17,17,17);
        background: linear-gradient(180deg, rgba(17,17,17,1) 0%, rgba(23,23,23,1) 100%);
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
    .element-container {
        background-color: transparent !important;
    }
    div[data-testid="stDecoration"] {
        background-image: none !important;
    }
    iframe {
        background-color: transparent !important;
    }
    .css-1kyxreq {
        background-color: transparent !important;
    }
    .css-1r6slb0 {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

st.title('📈 VIX Index Price Chart')

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
            use_container_width=True,
            config={'displayModeBar': True}
        )
        st.plotly_chart(
            create_figure(df, 'HIGH', 'Daily High Values', '#2ca02c'),
            use_container_width=True,
            config={'displayModeBar': True}
        )
    with col2:
        st.plotly_chart(
            create_figure(df, 'LOW', 'Daily Low Values', '#d62728'),
            use_container_width=True,
            config={'displayModeBar': True}
        )
        st.plotly_chart(
            create_figure(df, 'CLOSE', 'Closing Price Trends', '#9467bd'),
            use_container_width=True,
            config={'displayModeBar': True}
        )
