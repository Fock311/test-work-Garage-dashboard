import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Garage Dashboard", layout="centered")

# Кастомный CSS для адаптивных метрик
st.markdown("""
<style>
/* Контейнер для строк метрик */
.metrics-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-bottom: 0.6rem;
    justify-content: center;
}
/* Карточка метрики */
.metric-card {
    background-color: #f0f2f6;
    border-radius: 12px;
    padding: 0.5rem 0.3rem;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    flex: 1 1 30%;  /* на телефоне 3 карточки в ряд */
    min-width: 90px;
}
.metric-card h3 {
    font-size: 0.75rem;
    margin: 0;
    font-weight: 500;
    color: #333;
}
.metric-card p {
    font-size: 1.2rem;
    font-weight: bold;
    margin: 0.2rem 0 0 0;
    color: #000;
}
/* На широком экране (≥641px) — все 5 карточек в одну строку */
@media (min-width: 641px) {
    .metrics-row {
        flex-wrap: nowrap;
    }
    .metric-card {
        flex: 1;
    }
}
/* На телефоне вторая строка с двумя карточками — ширина около 48% */
@media (max-width: 640px) {
    .metrics-row:last-child .metric-card {
        flex: 1 1 48%;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("🏎️ Garage Club — управленческая сводка")

# Загрузка данных
@st.cache_data
def load_data():
    df = pd.read_excel("garage_export_sample.xlsx", engine="openpyxl")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

df_all = load_data()
dates = sorted(df_all["date"].unique(), reverse=True)

selected_date = st.selectbox("📅 Выберите дату:", dates, index=0)
df_day = df_all[df_all["date"] == selected_date].copy()

# Метрики
total_revenue = df_day["price_with_vat"].sum()
total_bookings = len(df_day)
cancelled = df_day[df_day["payment_status"] == "отменено"].shape[0]
refunds = df_day[df_day["payment_status"] == "возврат"].shape[0]

positive_revenue = df_day[df_day["price_with_vat"] > 0]["price_with_vat"].sum()
positive_count = df_day[df_day["price_with_vat"] > 0].shape[0]
avg_check = positive_revenue / positive_count if positive_count > 0 else 0

# Отображение метрик через HTML
st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card"><h3>💰 Выручка</h3><p>{total_revenue:,.0f} ₽</p></div>
    <div class="metric-card"><h3>📅 Бронирований</h3><p>{total_bookings}</p></div>
    <div class="metric-card"><h3>❌ Отмены</h3><p>{cancelled}</p></div>
</div>
<div class="metrics-row">
    <div class="metric-card"><h3>↩️ Возвраты</h3><p>{refunds}</p></div>
    <div class="metric-card"><h3>🧾 Средний чек*</h3><p>{avg_check:,.0f} ₽</p></div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.subheader(f"📊 Детализация за {selected_date.strftime('%d.%m.%Y')}")

# Графики (вертикально)
fig_station = px.pie(values=df_day["station"].value_counts(), names=df_day["station"].value_counts().index, title="Симуляторы")
st.plotly_chart(fig_station, use_container_width=True)

fig_session = px.pie(values=df_day["session_type"].value_counts(), names=df_day["session_type"].value_counts().index, title="Тип сессии")
st.plotly_chart(fig_session, use_container_width=True)

fig_source = px.pie(values=df_day["booking_source"].value_counts(), names=df_day["booking_source"].value_counts().index, title="Откуда пришли")
st.plotly_chart(fig_source, use_container_width=True)

st.caption("*Средний чек рассчитан только по бронированиям с положительной суммой (исключены возвраты и отмены).")
st.caption("📌 На графиках показаны **все** категории без объединения.")

if total_bookings == 0:
    st.warning("⚠️ В этот день бронирований не было.")