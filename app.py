import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime
from datetime import time
from datetime import timedelta

st.set_page_config(page_title='Covid19 - Análise por município', page_icon='😷')



def my_html(str):
    return st.markdown(str, unsafe_allow_html=True)



@st.cache(allow_output_mutation=True)
def load_data():
    token = 'dda547d6c827fdae16f8b0b33375a32012c0b6a9'
    url = 'https://api.brasil.io/v1/dataset/covid19/caso_full/data/?search=Pelotas&epidemiological_week=&date=&order_for_place=&state=RS&city=&city_ibge_code=&place_type=&last_available_date=&is_last=&is_repeated='
    #url = 'https://api.brasil.io/v1/dataset/covid19/caso_full/data/?search=florianópolis&epidemiological_week=&date=&order_for_place=&state=SC&city=&city_ibge_code=&place_type=&last_available_date=&is_last=&is_repeated='
    headers = {
            "User-Agent": "python-urllib/brasilio-client-0.1.0",
            "Authorization": f"Token {token}"
          }
    try:
        request = requests.get(url, headers=headers)
        print('fez request')
        if request.status_code == 200:
            return pd.DataFrame.from_dict(request.json()['results'])
        else:
            print('erroo!!!!!!!!!!!!!!!!!!!!!!')
            print(request.json())                    
    except:        
        print('deu pau nessa bagaça')                        
       # return False    


df = load_data()


#Removendo dados não confirmados
df = df[df['is_repeated'] == False]

# alterando o tipo de dados de data para date
df.date = pd.to_datetime(df['date'])


st.sidebar.markdown("""
    # Olá,  
    Seja bem vind@ ao painel de acompanhamento da evolução da Covid-19 

""")

start_time = st.sidebar.slider(
     "Altere as datas para consultar os números acumulados no período:",
     value=(datetime(df.date.min().year, df.date.min().month, df.date.min().day), datetime(df.date.max().year, df.date.max().month, df.date.max().day)),
     format="DD/MM")

inicial_date = start_time[0]
final_date = start_time[1]
if inicial_date > final_date - timedelta(13):
    inicial_date = final_date - timedelta(13)
    
st.markdown(f' <h1>😷 Covid em Pelotas</h1>', unsafe_allow_html=True)
st.markdown(f' <h2>Dados atualizados até <b style=\"color:#F63366\">{final_date.strftime("%d/%m/%Y")}</b></h2>', unsafe_allow_html=True)
st.markdown('___')


df_copy = df[  (df.date >= inicial_date) & (df.date <= final_date)  ]
 

# calculado a media Móvel
#reordenando o df para calcular a media Móvel
df_copy.sort_values(by='date', ascending=True, inplace=True)

df_copy['rolling_avg'] = df_copy['new_confirmed'].rolling(window=14).mean()
df_copy['rolling_avg_deaths'] = df_copy['new_deaths'].rolling(window=14).mean()

df_copy.sort_values(by='date', ascending=False, inplace=True)

 

if df_copy[df_copy.date == start_time[1] ].date.empty:
    st.warning('Não encontramos registros nessa data. Por favor, selecione outra.')
    st.stop()

last_update = df_copy[df_copy.date == start_time[1] ]
delta_date = last_update.date - timedelta(13)


confirmed = last_update.last_available_confirmed.array[0]
deaths = last_update.last_available_deaths.array[0]
last_date_mean = df_copy.iloc[13] #14 dias atras 


current_rolling_avg = last_update.rolling_avg.values[0]
current_rolling_avg_deaths = last_update.rolling_avg_deaths.values[0]


last_rolling_avg = last_date_mean.rolling_avg
last_rolling_avg_deaths = last_date_mean.rolling_avg_deaths

variacao_avg = round(current_rolling_avg / last_rolling_avg * 100 - 100, 2)
varaicao_avg_deaths = round(current_rolling_avg_deaths / last_rolling_avg_deaths * 100 -100, 2)


up = " aumentou ↗"
down = " diminuiu ↘"
keep = "está estável em "

col1, col2, = st.beta_columns(2)
with col1:   
    st.markdown(f'<h1 style="color:#F98270"> <i class="fa fa-check" aria-hidden="true"></i>{confirmed} CASOS</h1>', unsafe_allow_html=True)

with col2:    
    st.markdown(f'<h1 style="color:gray""> { deaths } MORTES</h1>', unsafe_allow_html=True)


col1, col2, = st.beta_columns(2)
with col1:    
    if  (variacao_avg < 15 and variacao_avg > -15):
        status = keep
    elif variacao_avg >= 15 :
        status = up
    else:
        status = down    

    st.markdown(f'A média móvel de casos {status}**{variacao_avg }%** em relação há duas semanas', unsafe_allow_html=True)

with col2:    
    if (varaicao_avg_deaths > -15 and varaicao_avg_deaths < 15):
        status = keep
    elif varaicao_avg_deaths >= 15:
        status = up
    else:
        status = down    
    st.markdown(f'A média móvel de mortes {status}**{varaicao_avg_deaths }**% em relação há duas semanas', unsafe_allow_html=True)



st.markdown("<p><p>", unsafe_allow_html=True)



st.markdown("## Média Móvel de Casos")
fig = go.Figure()
fig.add_trace(go.Bar(x=df_copy.date,
                y=df_copy.new_confirmed,
                name='Casos Confirmados',
                marker_color='rgb(26, 118, 255)'
                ))
fig.add_trace(go.Scatter(x=df_copy.date,
                y=df_copy.rolling_avg,
                name='Media Móvel',
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




st.markdown("## Média Móvel de Mortes")
fig = go.Figure()
fig.add_trace(go.Bar(x=df_copy.date,
                y=df_copy.new_deaths,
                name='Mortes Confirmadss',
                marker_color='rgb(26, 118, 255)'
                ))
fig.add_trace(go.Scatter(x=df_copy.date,
                y=df_copy.rolling_avg_deaths,
                name='Media Móvel de Mortes',
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


st.markdown('## Tabela com dados detalhados')

df_copy.rename(columns={
    'city':'Cidade', 
    'date':'Data', 
    'last_available_confirmed':'Casos Confirmados',
    'rolling_avg' : 'Média Móvel de casos',
    'rolling_avg_deaths': 'Média Móvel Mortes'
    } )[['Cidade', 'Data', 'Casos Confirmados', 'Média Móvel de casos', 'Média Móvel Mortes']]



my_html('<br><br><br>')

st.markdown("""
## Sobre o painel

Em meio ao caos da pandemia, que infelizmente atinge o auge em nossa região, podemos destacar um ponto positivo da administração pública que é disponibilização dos dados livremente para a comunidade. A análise porém sem a metodologia correta e ferramentas ágeis de visualização fica comprometida. Além disso, a média móvel, um dos indicadores mais utilizados pela imprensa para acompanhamento da evolução da doença, é publicado apenas a nível estadual e nacional. Não encontramos, de forma fácil, pelo menos, esse indicador por município e resolver desenvolver para Pelotas.

### Origem dos dados
As informações aqui apresentadas não tem, de forma nenhuma, a pretensão de substituir os dados oficiais. Nossa intenção é apenas demonstrar de forma simples e direta as informações sobre a covid-19.

Os dados são coletados na plataforma [Brasil.io](https://brasil.io), que por sua vez, compila as informações das secretarias estaduais de saúde e gentilmente libera sob a licença CC BY-SA 4.0, num belo trabalho de [Álvaro Justen e dezenas de colaboradores](https://blog.brasil.io/2020/03/23/dados-coronavirus-por-municipio-mais-atualizados/).

### Metodologia de cálculo da média móvel
A média móvel é calculada através da soma dos últimos 14 dias, dividido por 14.

### Quem somos?
Os dados são coletados, tratados, e disponibilizados pelos analistas [Fabrício Silva](https://www.linkedin.com/in/fabriciofsilva) e [Thiago Oliveira](https://www.linkedin.com/in/thiago-oliveira-30440552/)
""")