import streamlit as st
import pandas as pd
import random as r

with st.sidebar:
    st.markdown('## Настройки фильтрации')
    years = st.slider('Выберете диапозон лет:', 2021, 2025, (2021, 2025))
    option_main_chart = st.checkbox('Показать исходную таблицу данных', value=True)

st.markdown('# 📈 Интерактивный Дашборд Продаж (Streamlit)')
st.markdown('## Анализ данных за последние 5 лет')

main_chart = {
    'Год': [2021, 2022, 2023, 2024, 2025],
    'Продажи (тыс.)': [r.randint(50, 150), r.randint(50, 150), r.randint(50, 150), r.randint(50, 150), r.randint(50, 150), ],
    'Расходы (тыс.)': [r.randint(40, 140), r.randint(40, 140), r.randint(40, 140), r.randint(40, 140), r.randint(40, 140), ]
}
m_ch = pd.DataFrame(main_chart)
m_ch = m_ch[
    (m_ch['Год'] >= years[0]) &
    (m_ch['Год'] <= years[1])]

if option_main_chart:
    st.divider()
    st.markdown("<b style='font-size: 28px;'>Исходные данные (отфильтровано с 2021 по 2025):</b>", unsafe_allow_html=True)
    st.dataframe(m_ch)

st.divider()

st.markdown("<b style='font-size: 28px;'>Тренды Продаж и Расходов</b>", unsafe_allow_html=True)
st.line_chart(
    m_ch,
    x='Год',
    y=['Продажи (тыс.)', 'Расходы (тыс.)']
)

st.markdown("<b style='font-size: 28px;'>Ключевые Метрики</b>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    total_sum = sum(main_chart['Продажи (тыс.)'])
    st.markdown(f'Общие продажи<br><span style="font-size: 36px;">{total_sum} тыс.</span>', unsafe_allow_html=True)
with col2:
    total_cost = sum(main_chart['Расходы (тыс.)'])
    st.markdown(f'Общие расходы<br><span style="font-size: 36px;">{total_cost} тыс.</span>', unsafe_allow_html=True)
with col3:
    profit = total_sum - total_cost
    st.markdown(f'Прибыль<br><span style="font-size: 36px;">{profit} тыс.</span>', unsafe_allow_html=True)