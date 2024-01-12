import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_google_sheets_data():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SPREADSHEET_ID = st.secrets["spreadsheet_id"]
    RANGE_NAME = "city!A1:Q"  # Substitua pelo seu range de dados específico

    # Carrega as credenciais
    creds_dict = {
        "type": "service_account",
        "project_id": st.secrets["google_oauth"]["project_id"],
        "private_key_id": st.secrets["google_oauth"]["private_key_id"],
        "private_key": st.secrets["google_oauth"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["google_oauth"]["client_email"],
        "client_id": st.secrets["google_oauth"]["client_id"],
        "auth_uri": st.secrets["google_oauth"]["auth_uri"],
        "token_uri": st.secrets["google_oauth"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_oauth"]["auth_provider_x509_cert_url"],
        #"redirect_uris": st.secrets["google_oauth"]["redirect_uris"],
    }
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    # Constrói o serviço
    service = build("sheets", "v4", credentials=creds)

    # Obtém os dados da planilha
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get("values", [])

    # Retorna um DataFrame
    if not values:
        return None
    return pd.DataFrame(values[1:], columns=values[0])
def get_weather_emoji(weather_description):
    weather_description = weather_description.lower()
    if 'céu limpo' in weather_description:
        return '☀️'
    elif any(cond in weather_description for cond in ['poucas nuvens', 'nuvens dispersas']):
        return '⛅'
    elif 'nublado' in weather_description:
        return '☁️'
    elif 'chuva leve' in weather_description:
        return '🌦️'
    elif 'chuva' in weather_description:
        return '🌧️'
    elif 'trovoada' in weather_description:
        return '⛈️'
    elif 'neve' in weather_description:
        return '🌨️'
    elif 'névoa' in weather_description or 'neblina' in weather_description:
        return '🌫️'
    elif 'nuvens carregadas' in weather_description:
        return '☁️'
    elif 'garoa' in weather_description:
        return '🌧️'
    else:
        return '⛅'

def convert_to_float(value):
    try:
        return float(value.replace(',', '.'))
    except ValueError:
        return 0

def main():
    st.title("TempPad - Clima de Hoje")


    st.sidebar.image("pdilogo (1).png", use_column_width=True)

    # Escolher entre diferentes páginas
    page = st.sidebar.radio("Navegar", ["Previsão do Tempo", "Sobre", "Saiba Mais"])

    if page == "Previsão do Tempo":
        data = get_google_sheets_data()
        if data is not None:
            selected_uf = st.sidebar.selectbox("Selecione um Estado", data['UF'].unique())
            city_search = st.sidebar.text_input("Qual cidade deseja saber:")
            filtered_data = data[(data['UF'] == selected_uf) & (data['Cidade'].str.contains(city_search, case=False))]

        for _, row in filtered_data.iterrows():
                with st.container():
                    weather_emoji = get_weather_emoji(row['Descrição'])
                    st.markdown(f"#### {weather_emoji} {row['Cidade']} - {row['UF']}")
                    temperatura = convert_to_float(row['Temperatura'].replace('°C', ''))
                    sensacao_termica = convert_to_float(row['Sensação Térmica'].replace('°C', ''))
                    maxima = convert_to_float(row['Máxima'].replace('°C', ''))
                    minima = convert_to_float(row['Mínima'].replace('°C', ''))
                    st.markdown(f"Temperatura: {round(temperatura)}°C | Sensação Térmica: {round(sensacao_termica)}°C")
                    st.markdown(f"Máxima: {round(maxima)}°C | Mínima: {round(minima)}°C")
                    possibilidade_chuva = min(convert_to_float(row['Possibilidade de chuva'].replace('%', '')), 100)
                    st.markdown(f"Possibilidade de Chuva: {round(possibilidade_chuva)}% | Descrição: {row['Descrição']}")
                    umidade = convert_to_float(row['Umidade'].replace('%', ''))
                    st.markdown(f"Umidade: {round(umidade)}% | Visibilidade: {round(convert_to_float(row['Visibilidade'].replace('km', '').strip()) , 2)}km")
                    st.markdown(f"Nascer do Sol: {row['Nascer do sol']} | Pôr do Sol: {row['Por do sol']}")
                    velocidade_vento = convert_to_float(row['Velocidade dos ventos'].replace('km/h', '').strip())
                    st.markdown(f"Velocidade do Vento: {round(velocidade_vento, 2)} km/h | Direção do Vento: {row['Direção dos ventos']}")

                    alerta_de_chuva = row.get('Alerta de chuva')
                    if alerta_de_chuva:
                        alerta_de_chuva = alerta_de_chuva.strip()
                        if alerta_de_chuva.lower() == 'alerta':
                            st.markdown(
                                f"<span style='color: red;'>⚠️ **Possibilidade de Chuva:** </span> {alerta_de_chuva}🚨 ",
                                unsafe_allow_html=True)
                        else:
                            st.markdown(f"Alerta de Chuva: {alerta_de_chuva}")

                st.markdown("---")

    elif page == "Sobre":
        st.markdown("## Sobre o Aplicativo")
        st.markdown("'TempPad' é um aplicativo interativo e fácil de usar, desenvolvido em Streamlit, que fornece informações detalhadas e atualizadas sobre a previsão do tempo para diferentes cidades que a Ceneged é presente. Ele foi projetado para ser intuitivo, permitindo aos usuários uma navegação simples e uma experiência de usuário agradável.")

    elif page == "Saiba Mais":
        st.markdown("## Saiba Mais")
        st.markdown("Confira este vídeo para saber um pouco mais sobre o desenvolvimento desse App. Acesse o link abaixo:")
        st.markdown("https://www.youtube.com/")

    st.sidebar.markdown("---")
    st.sidebar.markdown("Desenvolvido por [PedroFS](https://linktr.ee/Pedrofsf)")

if __name__ == "__main__":
    main()
