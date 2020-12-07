import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime
from datetime import timedelta



@st.cache(allow_output_mutation=True)
def load_data():
    token = 'dda547d6c827fdae16f8b0b33375a32012c0b6a9'
    url = 'https://api.brasil.io/v1/dataset/covid19/caso_full/data/?search=Pelotas&epidemiological_week=&date=&order_for_place=&state=RS&city=&city_ibge_code=&place_type=&last_available_date=&is_last=&is_repeated='
    headers = {
            "User-Agent": "python-urllib/brasilio-client-0.1.0",
            "Authorization": f"Token {token}"
          }
    request = requests.get(url, headers=headers)
    print('fez request zdfg')
    if request.status_code == 200:
        return pd.DataFrame.from_dict(request.json()['results'])

df = load_data()

#Removendo dados não confirmados
df = df[df['is_repeated'] == False]

# alterando o tipo de dados de data para date
df.date = pd.to_datetime(df['date'])

# calculado a media movel
#reordenando o df para calcular a media movel
df.sort_values(by='date', ascending=True, inplace=True)

df['rolling_avg'] = df['new_confirmed'].rolling(window=14).mean()
df['rolling_avg_deaths'] = df['new_deaths'].rolling(window=14).mean()

df.sort_values(by='date', ascending=False, inplace=True)




last_update = df[df['is_last'] == 1]
delta_date = last_update.date - timedelta(14)

confirmed = last_update.last_available_confirmed.array[0]
deaths = last_update.last_available_deaths.array[0]
last_date_mean = df[df['date'] == delta_date.array[0]] #14 dias atras 


current_rolling_avg = last_update.rolling_avg.values[0]
current_rolling_avg_deaths = last_update.rolling_avg_deaths.values[0]

last_rolling_avg = last_date_mean.rolling_avg.values[0]
last_rolling_avg_deaths = last_date_mean.rolling_avg_deaths.values[0]


variacao_avg = round(current_rolling_avg / last_rolling_avg * 100 - 100, 2)
varaicao_avg_deaths = round(current_rolling_avg_deaths / last_rolling_avg_deaths * 100 -100, 2)

st.markdown('<script src="https://use.fontawesome.com/c61dec7cb9.js"></script>', unsafe_allow_html=True)


st.title('Covid em Pelotas')
st.markdown('___')
col1, col2, col3, col4 = st.beta_columns(4)
with col1:    
    st.markdown(f'<h1 style="color:#F98270"> <i class="fa fa-check" aria-hidden="true"></i>{  confirmed} </h1>Total de Casos', unsafe_allow_html=True)

with col2:    
    st.markdown(f'<h1 style="color:gray""> { deaths } </h1>Total de mortes', unsafe_allow_html=True)

with col3:    
    st.markdown(f'<h1 style="color:gray""> { variacao_avg } </h1>Variação média Móvel de casos', unsafe_allow_html=True)

with col4:    
    st.markdown(f'<h1 style="color:gray""> { varaicao_avg_deaths } </h1>Variação da média móvel de mortes', unsafe_allow_html=True)



st.markdown("<p><p>", unsafe_allow_html=True)



st.markdown("## Média Movel de Casos")
fig = go.Figure()
fig.add_trace(go.Bar(x=df.date,
                y=df.new_confirmed,
                name='Casos Confirmados',
                marker_color='rgb(26, 118, 255)'
                ))
fig.add_trace(go.Scatter(x=df.date,
                y=df.rolling_avg,
                name='Media Movel',
                marker_color='red'
                ))

fig.update_layout(
    title='Total de Casos Confirmados',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Casos',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    
)
st.plotly_chart(fig, use_container_width=True)




st.markdown("## Média Movel de Mortes")
fig = go.Figure()
fig.add_trace(go.Bar(x=df.date,
                y=df.new_deaths,
                name='Mortes Confirmadss',
                marker_color='rgb(26, 118, 255)'
                ))
fig.add_trace(go.Scatter(x=df.date,
                y=df.rolling_avg_deaths,
                name='Media Movel de Mortes',
                marker_color='red'
                ))

fig.update_layout(
    title='Mortes Confirmadas',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Mortes',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)
st.plotly_chart(fig, use_container_width=True)