import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы
st.set_page_config(page_title="Garage Dashboard", layout="centered")

st.title("🏎️ Garage Club — управленческая сводка")

# Загрузка данных
@st.cache_data
def load_data():
    df = pd.read_excel("garage_export_sample.xlsx", engine="openpyxl")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

df_all = load_data()
dates = sorted(df_all["date"].unique(), reverse=True)

# Выбор даты
selected_date = st.selectbox("📅 Выберите дату:", dates, index=0)
df_day = df_all[df_all["date"] == selected_date].copy()

# ---------- МЕТРИКИ ----------
total_revenue = df_day["price_with_vat"].sum()
total_bookings = len(df_day)
cancelled = df_day[df_day["payment_status"] == "отменено"].shape[0]
refunds = df_day[df_day["payment_status"] == "возврат"].shape[0]

# Средний чек только по положительным суммам (исключаем возвраты и отмены)
positive_revenue = df_day[df_day["price_with_vat"] > 0]["price_with_vat"].sum()
positive_count = df_day[df_day["price_with_vat"] > 0].shape[0]
avg_check = positive_revenue / positive_count if positive_count > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Выручка", f"{total_revenue:,.0f} ₽")
col2.metric("📅 Бронирований", total_bookings)
col3.metric("❌ Отмены", cancelled)
col4.metric("↩️ Возвраты", refunds)
col5.metric("🧾 Средний чек*", f"{avg_check:,.0f} ₽")

st.divider()
st.subheader(f"📊 Детализация за {selected_date.strftime('%d.%m.%Y')}")

# ---------- ГРАФИКИ (все категории, без объединения) ----------
# Станции
station_counts = df_day["station"].value_counts()
fig_station = px.pie(values=station_counts.values, names=station_counts.index, title="Симуляторы")

# Типы сессий
session_counts = df_day["session_type"].value_counts()
fig_session = px.pie(values=session_counts.values, names=session_counts.index, title="Тип сессии")

# Источники
source_counts = df_day["booking_source"].value_counts()
fig_source = px.pie(values=source_counts.values, names=source_counts.index, title="Откуда пришли")

col1g, col2g, col3g = st.columns(3)
with col1g:
    st.plotly_chart(fig_station, use_container_width=True)
with col2g:
    st.plotly_chart(fig_session, use_container_width=True)
with col3g:
    st.plotly_chart(fig_source, use_container_width=True)

# Пояснения
st.caption("*Средний чек рассчитан только по бронированиям с положительной суммой (исключены возвраты и отмены).")
st.caption("📌 На графиках показаны **все** категории, даже если их мало — для полной картины.")

if total_bookings == 0:
    st.warning("⚠️ В этот день бронирований не было.")