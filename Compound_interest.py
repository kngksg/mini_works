import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

def is_leap_year(year):
    if year % 400 == 0:
        return 1
    else: 
        if year % 100 == 0:
            return 0
        else:
            if year % 4 == 0:
                return 1
    return 0

percent_increase = 0

with st.sidebar:
    st.markdown("## Параметры расчета")
    investment_horizon = st.slider("Количесвто лет инвестирования", 1, 60, value=5)
    saving_plan = st.selectbox("Периодичность отчислений", ('День', 'Неделя', 'Месяц', 'Квартал', 'Год'))
    contribution_amount = st.number_input(
        label=f"Рублей в {saving_plan.lower()}",
        min_value=0,
        value=100,
        step=50,
        format="%d"
    )
    option_increase = st.checkbox('Повышать взнос каждый год')
    if option_increase:
        percent_increase = st.slider("Процент повышения", 0, 50, value=10)
    return_rate = st.number_input(
        label="Доходность в процентах",
        value=15.00,
        step=1.00,
        format="%f"
    )
    inflation_rate = st.number_input(
        label="Инфляция",
        value=10.00,
        step=1.00,
        format="%f"
    )
    option_own_saves = st.checkbox('Показать таймлайн без инвестироания накоплений', value=False)

current_year = datetime.now().year
years = [current_year + x for x in range(investment_horizon+1)]
years_tip = [f'{current_year + x} ({x} лет с начала накопления)' for x in range(investment_horizon+1)]
list_saves = [0]
list_real_saves = [0]
list_own_saves = [0]
list_own_real_saves = [0]

saves = 0 #рублей накопленно
real_saves = 0 #рублей накопленно фактически(с учетом инфляции)
own_saves = 0 #свои деньги, без процента
own_real_saves = 0 #свои деньги, без процента(с учетом инфляции)
total_inflation = 1 #инфляция за все время
quantity_of_contribution = 0
quantity_of_leap_years = sum([is_leap_year(y) for y in years[:-1]])
temporary_current_year = current_year
number_period = 0
day_in_actual_year = 0
day_in_actual_period = 0
for day in range(1, 365*investment_horizon + 1 + quantity_of_leap_years):
    day_in_actual_year += 1
    day_in_actual_period += 1
    index_inflation = (1+inflation_rate/100)**(1/(365 + is_leap_year(temporary_current_year)))
    return_index = (1+return_rate/100)**(1/(365 + is_leap_year(temporary_current_year)))
    days_in_months = [31, 28 + is_leap_year(temporary_current_year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    match saving_plan:
        case 'День': interval = 1
        case 'Неделя': interval = 7
        case 'Месяц': interval = days_in_months[number_period%12]
        case 'Квартал': interval = sum(days_in_months[(3*number_period)%12:(3*number_period)%12 + 3])
        case 'Год': interval = sum(days_in_months)
    if day_in_actual_period % interval == 0:
        quantity_of_contribution += 1
        saves += contribution_amount
        real_saves += contribution_amount/total_inflation #откладывем в копилку
        own_saves += contribution_amount
        own_real_saves += contribution_amount/total_inflation #прибавляем рубли подверженные инфляции
        number_period += 1
        day_in_actual_period = 0
    real_saves /= index_inflation
    own_real_saves /= index_inflation #учитывем ежедневную инфл.
    saves *= return_index
    real_saves *= return_index #прибавляем процент
    total_inflation *= index_inflation
    if day_in_actual_year % (365 + is_leap_year(temporary_current_year)) == 0:
        list_saves.append(saves)
        list_real_saves.append(real_saves)
        list_own_saves.append(own_saves)
        list_own_real_saves.append(own_real_saves)
        past_contribution = contribution_amount
        contribution_amount *= 1 + percent_increase/100
        temporary_current_year += 1
        day_in_actual_year = 0

saves_with_interest = saves - own_saves
real_saves_with_interest = real_saves - own_real_saves

st.markdown('# Таймлайн изменения капитала')

savings = {
    'Год': years,
    'Год_подсказка': years_tip,
    'Накопления': list_saves,
    'Реальные накопления': list_real_saves,
    'Свои накопления': list_own_saves,
    'Свои реальные накопления': list_own_real_saves
}

capital_timeline = pd.DataFrame(savings)
capital_timeline = capital_timeline[
    capital_timeline['Год'] <= (current_year + investment_horizon)
]

st.markdown('## Без учета инфляции')

base_chart_saves = alt.Chart(capital_timeline).encode(
    x = alt.X('Год:Q', axis=alt.Axis(format='d', title='Год', grid=True)),
    y = alt.Y('Накопления:Q', axis=alt.Axis(format=',.0f', title='Накопления (руб.)')),
)

chart_saves = alt.layer(
    base_chart_saves.mark_line(point=True),
    base_chart_saves.mark_area(opacity=0.4)
)

tooltip_saves = [
        alt.Tooltip('Год_подсказка:N', title='Год'),
        alt.Tooltip('Накопления:Q', format=',.0f', title='Накопления')
    ]

if option_own_saves:
    base_chart_own_saves = alt.Chart(capital_timeline).encode(
    x = alt.X('Год:Q', axis=alt.Axis(format='d', title='Год', grid=True)),
    y = alt.Y('Свои накопления:Q', axis = alt.Axis(format=',.0f'))
    )
    chart_own_saves = alt.layer(
        base_chart_own_saves.mark_line(point=True),
        base_chart_own_saves.mark_area(opacity=0.6),
    )
    chart_saves += chart_own_saves
    tooltip_saves.append(alt.Tooltip('Свои накопления', format=',.0f', title='Свои накопления'))

chart_saves += base_chart_saves.mark_rule(opacity=0).encode(
    tooltip = tooltip_saves
).add_params(
        alt.selection_point(on='mouseover', nearest=True, fields=['Год'])
    )

st.altair_chart(chart_saves.interactive(), use_container_width=True) #добавление графика накоплнний без инфляции

st.markdown(f"<b style= 'font-size:32px;'>Итог на {years[investment_horizon]}</b>", unsafe_allow_html=True)

col_saves_1, col_saves_2 = st.columns(2)

with col_saves_1:
    total_saves = st.metric(
        label= "Накоплено",
        value=f"{saves:,.0f}".replace(',', ' '),
    )
    if option_own_saves:
        total_own_saves = st.metric(
            label="Доход и доля от собственных вложений",
            value=f"{own_saves:,.0f}".replace(',', ' ')
        )
        persent_own_saves = st.metric(
            label="",
            value=f"{own_saves/saves:.2%}".replace(',', ' ') if saves!=0 else "0%"
        )
with col_saves_2:
    if option_increase:
        last_contribution = st.metric(
            label="Последний взнос",
            value=f"{past_contribution:,.0f} ₽".replace(',', ' ')
        )
    else:
        total_quantity_of_contribution = st.metric(
            label= "Вложений за все время",
            value=f"{quantity_of_contribution:,.0f}".replace(',', ' ')
        )
    if option_own_saves:
        total_saves_with_interst = st.metric(
            label="Доход и доля от процентов",
            value=f"{saves_with_interest:,.0f}".replace(',', ' ')
        )
        persent_saves_with_interest = st.metric(
            label="",
            value=f"{saves_with_interest/saves:.2%}".replace(',', ' ') if saves!=0 else "0%",
        )

st.markdown('## С учетом инфляции')

base_chart_real_saves = alt.Chart(capital_timeline).encode(
    x = alt.X('Год:Q', axis = alt.Axis(format = 'd', title = 'Год', grid=True)),
    y = alt.Y('Реальные накопления:Q', axis = alt.Axis(format = ',.0f', title = 'Накопления (руб.)')),
)

chart_real_saves = (
    base_chart_real_saves.mark_line(point=True)+
    base_chart_real_saves.mark_area(opacity=0.4)
)

tooltip_real_saves = tooltip = [
        alt.Tooltip('Год_подсказка:N', title = 'Год'),
        alt.Tooltip('Реальные накопления:Q', format = ',.0f', title = 'Накопления')
]

if option_own_saves:
    base_chart_own_real_saves = alt.Chart(capital_timeline).encode(
        x = alt.X('Год:Q', axis = alt.Axis(format = 'd', title = 'Год', grid = False)),
        y = alt.Y('Свои реальные накопления:Q', axis = alt.Axis(format = ',.0f'))
    )
    chart_own_real_saves = alt.layer(
        base_chart_own_real_saves.mark_line(point=True),
        base_chart_own_real_saves.mark_area(opacity=0.6)
    )
    chart_real_saves += chart_own_real_saves
    tooltip_real_saves.append(alt.Tooltip('Свои реальные накопления:Q', format = ',.0f', title = 'Свои накопления'))

chart_real_saves += base_chart_real_saves.mark_rule(opacity=0).encode(
    tooltip = tooltip_real_saves
).add_params(
    alt.selection_point(on='mouseover', nearest=True, fields=['Год'])
)

st.altair_chart(chart_real_saves.interactive(), use_container_width=True) #добавление графика накоплнний c инфляцией

#Вывод: real_saves, real_saves_with_interest; опционально: real_own_saves, v


st.markdown(f"<b style= 'font-size:32px;'>Итог на {years[investment_horizon]} (с инфляцией)</b>", unsafe_allow_html=True)

col_real_saves_1, col_real_saves_2 = st.columns(2)

with col_real_saves_1:
    total_real_saves = st.metric(
        label= "Накоплено",
        value=f"{real_saves:,.0f}".replace(',', ' '),
    )
    if option_own_saves:
        total_own_real_saves = st.metric(
            label="Доход и доля от собственных вложений",
            value=f"{own_real_saves:,.0f}".replace(',', ' ')
        )
        persent_own_real_saves = st.metric(
            label="",
            value=f"{own_real_saves/real_saves:.2%}".replace(',', ' ') if real_saves!=0 else "0%"
        )
with col_real_saves_2:
    if option_increase:
        last_contribution = st.metric(
            label="Последний взнос",
            value=f"{contribution_amount:,.0f} ₽".replace(',', ' ')
        )
    else:
        total_quantity_of_contribution = st.metric(
            label= "Вложений за все время",
            value=f"{quantity_of_contribution:,.0f}".replace(',', ' ')
        )
    if option_own_saves:
        total_real_saves_with_interst = st.metric(
            label="Доход и доля от процентов",
            value=f"{real_saves_with_interest:,.0f}".replace(',', ' ')
        )
        persent_real_saves_with_interest = st.metric(
            label="",
            value=f"{real_saves_with_interest/real_saves:.2%}".replace(',', ' ') if real_saves!=0 else "0%",
        )