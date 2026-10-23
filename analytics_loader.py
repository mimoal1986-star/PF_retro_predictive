# analytics_loader.py
# Загрузка и валидация Parquet-датасета ретро-аналитики визитов
# (перенесено из проекта «Аналитика визитов», блок загрузки Parquet)

import io
import pandas as pd
import streamlit as st


# ===============================================================
# СХЕМА ДАННЫХ
# ===============================================================
REQUIRED_COLUMNS = [
    "Тип файла",
    "Год",
    "Месяц",
    "Клиент",
    "Код проекта",
    "Волна",
    "ASM",
    "Регион short",
    "Регион long",
    "RS",
    "RS ID",
    "Дата визита",
    "План ТП, руб",
    "Факт ТП, руб",
    "ПФ ТП, руб",
    "Дата старта",
    "Дата финиша",
    "Длительность",
]


def validate_parquet(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Проверяет наличие обязательных колонок в датасете.

    Возвращает:
        (ok, missing) — флаг валидности и список отсутствующих колонок.
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return (len(missing) == 0, missing)


@st.cache_data(show_spinner=False)
def read_parquet_cached(file_bytes: bytes) -> pd.DataFrame:
    """Читает Parquet из байтов с кэшированием Streamlit."""
    return pd.read_parquet(io.BytesIO(file_bytes))
