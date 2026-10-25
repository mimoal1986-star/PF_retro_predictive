# utils/dataviz.py
# draft 4.1 
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from datetime import datetime
from io import BytesIO
from visit_calculator import visit_calculator

class DataVisualizer:

    def __init__(self):
        self.region_mapping = {
            'AD': 'Республика Адыгея', 'AL': 'Алтайский край', 'AM': 'Амурская область',
            'AR': 'Архангельская область', 'AS': 'Астраханская область', 'BK': 'Республика Башкортостан',
            'BL': 'Белгородская область', 'BR': 'Брянская область', 'BU': 'Республика Бурятия',
            'CK': 'Чукотский автономный округ', 'CL': 'Челябинская область', 'CN': 'Чеченская Республика',
            'CV': 'Чувашская Республика', 'DA': 'Республика Дагестан', 'DN': 'Донецкая Народная Республика',
            'GA': 'Республика Алтай', 'IN': 'Республика Ингушетия', 'IR': 'Иркутская область',
            'IV': 'Ивановская область', 'KA': 'Камчатский край', 'KB': 'Кабардино-Балкарская Республика',
            'KC': 'Карачаево-Черкесская Республика', 'KD': 'Краснодарский край', 'KE': 'Кемеровская область',
            'KG': 'Калужская область', 'KH': 'Хабаровский край', 'KI': 'Республика Карелия',
            'KK': 'Республика Хакасия', 'KL': 'Республика Калмыкия', 'KM': 'Ханты-Мансийский автономный округ',
            'KN': 'Калининградская область', 'KO': 'Республика Коми', 'KS': 'Курская область',
            'KT': 'Костромская область', 'KU': 'Курганская область', 'KV': 'Кировская область',
            'KY': 'Красноярский край', 'LG': 'Луганская Народная Республика', 'LN': 'Ленинградская область',
            'LP': 'Липецкая область', 'MC': 'Московская область', 'ME': 'Республика Марий Эл',
            'MG': 'Магаданская область', 'MM': 'Мурманская область', 'MR': 'Республика Мордовия',
            'MS': 'Московская область', 'NG': 'Новгородская область', 'NN': 'Ненецкий автономный округ',
            'NO': 'Республика Северная Осетия', 'NS': 'Новосибирская область', 'NZ': 'Нижегородская область',
            'OB': 'Оренбургская область', 'OL': 'Орловская область', 'OM': 'Омская область',
            'PE': 'Пермский край', 'PR': 'Приморский край', 'PS': 'Псковская область',
            'PZ': 'Пензенская область', 'RK': 'Республика Крым', 'RO': 'Ростовская область',
            'RZ': 'Рязанская область', 'SA': 'Самарская область', 'SK': 'Республика Саха (Якутия)',
            'SL': 'Сахалинская область', 'SM': 'Смоленская область', 'SR': 'Саратовская область',
            'ST': 'Ставропольский край', 'SV': 'Свердловская область', 'TB': 'Тамбовская область',
            'TL': 'Тульская область', 'TO': 'Томская область', 'TT': 'Республика Татарстан',
            'TU': 'Республика Тыва', 'TV': 'Тверская область', 'TY': 'Тюменская область',
            'UD': 'Удмуртская Республика', 'UL': 'Ульяновская область', 'VG': 'Волгоградская область',
            'VL': 'Владимирская область', 'VO': 'Вологодская область', 'VR': 'Воронежская область',
            'YN': 'Ямало-Ненецкий автономный округ', 'YS': 'Ярославская область', 'YV': 'Еврейская автономная область',
            'ZK': 'Забайкальский край', 'ZO': 'Запорожская область'
        }

    def _compute_base_planfact_aggregations(self, data, region_col):
        """Вычисляет базовые агрегации для вкладки ПланФакт"""
        
        # Уникальные значения
        all_dsm = sorted(data['DSM'].dropna().unique()) if 'DSM' in data.columns else []
        all_asm = sorted(data['ASM'].dropna().unique()) if 'ASM' in data.columns else []
        all_clients = sorted(data['Клиент'].dropna().unique()) if 'Клиент' in data.columns else []
        
        # Регионы
        if region_col in data.columns:
            unique_codes = data[region_col].dropna().unique()
            region_map = {}
            regions_display = []
            for code in unique_codes:
                long_name = self._get_long_region(code)
                region_map[long_name] = code
                regions_display.append(long_name)
            regions_display.sort()
        else:
            region_map = {}
            regions_display = []
        
        return {
            'raw_data': data.copy(),
            'all_dsm': all_dsm,
            'all_asm': all_asm,
            'all_clients': all_clients,
            'region_map': region_map,
            'regions_display': regions_display
        }

    def _apply_planfact_filters(self, data, dsm_selected, dsm_mode, asm_selected, asm_mode,region_selected, region_mode, client_selected, client_mode, region_col):
        """Применяет фильтры к данным"""
        filtered = data.copy()
        
        # DSM
        if dsm_selected:
            if dsm_mode == 'Включить':
                filtered = filtered[filtered['DSM'].isin(dsm_selected)]
            else:
                filtered = filtered[~filtered['DSM'].isin(dsm_selected)]
        
        # ASM
        if asm_selected:
            if asm_mode == 'Включить':
                filtered = filtered[filtered['ASM'].isin(asm_selected)]
            else:
                filtered = filtered[~filtered['ASM'].isin(asm_selected)]
        
        # Регион
        if region_selected:
            if region_mode == 'Включить':
                filtered = filtered[filtered[region_col].isin(region_selected)]
            else:
                filtered = filtered[~filtered[region_col].isin(region_selected)]
        
        # Клиент
        if client_selected:
            if client_mode == 'Включить':
                filtered = filtered[filtered['Клиент'].isin(client_selected)]
            else:
                filtered = filtered[~filtered['Клиент'].isin(client_selected)]
        
        return filtered

    def _compute_base_region_aggregations(self, data, region_col):
        """Вычисляет базовые агрегации для вкладки Регионы"""
        
        # Уникальные значения
        all_dsm = sorted(data['DSM'].dropna().unique()) if 'DSM' in data.columns else []
        all_asm = sorted(data['ASM'].dropna().unique()) if 'ASM' in data.columns else []
        all_clients = sorted(data['Клиент'].dropna().unique()) if 'Клиент' in data.columns else []
        
        # Регионы
        if region_col in data.columns:
            unique_codes = data[region_col].dropna().unique()
            region_map = {}
            regions_display = []
            for code in unique_codes:
                long_name = self._get_long_region(code)
                region_map[long_name] = code
                regions_display.append(long_name)
            regions_display.sort()
        else:
            region_map = {}
            regions_display = []
        
        return {
            'raw_data': data.copy(),
            'all_dsm': all_dsm,
            'all_asm': all_asm,
            'all_clients': all_clients,
            'region_map': region_map,
            'regions_display': regions_display
        }

    def _compute_base_dsm_aggregations(self, data, region_col):
        """Вычисляет базовые агрегации для вкладки DSM"""
        
        # Уникальные значения
        all_dsm = sorted(data['DSM'].dropna().unique()) if 'DSM' in data.columns else []
        all_asm = sorted(data['ASM'].dropna().unique()) if 'ASM' in data.columns else []
        all_clients = sorted(data['Клиент'].dropna().unique()) if 'Клиент' in data.columns else []
        all_projects = sorted(data['Проект'].dropna().unique()) if 'Проект' in data.columns else []
        all_waves = sorted(data['Волна'].dropna().unique()) if 'Волна' in data.columns else []
        
        # Регионы
        if region_col in data.columns:
            unique_codes = data[region_col].dropna().unique()
            region_map = {}
            regions_display = []
            for code in unique_codes:
                long_name = self._get_long_region(code)
                region_map[long_name] = code
                regions_display.append(long_name)
            regions_display.sort()
        else:
            region_map = {}
            regions_display = []
        
        return {
            'raw_data': data.copy(),
            'all_dsm': all_dsm,
            'all_asm': all_asm,
            'all_clients': all_clients,
            'all_projects': all_projects,
            'all_waves': all_waves,
            'region_map': region_map,
            'regions_display': regions_display
        }

    def _apply_region_filters(self, data, dsm_selected, dsm_mode, asm_selected, asm_mode,
                              region_selected, region_mode, client_selected, client_mode, region_col):
        """Применяет фильтры к данным для вкладки Регионы"""
        filtered = data.copy()
        
        # DSM
        if dsm_selected:
            if dsm_mode == 'Включить':
                filtered = filtered[filtered['DSM'].isin(dsm_selected)]
            else:
                filtered = filtered[~filtered['DSM'].isin(dsm_selected)]
        
        # ASM
        if asm_selected:
            if asm_mode == 'Включить':
                filtered = filtered[filtered['ASM'].isin(asm_selected)]
            else:
                filtered = filtered[~filtered['ASM'].isin(asm_selected)]
        
        # Регион
        if region_selected:
            if region_mode == 'Включить':
                filtered = filtered[filtered[region_col].isin(region_selected)]
            else:
                filtered = filtered[~filtered[region_col].isin(region_selected)]
        
        # Клиент
        if client_selected:
            if client_mode == 'Включить':
                filtered = filtered[filtered['Клиент'].isin(client_selected)]
            else:
                filtered = filtered[~filtered['Клиент'].isin(client_selected)]
        
        return filtered
    

    def _apply_dsm_filters(self, data, dsm_selected, dsm_mode, asm_selected, asm_mode,
                           client_selected, client_mode, region_selected, region_mode, region_col):
        """Применяет фильтры к данным для вкладки DSM"""
        filtered = data.copy()
        
        # DSM
        if dsm_selected:
            if dsm_mode == 'Включить':
                filtered = filtered[filtered['DSM'].isin(dsm_selected)]
            else:
                filtered = filtered[~filtered['DSM'].isin(dsm_selected)]
        
        # ASM
        if asm_selected:
            if asm_mode == 'Включить':
                filtered = filtered[filtered['ASM'].isin(asm_selected)]
            else:
                filtered = filtered[~filtered['ASM'].isin(asm_selected)]
        
        # Клиент
        if client_selected:
            if client_mode == 'Включить':
                filtered = filtered[filtered['Клиент'].isin(client_selected)]
            else:
                filtered = filtered[~filtered['Клиент'].isin(client_selected)]
        
        # Регион
        if region_selected:
            if region_mode == 'Включить':
                filtered = filtered[filtered[region_col].isin(region_selected)]
            else:
                filtered = filtered[~filtered[region_col].isin(region_selected)]
        
        return filtered
                               

    def _get_long_region(self, short_code):
        if pd.isna(short_code) or short_code == '':
            return short_code
        clean_code = str(short_code).strip().upper().replace('\xa0', ' ').strip()
        return self.region_mapping.get(clean_code, short_code)

    # def create_project_summary(self, df):
    #     """
    #     Агрегация данных по проектам
    #     Одна строка = один проект
    #     """
    #     if df is None or df.empty:
    #         return pd.DataFrame()
        
    #     # Проверяем наличие колонки 'Проект'
    #     project_col = 'Проект'
    #     if project_col not in df.columns:
    #         st.error(f"❌ В данных нет колонки '{project_col}'")
    #         return pd.DataFrame()
        
    #     # Список колонок для агрегации
    #     agg_columns = {
    #         'План проекта, шт.': 'sum',
    #         'План на дату, шт.': 'sum',
    #         'Факт проекта, шт.': 'sum',
    #         'Факт на дату, шт.': 'sum',
    #         'Длительность': 'first',
    #         'Дата старта': 'first',
    #         'Дата финиша': 'first',
    #         'Клиент': 'first',
    #         'ПО': 'first',
    #         'Дней до конца проекта': 'first',
    #         'Утилизация тайминга, %': 'first',
    #         'Ср. план на день для 100% плана': 'sum'
    #     }
        
    #     # Только существующие колонки
    #     existing_agg = {k: v for k, v in agg_columns.items() if k in df.columns}
        
    #     # Группируем по проекту
    #     project_agg = df.groupby(project_col).agg(existing_agg).reset_index()
        
    #     # 1. План/Факт на дату,% (было Исполнение проекта,%)
    #     project_agg['План/Факт на дату,%'] = 0.0
    #     mask_plan = project_agg['План на дату, шт.'] > 0
    #     if mask_plan.any():
    #         project_agg.loc[mask_plan, 'План/Факт на дату,%'] = (
    #             project_agg.loc[mask_plan, 'Факт на дату, шт.'] / 
    #             project_agg.loc[mask_plan, 'План на дату, шт.'] * 100
    #         ).round(1)
        
    #     # 2. △План/Факт на дату, шт (исправленная формула: Факт - План)
    #     project_agg['△План/Факт на дату, шт'] = (
    #         project_agg['Факт на дату, шт.'] - project_agg['План на дату, шт.']
    #     ).round(1)
        
    #     # 3. △План/Факт на дату, % (исправленная формула)
    #     project_agg['△План/Факт на дату, %'] = 0.0
    #     if mask_plan.any():
    #         project_agg.loc[mask_plan, '△План/Факт на дату, %'] = (
    #             (project_agg.loc[mask_plan, 'Факт на дату, шт.'] / 
    #              project_agg.loc[mask_plan, 'План на дату, шт.']) - 1
    #         ).round(3) * 100
        
    #     # 4. Исполнение проекта,% (было %ПФ проекта)
    #     project_agg['План/Факт проекта,%'] = 0.0
    #     mask_project_plan = project_agg['План проекта, шт.'] > 0
    #     if mask_project_plan.any():
    #         project_agg.loc[mask_project_plan, 'План/Факт проекта,%'] = (
    #             project_agg.loc[mask_project_plan, 'Факт проекта, шт.'] / 
    #             project_agg.loc[mask_project_plan, 'План проекта, шт.'] * 100
    #         ).round(1)
        
    #     # 5. Прогноз на месяц, шт.
    #     if 'plan_calc_params' in st.session_state:
    #         days_in_period = (st.session_state['plan_calc_params']['end_date'] - 
    #                         st.session_state['plan_calc_params']['start_date']).days + 1
    #     else:
    #         days_in_period = 12
            
    #     project_agg['Прогноз на месяц, шт.'] = (
    #         project_agg['Факт на дату, шт.'] / days_in_period * 28
    #     ).round(1)
        
    #     # 6. Фокус
    #     project_agg['Фокус'] = 'Нет'
    #     if all(col in project_agg.columns for col in ['План/Факт проекта,%', 'Утилизация тайминга, %']):
    #         mask_focus = (
    #             (project_agg['План/Факт проекта,%'] < 80) & 
    #             (project_agg['Утилизация тайминга, %'] > 80) & 
    #             (project_agg['Утилизация тайминга, %'] < 100)
    #         )
    #         project_agg.loc[mask_focus, 'Фокус'] = 'Да'
        
    #     # Сортируем по План/Факт на дату,%
    #     project_agg = project_agg.sort_values('План/Факт на дату,%', ascending=True)
        
    #     return project_agg
    
    def create_planfact_tab(self, data, hierarchy_df=None):
        """Создает вкладку ПланФакт на дату с фильтрами в форме"""
        if data is None or data.empty:
            st.warning("⚠️ Нет данных для отчета")
            return
        
        st.subheader("📊 Сводка по проектам")
        
        # Переименовываем колонки
        rename_cols = {'ЗОД': 'DSM', 'АСС': 'ASM', 'ЭМ': 'RS'}
        data = data.rename(columns=rename_cols)
        
        region_col = 'Регион'
        if 'Регион short' in data.columns and 'Регион' not in data.columns:
            region_col = 'Регион short'
        
        # ============================================
        # 1. БАЗОВЫЕ АГРЕГАЦИИ (один раз за сессию)
        # ============================================
        
        data_hash = hash(data.values.tobytes()) if not data.empty else 0
        
        if 'planfact_base_data' not in st.session_state or st.session_state.get('planfact_data_hash') != data_hash:
            base_agg = self._compute_base_planfact_aggregations(data, region_col)
            st.session_state.planfact_base_data = base_agg
            st.session_state.planfact_data_hash = data_hash
            st.session_state.planfact_filtered_data = None
        
        base_data = st.session_state.planfact_base_data
        
        # ============================================
        # 2. ФИЛЬТРЫ В ФОРМЕ
        # ============================================
        
        with st.form("planfact_filters_form"):
            
            all_dsm = base_data['all_dsm']
            all_asm = base_data['all_asm']
            all_clients = base_data['all_clients']
            all_regions_display = base_data['regions_display']
            region_map = base_data['region_map']
            
            st.markdown("### 🔍 Фильтры")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**DSM**")
                dsm_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="planfact_dsm_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('planfact_dsm_mode', 'Включить') == 'Включить' else 1
                )
                dsm_mode = st.session_state.planfact_dsm_mode
                
                dsm_selected = st.multiselect(
                    "Выбрать DSM",
                    all_dsm,
                    key="planfact_dsm_values",
                    default=[]
                )
            
            with col2:
                st.markdown("**ASM**")
                asm_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="planfact_asm_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('planfact_asm_mode', 'Включить') == 'Включить' else 1
                )
                asm_mode = st.session_state.planfact_asm_mode
                
                asm_options = all_asm
                asm_selected = st.multiselect(
                    "Выбрать ASM",
                    asm_options,
                    key="planfact_asm_values",
                    default=[]
                )
            
            with col3:
                st.markdown("**Регион**")
                region_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="planfact_region_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('planfact_region_mode', 'Включить') == 'Включить' else 1
                )
                region_mode = st.session_state.planfact_region_mode
                
                region_selected_display = st.multiselect(
                    "Выбрать регион",
                    all_regions_display,
                    key="planfact_region_values",
                    default=[]
                )
                region_selected = [region_map.get(name, name) for name in region_selected_display]
            
            with col4:
                st.markdown("**Клиент**")
                client_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="planfact_client_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('planfact_client_mode', 'Включить') == 'Включить' else 1
                )
                client_mode = st.session_state.planfact_client_mode
                
                client_filtered = all_clients
                
                client_selected = st.multiselect(
                    "Выбрать клиента",
                    client_filtered,
                    key="planfact_client_values",
                    default=[]
                )
            
            st.markdown("---")
            
            apply_filters = st.form_submit_button(
                "✅ Применить фильтры",
                type="primary",
                use_container_width=True,
                key="planfact_apply_filters_btn"
            )
        
        # ============================================
        # 3. ПРИМЕНЯЕМ ФИЛЬТРЫ
        # ============================================
        
        if apply_filters:
            filtered_data = self._apply_planfact_filters(
                base_data['raw_data'],
                dsm_selected, st.session_state.planfact_dsm_mode,
                asm_selected, st.session_state.planfact_asm_mode,
                region_selected, st.session_state.planfact_region_mode,
                client_selected, st.session_state.planfact_client_mode,
                region_col
            )
            st.session_state.planfact_filtered_data = filtered_data
        
        if st.session_state.planfact_filtered_data is not None:
            display_data = st.session_state.planfact_filtered_data
        else:
            display_data = base_data['raw_data']

        # ФИЛЬТР ПО КОЛОНКЕ "ПРОДЛЕНИЕ"
        if st.session_state.get('planfact_include_prodlenie', False):
            if 'Продление' in display_data.columns:
                display_data = display_data[display_data['Продление'] == 1]
            else:
                st.warning("⚠️ Колонка 'Продление' не найдена в данных")
        
        # ============================================
        # 4. РАЗВЕРТКА
        # ============================================
        
        st.subheader("📊 Детализация")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            show_project = st.checkbox("Код проекта", key='planfact_show_project')
        with col2:
            show_wave = st.checkbox("Волна", key='planfact_show_wave')
        with col3:
            show_regions = st.checkbox("Регионы", key='planfact_show_regions')
        with col4:
            show_dsm = st.checkbox("DSM", key='planfact_show_dsm')
        with col5:
            show_asm = st.checkbox("ASM", key='planfact_show_asm')
        with col6:
            show_rs = st.checkbox("RS", key='planfact_show_rs')
        with col7:
            show_po = st.checkbox("ПО", key='planfact_show_po')
        
        # Формируем groupby в зависимости от чек-боксов
        group_cols = ['Клиент']
        
        if show_project and 'Проект' in display_data.columns:
            group_cols.append('Проект')
        if show_wave and 'Волна' in display_data.columns:
            group_cols.append('Волна')
        if show_regions and region_col in display_data.columns:
            group_cols.append(region_col)
        if show_dsm and 'DSM' in display_data.columns:
            group_cols.append('DSM')
        if show_asm and 'ASM' in display_data.columns:
            group_cols.append('ASM')
        if show_rs and 'RS' in display_data.columns:
            group_cols.append('RS')
        if show_po and 'ПО' in display_data.columns:
            group_cols.append('ПО')

        display_data = self.calculate_focus(display_data, aggregation_level='wave')
        
        agg_columns = {
            'План проекта, шт.': 'sum',
            'План на дату, шт.': 'sum',
            'Факт проекта, шт.': 'sum',
            'Факт на дату, шт.': 'sum',
            'Длительность': 'first',
            'Дата старта': 'first',
            'Дата финиша': 'first',
            'Дата старта_гугл': 'first',
            'Дата финиша_гугл': 'first',
            'Коэффициент месяца': 'first',
            'Метод подбора дат': 'first',
            'Дней до конца проекта': 'first',
            'Прогноз, шт.': 'sum',
            'Утилизация тайминга, %': 'first',
            'Ср. план на день для 100% плана': 'sum',
            'Фокус': 'first',
            'Оплата план': 'sum',
            'plan_payment_per_visit': 'first',
            'Оплата факт': 'sum',
            'Оплата_поручено': 'sum',
            'Факт проекта_поручено, шт.': 'sum',
            'Факт проекта_не_поручено, шт.': 'sum',
            'Оплата план средн., руб.': 'first',
            'Оплата факт средн., руб.': 'first',
            'Оплата план-факт средн., руб.': 'first',
            'Оплата факт/план средн., %': 'first',
            'Оплата средн. в динамике, руб.': 'first',
            'Оплата средн. прогноз, руб.': 'first',
            'Клиент_дата_старта': 'first',
            'Клиент_дата_финиша': 'first',
            'Клиент_длительность': 'first',
            'Продление': 'first',
            'RS': 'nunique',
        }
        
        existing_agg = {k: v for k, v in agg_columns.items() if k in display_data.columns}

        project_data = display_data.groupby(group_cols).agg(existing_agg).reset_index()
        
        # Кол-во анкет на 1 RS = Факт проекта / кол-во уникальных RS
        if 'RS' in project_data.columns and 'Факт проекта, шт.' in project_data.columns:
            project_data['Кол-во анкет на 1 RS, шт.'] = 0.0
            mask_rs = project_data['RS'] > 0
            if mask_rs.any():
                project_data.loc[mask_rs, 'Кол-во анкет на 1 RS, шт.'] = (
                    project_data.loc[mask_rs, 'Факт проекта, шт.'] / project_data.loc[mask_rs, 'RS']
                ).round(1)

        if group_cols == ['Клиент']:
            if 'Клиент_дата_старта' in project_data.columns:
                project_data['Дата старта'] = project_data['Клиент_дата_старта']
                project_data['Дата финиша'] = project_data['Клиент_дата_финиша']
                project_data['Длительность'] = project_data['Клиент_длительность']

        if 'Оплата план' in project_data.columns and 'План проекта, шт.' in project_data.columns:
            mask_plan_positive = project_data['План проекта, шт.'] > 0
            project_data['Оплата план средн., руб.'] = 0.0
            if mask_plan_positive.any():
                project_data.loc[mask_plan_positive, 'Оплата план средн., руб.'] = (
                    project_data.loc[mask_plan_positive, 'Оплата план'] / 
                    project_data.loc[mask_plan_positive, 'План проекта, шт.']
                ).round(2)

        if 'Оплата факт' in project_data.columns and 'Факт проекта, шт.' in project_data.columns:
            mask_fact_positive = project_data['Факт проекта, шт.'] > 0
            project_data['Оплата факт средн., руб.'] = 0.0
            if mask_fact_positive.any():
                project_data.loc[mask_fact_positive, 'Оплата факт средн., руб.'] = (
                    project_data.loc[mask_fact_positive, 'Оплата факт'] / 
                    project_data.loc[mask_fact_positive, 'Факт проекта, шт.']
                ).round(2)
        
        forecast_col = None
        if 'Прогноз, шт' in project_data.columns:
            forecast_col = 'Прогноз, шт'
        elif 'Прогноз, шт.' in project_data.columns:
            forecast_col = 'Прогноз, шт.'
        
        if 'Оплата план средн., руб.' in project_data.columns and 'Оплата факт средн., руб.' in project_data.columns:
            project_data['Оплата план-факт средн., руб.'] = (
                project_data['Оплата план средн., руб.'] - project_data['Оплата факт средн., руб.']
            ).round(2)
        
        if 'Оплата план средн., руб.' in project_data.columns and 'Оплата факт средн., руб.' in project_data.columns:
            mask = project_data['Оплата план средн., руб.'] > 0
            project_data['Оплата факт/план средн., %'] = 0.0
            if mask.any():
                project_data.loc[mask, 'Оплата факт/план средн., %'] = (
                    project_data.loc[mask, 'Оплата факт средн., руб.'] / 
                    project_data.loc[mask, 'Оплата план средн., руб.'] * 100
                ).round(1)
        
        if forecast_col and 'Оплата план средн., руб.' in project_data.columns and 'Оплата факт средн., руб.' in project_data.columns:
            project_data['Оплата средн. в динамике, руб.'] = (
                (project_data['Оплата план средн., руб.'] - project_data['Оплата факт средн., руб.']) * 
                project_data[forecast_col]
            ).round(2)
        
        if 'Оплата план средн., руб.' in project_data.columns and 'Оплата факт средн., руб.' in project_data.columns and 'План проекта, шт.' in project_data.columns:
            project_data['Оплата средн. прогноз, руб.'] = (
                (project_data['Оплата план средн., руб.'] - project_data['Оплата факт средн., руб.']) * 
                project_data['План проекта, шт.']
            ).round(2)
        
        if 'Прогноз, шт' not in project_data.columns and 'Прогноз, шт.' in project_data.columns:
            project_data['Прогноз, шт'] = project_data['Прогноз, шт.']
        
        if 'Прогноз ВП, %' not in project_data.columns:
            if 'Прогноз, шт' in project_data.columns and 'План проекта, шт.' in project_data.columns:
                mask = project_data['План проекта, шт.'] > 0
                project_data['Прогноз ВП, %'] = 0.0
                project_data.loc[mask, 'Прогноз ВП, %'] = (
                    project_data.loc[mask, 'Прогноз, шт'] / 
                    project_data.loc[mask, 'План проекта, шт.'] * 100
                ).round(1)
        
        if 'Отклонение от плана на сегодня, шт.' not in project_data.columns:
            if 'Факт проекта, шт.' in project_data.columns and 'План на дату, шт.' in project_data.columns:
                project_data['Отклонение от плана на сегодня, шт.'] = (
                    project_data['Факт проекта, шт.'] - project_data['План на дату, шт.']
                ).round(1)

        if 'Факт ВП, %' not in project_data.columns:
            if 'Факт проекта, шт.' in project_data.columns and 'План проекта, шт.' in project_data.columns:
                mask = project_data['План проекта, шт.'] > 0
                project_data['Факт ВП, %'] = 0.0
                project_data.loc[mask, 'Факт ВП, %'] = (
                    project_data.loc[mask, 'Факт проекта, шт.'] / 
                    project_data.loc[mask, 'План проекта, шт.'] * 100
                ).round(1)
        
        if 'Оплата факт' in project_data.columns and 'Факт проекта, шт.' in project_data.columns:
            mask = project_data['Факт проекта, шт.'] > 0
            project_data['Оплата факт средн., руб.'] = 0.0
            project_data.loc[mask, 'Оплата факт средн., руб.'] = (
                project_data.loc[mask, 'Оплата факт'] / project_data.loc[mask, 'Факт проекта, шт.']
            ).round(2)
            project_data = project_data.drop('Оплата факт', axis=1)

        if 'Оплата_поручено' in project_data.columns and 'Факт проекта_поручено, шт.' in project_data.columns:
            mask_assigned = project_data['Факт проекта_поручено, шт.'] > 0
            project_data['Оплата поручено средн., руб.'] = 0.0
            project_data.loc[mask_assigned, 'Оплата поручено средн., руб.'] = (
                project_data.loc[mask_assigned, 'Оплата_поручено'] / project_data.loc[mask_assigned, 'Факт проекта_поручено, шт.']
            ).round(2)

        remaining_plan = project_data['План проекта, шт.'] - project_data['Факт проекта, шт.']
        remaining_plan = remaining_plan.clip(lower=0)
        days_left = project_data['Дней до конца проекта'].replace(0, 1)
        
        project_data['Ср. план на день для 100% плана'] = (
            np.ceil(remaining_plan / days_left)
        ).astype(int)
        
        if 'Регион' in project_data.columns:
            project_data['Регион'] = project_data['Регион'].apply(self._get_long_region)
        elif region_col in project_data.columns and region_col != 'Регион':
            project_data[region_col] = project_data[region_col].apply(self._get_long_region)
            
        mask_plan = project_data['План на дату, шт.'] > 0
        project_data['План/Факт на дату,%'] = 0.0
        if mask_plan.any():
            project_data.loc[mask_plan, 'План/Факт на дату,%'] = (
                project_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                project_data.loc[mask_plan, 'План на дату, шт.'] * 100
            ).round(1)
        
        mask_project_plan = project_data['План проекта, шт.'] > 0
        project_data['План/Факт проекта,%'] = 0.0
        if mask_project_plan.any():
            project_data.loc[mask_project_plan, 'План/Факт проекта,%'] = (
                project_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                project_data.loc[mask_project_plan, 'План проекта, шт.'] * 100
            ).round(1)
        
        project_data['△План/Факт на дату, шт'] = (
            project_data['Факт на дату, шт.'] - project_data['План на дату, шт.']
        ).round(1)
        
        project_data['△План/Факт на дату, %'] = 0.0
        if mask_plan.any():
            project_data.loc[mask_plan, '△План/Факт на дату, %'] = (
                (project_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                 project_data.loc[mask_plan, 'План на дату, шт.']) - 1
            ).round(3) * 100

        project_data['△План/Факт проекта, шт'] = (
            project_data['Факт проекта, шт.'] - project_data['План проекта, шт.']
        ).round(1)
        
        mask_project_plan = project_data['План проекта, шт.'] > 0
        project_data['△План/Факт проекта, %'] = 0.0
        if mask_project_plan.any():
            project_data.loc[mask_project_plan, '△План/Факт проекта, %'] = (
                (project_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                 project_data.loc[mask_project_plan, 'План проекта, шт.']) - 1
            ).round(3) * 100
        
        # KPI
        st.markdown("### 📊 Ключевые показатели")
        
        col_kpi1, col_kpi2, col_kpi3, col_checkbox1, col_checkbox2, col_checkbox3 = st.columns([1, 1, 1, 0.3, 0.3, 0.3])
        with col_checkbox1:
            include_prodata = st.checkbox("📊 Продата", key="planfact_include_prodata")
        with col_checkbox2:
            include_prodlenie = st.checkbox("🔄 Продление", key="planfact_include_prodlenie")
        with col_checkbox3:
            include_retro = st.checkbox("🔄 Ретро", key="planfact_include_retro")
        
        prodata_df = st.session_state.cleaned_data.get('prodata_processed', None)
        
        prodata_plan_total = 0
        prodata_fact_total = 0
        prodata_plan_date_total = 0
        prodata_fact_date_total = 0
        
        if include_prodata and prodata_df is not None and not prodata_df.empty:
            if 'План проекта, шт.' in prodata_df.columns:
                prodata_plan_total = prodata_df['План проекта, шт.'].sum()
            if 'Факт проекта, шт.' in prodata_df.columns:
                prodata_fact_total = prodata_df['Факт проекта, шт.'].sum()
            if 'План на дату, шт.' in prodata_df.columns:
                prodata_plan_date_total = prodata_df['План на дату, шт.'].sum()
            if 'Факт на дату, шт.' in prodata_df.columns:
                prodata_fact_date_total = prodata_df['Факт на дату, шт.'].sum()
        
        plan_total = project_data['План проекта, шт.'].sum() if 'План проекта, шт.' in project_data.columns else 0
        fact_total = project_data['Факт проекта, шт.'].sum() if 'Факт проекта, шт.' in project_data.columns else 0
        plan_date_total = project_data['План на дату, шт.'].sum() if 'План на дату, шт.' in project_data.columns else 0
        fact_date_total = project_data['Факт на дату, шт.'].sum() if 'Факт на дату, шт.' in project_data.columns else 0
        assigned_total = project_data['Факт проекта_поручено, шт.'].sum() if 'Факт проекта_поручено, шт.' in project_data.columns else 0
        
        if include_prodata:
            plan_total += prodata_plan_total
            fact_total += prodata_fact_total
            plan_date_total += prodata_plan_date_total
            fact_date_total += prodata_fact_date_total
        
        deviation = fact_total - plan_date_total
        pf_percent = (fact_total / plan_total * 100) if plan_total > 0 else 0
        
        if 'Прогноз, шт.' in project_data.columns:
            forecast_total = project_data['Прогноз, шт.'].sum()
        else:
            forecast_total = 0
        
        if include_prodata and prodata_df is not None and not prodata_df.empty:
            if 'Прогноз, шт.' in prodata_df.columns:
                forecast_total += prodata_df['Прогноз, шт.'].sum()
        
        forecast_percent = (forecast_total / plan_total * 100) if plan_total > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 План проекта", f"{plan_total:,.0f} шт")
        with col2:
            st.metric("✅ Факт проекта", f"{fact_total:,.0f} шт")
        with col3:
            st.metric("🎯 Факт ВП, %", f"{pf_percent:.1f}%")
        
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("📉 Отклонение от плана на сегодня, шт", f"{deviation:+,.0f}")
        with col5:
            st.metric("📋 Факт поручено, шт", f"{assigned_total:,.0f}")
        with col6:
            st.metric("🔮 Прогноз ВП, %", f"{forecast_percent:.1f}%")
        
        # ============================================
        # 5. ОТОБРАЖЕНИЕ
        # ============================================
        
        if not include_retro:
            # ============================================
            # ДЕФОЛТНЫЙ РЕЖИМ (без ретро)
            # ============================================
            
            display_cols = ['Клиент']
            
            if show_project and 'Проект' in project_data.columns:
                display_cols.append('Проект')
            if show_wave and 'Волна' in project_data.columns:
                display_cols.append('Волна')
            if show_regions and region_col in project_data.columns:
                display_cols.append(region_col)
            if show_dsm and 'DSM' in project_data.columns:
                display_cols.append('DSM')
            if show_asm and 'ASM' in project_data.columns:
                display_cols.append('ASM')
            if show_rs and 'RS' in project_data.columns:
                display_cols.append('RS')
            if show_po and 'ПО' in project_data.columns:
                display_cols.append('ПО')
            
            always_show = [
                'План проекта, шт.', 
                'Факт проекта, шт.',
                'План на дату, шт.',
                'Факт на дату, шт.',
                'План/Факт проекта,%',
                '△План/Факт проекта, шт',
                '△План/Факт проекта, %',
                'План/Факт на дату,%',
                '△План/Факт на дату, шт',
                '△План/Факт на дату, %',
                'Фокус',
                'Прогноз на месяц, шт.',
                'Длительность',
                'Дней до конца проекта',
                'Утилизация тайминга, %',
                'Ср. план на день для 100% плана',
                'Метод подбора дат',
                'Оплата план',
                'Оплата план средн., руб.',
                'Оплата факт средн., руб.',
                'Оплата план-факт средн., руб.',
                'Оплата факт/план средн., %',
                'Оплата средн. в динамике, руб.',
                'Оплата средн. прогноз, руб.',
                'Оплата поручено средн., руб.',
                'Факт проекта_поручено, шт.',
                'Факт проекта_не_поручено, шт.',
                'RS',
                'Кол-во анкет на 1 RS, шт.',
            ]
            
            for col in always_show:
                if col in project_data.columns:
                    display_cols.append(col)
            
            existing_display = [c for c in display_cols if c in project_data.columns]
            
            st.dataframe(project_data[existing_display], use_container_width=True, hide_index=True)
        
        else:
            # ============================================
            # РЕЖИМ С РЕТРО
            # ============================================
            
            analytics_df = st.session_state.get('analytics_df')
            retro_available = analytics_df is not None and not analytics_df.empty
            
            # Один раз группируем analytics_df по нормализованному клиенту
            retro_by_client = {}
            if retro_available and 'Клиент' in analytics_df.columns:
                analytics_df_norm = analytics_df.copy()
                analytics_df_norm['_client_norm'] = analytics_df_norm['Клиент'].astype(str).str.strip()
                retro_by_client = {k: v for k, v in analytics_df_norm.groupby('_client_norm')}
            
            project_data_sorted = project_data.copy()
            
            rows = []
            
            for _, current_row in project_data_sorted.iterrows():
                client_name = str(current_row['Клиент']).strip()
                
                # 1. Строка 'текущий'
                current_dict = current_row.to_dict()
                current_dict['Клиент'] = client_name
                current_dict['Период'] = 'текущий'
                rows.append(current_dict)
                
                # 2. Строка 'ретро'
                retro_row = {c: None for c in current_row.index}
                retro_row['Клиент'] = ''
                retro_row['Период'] = 'ретро'
                
                client_retro_df = retro_by_client.get(client_name)
                
                if client_retro_df is not None and not client_retro_df.empty:
                    pairs = sorted(set(
                        (int(y), int(m)) for y, m in client_retro_df[['Год', 'Месяц']]
                        .dropna().itertuples(index=False, name=None)
                    ))
                    
                    if pairs:
                        y_min, m_min = pairs[0]
                        y_max, m_max = pairs[-1]
                        months_list = []
                        y, m = y_min, m_min
                        while (y, m) <= (y_max, m_max):
                            months_list.append((y, m))
                            if m == 12:
                                y, m = y + 1, 1
                            else:
                                m += 1
                    else:
                        months_list = []
                    
                    if months_list:
                        kpi = self._compute_kpi_retro(client_retro_df, months_list)
                        retro_row['План проекта, шт.'] = kpi['plan_avg']
                        retro_row['Факт проекта, шт.'] = kpi['fact_avg']
                        retro_row['План/Факт проекта,%'] = kpi['pf_percent']
                        retro_row['RS'] = kpi['rs_count_avg']
                        retro_row['Кол-во анкет на 1 RS, шт.'] = kpi['ankets_per_rs']
                rows.append(retro_row)
            
            extended_df = pd.DataFrame(rows)
            
            # Нормализация ТОЛЬКО числовых колонок (даты не трогаем!)
            numeric_cols_ext = [
                'План проекта, шт.', 'План на дату, шт.', 'Факт проекта, шт.', 'Факт на дату, шт.',
                'Длительность', 'Коэффициент месяца', 'Дней до конца проекта', 'Прогноз, шт.',
                'Утилизация тайминга, %',
                'Факт проекта_поручено, шт.', 'Факт проекта_не_поручено, шт.',
                'Оплата факт средн., руб.', 'Клиент_длительность',
                'Продление',
                'Прогноз, шт', 'Прогноз ВП, %',
                'Отклонение от плана на сегодня, шт.', 'Факт ВП, %',
                'Оплата поручено средн., руб.',
                'Ср. план на день для 100% плана',
                'План/Факт на дату,%', 'План/Факт проекта,%',
                '△План/Факт на дату, шт', '△План/Факт на дату, %',
                '△План/Факт проекта, шт', '△План/Факт проекта, %',
                'RS','Кол-во анкет на 1 RS, шт.',
            ]
            
            for c in numeric_cols_ext:
                if c in extended_df.columns:
                    extended_df[c] = pd.to_numeric(extended_df[c], errors='coerce')
            
            # Порядок колонок: Клиент | Период | развертки | always_show
            display_cols = ['Клиент', 'Период']
            
            if show_project and 'Проект' in extended_df.columns:
                display_cols.append('Проект')
            if show_wave and 'Волна' in extended_df.columns:
                display_cols.append('Волна')
            if show_regions and region_col in extended_df.columns:
                display_cols.append(region_col)
            if show_dsm and 'DSM' in extended_df.columns:
                display_cols.append('DSM')
            if show_asm and 'ASM' in extended_df.columns:
                display_cols.append('ASM')
            if show_rs and 'RS' in extended_df.columns:
                display_cols.append('RS')
            if show_po and 'ПО' in extended_df.columns:
                display_cols.append('ПО')
            
            always_show = [
                'План проекта, шт.', 
                'Факт проекта, шт.',
                'План на дату, шт.',
                'Факт на дату, шт.',
                'План/Факт проекта,%',
                '△План/Факт проекта, шт',
                '△План/Факт проекта, %',
                'План/Факт на дату,%',
                '△План/Факт на дату, шт',
                '△План/Факт на дату, %',
                'Фокус',
                'Прогноз на месяц, шт.',
                'Длительность',
                'Дней до конца проекта',
                'Утилизация тайминга, %',
                'Ср. план на день для 100% плана',
                'Метод подбора дат',
                'Оплата план',
                'Оплата план средн., руб.',
                'Оплата факт средн., руб.',
                'Оплата план-факт средн., руб.',
                'Оплата факт/план средн., %',
                'Оплата средн. в динамике, руб.',
                'Оплата средн. прогноз, руб.',
                'Оплата поручено средн., руб.',
                'Факт проекта_поручено, шт.',
                'Факт проекта_не_поручено, шт.',
                'RS',
                'Кол-во анкет на 1 RS, шт.',
            ]
            
            for col in always_show:
                if col in extended_df.columns:
                    display_cols.append(col)
            
            existing_display = [c for c in display_cols if c in extended_df.columns]
            
            st.dataframe(extended_df[existing_display], use_container_width=True, hide_index=True)
        
        # ============================================
        # 6. СКАЧИВАНИЕ (project_data, без ретро)
        # ============================================
        
        cols_to_drop = ['Оплата_поручено']
        for col in cols_to_drop:
            if col in project_data.columns:
                project_data = project_data.drop(col, axis=1)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            project_data.to_excel(writer, sheet_name='План_факт_проекты', index=False)
        
        st.download_button(
            label="⬇️ Скачать Excel",
            data=output.getvalue(),
            file_name=f"план_факт_проекты_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
        
        brief_cols = [
            'Клиент',
            'План проекта, шт.',
            'Факт проекта, шт.',
            'Факт ВП, %',
            'Факт проекта_поручено, шт.',
            'Факт проекта_не_поручено, шт.',
            'Длительность',
            'Дата старта',
            'Дата финиша',
            'Дней до конца проекта',
            'Прогноз, шт',
            'Прогноз ВП, %',
            'Отклонение от плана на сегодня, шт.',
            'Ср. план на день для 100% плана',
            'Оплата план',
            'Оплата план средн., руб.',
            'Оплата факт средн., руб.',
            'Оплата план-факт средн., руб.',
            'Оплата факт/план средн., %',
            'Оплата средн. в динамике, руб.',
            'Оплата средн. прогноз, руб.',
            'Оплата поручено средн., руб.',
            'RS',
            'Кол-во анкет на 1 RS, шт.',
        ]
        
        existing_brief_cols = [col for col in brief_cols if col in project_data.columns]
        brief_report = project_data[existing_brief_cols].copy()
        
        output_brief = BytesIO()
        with pd.ExcelWriter(output_brief, engine='openpyxl') as writer:
            brief_report.to_excel(writer, sheet_name='Краткий_отчет', index=False)
        
        st.download_button(
            label="📊 Скачать краткий отчет",
            data=output_brief.getvalue(),
            file_name=f"краткий_отчет_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True,
            key="download_brief_planfact" 
        )

    def create_region_summary(self, df):
        """
        Агрегация данных по регионам
        Одна строка = один регион
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        region_col = 'Регион'
        if 'Регион short' in df.columns and 'Регион' not in df.columns:
            region_col = 'Регион short'
        
        if region_col not in df.columns:
            st.error(f"❌ В данных нет колонки региона")
            return pd.DataFrame()
        
        agg_columns = {
            'План проекта, шт.': 'sum',
            'План на дату, шт.': 'sum',
            'Факт проекта, шт.': 'sum',
            'Факт на дату, шт.': 'sum',
            'Длительность': 'mean',
            'Клиент': lambda x: ', '.join(x.dropna().unique()[:3]),
            'Проект': 'nunique',
            'RS': 'nunique',
            'ПО': lambda x: ', '.join(x.dropna().unique()[:3])
        }
        
        existing_agg = {}
        for k, v in agg_columns.items():
            if k in df.columns:
                existing_agg[k] = v
        
        region_agg = df.groupby(region_col).agg(existing_agg).reset_index()
        region_agg = region_agg.rename(columns={region_col: 'Регион'})
        
        rename_map = {'Проект': 'Кол-во проектов', 'RS': 'Кол-во сотрудников'}
        region_agg = region_agg.rename(columns=rename_map)
        
        region_agg['План/Факт на дату,%'] = 0.0
        mask_plan = region_agg['План на дату, шт.'] > 0
        if mask_plan.any():
            region_agg.loc[mask_plan, 'План/Факт на дату,%'] = (
                region_agg.loc[mask_plan, 'Факт на дату, шт.'] / 
                region_agg.loc[mask_plan, 'План на дату, шт.'] * 100
            ).round(1)
        
        region_agg['План/Факт проекта,%'] = 0.0
        mask_project_plan = region_agg['План проекта, шт.'] > 0
        if mask_project_plan.any():
            region_agg.loc[mask_project_plan, 'План/Факт проекта,%'] = (
                region_agg.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                region_agg.loc[mask_project_plan, 'План проекта, шт.'] * 100
            ).round(1)
        
        region_agg['△План/Факт на дату, шт'] = (
            region_agg['Факт на дату, шт.'] - region_agg['План на дату, шт.']
        ).round(1)
        
        region_agg['△План/Факт на дату, %'] = 0.0
        if mask_plan.any():
            region_agg.loc[mask_plan, '△План/Факт на дату, %'] = (
                (region_agg.loc[mask_plan, 'Факт на дату, шт.'] / 
                 region_agg.loc[mask_plan, 'План на дату, шт.']) - 1
            ).round(3) * 100
        
        if 'plan_calc_params' in st.session_state:
            days_in_period = (st.session_state['plan_calc_params']['end_date'] - 
                            st.session_state['plan_calc_params']['start_date']).days + 1
        else:
            days_in_period = 12
            
        region_agg['Прогноз на месяц, шт.'] = (
            region_agg['Факт на дату, шт.'] / days_in_period * 28
        ).round(1)
        
        region_agg = region_agg.sort_values('Регион')
        return region_agg
        
    def create_region_tab(self, data, hierarchy_df=None):
        """Создает вкладку Регионы с фильтрами в форме"""
        if data is None or data.empty:
            st.warning("⚠️ Нет данных для отчета")
            return
        
        st.subheader("📊 Сводка по регионам")
        
        # Переименовываем колонки
        rename_cols = {'ЗОД': 'DSM', 'АСС': 'ASM', 'ЭМ': 'RS'}
        data = data.rename(columns=rename_cols)
        
        region_col = 'Регион'
        if 'Регион short' in data.columns and 'Регион' not in data.columns:
            region_col = 'Регион short'
        
        # ============================================
        # 1. БАЗОВЫЕ АГРЕГАЦИИ (один раз за сессию)
        # ============================================
        
        data_hash = hash(data.values.tobytes()) if not data.empty else 0
        
        if 'region_base_data' not in st.session_state or st.session_state.get('region_data_hash') != data_hash:
            base_agg = self._compute_base_region_aggregations(data, region_col)
            st.session_state.region_base_data = base_agg
            st.session_state.region_data_hash = data_hash
            st.session_state.region_filtered_data = None
        
        base_data = st.session_state.region_base_data
        
        # ============================================
        # 2. ФИЛЬТРЫ В ФОРМЕ
        # ============================================
        
        with st.form("region_filters_form"):
            
            all_dsm = base_data['all_dsm']
            all_asm = base_data['all_asm']
            all_clients = base_data['all_clients']
            all_regions_display = base_data['regions_display']
            region_map = base_data['region_map']
            
            st.markdown("### 🔍 Фильтры")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**DSM**")
                dsm_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="region_dsm_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('region_dsm_mode', 'Включить') == 'Включить' else 1
                )
                dsm_mode = st.session_state.region_dsm_mode
                
                dsm_selected = st.multiselect(
                    "Выбрать DSM",
                    all_dsm,
                    key="region_dsm_values",
                    default=[]
                )
            
            with col2:
                st.markdown("**ASM**")
                asm_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="region_asm_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('region_asm_mode', 'Включить') == 'Включить' else 1
                )
                asm_mode = st.session_state.region_asm_mode
                
                
                asm_options = all_asm
                asm_selected = st.multiselect(
                    "Выбрать ASM",
                    asm_options,
                    key="region_asm_values",
                    default=[]
                )
            
            with col3:
                st.markdown("**Регион**")
                region_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="region_region_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('region_region_mode', 'Включить') == 'Включить' else 1
                )
                region_mode = st.session_state.region_region_mode
                
                region_selected_display = st.multiselect(
                    "Выбрать регион",
                    all_regions_display,
                    key="region_region_values",
                    default=[]
                )
                region_selected = [region_map.get(name, name) for name in region_selected_display]
            
            with col4:
                st.markdown("**Клиент**")
                client_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="region_client_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('region_client_mode', 'Включить') == 'Включить' else 1
                )
                client_mode = st.session_state.region_client_mode
                
                client_selected = st.multiselect(
                    "Выбрать клиента",
                    all_clients,
                    key="region_client_values",
                    default=[]
                )
            
            st.markdown("---")
            
            apply_filters = st.form_submit_button(
                "✅ Применить фильтры",
                type="primary",
                use_container_width=True,
                key="region_apply_filters_btn"
            )
        
        # ============================================
        # 3. ПРИМЕНЯЕМ ФИЛЬТРЫ
        # ============================================
        
        if apply_filters:
            filtered_data = self._apply_region_filters(
                base_data['raw_data'],
                dsm_selected, st.session_state.region_dsm_mode,
                asm_selected, st.session_state.region_asm_mode,
                region_selected, st.session_state.region_region_mode,
                client_selected, st.session_state.region_client_mode,
                region_col
            )
            st.session_state.region_filtered_data = filtered_data
        
        if st.session_state.region_filtered_data is not None:
            display_data = st.session_state.region_filtered_data
        else:
            display_data = base_data['raw_data']

        # ============================================
        # ФИЛЬТР ПО КОЛОНКЕ "ПРОДЛЕНИЕ"
        # ============================================
        if st.session_state.get('region_include_prodlenie', False):
            if 'Продление' in display_data.columns:
                display_data = display_data[display_data['Продление'] == 1]
            else:
                st.warning("⚠️ Колонка 'Продление' не найдена в данных")
        # ============================================
        
        # ============================================
        # 4. РАЗВЕРТКА И ОТОБРАЖЕНИЕ
        # ============================================
        
        st.subheader("📊 Детализация")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            show_client = st.checkbox("Клиент", key='region_show_client')
        with col2:
            show_project = st.checkbox("Код проекта", key='region_show_project')
        with col3:
            show_wave = st.checkbox("Волна", key='region_show_wave')
        with col4:
            show_dsm = st.checkbox("DSM", key='region_show_dsm')
        with col5:
            show_asm = st.checkbox("ASM", key='region_show_asm')
        with col6:
            show_rs = st.checkbox("RS", key='region_show_rs')
        with col7:
            show_po = st.checkbox("ПО", key='region_show_po')
        
        # Формируем groupby в зависимости от чек-боксов
        group_cols = ['Регион']
        
        if show_client and 'Клиент' in display_data.columns:
            group_cols.append('Клиент')
        if show_project and 'Проект' in display_data.columns:
            group_cols.append('Проект')
        if show_wave and 'Волна' in display_data.columns:
            group_cols.append('Волна')
        if show_dsm and 'DSM' in display_data.columns:
            group_cols.append('DSM')
        if show_asm and 'ASM' in display_data.columns:
            group_cols.append('ASM')
        if show_rs and 'RS' in display_data.columns:
            group_cols.append('RS')
        if show_po and 'ПО' in display_data.columns:
            group_cols.append('ПО')

        display_data = self.calculate_focus(display_data, aggregation_level='wave')
        # Агрегируем для отображения
        agg_columns = {
            'План проекта, шт.': 'sum',
            'План на дату, шт.': 'sum',
            'Факт проекта, шт.': 'sum',
            'Факт на дату, шт.': 'sum',
            'Длительность': 'first',
            'Дата старта': 'first',
            'Дата финиша': 'first',
            'Дата старта_гугл': 'first',
            'Дата финиша_гугл': 'first',
            'Коэффициент месяца': 'first',
            'Метод подбора дат': 'first',
            'Дней до конца проекта': 'first',
            'Прогноз, шт.': 'sum',
            'Утилизация тайминга, %': 'first',
            'Ср. план на день для 100% плана': 'sum',
            'Фокус': 'first',
            'Оплата план': 'sum',
            'plan_payment_per_visit': 'first',
            'Оплата факт': 'sum',
            'Оплата_поручено': 'sum',
            'Факт проекта_поручено, шт.': 'sum',
            'Факт проекта_не_поручено, шт.': 'sum',
            'Оплата план средн., руб.': 'first',
            'Оплата факт средн., руб.': 'first',
            'Оплата план-факт средн., руб.': 'first',
            'Оплата факт/план средн., %': 'first',
            'Оплата средн. в динамике, руб.': 'first',
            'Оплата средн. прогноз, руб.': 'first',
            'Клиент_дата_старта': 'first',
            'Клиент_дата_финиша': 'first',
            'Клиент_длительность': 'first',
            'Продление': 'first',
        }
        
        existing_agg = {k: v for k, v in agg_columns.items() if k in display_data.columns}
        
        # ВСЕГДА группируем
        region_data = display_data.groupby(group_cols).agg(existing_agg).reset_index()

        # ============================================
        # 4.5. ПОДМЕНА ДАТ НА УРОВНЕ КЛИЕНТА (только для выгрузки)
        # ============================================
        if group_cols == ['Регион']:
            if 'Клиент_дата_старта' in region_data.columns:
                region_data['Дата старта'] = region_data['Клиент_дата_старта']
                region_data['Дата финиша'] = region_data['Клиент_дата_финиша']
                region_data['Длительность'] = region_data['Клиент_длительность']
        
        # === ПЕРЕСЧЕТ ОПЛАТА ПЛАН СРЕДН. ПОСЛЕ АГРЕГАЦИИ ===
        if 'Оплата план' in region_data.columns and 'План проекта, шт.' in region_data.columns:
            mask_plan_positive = region_data['План проекта, шт.'] > 0
            region_data['Оплата план средн., руб.'] = 0.0
            if mask_plan_positive.any():
                region_data.loc[mask_plan_positive, 'Оплата план средн., руб.'] = (
                    region_data.loc[mask_plan_positive, 'Оплата план'] / 
                    region_data.loc[mask_plan_positive, 'План проекта, шт.']
                ).round(2)

        # === ПЕРЕСЧЕТ ОПЛАТА ФАКТ СРЕДН. ПОСЛЕ АГРЕГАЦИИ (ВСЕГДА) ===
        if 'Оплата факт' in region_data.columns and 'Факт проекта, шт.' in region_data.columns:
            mask_fact_positive = region_data['Факт проекта, шт.'] > 0
            region_data['Оплата факт средн., руб.'] = 0.0
            if mask_fact_positive.any():
                region_data.loc[mask_fact_positive, 'Оплата факт средн., руб.'] = (
                    region_data.loc[mask_fact_positive, 'Оплата факт'] / 
                    region_data.loc[mask_fact_positive, 'Факт проекта, шт.']
                ).round(2)
        
        # Определяем колонку прогноза
        forecast_col = None
        if 'Прогноз, шт' in region_data.columns:
            forecast_col = 'Прогноз, шт'
        elif 'Прогноз, шт.' in region_data.columns:
            forecast_col = 'Прогноз, шт.'
        
        # Метрика 1: Оплата план-факт средн., руб.
        if 'Оплата план средн., руб.' in region_data.columns and 'Оплата факт средн., руб.' in region_data.columns:
            region_data['Оплата план-факт средн., руб.'] = (
                region_data['Оплата план средн., руб.'] - region_data['Оплата факт средн., руб.']
            ).round(2)
        
        # Метрика 2: Оплата факт/план средн., %
        if 'Оплата план средн., руб.' in region_data.columns and 'Оплата факт средн., руб.' in region_data.columns:
            mask = region_data['Оплата план средн., руб.'] > 0
            region_data['Оплата факт/план средн., %'] = 0.0
            if mask.any():
                region_data.loc[mask, 'Оплата факт/план средн., %'] = (
                    region_data.loc[mask, 'Оплата факт средн., руб.'] / 
                    region_data.loc[mask, 'Оплата план средн., руб.'] * 100
                ).round(1)
        
        # Метрика 3: Оплата средн. в динамике, руб.
        if forecast_col and 'Оплата план средн., руб.' in region_data.columns and 'Оплата факт средн., руб.' in region_data.columns:
            region_data['Оплата средн. в динамике, руб.'] = (
                (region_data['Оплата план средн., руб.'] - region_data['Оплата факт средн., руб.']) * 
                region_data[forecast_col]
            ).round(2)
        
        # Метрика 4: Оплата средн. прогноз, руб.
        if 'Оплата план средн., руб.' in region_data.columns and 'Оплата факт средн., руб.' in region_data.columns and 'План проекта, шт.' in region_data.columns:
            region_data['Оплата средн. прогноз, руб.'] = (
                (region_data['Оплата план средн., руб.'] - region_data['Оплата факт средн., руб.']) * 
                region_data['План проекта, шт.']
            ).round(2)
        # ===================================================
        
        # ========== ДОБАВЛЕНИЕ КОЛОНОК ДЛЯ КРАТКОГО ОТЧЕТА ==========
        # 1. Прогноз, шт - используем существующий расчет из _calculate_metrics
        if 'Прогноз, шт' not in region_data.columns and 'Прогноз, шт.' in region_data.columns:
            region_data['Прогноз, шт'] = region_data['Прогноз, шт.']
        
        # 2. Прогноз ВП, % - рассчитываем если есть прогноз и план
        if 'Прогноз ВП, %' not in region_data.columns:
            if 'Прогноз, шт' in region_data.columns and 'План проекта, шт.' in region_data.columns:
                mask = region_data['План проекта, шт.'] > 0
                region_data['Прогноз ВП, %'] = 0.0
                region_data.loc[mask, 'Прогноз ВП, %'] = (
                    region_data.loc[mask, 'Прогноз, шт'] / 
                    region_data.loc[mask, 'План проекта, шт.'] * 100
                ).round(1)
        
        # 3. Отклонение от плана на сегодня, шт. = Факт проекта, шт. - План на дату, шт.
        if 'Отклонение от плана на сегодня, шт.' not in region_data.columns:
            if 'Факт проекта, шт.' in region_data.columns and 'План на дату, шт.' in region_data.columns:
                region_data['Отклонение от плана на сегодня, шт.'] = (
                    region_data['Факт проекта, шт.'] - region_data['План на дату, шт.']
                ).round(1)

        # 4. Факт ВП, % - рассчитываем из фактических данных
        if 'Факт ВП, %' not in region_data.columns:
            if 'Факт проекта, шт.' in region_data.columns and 'План проекта, шт.' in region_data.columns:
                mask = region_data['План проекта, шт.'] > 0
                region_data['Факт ВП, %'] = 0.0
                region_data.loc[mask, 'Факт ВП, %'] = (
                    region_data.loc[mask, 'Факт проекта, шт.'] / 
                    region_data.loc[mask, 'План проекта, шт.'] * 100
                ).round(1)
        # ============================================================
        
        # Расчет средней оплаты
        if 'Оплата факт' in region_data.columns and 'Факт проекта, шт.' in region_data.columns:
            mask = region_data['Факт проекта, шт.'] > 0
            region_data['Оплата факт средн., руб.'] = 0.0
            region_data.loc[mask, 'Оплата факт средн., руб.'] = (
                region_data.loc[mask, 'Оплата факт'] / region_data.loc[mask, 'Факт проекта, шт.']
            ).round(2)
            region_data = region_data.drop('Оплата факт', axis=1)

        # Расчет средней оплаты для порученных
        if 'Оплата_поручено' in region_data.columns and 'Факт проекта_поручено, шт.' in region_data.columns:
            mask_assigned = region_data['Факт проекта_поручено, шт.'] > 0
            region_data['Оплата поручено средн., руб.'] = 0.0
            region_data.loc[mask_assigned, 'Оплата поручено средн., руб.'] = (
                region_data.loc[mask_assigned, 'Оплата_поручено'] / region_data.loc[mask_assigned, 'Факт проекта_поручено, шт.']
            ).round(2)
        
        # === СРЕДНИЙ ПЛАН НА ДЕНЬ ДЛЯ 100% ПЛАНА ===
        remaining_plan = region_data['План проекта, шт.'] - region_data['Факт проекта, шт.']
        remaining_plan = remaining_plan.clip(lower=0)
        days_left = region_data['Дней до конца проекта'].replace(0, 1)
        
        region_data['Ср. план на день для 100% плана'] = (
            np.ceil(remaining_plan / days_left)
        ).astype(int)
        
        # Преобразуем коды регионов в длинные названия
        if 'Регион' in region_data.columns:
            region_data['Регион'] = region_data['Регион'].apply(self._get_long_region)
    
        # Добавляем вычисляемые метрики
        mask_plan = region_data['План на дату, шт.'] > 0
        region_data['План/Факт на дату,%'] = 0.0
        if mask_plan.any():
            region_data.loc[mask_plan, 'План/Факт на дату,%'] = (
                region_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                region_data.loc[mask_plan, 'План на дату, шт.'] * 100
            ).round(1)
        
        mask_project_plan = region_data['План проекта, шт.'] > 0
        region_data['План/Факт проекта,%'] = 0.0
        if mask_project_plan.any():
            region_data.loc[mask_project_plan, 'План/Факт проекта,%'] = (
                region_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                region_data.loc[mask_project_plan, 'План проекта, шт.'] * 100
            ).round(1)
        
        region_data['△План/Факт на дату, шт'] = (
            region_data['Факт на дату, шт.'] - region_data['План на дату, шт.']
        ).round(1)
        
        region_data['△План/Факт на дату, %'] = 0.0
        if mask_plan.any():
            region_data.loc[mask_plan, '△План/Факт на дату, %'] = (
                (region_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                 region_data.loc[mask_plan, 'План на дату, шт.']) - 1
            ).round(3) * 100

        region_data['△План/Факт проекта, шт'] = (
            region_data['Факт проекта, шт.'] - region_data['План проекта, шт.']
        ).round(1)
        
        mask_project_plan = region_data['План проекта, шт.'] > 0
        region_data['△План/Факт проекта, %'] = 0.0
        if mask_project_plan.any():
            region_data.loc[mask_project_plan, '△План/Факт проекта, %'] = (
                (region_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                 region_data.loc[mask_project_plan, 'План проекта, шт.']) - 1
            ).round(3) * 100
        
        
        region_data['△План/Факт на дату, шт'] = (
            region_data['Факт на дату, шт.'] - region_data['План на дату, шт.']
        ).round(1)
        
        region_data['△План/Факт на дату, %'] = 0.0
        if mask_plan.any():
            region_data.loc[mask_plan, '△План/Факт на дату, %'] = (
                (region_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                 region_data.loc[mask_plan, 'План на дату, шт.']) - 1
            ).round(3) * 100

        region_data['△План/Факт проекта, шт'] = (
            region_data['Факт проекта, шт.'] - region_data['План проекта, шт.']
        ).round(1)
        
        mask_project_plan = region_data['План проекта, шт.'] > 0
        region_data['△План/Факт проекта, %'] = 0.0
        if mask_project_plan.any():
            region_data.loc[mask_project_plan, '△План/Факт проекта, %'] = (
                (region_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                 region_data.loc[mask_project_plan, 'План проекта, шт.']) - 1
            ).round(3) * 100
        
        
        # KPI
        st.markdown("### 📊 Ключевые показатели")
        
        col_kpi1, col_kpi2, col_kpi3, col_checkbox1, col_checkbox2 = st.columns([1, 1, 1, 0.35, 0.35])
        with col_checkbox1:
            include_prodata = st.checkbox("📊 Продата", key="region_include_prodata")
        with col_checkbox2:
            include_prodlenie = st.checkbox("🔄 Продление", key="region_include_prodlenie")
        
        prodata_df = st.session_state.cleaned_data.get('prodata_processed', None)
        
        prodata_plan_total = 0
        prodata_fact_total = 0
        prodata_plan_date_total = 0
        prodata_fact_date_total = 0
        
        if include_prodata and prodata_df is not None and not prodata_df.empty:
            if 'План проекта, шт.' in prodata_df.columns:
                prodata_plan_total = prodata_df['План проекта, шт.'].sum()
            if 'Факт проекта, шт.' in prodata_df.columns:
                prodata_fact_total = prodata_df['Факт проекта, шт.'].sum()
            if 'План на дату, шт.' in prodata_df.columns:
                prodata_plan_date_total = prodata_df['План на дату, шт.'].sum()
            if 'Факт на дату, шт.' in prodata_df.columns:
                prodata_fact_date_total = prodata_df['Факт на дату, шт.'].sum()
        
        # Рассчитываем общие значения
        plan_total = region_data['План проекта, шт.'].sum() if 'План проекта, шт.' in region_data.columns else 0
        fact_total = region_data['Факт проекта, шт.'].sum() if 'Факт проекта, шт.' in region_data.columns else 0
        plan_date_total = region_data['План на дату, шт.'].sum() if 'План на дату, шт.' in region_data.columns else 0
        fact_date_total = region_data['Факт на дату, шт.'].sum() if 'Факт на дату, шт.' in region_data.columns else 0
        assigned_total = region_data['Факт проекта_поручено, шт.'].sum() if 'Факт проекта_поручено, шт.' in region_data.columns else 0
        
        if include_prodata:
            plan_total += prodata_plan_total
            fact_total += prodata_fact_total
            plan_date_total += prodata_plan_date_total
            fact_date_total += prodata_fact_date_total
        
        # Отклонение от плана на сегодня, шт (Факт проекта - План на дату)
        deviation = fact_total - plan_date_total
        
        # Проценты
        pf_percent = (fact_total / plan_total * 100) if plan_total > 0 else 0
        
        # Расчет прогноза ВП по всем проектам
        if 'Прогноз, шт.' in region_data.columns:
            forecast_total = region_data['Прогноз, шт.'].sum()
        else:
            forecast_total = 0
        
        if include_prodata and prodata_df is not None and not prodata_df.empty:
            if 'Прогноз, шт.' in prodata_df.columns:
                forecast_total += prodata_df['Прогноз, шт.'].sum()
        
        forecast_percent = (forecast_total / plan_total * 100) if plan_total > 0 else 0
        
        # РЯД 1: План проекта, Факт проекта, Факт ВП, %
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 План проекта", f"{plan_total:,.0f} шт")
        with col2:
            st.metric("✅ Факт проекта", f"{fact_total:,.0f} шт")
        with col3:
            st.metric("🎯 Факт ВП, %", f"{pf_percent:.1f}%")
        
        # РЯД 2: Отклонение, Факт поручено, Прогноз ВП, %
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("📉 Отклонение от плана на сегодня, шт", f"{deviation:+,.0f}")
        with col5:
            st.metric("📋 Факт поручено, шт", f"{assigned_total:,.0f}")
        with col6:
            st.metric("🔮 Прогноз ВП, %", f"{forecast_percent:.1f}%")
        
        # Отображаем таблицу
        display_cols = ['Регион']
        
        if show_client and 'Клиент' in region_data.columns:
            display_cols.append('Клиент')
        if show_project and 'Проект' in region_data.columns:
            display_cols.append('Проект')
        if show_wave and 'Волна' in region_data.columns:
            display_cols.append('Волна')
        if show_dsm and 'DSM' in region_data.columns:
            display_cols.append('DSM')
        if show_asm and 'ASM' in region_data.columns:
            display_cols.append('ASM')
        if show_rs and 'RS' in region_data.columns:
            display_cols.append('RS')
        if show_po and 'ПО' in region_data.columns:
            display_cols.append('ПО')
        
        # Колонки, которые показываются всегда
        always_show = [
            'План проекта, шт.', 
            'Факт проекта, шт.',
            'План на дату, шт.',
            'Факт на дату, шт.',
            'План/Факт проекта,%',
            '△План/Факт проекта, шт',
            '△План/Факт проекта, %',
            'План/Факт на дату,%',
            '△План/Факт на дату, шт',
            '△План/Факт на дату, %',
            'Фокус',
            'Прогноз на месяц, шт.',
            'Длительность',
            'Дней до конца проекта',
            'Утилизация тайминга, %',
            'Ср. план на день для 100% плана',
            'Метод подбора дат',
            'Оплата план',
            'Оплата план средн., руб.',
            'Оплата факт средн., руб.',
            'Оплата план-факт средн., руб.',
            'Оплата факт/план средн., %',
            'Оплата средн. в динамике, руб.',
            'Оплата средн. прогноз, руб.',
            'Оплата поручено средн., руб.',
            'Факт проекта_поручено, шт.',
            'Факт проекта_не_поручено, шт.' 
        ]
        
        for col in always_show:
            if col in region_data.columns:
                display_cols.append(col)
        
        existing_display = [c for c in display_cols if c in region_data.columns]
        
        # Преобразуем коды регионов в названия
        if 'Регион' in region_data.columns:
            region_data['Регион'] = region_data['Регион'].apply(self._get_long_region)
        
        st.dataframe(region_data[existing_display], use_container_width=True, hide_index=True)
        
        # Удаляем лишние колонки перед выгрузкой
        cols_to_drop = ['Оплата_поручено']
        for col in cols_to_drop:
            if col in region_data.columns:
                region_data = region_data.drop(col, axis=1)
        
        # Кнопка скачивания
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            region_data.to_excel(writer, sheet_name='Регионы', index=False)
        
        st.download_button(
            label="⬇️ Скачать Excel",
            data=output.getvalue(),
            file_name=f"регионы_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

        # Кнопка скачивания краткого отчета
        brief_cols = [
            'Клиент',
            'План проекта, шт.',
            'Факт проекта, шт.',
            'Факт ВП, %',
            'Факт проекта_поручено, шт.',
            'Факт проекта_не_поручено, шт.',
            'Длительность',
            'Дата старта',
            'Дата финиша',
            'Дней до конца проекта',
            'Прогноз, шт',
            'Прогноз ВП, %',
            'Отклонение от плана на сегодня, шт.',
            'Ср. план на день для 100% плана',
            'Оплата план',
            'Оплата план средн., руб.',
            'Оплата факт средн., руб.',
            'Оплата план-факт средн., руб.',
            'Оплата факт/план средн., %',
            'Оплата средн. в динамике, руб.',
            'Оплата средн. прогноз, руб.',
            'Оплата поручено средн., руб.'
        ]
        
        # Оставляем только существующие колонки
        existing_brief_cols = [col for col in brief_cols if col in region_data.columns]
        brief_report = region_data[existing_brief_cols].copy()
        
        output_brief = BytesIO()
        with pd.ExcelWriter(output_brief, engine='openpyxl') as writer:
            brief_report.to_excel(writer, sheet_name='Краткий_отчет', index=False)
        
        st.download_button(
            label="📊 Скачать краткий отчет",
            data=output_brief.getvalue(),
            file_name=f"краткий_отчет_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True,
            key="download_brief_region"
        )
    
    def create_dsm_tab(self, data, hierarchy_df=None):
        """Создает вкладку DSM с фильтрами в форме"""
        if data is None or data.empty:
            st.warning("⚠️ Нет данных для отчета")
            return
        
        st.subheader("📊 Сводка по DSM")
        
        # Переименовываем колонки
        rename_cols = {'ЗОД': 'DSM', 'АСС': 'ASM', 'ЭМ': 'RS'}
        data = data.rename(columns=rename_cols)
        
        region_col = 'Регион'
        if 'Регион short' in data.columns and 'Регион' not in data.columns:
            region_col = 'Регион short'
        
        # ============================================
        # 1. БАЗОВЫЕ АГРЕГАЦИИ (один раз за сессию)
        # ============================================
        
        data_hash = hash(data.values.tobytes()) if not data.empty else 0
        
        if 'dsm_base_data' not in st.session_state or st.session_state.get('dsm_data_hash') != data_hash:
            base_agg = self._compute_base_dsm_aggregations(data, region_col)
            st.session_state.dsm_base_data = base_agg
            st.session_state.dsm_data_hash = data_hash
            st.session_state.dsm_filtered_data = None
        
        base_data = st.session_state.dsm_base_data
        all_dsm = base_data['all_dsm']
        
        # ============================================
        # 2. ФИЛЬТРЫ В ФОРМЕ
        # ============================================
        
        with st.form("dsm_filters_form"):
            
            all_asm = base_data['all_asm']
            all_clients = base_data['all_clients']
            all_projects = base_data['all_projects']
            all_waves = base_data['all_waves']
            all_regions_display = base_data['regions_display']
            region_map = base_data['region_map']
            
            st.markdown("### 🔍 Фильтры")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**DSM**")
                dsm_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="dsm_dsm_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('dsm_dsm_mode', 'Включить') == 'Включить' else 1
                )
                dsm_mode = st.session_state.dsm_dsm_mode
                
                dsm_selected = st.multiselect(
                    "Выбрать DSM",
                    all_dsm,
                    key="dsm_dsm_values",
                    default=[]
                )
            
            with col2:
                st.markdown("**ASM**")
                asm_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="dsm_asm_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('dsm_asm_mode', 'Включить') == 'Включить' else 1
                )
                asm_mode = st.session_state.dsm_asm_mode

                asm_options = all_asm
                asm_selected = st.multiselect(
                    "Выбрать ASM",
                    asm_options,
                    key="dsm_asm_values",
                    default=[]
                )
            
            with col3:
                st.markdown("**Клиент**")
                client_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="dsm_client_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('dsm_client_mode', 'Включить') == 'Включить' else 1
                )
                client_mode = st.session_state.dsm_client_mode
                
                client_filtered = all_clients
                if dsm_selected:
                    client_filtered = [c for c in client_filtered if c in dsm_selected]
                
                client_selected = st.multiselect(
                    "Выбрать клиента",
                    client_filtered,
                    key="dsm_client_values",
                    default=[]
                )
            
            with col4:
                st.markdown("**Регион**")
                region_mode = st.radio(
                    "Режим",
                    ["Включить", "Исключить"],
                    key="dsm_region_mode",
                    horizontal=True,
                    index=0 if st.session_state.get('dsm_region_mode', 'Включить') == 'Включить' else 1
                )
                region_mode = st.session_state.dsm_region_mode
                
                region_selected_display = st.multiselect(
                    "Выбрать регион",
                    all_regions_display,
                    key="dsm_region_values",
                    default=[]
                )
                region_selected = [region_map.get(name, name) for name in region_selected_display]
                
                region_mode = st.session_state.dsm_region_mode
            
            st.markdown("---")
            
            apply_filters = st.form_submit_button(
                "✅ Применить фильтры",
                type="primary",
                use_container_width=True,
                key="dsm_apply_filters_btn"
            )
        
        # ============================================
        # 3. ПРИМЕНЯЕМ ФИЛЬТРЫ
        # ============================================
        
        if apply_filters:
            filtered_data = self._apply_dsm_filters(
                base_data['raw_data'],
                dsm_selected, st.session_state.dsm_dsm_mode,
                asm_selected, st.session_state.dsm_asm_mode,
                client_selected, st.session_state.dsm_client_mode,
                region_selected, st.session_state.dsm_region_mode,
                region_col
            )
            st.session_state.dsm_filtered_data = filtered_data
        
        if st.session_state.dsm_filtered_data is not None:
            display_data = st.session_state.dsm_filtered_data
        else:
            display_data = base_data['raw_data']

        # ============================================
        # ФИЛЬТР ПО КОЛОНКЕ "ПРОДЛЕНИЕ"
        # ============================================
        if st.session_state.get('dsm_include_prodlenie', False):
            if 'Продление' in display_data.columns:
                display_data = display_data[display_data['Продление'] == 1]
            else:
                st.warning("⚠️ Колонка 'Продление' не найдена в данных")
        # ============================================
        
        # ============================================
        # 4. РАЗВЕРТКА И ОТОБРАЖЕНИЕ
        # ============================================
        
        st.subheader("📊 Детализация")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            show_client = st.checkbox("Клиент", key='dsm_show_client')
        with col2:
            show_project = st.checkbox("Код проекта", key='dsm_show_project')
        with col3:
            show_wave = st.checkbox("Волна", key='dsm_show_wave')
        with col4:
            show_region = st.checkbox("Регионы", key='dsm_show_region')
        with col5:
            show_asm = st.checkbox("ASM", key='dsm_show_asm')
        with col6:
            show_rs = st.checkbox("RS", key='dsm_show_rs')
        with col7:
            show_po = st.checkbox("ПО", key='dsm_show_po')
        
        # Формируем groupby в зависимости от чек-боксов
        group_cols = ['DSM']
        
        if show_client and 'Клиент' in display_data.columns:
            group_cols.append('Клиент')
        if show_project and 'Проект' in display_data.columns:
            group_cols.append('Проект')
        if show_wave and 'Волна' in display_data.columns:
            group_cols.append('Волна')
        if show_region and region_col in display_data.columns:
            group_cols.append(region_col)
        if show_asm and 'ASM' in display_data.columns:
            group_cols.append('ASM')
        if show_rs and 'RS' in display_data.columns:
            group_cols.append('RS')
        if show_po and 'ПО' in display_data.columns:
            group_cols.append('ПО')
        
        display_data = self.calculate_focus(display_data, aggregation_level='wave')
        
        # Агрегируем для отображения
        agg_columns = {
            'План проекта, шт.': 'sum',
            'План на дату, шт.': 'sum',
            'Факт проекта, шт.': 'sum',
            'Факт на дату, шт.': 'sum',
            'Длительность': 'first',
            'Дата старта': 'first',
            'Дата финиша': 'first',
            'Дата старта_гугл': 'first',
            'Дата финиша_гугл': 'first',
            'Коэффициент месяца': 'first',
            'Метод подбора дат': 'first',
            'Дней до конца проекта': 'first',
            'Прогноз, шт.': 'sum',
            'Утилизация тайминга, %': 'first',
            'Ср. план на день для 100% плана': 'sum',
            'Фокус': 'first',
            'Оплата план': 'sum',
            'plan_payment_per_visit': 'first',
            'Оплата факт': 'sum',
            'Оплата_поручено': 'sum',
            'Факт проекта_поручено, шт.': 'sum',
            'Факт проекта_не_поручено, шт.': 'sum',
            'Оплата план средн., руб.': 'first',
            'Оплата факт средн., руб.': 'first',
            'Оплата план-факт средн., руб.': 'first',
            'Оплата факт/план средн., %': 'first',
            'Оплата средн. в динамике, руб.': 'first',
            'Оплата средн. прогноз, руб.': 'first',
            'Клиент_дата_старта': 'first',
            'Клиент_дата_финиша': 'first',
            'Клиент_длительность': 'first',
            'Продление': 'first',
        }
        
        existing_agg = {k: v for k, v in agg_columns.items() if k in display_data.columns}

        # ВСЕГДА группируем
        dsm_data = display_data.groupby(group_cols).agg(existing_agg).reset_index()

        # ============================================
        # 4.5. ПОДМЕНА ДАТ НА УРОВНЕ КЛИЕНТА (только для выгрузки)
        # ============================================
        if group_cols == ['DSM']:
            if 'Клиент_дата_старта' in dsm_data.columns:
                dsm_data['Дата старта'] = dsm_data['Клиент_дата_старта']
                dsm_data['Дата финиша'] = dsm_data['Клиент_дата_финиша']
                dsm_data['Длительность'] = dsm_data['Клиент_длительность']
        
        # === ПЕРЕСЧЕТ ОПЛАТА ПЛАН СРЕДН. ПОСЛЕ АГРЕГАЦИИ ===
        if 'Оплата план' in dsm_data.columns and 'План проекта, шт.' in dsm_data.columns:
            mask_plan_positive = dsm_data['План проекта, шт.'] > 0
            dsm_data['Оплата план средн., руб.'] = 0.0
            if mask_plan_positive.any():
                dsm_data.loc[mask_plan_positive, 'Оплата план средн., руб.'] = (
                    dsm_data.loc[mask_plan_positive, 'Оплата план'] / 
                    dsm_data.loc[mask_plan_positive, 'План проекта, шт.']
                ).round(2)

        # === ПЕРЕСЧЕТ ОПЛАТА ФАКТ СРЕДН. ПОСЛЕ АГРЕГАЦИИ (ВСЕГДА) ===
        if 'Оплата факт' in dsm_data.columns and 'Факт проекта, шт.' in dsm_data.columns:
            mask_fact_positive = dsm_data['Факт проекта, шт.'] > 0
            dsm_data['Оплата факт средн., руб.'] = 0.0
            if mask_fact_positive.any():
                dsm_data.loc[mask_fact_positive, 'Оплата факт средн., руб.'] = (
                    dsm_data.loc[mask_fact_positive, 'Оплата факт'] / 
                    dsm_data.loc[mask_fact_positive, 'Факт проекта, шт.']
                ).round(2)
        
        # Определяем колонку прогноза
        forecast_col = None
        if 'Прогноз, шт' in dsm_data.columns:
            forecast_col = 'Прогноз, шт'
        elif 'Прогноз, шт.' in dsm_data.columns:
            forecast_col = 'Прогноз, шт.'
        
        # Метрика 1: Оплата план-факт средн., руб.
        if 'Оплата план средн., руб.' in dsm_data.columns and 'Оплата факт средн., руб.' in dsm_data.columns:
            dsm_data['Оплата план-факт средн., руб.'] = (
                dsm_data['Оплата план средн., руб.'] - dsm_data['Оплата факт средн., руб.']
            ).round(2)
        
        # Метрика 2: Оплата факт/план средн., %
        if 'Оплата план средн., руб.' in dsm_data.columns and 'Оплата факт средн., руб.' in dsm_data.columns:
            mask = dsm_data['Оплата план средн., руб.'] > 0
            dsm_data['Оплата факт/план средн., %'] = 0.0
            if mask.any():
                dsm_data.loc[mask, 'Оплата факт/план средн., %'] = (
                    dsm_data.loc[mask, 'Оплата факт средн., руб.'] / 
                    dsm_data.loc[mask, 'Оплата план средн., руб.'] * 100
                ).round(1)
        
        # Метрика 3: Оплата средн. в динамике, руб.
        if forecast_col and 'Оплата план средн., руб.' in dsm_data.columns and 'Оплата факт средн., руб.' in dsm_data.columns:
            dsm_data['Оплата средн. в динамике, руб.'] = (
                (dsm_data['Оплата план средн., руб.'] - dsm_data['Оплата факт средн., руб.']) * 
                dsm_data[forecast_col]
            ).round(2)
        
        # Метрика 4: Оплата средн. прогноз, руб.
        if 'Оплата план средн., руб.' in dsm_data.columns and 'Оплата факт средн., руб.' in dsm_data.columns and 'План проекта, шт.' in dsm_data.columns:
            dsm_data['Оплата средн. прогноз, руб.'] = (
                (dsm_data['Оплата план средн., руб.'] - dsm_data['Оплата факт средн., руб.']) * 
                dsm_data['План проекта, шт.']
            ).round(2)
        
        # ========== ДОБАВЛЕНИЕ КОЛОНОК ДЛЯ КРАТКОГО ОТЧЕТА ==========
        # 1. Прогноз, шт - используем существующий расчет из _calculate_metrics
        if 'Прогноз, шт' not in dsm_data.columns and 'Прогноз, шт.' in dsm_data.columns:
            dsm_data['Прогноз, шт'] = dsm_data['Прогноз, шт.']
        
        # 2. Прогноз ВП, % - рассчитываем если есть прогноз и план
        if 'Прогноз ВП, %' not in dsm_data.columns:
            if 'Прогноз, шт' in dsm_data.columns and 'План проекта, шт.' in dsm_data.columns:
                mask = dsm_data['План проекта, шт.'] > 0
                dsm_data['Прогноз ВП, %'] = 0.0
                dsm_data.loc[mask, 'Прогноз ВП, %'] = (
                    dsm_data.loc[mask, 'Прогноз, шт'] / 
                    dsm_data.loc[mask, 'План проекта, шт.'] * 100
                ).round(1)
        
        # 3. Отклонение от плана на сегодня, шт. = Факт проекта, шт. - План на дату, шт.
        if 'Отклонение от плана на сегодня, шт.' not in dsm_data.columns:
            if 'Факт проекта, шт.' in dsm_data.columns and 'План на дату, шт.' in dsm_data.columns:
                dsm_data['Отклонение от плана на сегодня, шт.'] = (
                    dsm_data['Факт проекта, шт.'] - dsm_data['План на дату, шт.']
                ).round(1)

        # 4. Факт ВП, % - рассчитываем из фактических данных
        if 'Факт ВП, %' not in dsm_data.columns:
            if 'Факт проекта, шт.' in dsm_data.columns and 'План проекта, шт.' in dsm_data.columns:
                mask = dsm_data['План проекта, шт.'] > 0
                dsm_data['Факт ВП, %'] = 0.0
                dsm_data.loc[mask, 'Факт ВП, %'] = (
                    dsm_data.loc[mask, 'Факт проекта, шт.'] / 
                    dsm_data.loc[mask, 'План проекта, шт.'] * 100
                ).round(1)
        # ============================================================
        
        # Расчет средней оплаты
        if 'Оплата факт' in dsm_data.columns and 'Факт проекта, шт.' in dsm_data.columns:
            mask = dsm_data['Факт проекта, шт.'] > 0
            dsm_data['Оплата факт средн., руб.'] = 0.0
            dsm_data.loc[mask, 'Оплата факт средн., руб.'] = (
                dsm_data.loc[mask, 'Оплата факт'] / dsm_data.loc[mask, 'Факт проекта, шт.']
            ).round(2)
            dsm_data = dsm_data.drop('Оплата факт', axis=1)

        # Расчет средней оплаты для порученных
        if 'Оплата_поручено' in dsm_data.columns and 'Факт проекта_поручено, шт.' in dsm_data.columns:
            mask_assigned = dsm_data['Факт проекта_поручено, шт.'] > 0
            dsm_data['Оплата поручено средн., руб.'] = 0.0
            dsm_data.loc[mask_assigned, 'Оплата поручено средн., руб.'] = (
                dsm_data.loc[mask_assigned, 'Оплата_поручено'] / dsm_data.loc[mask_assigned, 'Факт проекта_поручено, шт.']
            ).round(2)
        
        # === СРЕДНИЙ ПЛАН НА ДЕНЬ ДЛЯ 100% ПЛАНА ===
        remaining_plan = dsm_data['План проекта, шт.'] - dsm_data['Факт проекта, шт.']
        remaining_plan = remaining_plan.clip(lower=0)
        days_left = dsm_data['Дней до конца проекта'].replace(0, 1)
        
        dsm_data['Ср. план на день для 100% плана'] = (
            np.ceil(remaining_plan / days_left)
        ).astype(int)

        # Добавляем вычисляемые метрики
        mask_plan = dsm_data['План на дату, шт.'] > 0

        # Преобразуем коды регионов в длинные названия
        if 'Регион' in dsm_data.columns:
            dsm_data['Регион'] = dsm_data['Регион'].apply(self._get_long_region)
        
        # Добавляем вычисляемые метрики
        mask_plan = dsm_data['План на дату, шт.'] > 0
        dsm_data['План/Факт на дату,%'] = 0.0
        if mask_plan.any():
            dsm_data.loc[mask_plan, 'План/Факт на дату,%'] = (
                dsm_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                dsm_data.loc[mask_plan, 'План на дату, шт.'] * 100
            ).round(1)
        
        mask_project_plan = dsm_data['План проекта, шт.'] > 0
        dsm_data['План/Факт проекта,%'] = 0.0
        if mask_project_plan.any():
            dsm_data.loc[mask_project_plan, 'План/Факт проекта,%'] = (
                dsm_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                dsm_data.loc[mask_project_plan, 'План проекта, шт.'] * 100
            ).round(1)
        
        dsm_data['△План/Факт на дату, шт'] = (
            dsm_data['Факт на дату, шт.'] - dsm_data['План на дату, шт.']
        ).round(1)
        
        dsm_data['△План/Факт на дату, %'] = 0.0
        if mask_plan.any():
            dsm_data.loc[mask_plan, '△План/Факт на дату, %'] = (
                (dsm_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                 dsm_data.loc[mask_plan, 'План на дату, шт.']) - 1
            ).round(3) * 100

        dsm_data['△План/Факт проекта, шт'] = (
            dsm_data['Факт проекта, шт.'] - dsm_data['План проекта, шт.']
        ).round(1)
        
        mask_project_plan = dsm_data['План проекта, шт.'] > 0
        dsm_data['△План/Факт проекта, %'] = 0.0
        if mask_project_plan.any():
            dsm_data.loc[mask_project_plan, '△План/Факт проекта, %'] = (
                (dsm_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                 dsm_data.loc[mask_project_plan, 'План проекта, шт.']) - 1
            ).round(3) * 100
        
        dsm_data['△План/Факт на дату, шт'] = (
            dsm_data['Факт на дату, шт.'] - dsm_data['План на дату, шт.']
        ).round(1)
        
        dsm_data['△План/Факт на дату, %'] = 0.0
        if mask_plan.any():
            dsm_data.loc[mask_plan, '△План/Факт на дату, %'] = (
                (dsm_data.loc[mask_plan, 'Факт на дату, шт.'] / 
                 dsm_data.loc[mask_plan, 'План на дату, шт.']) - 1
            ).round(3) * 100

        dsm_data['△План/Факт проекта, шт'] = (
            dsm_data['Факт проекта, шт.'] - dsm_data['План проекта, шт.']
        ).round(1)
        
        mask_project_plan = dsm_data['План проекта, шт.'] > 0
        dsm_data['△План/Факт проекта, %'] = 0.0
        if mask_project_plan.any():
            dsm_data.loc[mask_project_plan, '△План/Факт проекта, %'] = (
                (dsm_data.loc[mask_project_plan, 'Факт проекта, шт.'] / 
                 dsm_data.loc[mask_project_plan, 'План проекта, шт.']) - 1
            ).round(3) * 100
        
        
        # KPI
        st.markdown("### 📊 Ключевые показатели")
        
        col_kpi1, col_kpi2, col_kpi3, col_checkbox1, col_checkbox2 = st.columns([1, 1, 1, 0.35, 0.35])
        with col_checkbox1:
            include_prodata = st.checkbox("📊 Продата", key="dsm_include_prodata")
        with col_checkbox2:
            include_prodlenie = st.checkbox("🔄 Продление", key="dsm_include_prodlenie")
        
        prodata_df = st.session_state.cleaned_data.get('prodata_processed', None)
        
        prodata_plan_total = 0
        prodata_fact_total = 0
        prodata_plan_date_total = 0
        prodata_fact_date_total = 0
        
        if include_prodata and prodata_df is not None and not prodata_df.empty:
            if 'План проекта, шт.' in prodata_df.columns:
                prodata_plan_total = prodata_df['План проекта, шт.'].sum()
            if 'Факт проекта, шт.' in prodata_df.columns:
                prodata_fact_total = prodata_df['Факт проекта, шт.'].sum()
            if 'План на дату, шт.' in prodata_df.columns:
                prodata_plan_date_total = prodata_df['План на дату, шт.'].sum()
            if 'Факт на дату, шт.' in prodata_df.columns:
                prodata_fact_date_total = prodata_df['Факт на дату, шт.'].sum()
        
        # Рассчитываем общие значения
        plan_total = dsm_data['План проекта, шт.'].sum() if 'План проекта, шт.' in dsm_data.columns else 0
        fact_total = dsm_data['Факт проекта, шт.'].sum() if 'Факт проекта, шт.' in dsm_data.columns else 0
        plan_date_total = dsm_data['План на дату, шт.'].sum() if 'План на дату, шт.' in dsm_data.columns else 0
        fact_date_total = dsm_data['Факт на дату, шт.'].sum() if 'Факт на дату, шт.' in dsm_data.columns else 0
        assigned_total = dsm_data['Факт проекта_поручено, шт.'].sum() if 'Факт проекта_поручено, шт.' in dsm_data.columns else 0
        
        if include_prodata:
            plan_total += prodata_plan_total
            fact_total += prodata_fact_total
            plan_date_total += prodata_plan_date_total
            fact_date_total += prodata_fact_date_total
        
        # Отклонение от плана на сегодня, шт (Факт проекта - План на дату)
        deviation = fact_total - plan_date_total
        
        # Проценты
        pf_percent = (fact_total / plan_total * 100) if plan_total > 0 else 0
        # Расчет прогноза ВП по всем проектам
        if 'Прогноз, шт.' in dsm_data.columns:
            forecast_total = dsm_data['Прогноз, шт.'].sum()
        else:
            forecast_total = 0
        
        if include_prodata and prodata_df is not None and not prodata_df.empty:
            if 'Прогноз, шт.' in prodata_df.columns:
                forecast_total += prodata_df['Прогноз, шт.'].sum()
        
        forecast_percent = (forecast_total / plan_total * 100) if plan_total > 0 else 0
        
        # РЯД 1: План проекта, Факт проекта, Факт ВП, %
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 План проекта", f"{plan_total:,.0f} шт")
        with col2:
            st.metric("✅ Факт проекта", f"{fact_total:,.0f} шт")
        with col3:
            st.metric("🎯 Факт ВП, %", f"{pf_percent:.1f}%")
        
        # РЯД 2: Отклонение, Факт поручено, Прогноз ВП, %
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("📉 Отклонение от плана на сегодня, шт", f"{deviation:+,.0f}")
        with col5:
            st.metric("📋 Факт поручено, шт", f"{assigned_total:,.0f}")
        with col6:
            st.metric("🔮 Прогноз ВП, %", f"{forecast_percent:.1f}%")
        
        # Отображаем таблицу
        display_cols = ['DSM']
        
        if show_client and 'Клиент' in dsm_data.columns:
            display_cols.append('Клиент')
        if show_project and 'Проект' in dsm_data.columns:
            display_cols.append('Проект')
        if show_wave and 'Волна' in dsm_data.columns:
            display_cols.append('Волна')
        if show_region and region_col in dsm_data.columns:
            display_cols.append(region_col)
        if show_asm and 'ASM' in dsm_data.columns:
            display_cols.append('ASM')
        if show_rs and 'RS' in dsm_data.columns:
            display_cols.append('RS')
        if show_po and 'ПО' in dsm_data.columns:
            display_cols.append('ПО')
        
        # Колонки, которые показываются всегда
        always_show = [
            'План проекта, шт.', 
            'Факт проекта, шт.',
            'План на дату, шт.',
            'Факт на дату, шт.',
            'План/Факт проекта,%',
            '△План/Факт проекта, шт',
            '△План/Факт проекта, %',
            'План/Факт на дату,%',
            '△План/Факт на дату, шт',
            '△План/Факт на дату, %',
            'Фокус',
            'Прогноз на месяц, шт.',
            'Длительность',
            'Дней до конца проекта',
            'Утилизация тайминга, %',
            'Ср. план на день для 100% плана',
            'Метод подбора дат',
            'Оплата план',
            'Оплата план средн., руб.',
            'Оплата факт средн., руб.',
            'Оплата план-факт средн., руб.',
            'Оплата факт/план средн., %',
            'Оплата средн. в динамике, руб.',
            'Оплата средн. прогноз, руб.',
            'Оплата поручено средн., руб.',
            'Факт проекта_поручено, шт.',
            'Факт проекта_не_поручено, шт.' 
        ]
        
        for col in always_show:
            if col in dsm_data.columns:
                display_cols.append(col)
        
        existing_display = [c for c in display_cols if c in dsm_data.columns]
        
        st.dataframe(dsm_data[existing_display], use_container_width=True, hide_index=True)

        # Удаляем лишние колонки перед выгрузкой
        cols_to_drop = ['Оплата_поручено']
        for col in cols_to_drop:
            if col in dsm_data.columns:
                dsm_data = dsm_data.drop(col, axis=1)
        
        # Кнопка скачивания
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dsm_data.to_excel(writer, sheet_name='DSM', index=False)
        
        st.download_button(
            label="⬇️ Скачать Excel",
            data=output.getvalue(),
            file_name=f"dsm_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

        # Кнопка скачивания краткого отчета
        brief_cols = [
            'Клиент',
            'План проекта, шт.',
            'Факт проекта, шт.',
            'Факт ВП, %',
            'Факт проекта_поручено, шт.',
            'Факт проекта_не_поручено, шт.',
            'Длительность',
            'Дата старта',
            'Дата финиша',
            'Дней до конца проекта',
            'Прогноз, шт',
            'Прогноз ВП, %',
            'Отклонение от плана на сегодня, шт.',
            'Ср. план на день для 100% плана',
            'Оплата план',
            'Оплата план средн., руб.',
            'Оплата факт средн., руб.',
            'Оплата план-факт средн., руб.',
            'Оплата факт/план средн., %',
            'Оплата средн. в динамике, руб.',
            'Оплата средн. прогноз, руб.',
            'Оплата поручено средн., руб.'
        ]
        
        # Оставляем только существующие колонки
        existing_brief_cols = [col for col in brief_cols if col in dsm_data.columns]
        brief_report = dsm_data[existing_brief_cols].copy()
        
        output_brief = BytesIO()
        with pd.ExcelWriter(output_brief, engine='openpyxl') as writer:
            brief_report.to_excel(writer, sheet_name='Краткий_отчет', index=False)
        
        st.download_button(
            label="📊 Скачать краткий отчет",
            data=output_brief.getvalue(),
            file_name=f"краткий_отчет_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True,
            key="download_brief_dsm"
        )
    def create_prodata_table(self, prodata_df):
        """
        Создает отдельную таблицу для ПроДата с возможностью развертки по Типу мониторинга
        Формат: Клиент | Тип мониторинга | Факт проекта
        """
        if prodata_df is None or prodata_df.empty:
            return
        
        st.markdown("---")
        st.subheader("📊 ПроДата (Мониторинги)")
        st.caption("Данные ПроДата не участвуют в основной таблице проектов")
        
        # Чек-бокс для развертки (по умолчанию выключен)
        show_detail = st.checkbox("📋 Показать детализацию по типам мониторинга", key="prodata_detail", value=False)
        
        if show_detail:
            # Развернутая таблица - показываем каждый тип мониторинга отдельно
            table_df = prodata_df[['Клиент', 'Тип мониторинга', 'Факт проекта, шт.']].copy()
            table_df = table_df.sort_values(['Клиент', 'Тип мониторинга'])
            
            # Форматирование
            table_df['Факт проекта, шт.'] = table_df['Факт проекта, шт.'].map(lambda x: f"{x:.1f}")
            
            # Отображаем таблицу
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Клиент': 'Клиент',
                    'Тип мониторинга': 'Тип мониторинга',
                    'Факт проекта, шт.': st.column_config.TextColumn('Факт проекта, шт.')
                }
            )
            
            # Кнопка скачивания для развернутой таблицы
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                table_df.to_excel(writer, sheet_name='ПроДата_детально', index=False)
            
            st.download_button(
                label="⬇️ Скачать ПроДата (детально)",
                data=output.getvalue(),
                file_name=f"prodata_detailed_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary",
                use_container_width=True
            )
        else:
            # Свернутая таблица - группируем по клиенту (суммируем все типы мониторинга)
            prodata_agg = prodata_df.groupby('Клиент')['Факт проекта, шт.'].sum().reset_index()
            prodata_agg = prodata_agg.sort_values('Клиент')
            
            # Форматирование
            prodata_agg['Факт проекта, шт.'] = prodata_agg['Факт проекта, шт.'].map(lambda x: f"{x:.1f}")
            
            # Отображаем таблицу
            st.dataframe(
                prodata_agg,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Клиент': 'Клиент',
                    'Факт проекта, шт.': st.column_config.TextColumn('Факт проекта, шт.')
                }
            )
            
            # Кнопка скачивания для свернутой таблицы
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                prodata_agg.to_excel(writer, sheet_name='ПроДата', index=False)
            
            st.download_button(
                label="⬇️ Скачать ПроДата",
                data=output.getvalue(),
                file_name=f"prodata_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary",
                use_container_width=True
            )
    def create_dynamics_tab(self, data, visits_df, calc_params):
        """
        Создает вкладку Динамика с фактом визитов по дням
        АСМ — основные строки, Клиент — в детализацию
        """
        if visits_df is None or visits_df.empty:
            st.warning("⚠️ Нет данных визитов для динамики")
            return
        
        st.subheader("📈 Динамика факта визитов")
        
        # Реальные имена колонок в visits_df (полевые_проекты)
        col_client = 'Имя клиента'
        col_project = 'Код анкеты'
        col_wave = 'Название проекта'
        col_dsm = 'ЗОД'
        col_asm = 'АСС'
        col_rs = 'ЭМ'
        col_region = 'Регион short' if 'Регион short' in visits_df.columns else 'Регион'
        col_status = 'Статус'
        col_date = 'Дата визита'
        
        # Получаем уникальные значения для фильтров
        all_dsm = sorted(visits_df[col_dsm].dropna().unique())
        all_asm = sorted(visits_df[col_asm].dropna().unique())
        all_clients = sorted(visits_df[col_client].dropna().unique())
        all_regions = sorted(visits_df[col_region].dropna().unique())
        
        # Форма с фильтрами
        with st.form("dynamics_filters_form"):
            st.markdown("### 🔍 Фильтры")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                dsm_selected = st.multiselect("DSM", all_dsm, key="dynamics_dsm_values")
            with col2:
                asm_selected = st.multiselect("ASM", all_asm, key="dynamics_asm_values")
            with col3:
                region_selected = st.multiselect("Регион", all_regions, key="dynamics_region_values")
            with col4:
                client_selected = st.multiselect("Клиент", all_clients, key="dynamics_client_values")
            
            st.markdown("---")
            st.markdown("### 📊 Детализация")
            
            # 6 колонок для галочек (АСМ убран, так как всегда в таблице)
            col_detail1, col_detail2, col_detail3, col_detail4, col_detail5, col_detail6 = st.columns(6)
            
            with col_detail1:
                show_client = st.checkbox("Клиент", key="dynamics_show_client")
            with col_detail2:
                show_project = st.checkbox("Код проекта", key="dynamics_show_project")
            with col_detail3:
                show_wave = st.checkbox("Волна", key="dynamics_show_wave")
            with col_detail4:
                show_region_detail = st.checkbox("Регионы", key="dynamics_show_region")
            with col_detail5:
                show_dsm = st.checkbox("DSM", key="dynamics_show_dsm")
            with col_detail6:
                show_rs = st.checkbox("RS", key="dynamics_show_rs")
            
            apply_filters = st.form_submit_button("✅ Применить фильтры", type="primary", use_container_width=True)
        
        # Применяем фильтры напрямую к visits_df
        filtered_visits = visits_df.copy()
        
        if dsm_selected:
            filtered_visits = filtered_visits[filtered_visits[col_dsm].isin(dsm_selected)]
        if asm_selected:
            filtered_visits = filtered_visits[filtered_visits[col_asm].isin(asm_selected)]
        if region_selected:
            filtered_visits = filtered_visits[filtered_visits[col_region].isin(region_selected)]
        if client_selected:
            filtered_visits = filtered_visits[filtered_visits[col_client].isin(client_selected)]
        
        if filtered_visits.empty:
            st.warning("⚠️ Нет визитов, соответствующих выбранным фильтрам")
            return
        
        # Формируем group_cols
        # АСМ (col_asm) — всегда в основных строках
        group_cols = [col_asm]  # 'АСС'
        
        if show_client:
            group_cols.append(col_client)   # 'Имя клиента'
        if show_project:
            group_cols.append(col_project)  # 'Код анкеты'
        if show_wave:
            group_cols.append(col_wave)     # 'Название проекта'
        if show_region_detail:
            group_cols.append(col_region)   # 'Регион short'
        if show_dsm:
            group_cols.append(col_dsm)      # 'ЗОД'
        if show_rs:
            group_cols.append(col_rs)       # 'ЭМ'
        
        # Расчет динамики
        dynamics_df = visit_calculator.calculate_dynamics_fact(filtered_visits, calc_params, group_cols)
        
        if dynamics_df.empty:
            st.warning("⚠️ Нет данных для отображения динамики (нет выполненных визитов за период)")
            return
        
        # Фильтруем group_cols - оставляем только те, что есть в dynamics_df
        available_group_cols = [col for col in group_cols if col in dynamics_df.columns]
        
        if not available_group_cols:
            st.warning("⚠️ Нет доступных колонок для группировки в данных динамики")
            return
        
        # Сводная таблица
        pivot_df = dynamics_df.pivot_table(
            index=available_group_cols,
            columns='Дата',
            values='Факт',
            fill_value=0,
            aggfunc='sum'
        )
        
        # Добавляем все даты периода
        start_date = calc_params['start_date']
        end_date = calc_params['end_date']
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        all_dates_str = [d.strftime('%d.%b') for d in all_dates]
        
        # Переименовываем колонки в формат дд.мес
        pivot_df.columns = [col.strftime('%d.%b') if hasattr(col, 'strftime') else str(col) for col in pivot_df.columns]
        
        # Добавляем недостающие даты
        for date_str in all_dates_str:
            if date_str not in pivot_df.columns:
                pivot_df[date_str] = 0
        
        # Сортируем колонки по датам
        try:
            pivot_df = pivot_df.reindex(sorted(pivot_df.columns, key=lambda x: x.split('.')[0].zfill(2)), axis=1)
        except:
            pass
        
        result_df = pivot_df.reset_index()
        
        # Переименовываем колонки для отображения (АСМ — первая)
        display_name_map = {
            col_asm: 'АСМ',              # ← основная колонка
            col_client: 'Клиент',
            col_project: 'Проект',
            col_wave: 'Волна',
            col_dsm: 'DSM',
            col_rs: 'RS',
            col_region: 'Регион'
        }
        result_df = result_df.rename(columns=display_name_map)
        
        # Отображение
        total_fact = dynamics_df['Факт'].sum()
        st.metric("📊 Всего визитов за период", f"{total_fact:,.0f}")
        st.markdown("---")
        
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        
        # Скачивание
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Динамика_факта', index=False)
        
        st.download_button(
            label="⬇️ Скачать Excel",
            data=output.getvalue(),
            file_name=f"динамика_факта_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
    
    def calculate_focus(self, df, aggregation_level='auto'):
        """
        Рассчитывает метрику Фокус по новой логике.
        
        aggregation_level:
            - 'wave': данные на уровне волны (рассчитываем заново)
            - 'aggregated': данные агрегированы выше волны (наследуем)
            - 'auto': определяем автоматически
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # Определяем уровень детализации
        has_wave = 'Волна' in df.columns
        is_wave_level = has_wave and (df['Волна'].nunique() > 1 or len(df) == df['Волна'].nunique())
        
        if is_wave_level or aggregation_level == 'wave':
            # === УРОВЕНЬ ВОЛНЫ: рассчитываем фокус ===
            wave_focus = {}
            
            for (project, client, wave), group in df.groupby(['Проект', 'Клиент', 'Волна']):
                plan_total = group['План проекта, шт.'].sum()
                fact_total = group['Факт проекта, шт.'].sum()
                plan_vs_fact = (fact_total / plan_total * 100) if plan_total > 0 else 0
                
                timing_col = 'Утилизация тайминга, %'
                timing = group[timing_col].iloc[0] if timing_col in group.columns and len(group) > 0 else 0
                
                is_focus = (plan_vs_fact < 80) and (timing > 80) and (timing < 100)
                wave_focus[(project, client, wave)] = 'Да' if is_focus else 'Нет'
            
            df['Фокус'] = df.apply(lambda row: wave_focus.get((row['Проект'], row['Клиент'], row['Волна']), 'Нет'), axis=1)
            
        else:
            # === АГРЕГИРОВАННЫЙ УРОВЕНЬ: наследуем фокус (если есть колонка Фокус) ===
            if 'Фокус' not in df.columns:
                df['Фокус'] = 'Нет'
            else:
                # Для уровней выше волны: если хотя бы одна строка в группе имеет 'Да'
                higher_levels = [col for col in ['Клиент', 'Проект'] if col in df.columns]
                if higher_levels:
                    for _, group in df.groupby(higher_levels):
                        if (group['Фокус'] == 'Да').any():
                            df.loc[group.index, 'Фокус'] = 'Да'
        
        return df

    def create_asm_summary_tab(self, data):
        """
        Создает сводную таблицу по ASM для вкладки АСМ
        Структура: Общий итог → ASM Total → клиенты внутри ASM
        """
        if data is None or data.empty:
            st.warning("⚠️ Нет данных для сводной таблицы АСМ")
            return
        
        st.markdown("---")
        st.subheader("📊 Сводная таблица по АСМ")
        st.caption("📌 Основные метрики — по всем проектам | План/Факт продление — только проекты с Продление = 1")
        
        # 1. Проверяем наличие колонки Продление
        if 'Продление' not in data.columns:
            st.warning("⚠️ Колонка 'Продление' не найдена в данных. Сводная таблица недоступна.")
            return
        
        # 2. Переименовываем колонки
        rename_cols = {'ЗОД': 'DSM', 'АСС': 'ASM', 'ЭМ': 'RS'}
        data = data.rename(columns=rename_cols)
        
        if 'ASM' not in data.columns:
            st.warning("⚠️ Колонка 'ASM' (АСС) не найдена в данных")
            return
        
        # 3. Создаем два датафрейма
        df_all = data.copy()  # все проекты
        df_prodlenie = data[data['Продление'] == 1].copy()  # только продление
        
        # 4. Определяем колонки для агрегации (только существующие)
        agg_cols = ['План проекта, шт.', 'Факт проекта, шт.', 'План на дату, шт.']
        if 'Прогноз, шт.' in df_all.columns:
            agg_cols.append('Прогноз, шт.')
        
        existing_agg = [col for col in agg_cols if col in df_all.columns]
        
        if not existing_agg:
            st.warning("⚠️ Нет данных для агрегации")
            return
        
        # 5. Агрегация для основных колонок (из df_all)
        grouped_all = df_all.groupby(['ASM', 'Клиент'])[existing_agg].sum().reset_index()
        
        # 6. Агрегация для продления (из df_prodlenie)
        prodlenie_cols = ['План проекта, шт.', 'Факт проекта, шт.']
        existing_prodlenie = [col for col in prodlenie_cols if col in df_prodlenie.columns]
        
        if df_prodlenie.empty or not existing_prodlenie:
            # Если нет данных с Продление=1, заполняем нулями
            grouped_prodlenie = grouped_all[['ASM', 'Клиент']].copy()
            grouped_prodlenie['План продление'] = 0
            grouped_prodlenie['Факт продление'] = 0
        else:
            grouped_prodlenie = df_prodlenie.groupby(['ASM', 'Клиент'])[existing_prodlenie].sum().reset_index()
            grouped_prodlenie = grouped_prodlenie.rename(columns={
                'План проекта, шт.': 'План продление',
                'Факт проекта, шт.': 'Факт продление'
            })
        
        # 7. Объединяем два датафрейма
        if grouped_all.empty and grouped_prodlenie.empty:
            st.info("ℹ️ Нет данных для отображения")
            return
        
        merged = pd.merge(grouped_all, grouped_prodlenie, on=['ASM', 'Клиент'], how='outer')
        
        # Проверяем, что колонка ASM существует
        if 'ASM' not in merged.columns:
            st.warning("⚠️ Колонка 'ASM' отсутствует после объединения")
            return
        
        merged['План продление'] = merged['План продление'].fillna(0)
        merged['Факт продление'] = merged['Факт продление'].fillna(0)
        
        # Заполняем пропуски в основных колонках
        for col in existing_agg:
            if col in merged.columns:
                merged[col] = merged[col].fillna(0)
        
        # 8. Фильтруем нулевые значения
        numeric_cols = existing_agg + ['План продление', 'Факт продление']
        existing_numeric = [col for col in numeric_cols if col in merged.columns]
        
        if existing_numeric:
            mask = merged[existing_numeric].sum(axis=1) != 0
            merged = merged[mask].copy()
        
        if merged.empty:
            st.info("ℹ️ Нет данных для отображения после фильтрации")
            return
        
        # 9. Рассчитываем метрики
        merged['Отклонение'] = 0.0
        if 'Факт проекта, шт.' in merged.columns and 'План на дату, шт.' in merged.columns:
            merged['Отклонение'] = (merged['Факт проекта, шт.'] - merged['План на дату, шт.']).round(1)
        
        merged['Прогноз ВП, %'] = 0.0
        if 'Прогноз, шт.' in merged.columns and 'План проекта, шт.' in merged.columns:
            mask_plan = merged['План проекта, шт.'] > 0
            merged.loc[mask_plan, 'Прогноз ВП, %'] = (
                merged.loc[mask_plan, 'Прогноз, шт.'] / 
                merged.loc[mask_plan, 'План проекта, шт.'] * 100
            ).round(1)
        
        merged['Факт ВП, %'] = 0.0
        if 'Факт проекта, шт.' in merged.columns and 'План проекта, шт.' in merged.columns:
            mask_plan = merged['План проекта, шт.'] > 0
            merged.loc[mask_plan, 'Факт ВП, %'] = (
                merged.loc[mask_plan, 'Факт проекта, шт.'] / 
                merged.loc[mask_plan, 'План проекта, шт.'] * 100
            ).round(1)
        
        # 10. Формируем итоговую таблицу
        result_rows = []
        
        # Получаем список ASM (если merged не пустой)
        asm_list = sorted(merged['ASM'].unique()) if not merged.empty else []
        
        # Функция для создания строки итога
        def create_summary_row(label, data_df):
            # Проверка: если data_df пустой, возвращаем строку с нулями
            if data_df.empty:
                return {
                    'ASM': label,
                    'Клиент': '',
                    'План проекта, шт.': 0,
                    'Факт проекта, шт.': 0,
                    'План на сегодня': 0,
                    'Отклонение': 0.0,
                    'Прогноз ВП, %': 0.0,
                    'Факт ВП, %': 0.0,
                    'План продление': 0,
                    'Факт продление': 0
                }
            
            row = {
                'ASM': label,
                'Клиент': '',
                'План проекта, шт.': data_df['План проекта, шт.'].sum() if 'План проекта, шт.' in data_df.columns else 0,
                'Факт проекта, шт.': data_df['Факт проекта, шт.'].sum() if 'Факт проекта, шт.' in data_df.columns else 0,
                'План на сегодня': data_df['План на дату, шт.'].sum() if 'План на дату, шт.' in data_df.columns else 0,
                'Отклонение': 0.0,
                'Прогноз ВП, %': 0.0,
                'Факт ВП, %': 0.0,
                'План продление': data_df['План продление'].sum() if 'План продление' in data_df.columns else 0,
                'Факт продление': data_df['Факт продление'].sum() if 'Факт продление' in data_df.columns else 0
            }
            
            row['Отклонение'] = (row['Факт проекта, шт.'] - row['План на сегодня']).round(1)
            
            plan = row['План проекта, шт.']
            if plan > 0:
                if 'Прогноз, шт.' in data_df.columns:
                    row['Прогноз ВП, %'] = (data_df['Прогноз, шт.'].sum() / plan * 100).round(1)
                row['Факт ВП, %'] = (row['Факт проекта, шт.'] / plan * 100).round(1)
            
            return row
        
        # === 10.1. СЧИТАЕМ ОБЩИЙ ИТОГ (первая строка) ===
        if asm_list:
            all_data = merged[merged['ASM'].isin(asm_list)]
        else:
            all_data = merged
        
        # Добавляем Общий итог
        result_rows.append(create_summary_row('▪️ Общий итог', all_data))
        
        # === 10.2. СТРОКИ ПО ASM ===
        for asm in asm_list:
            asm_data = merged[merged['ASM'] == asm]
            
            if asm_data.empty:
                continue
            
            # Добавляем строку ASM Total
            result_rows.append(create_summary_row(f'▫️ {asm}', asm_data))
            
            # Клиенты внутри ASM (если развернуто)
            if st.session_state.get('asm_show_clients', True):
                client_data = asm_data.sort_values('Клиент')
                for _, row in client_data.iterrows():
                    # Пропускаем клиентов с пустым именем
                    client_name = row.get('Клиент', '')
                    if pd.isna(client_name) or str(client_name).strip() == '':
                        client_name = '(без названия)'
                    
                    result_rows.append({
                        'ASM': '',
                        'Клиент': client_name,
                        'План проекта, шт.': row.get('План проекта, шт.', 0),
                        'Факт проекта, шт.': row.get('Факт проекта, шт.', 0),
                        'План на сегодня': row.get('План на дату, шт.', 0),
                        'Отклонение': row.get('Отклонение', 0),
                        'Прогноз ВП, %': row.get('Прогноз ВП, %', 0),
                        'Факт ВП, %': row.get('Факт ВП, %', 0),
                        'План продление': row.get('План продление', 0),
                        'Факт продление': row.get('Факт продление', 0)
                    })
        
        if not result_rows:
            st.info("ℹ️ Нет данных для отображения")
            return
        
        result_df = pd.DataFrame(result_rows)
        
        # ============================================
        # 11. ЧЕК-БОКСЫ ДЛЯ УПРАВЛЕНИЯ ОТОБРАЖЕНИЕМ
        # ============================================
        col1, col2 = st.columns(2)
        
        with col1:
            # Чек-бокс для показа только продления
            show_only_prodlenie = st.checkbox(
                "📋 Только продление",
                value=st.session_state.get('asm_show_only_prodlenie', False),
                key="asm_show_only_prodlenie",
                help="Показывать только строки, где План продление > 0"
            )
        
        with col2:
            # Чек-бокс для развертывания клиентов (вместо кнопки)
            show_clients = st.checkbox(
                "📋 Развернуть клиентов",
                value=st.session_state.get('asm_show_clients', True),
                key="asm_show_clients",
                help="Показывать клиентов внутри ASM"
            )
        
        # === ПРИМЕНЯЕМ ФИЛЬТР ПО ПРОДЛЕНИЮ ===
        if show_only_prodlenie:
            # Оставляем только строки, где План продление > 0
            result_df = result_df[result_df['План продление'] > 0].copy()
            
            if result_df.empty:
                st.info("ℹ️ Нет данных с План продление > 0")
                return
        
        # 12. Отображаем таблицу
        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'ASM': st.column_config.TextColumn('ASM'),
                'Клиент': st.column_config.TextColumn('Клиент'),
                'План проекта, шт.': st.column_config.NumberColumn('План проекта, шт.', format="%.0f"),
                'Факт проекта, шт.': st.column_config.NumberColumn('Факт проекта, шт.', format="%.0f"),
                'План на сегодня': st.column_config.NumberColumn('План на сегодня', format="%.0f"),
                'Отклонение': st.column_config.NumberColumn('Отклонение', format="%.1f"),
                'Прогноз ВП, %': st.column_config.NumberColumn('Прогноз ВП, %', format="%.1f%%"),
                'Факт ВП, %': st.column_config.NumberColumn('Факт ВП, %', format="%.1f%%"),
                'План продление': st.column_config.NumberColumn('План продление', format="%.0f"),
                'Факт продление': st.column_config.NumberColumn('Факт продление', format="%.0f"),
            }
        )
        
        # 13. Кнопка скачивания
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Сводная_АСМ', index=False)
        
        st.download_button(
            label="⬇️ Скачать сводную таблицу АСМ",
            data=output.getvalue(),
            file_name=f"сводная_АСМ_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True,
            key="download_asm_summary"
        )

    # ============================================================
    # РЕТРО-АНАЛИТИКА (перенесено из проекта «Аналитика визитов»)
    # ============================================================

    def _month_label(self, year: int, month: int) -> str:
        return f"{month}_{year % 100:02d}"

    def _compute_kpi_retro(
        self,
        df_client_all: pd.DataFrame,
        months: list,
    ) -> dict:
        plans = []
        facts = []
        rs_counts = []
        durations = []

        plan_tp_values = []
        fact_tp_values = []

        for y, m in months:
            sub = df_client_all[
                (df_client_all["Год"] == y)
                & (df_client_all["Месяц"] == m)
            ]
            if sub.empty:
                continue
            plans.append(len(sub))
            facts.append(int((sub["Тип файла"] == "ЗП").sum()))
            rs_counts.append(sub["RS"].dropna().nunique())
            
            # <-- НОВОЕ: расчет длительности
            if "Длительность" in sub.columns:
                durations.extend(sub["Длительность"].dropna().tolist())
            elif "Дата старта" in sub.columns and "Дата финиша" in sub.columns:
                start = pd.to_datetime(sub["Дата старта"], errors='coerce')
                finish = pd.to_datetime(sub["Дата финиша"], errors='coerce')
                diff = (finish - start).dt.days + 1
                durations.extend(diff.dropna().tolist())
            # ---------------------

            zp_sub = sub[sub["Тип файла"] == "ЗП"]
            if not zp_sub.empty:
                if "План ТП, руб" in zp_sub.columns:
                    plan_tp_values.extend(zp_sub["План ТП, руб"].dropna().tolist())
                if "Факт ТП, руб" in zp_sub.columns:
                    fact_tp_values.extend(zp_sub["Факт ТП, руб"].dropna().tolist())

        n = len(plans)
        if n == 0:
            return {
                "plan_avg": 0, "fact_avg": 0, "pf_percent": 0,
                "rs_count_avg": 0, "ankets_per_rs": 0,
                "plan_tp_avg": 0, "fact_tp_avg": 0, "pf_tp_avg": 0,
                "duration_avg": 0,
            }

        plan_avg = round(sum(plans) / n)
        fact_avg = round(sum(facts) / n)
        rs_avg = round(sum(rs_counts) / n)
        pf_percent = (round(fact_avg / plan_avg * 100) if plan_avg > 0 else 0)
        ankets = (round(fact_avg / rs_avg) if rs_avg > 0 else 0)
        
        plan_tp_avg = round(sum(plan_tp_values) / len(plan_tp_values)) if plan_tp_values else 0
        fact_tp_avg = round(sum(fact_tp_values) / len(fact_tp_values)) if fact_tp_values else 0
        pf_tp_avg = plan_tp_avg - fact_tp_avg

        # <-- НОВОЕ: среднее по длительности
        duration_avg = round(sum(durations) / len(durations)) if durations else 0

        return {
            "plan_avg": plan_avg, "fact_avg": fact_avg, "pf_percent": pf_percent,
            "rs_count_avg": rs_avg, "ankets_per_rs": ankets,
            "plan_tp_avg": plan_tp_avg, "fact_tp_avg": fact_tp_avg, "pf_tp_avg": pf_tp_avg,
            "duration_avg": duration_avg, 
        }

    def _compute_monthly_table_retro(
        self,
        df_client_all: pd.DataFrame,
        months: list,
    ) -> pd.DataFrame:
        rows = {
            "План проекта, шт": [],
            "Факт проекта, шт": [],
            "ПФ клиент, %": [],
            "Кол-во RS, чел.": [],
            "Кол-во анкет на 1 RS, шт.": [],
            "План ТП, руб": [],
            "Факт ТП, руб": [],
            "ПФ ТП, руб": [],
            "Длительность": [],  # <-- НОВОЕ
        }
        for y, m in reversed(months):
            sub = df_client_all[
                (df_client_all["Год"] == y)
                & (df_client_all["Месяц"] == m)
            ]
            if sub.empty:
                for k in rows.keys():
                    rows[k].append(None)
            else:
                plan = len(sub)
                fact = int((sub["Тип файла"] == "ЗП").sum())
                pf = (fact / plan * 100) if plan > 0 else 0.0
                rs_unique = sub["RS"].dropna().nunique()
                ankets = (fact / rs_unique) if rs_unique > 0 else 0.0
                
                # <-- НОВОЕ: Расчет длительности
                if "Длительность" in sub.columns:
                    dur_values = sub["Длительность"].dropna().tolist()
                elif "Дата старта" in sub.columns and "Дата финиша" in sub.columns:
                    start = pd.to_datetime(sub["Дата старта"], errors='coerce')
                    finish = pd.to_datetime(sub["Дата финиша"], errors='coerce')
                    diff = (finish - start).dt.days + 1
                    dur_values = diff.dropna().tolist()
                else:
                    dur_values = []
                
                avg_dur = round(sum(dur_values) / len(dur_values)) if dur_values else None
                # ------------------------------------------

                zp_sub = sub[sub["Тип файла"] == "ЗП"]
                if not zp_sub.empty:
                    plan_tp = zp_sub["План ТП, руб"].mean() if "План ТП, руб" in zp_sub.columns else None
                    fact_tp = zp_sub["Факт ТП, руб"].mean() if "Факт ТП, руб" in zp_sub.columns else None
                    plan_tp = None if pd.isna(plan_tp) else round(float(plan_tp))
                    fact_tp = None if pd.isna(fact_tp) else round(float(fact_tp))
                    pf_tp = (plan_tp - fact_tp) if (plan_tp is not None and fact_tp is not None) else None
                else:
                    plan_tp = None
                    fact_tp = None
                    pf_tp = None
                
                rows["План проекта, шт"].append(plan)
                rows["Факт проекта, шт"].append(fact)
                rows["ПФ клиент, %"].append(round(pf))
                rows["Кол-во RS, чел."].append(rs_unique)
                rows["Кол-во анкет на 1 RS, шт."].append(round(ankets))
                rows["План ТП, руб"].append(plan_tp)
                rows["Факт ТП, руб"].append(fact_tp)
                rows["ПФ ТП, руб"].append(pf_tp)
                rows["Длительность"].append(avg_dur) # <-- НОВОЕ

        columns = [self._month_label(y, m) for y, m in reversed(months)]
        table = pd.DataFrame(rows, index=columns).T
        table.index.name = "Метрика"
        return table

    def _render_bar_chart_retro(
        self,
        df: pd.DataFrame, metric_name: str, title: str, y_title: str,
        color_rule, is_currency=False
    ):
        font = (
            "Inter, -apple-system, BlinkMacSystemFont, "
            "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
        )
        series = df.loc[metric_name]

        all_months = list(series.index)
        all_months_rev = all_months[::-1]

        chart_data = pd.DataFrame({
            "Месяц": series.index, "Value": series.values
        })
        chart_data = chart_data.iloc[::-1].reset_index(drop=True)

        if chart_data.empty:
            return

        chart_data["Value"] = pd.to_numeric(chart_data["Value"], errors="coerce")
        chart_data["Цвет"] = chart_data["Value"].apply(
            lambda v: color_rule(v) if pd.notna(v) else "#E0E0E0"
        )

        bars = alt.Chart(chart_data).mark_bar(
            cornerRadiusTopLeft=2, cornerRadiusTopRight=2,
        ).encode(
            x=alt.X(
                "Месяц:N",
                sort=all_months_rev,
                axis=alt.Axis(
                    labelAngle=0,
                    labelFont=font,
                    title=None,
                    values=all_months_rev,
                ),
            ),
            y=alt.Y(
                "Value:Q",
                scale=alt.Scale(zero=True),
                axis=alt.Axis(format=".0f", title=None, labelFont=font, titleFont=font),
            ),
            color=alt.Color("Цвет:N", scale=None, legend=None),
        )

        text_fmt = ".0f" if not is_currency else ",.0f"

        # Положительные значения: текст НАД столбцом
        text_pos = alt.Chart(chart_data).mark_text(
            align="center",
            baseline="bottom",     # ← здесь, а не в encode
            dy=-5,
            fontSize=12,
            color="#333333",
        ).encode(
            x=alt.X("Месяц:N", sort=all_months_rev),
            y=alt.Y("Value:Q", scale=alt.Scale(zero=True)),
            text=alt.Text("Value:Q", format=text_fmt),
            # Только положительные значения (иначе будет дубль)
            opacity=alt.condition(
                alt.datum.Value >= 0,
                alt.value(1),
                alt.value(0),
            ),
        )

        # Отрицательные значения: текст НАД столбцом (в сторону 0)
        text_neg = alt.Chart(chart_data).mark_text(
            align="center",
            baseline="top",        # ← здесь
            dy=5,
            fontSize=12,
            color="#333333",
        ).encode(
            x=alt.X("Месяц:N", sort=all_months_rev),
            y=alt.Y("Value:Q", scale=alt.Scale(zero=True)),
            text=alt.Text("Value:Q", format=text_fmt),
            opacity=alt.condition(
                alt.datum.Value < 0,
                alt.value(1),
                alt.value(0),
            ),
        )

        chart = (bars + text_pos + text_neg).properties(
            title=alt.TitleParams(text=title, font=font, fontSize=16, anchor="start"),
            height=400,
        ).configure_view(strokeWidth=0).configure_axis(grid=False)

        st.altair_chart(chart, use_container_width=True)

    def _render_region_heatmap_retro(self, df_client_all, months):
        """Тепловая карта ПФ % по регионам и месяцам"""
        if df_client_all is None or df_client_all.empty or not months:
            return


        # 1. Получаем список ВСЕХ уникальных регионов клиента (за всё время)
        all_regions = df_client_all["Регион short"].dropna().astype(str).unique()
        if len(all_regions) == 0:
            st.info("Нет данных по регионам для построения тепловой карты.")
            return

        regions_sorted = sorted(all_regions)
        months_sorted = [self._month_label(y, m) for y, m in months]

        # 2. Считаем реальные значения ПФ
        heatmap_data = []
        
        for y, m in months:
            sub = df_client_all[
                (df_client_all["Год"] == y)
                & (df_client_all["Месяц"] == m)
            ]
            
            month_label = self._month_label(y, m)
            
            for reg in regions_sorted:
                reg_sub = sub[sub["Регион short"].astype(str) == reg]
                
                if reg_sub.empty:
                    pf = 0.0
                    has_plan = False
                else:
                    plan = len(reg_sub)
                    fact = int((reg_sub["Тип файла"] == "ЗП").sum())
                    pf = (fact / plan * 100) if plan > 0 else 0.0
                    has_plan = True
                    
                heatmap_data.append({
                    "Регион": reg,
                    "Регион_полный": self._get_long_region(reg),
                    "Месяц": month_label,
                    "ПФ, %": round(pf, 1),
                    "Есть_план": has_plan
                })

        heatmap_df = pd.DataFrame(heatmap_data)

        # 3. Отрисовка
        font = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

        base = alt.Chart(heatmap_df).encode(
            x=alt.X(
                "Месяц:N", 
                sort=months_sorted, 
                # Ось X вверху!
                axis=alt.Axis(orient='top', labelAngle=0, labelFont=font, title=None)
            ),
            y=alt.Y(
                "Регион:N", 
                sort=regions_sorted, 
                axis=alt.Axis(labelFont=font, title=None)
            )
        )


        # Прямоугольники (цвет)
        rect = base.mark_rect(
            cornerRadius=2,
            stroke="#D3D3D3",
            strokeWidth=0.5
        ).encode(
            color=alt.condition(
                alt.datum["Есть_план"] == True,
                alt.Color(
                    "ПФ, %:Q",
                    scale=alt.Scale(
                        domain=[0, 50, 100],
                        range=["#F9F9F9", "#C9C0E8", "#7C6BC7"]
                    ),
                    legend=alt.Legend(title="ПФ, %", orient="right")
                ),
                alt.value("#F0F0F0")  # Если плана нет — светло-серый
            ),
            tooltip=[
                alt.Tooltip("Регион_полный:N", title="Регион"),
                alt.Tooltip("Месяц:N", title="Месяц"),
                alt.Tooltip("ПФ, %:Q", title="ПФ, %", format=".0f")
            ]
        )

        # Текст поверх прямоугольников (скрываем на пустых)
        text = base.mark_text(
            align="center", 
            baseline="middle", 
            font=font, 
            fontSize=14,
            dy=1
        ).encode(
            text=alt.condition(
                alt.datum["Есть_план"] == True,  # <-- Показываем цифру только если есть план
                alt.Text("ПФ, %:Q", format=".0f"),
                alt.value("")  # Иначе пустой текст
            ),
            color=alt.condition(
                alt.datum["ПФ, %"] > 50,
                alt.value("white"),
                alt.value("#333333")
            )
        )

        chart = (rect + text).properties(
            height=max(200, len(regions_sorted) * 35) # Динамическая высота
        ).configure_view(strokeWidth=0).configure_axis(grid=False)

        st.altair_chart(chart, use_container_width=True)

    def _get_quantile_colors(self, series, top_is_violet=True):
        clean_series = series.dropna()
        if clean_series.empty or clean_series.min() == clean_series.max():
            return lambda x: "#757575"
        q10 = clean_series.quantile(0.1)
        q90 = clean_series.quantile(0.9)

        def color_func(val):
            if val >= q90:
                return "#6A1B9A" if top_is_violet else "#F50057"
            elif val <= q10:
                return "#F50057" if top_is_violet else "#6A1B9A"
            else:
                return "#757575"
        return color_func

    def _pf_color(self, val):
        if val == 100:
            return "#6A1B9A"
        elif val < 80:
            return "#F50057"
        else:
            return "#757575"

    def create_retro_clients_tab(self, df_dataset):
        """Ретро-аналитика: вкладка «Клиенты»"""
        if df_dataset is None or df_dataset.empty:
            st.info("Нет данных для отображения.")
            return

        clients = sorted(
            df_dataset["Клиент"].dropna().unique().astype(str).tolist()
        )

        if not clients:
            st.warning("В датасете нет клиентов.")
            return

        client = st.selectbox(
            "Клиент", options=clients, key="retro_clients_client"
        )

        df_client_all = df_dataset[df_dataset["Клиент"] == client]

        st.markdown("### 📊 Ключевые показатели")
        report_key = (client,)

        if st.button("Рассчитать", type="primary", key="retro_calc_btn"):
            if df_client_all.empty:
                st.session_state.analytics_report = {
                    "key": report_key, "empty": True, "kpi": None, "table": None,
                }
            else:
                pairs = sorted(set(
                    (int(y), int(m)) for y, m in df_client_all[["Год", "Месяц"]]
                    .dropna().itertuples(index=False, name=None)
                ))
                if pairs:
                    y_min, m_min = pairs[0]
                    y_max, m_max = pairs[-1]
                    months = []
                    y, m = y_min, m_min
                    while (y, m) <= (y_max, m_max):
                        months.append((y, m))
                        if m == 12:
                            y, m = y + 1, 1
                        else:
                            m += 1
                else:
                    months = []

                kpi = self._compute_kpi_retro(df_client_all, months)
                table = self._compute_monthly_table_retro(df_client_all, months)
                st.session_state.analytics_report = {
                    "key": report_key, "empty": False, "kpi": kpi, "table": table,
                    "months": months,  # <-- СОХРАНЯЕМ МЕСЯЦЫ В КЭШ
                }

        report = st.session_state.get("analytics_report")
        if report is None or report["key"] != report_key:
            st.info("Нажмите «Рассчитать», чтобы построить отчёт.")
        elif report["empty"]:
            st.info("Нет данных по выбранному клиенту.")
        else:
            kpi = report["kpi"]
            table = report["table"]
            months = report.get("months", [])

            # Ряд 1
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📊 План ср., шт", f"{kpi['plan_avg']:,}")
            k2.metric("✅ Факт ср., шт", f"{kpi['fact_avg']:,}")
            k3.metric("🎯 ПФ ср., %", f"{kpi['pf_percent']}%")
            k4.metric("👥 Кол-во RS ср., чел.", f"{kpi['rs_count_avg']:,}")
            
            # Ряд 2
            tk1, tk2, tk3, tk4 = st.columns(4)
            tk1.metric("💰 План ТП ср., руб", f"{kpi['plan_tp_avg']:,.0f}")
            tk2.metric("💵 Факт ТП ср., руб", f"{kpi['fact_tp_avg']:,.0f}")
            tk3.metric("📉 ΔПФ ТП ср., руб", f"{kpi['pf_tp_avg']:,.0f}")
            tk4.metric("📋 Кол-во анкет на 1 RS ср., шт.", f"{kpi['ankets_per_rs']}")

            # НОВЫЙ Ряд 3 (Длительность)
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("📅 Длительность ср., дн.", f"{kpi.get('duration_avg', 0):,.0f}")

            # Кнопки выгрузки (видны всегда)
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    table.to_excel(writer, sheet_name="Ключевые показатели")
                st.download_button(
                    "📥 Выгрузить KPI в Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"kpi_{client}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="retro_download_kpi_btn"
                )
            
            with col_dl2:
                dataset_buffer = BytesIO()
                with pd.ExcelWriter(dataset_buffer, engine="openpyxl") as writer:
                    df_client_all.to_excel(writer, index=False, sheet_name="Датасет")
                st.download_button(
                    "📥 Выгрузить датасет",
                    data=dataset_buffer.getvalue(),
                    file_name=f"dataset_{client}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="retro_download_dataset_btn"
                )


            # Таблица по месяцам — в раскрывающемся списке
            with st.expander("📈 Ключевые показатели по месяцам", expanded=False):
                st.dataframe(table, use_container_width=True)

            # ============================================
            # ИИ-АГЕНТ (Сценарий 2: Анализ истории)
            # ============================================
            st.markdown("### 🤖 ИИ-Аналитик")
            st.caption("Нейросеть проанализирует историю и даст рекомендации для нового проекта.")
            
            if st.button("✨ Сгенерировать рекомендации", type="primary", key=f"btn_ai_{client}"):
                with st.spinner("ИИ изучает данные..."):
                    ai_response = self._generate_ai_recommendations(
                        client, kpi, table, df_client_all, is_current_project=False
                    )
                    st.session_state[f"ai_response_{client}"] = ai_response
            
            # Рекомендации в аккордеоне
            if f"ai_response_{client}" in st.session_state:
                with st.expander("📝 Рекомендации ИИ", expanded=True):
                    st.markdown(st.session_state[f"ai_response_{client}"])

            # Дашборд — без изменений (всегда виден)
            st.markdown("### 📊 Дашборд")
            st.markdown("<br>", unsafe_allow_html=True)

            self._render_bar_chart_retro(
                table, "ПФ клиент, %", "ПФ клиент, %", "ПФ клиент, %", self._pf_color
            )

            rs_series = table.loc["Кол-во RS, чел."]
            self._render_bar_chart_retro(
                table, "Кол-во RS, чел.", "Кол-во RS, чел.", "Кол-во RS, чел.",
                self._get_quantile_colors(rs_series, True)
            )

            ankets_series = table.loc["Кол-во анкет на 1 RS, шт."]
            self._render_bar_chart_retro(
                table, "Кол-во анкет на 1 RS, шт.", "Кол-во анкет на 1 RS, шт.", "Кол-во анкет на 1 RS, шт.",
                self._get_quantile_colors(ankets_series, False)
            )
            
            pf_tp_series = table.loc["ПФ ТП, руб"]
            self._render_bar_chart_retro(
                table, "ПФ ТП, руб", "ПФ ТП, руб", "ПФ ТП, руб",
                self._get_quantile_colors(pf_tp_series, True), is_currency=True
            )
            

            # Тепловая карта по регионам — в аккордеоне!
            with st.expander("🗺️ Тепловая карта ПФ по регионам", expanded=False):
                self._render_region_heatmap_retro(df_client_all, months)


    def create_retro_regions_tab(self, df_dataset):
        """Ретро-аналитика: вкладка «Регионы» (в разработке)"""
        st.info("В разработке.")

    def create_retro_dsm_tab(self, df_dataset):
        """Ретро-аналитика: вкладка «DSM» (в разработке)"""
        st.info("В разработке.")

    def create_retro_summary_tab(self, df_dataset):
        """Ретро-аналитика: вкладка «Сводный» (в разработке)"""
        st.info("В разработке.")

    def create_retro_export_tab(self, df_dataset):
        """Ретро-аналитика: вкладка «Выгрузка датасета»"""
        if df_dataset is None or df_dataset.empty:
            st.info("Нет данных для выгрузки. Загрузите Parquet на вкладке «Загрузка данных».")
            return

        st.markdown("### 📥 Выгрузка датасета")
        st.caption("Выберите месяцы и клиентов, затем сформируйте Excel-файл.")
        
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            pairs = sorted(set(
                (int(y), int(m)) for y, m in df_dataset[["Год", "Месяц"]]
                .dropna().itertuples(index=False, name=None)
            ))
            
            period_opts = []
            if pairs:
                y_min, m_min = pairs[0]
                y_max, m_max = pairs[-1]
                
                y, m = y_min, m_min
                while (y, m) <= (y_max, m_max):
                    period_opts.append(f"{m:02d}.{y}")
                    if m == 12:
                        y, m = y + 1, 1
                    else:
                        m += 1
            
            period_selected = st.multiselect(
                "Выберите месяцы для выгрузки",
                options=period_opts,
                default=period_opts[-3:] if len(period_opts) >= 3 else period_opts,
                key="retro_export_period"
            )
        
        with col_f2:
            all_clients = sorted(df_dataset["Клиент"].dropna().unique().astype(str).tolist())
            clients_selected = st.multiselect(
                "Выберите клиентов для выгрузки",
                options=all_clients,
                default=[],
                key="retro_export_clients"
            )

        if st.button("📥 Сформировать Excel для выгрузки", type="primary", key="retro_build_export_btn"):
            df_export = df_dataset.copy()
            
            if period_selected:
                parsed_periods = set()
                for p in period_selected:
                    mm, yyyy = p.split(".")
                    parsed_periods.add(int(yyyy) * 100 + int(mm))
                
                ym = (
                    df_export["Год"].astype("int64") * 100
                    + df_export["Месяц"].astype("int64")
                )
                df_export = df_export[ym.isin(parsed_periods)]
                
            if clients_selected:
                df_export = df_export[df_export["Клиент"].isin(clients_selected)]
                
            if df_export.empty:
                st.warning("По выбранным фильтрам данных нет.")
            else:
                export_buffer = BytesIO()
                with pd.ExcelWriter(export_buffer, engine="openpyxl") as writer:
                    df_export.to_excel(writer, index=False, sheet_name="Данные")
                
                st.session_state.analytics_export_bytes = export_buffer.getvalue()
                st.session_state.analytics_export_rows = len(df_export)
        
        if st.session_state.get("analytics_export_bytes"):
            st.success(f"Файл готов ({st.session_state.analytics_export_rows} строк)")
            st.download_button(
                "Скачать Excel",
                data=st.session_state.analytics_export_bytes,
                file_name="dataset_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="retro_download_export_btn"
            )

    def _generate_ai_recommendations(self, client_name, kpi, table, df_client_all, is_current_project):
        """Генерирует умные рекомендации через GigaChat API"""
        import openai
        import requests
        import uuid
        
        # 1. Проверка ключа
        if "gigachat" not in st.secrets or "credentials" not in st.secrets["gigachat"]:
            return "⚠️ Ключ API GigaChat не настроен в секретах."
            
        auth_key = st.secrets["gigachat"]["credentials"]

        # 2. Получаем Access Token
        try:
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            payload = "scope=GIGACHAT_API_PERS"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Basic {auth_key}"
            }
            token_response = requests.post(url, headers=headers, data=payload, verify=False)
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]
        except Exception as e:
            return f"Ошибка получения токена GigaChat: {e}"

        # 3. Сбор статистики по клиенту (история)
        def get_stats(df, group_col):
            if group_col not in df.columns:
                return []
            
            stats = []
            for name, group in df.groupby(group_col):
                if pd.isna(name) or str(name).strip() == '': continue
                
                plan = len(group)
                fact = int((group["Тип файла"] == "ЗП").sum())
                pf = (fact / plan * 100) if plan > 0 else 0
                
                dur = group["Длительность"].mean() if "Длительность" in group.columns else 0
                tp_plan = group["План ТП, руб"].mean() if "План ТП, руб" in group.columns else 0
                rs_load = fact / group["RS"].dropna().nunique() if group["RS"].dropna().nunique() > 0 else 0
                
                stats.append({"name": str(name), "pf": round(pf, 1), "dur": round(dur, 1), "tp": round(tp_plan, 1), "load": round(rs_load, 1)})
            
            stats.sort(key=lambda x: x['pf'])
            return stats

        all_regions = get_stats(df_client_all, 'Регион short')
        all_rs = get_stats(df_client_all, 'ЭМ')

        # 4. Бенчмаркинг по региону (медианы по другим проектам из cleaned_data)
        regional_benchmark = {}
        try:
            other_projects = st.session_state.cleaned_data.get('полевые_проекты')
            if other_projects is not None and not other_projects.empty:
                others = other_projects[other_projects['Имя клиента'].astype(str).str.strip() != str(client_name).strip()]
                
                if not others.empty:
                    for reg_name, group in others.groupby('Регион short'):
                        reg_clean = str(reg_name).strip()
                        if not reg_clean: continue
                        
                        if 'Оплата план средн., руб.' in group.columns:
                            prices = group['Оплата план средн., руб.'].dropna()
                        elif 'План ТП, руб' in group.columns:
                            prices = group['План ТП, руб'].dropna()
                        else:
                            prices = pd.Series()
                        
                        median_price = prices.median() if not prices.empty else 0
                        durations = group['Длительность'].dropna() if 'Длительность' in group.columns else pd.Series()
                        median_dur = durations.median() if not durations.empty else 0
                        rs_counts = group.groupby('RS').size()
                        median_load = rs_counts.median() if not rs_counts.empty else 0
                        
                        if median_price > 0 or median_dur > 0:
                            regional_benchmark[reg_clean] = {
                                "price": round(median_price, 1),
                                "dur": round(median_dur, 1),
                                "load": round(median_load, 1)
                            }
        except Exception:
            pass

        # 5. Анализ успешных/провальных периодов по проблемным регионам (частотный анализ)
        region_success_analysis = []
        for r in all_regions:
            if r['pf'] >= 80:
                continue
            
            reg_data = df_client_all[df_client_all['Регион short'].astype(str) == r['name']]
            
            # План и факт для этого региона
            plan_total = len(reg_data)
            fact_total = int((reg_data["Тип файла"] == "ЗП").sum())
            
            # Динамика по месяцам
            trend_parts = []
            for y, m in sorted(set((int(y), int(m)) for y, m in reg_data[['Год', 'Месяц']].dropna().itertuples(index=False, name=None))):
                sub = reg_data[(reg_data['Год'] == y) & (reg_data['Месяц'] == m)]
                if sub.empty: continue
                m_plan = len(sub)
                m_fact = int((sub["Тип файла"] == "ЗП").sum())
                m_pf = (m_fact / m_plan * 100) if m_plan > 0 else 0
                trend_parts.append(f"{self._month_label(y, m)}: {m_pf:.0f}%")
            
            trend_str = ", ".join(trend_parts[-5:]) if trend_parts else "нет данных"
            
            good_months = []
            bad_months = []
            
            for y, m in sorted(set((int(y), int(m)) for y, m in reg_data[['Год', 'Месяц']].dropna().itertuples(index=False, name=None))):
                sub = reg_data[(reg_data['Год'] == y) & (reg_data['Месяц'] == m)]
                if sub.empty: continue
                
                m_plan = len(sub)
                m_fact = int((sub["Тип файла"] == "ЗП").sum())
                pf = (m_fact / m_plan * 100) if m_plan > 0 else 0
                
                dur = sub["Длительность"].mean() if "Длительность" in sub.columns else 0
                tp = sub["План ТП, руб"].mean() if "План ТП, руб" in sub.columns else 0
                rs_cnt = sub["RS"].dropna().nunique()
                load = m_fact / rs_cnt if rs_cnt > 0 else 0
                
                month_info = {"pf": pf, "dur": dur, "tp": tp, "load": load}
                
                if pf == 100:
                    good_months.append(month_info)
                elif pf < 80:
                    bad_months.append(month_info)
            
            if good_months and bad_months:
                avg_good_dur = sum([m['dur'] for m in good_months]) / len(good_months)
                avg_good_tp = sum([m['tp'] for m in good_months]) / len(good_months)
                avg_good_load = sum([m['load'] for m in good_months]) / len(good_months)
                
                avg_bad_dur = sum([m['dur'] for m in bad_months]) / len(bad_months)
                avg_bad_tp = sum([m['tp'] for m in bad_months]) / len(bad_months)
                avg_bad_load = sum([m['load'] for m in bad_months]) / len(bad_months)
                
                analysis_entry = {
                    "name": r['name'],
                    "plan_total": plan_total,
                    "fact_total": fact_total,
                    "trend": trend_str,
                    "good_count": len(good_months),
                    "bad_count": len(bad_months),
                    "avg_good_dur": round(avg_good_dur, 1),
                    "avg_good_tp": round(avg_good_tp, 1),
                    "avg_good_load": round(avg_good_load, 1),
                    "avg_bad_dur": round(avg_bad_dur, 1),
                    "avg_bad_tp": round(avg_bad_tp, 1),
                    "avg_bad_load": round(avg_bad_load, 1)
                }
                
                if r['name'] in regional_benchmark:
                    analysis_entry["benchmark"] = regional_benchmark[r['name']]
                
                region_success_analysis.append(analysis_entry)

        # 6. Формируем контекст
        context = f"=== КЛИЕНТ: {client_name} ===\n"
        context += f"Средний ПФ за всю историю: {kpi['pf_percent']}%\n"
        context += f"Средняя длительность: {kpi.get('duration_avg', 0)} дн.\n"
        context += f"Средняя цена (План ТП): {kpi['plan_tp_avg']} руб.\n"
        context += f"Средняя нагрузка на 1 RS: {kpi['ankets_per_rs']} шт.\n\n"

        # Добавляем данные текущего проекта
        if is_current_project:
            context += "=== ТЕКУЩИЙ ПРОЕКТ (данные из ПФ проекты) ===\n"
            current_data = st.session_state.visit_report.get('calculated_data')
            
            if current_data is not None and not current_data.empty:
                client_current = current_data[current_data['Клиент'].astype(str).str.strip() == str(client_name).strip()]
                if not client_current.empty:
                    cur_plan = client_current['План проекта, шт.'].sum()
                    cur_fact = client_current['Факт проекта, шт.'].sum()
                    cur_pf = (cur_fact / cur_plan * 100) if cur_plan > 0 else 0
                    cur_dur = client_current['Длительность'].mean() if 'Длительность' in client_current.columns else 0
                    cur_tp = client_current['Оплата план средн., руб.'].mean() if 'Оплата план средн., руб.' in client_current.columns else 0
                    context += f"План текущего проекта: {cur_plan:.0f} шт.\n"
                    context += f"Факт текущего проекта: {cur_fact:.0f} шт.\n"
                    context += f"Текущий ПФ: {cur_pf:.1f}%\n"
                    context += f"Текущая длительность: {cur_dur:.1f} дн.\n"
                    context += f"Текущая цена: {cur_tp:.1f} руб.\n\n"

        # Передаем анализ проблемных регионов
        if region_success_analysis:
            context += "=== АНАЛИЗ ПРОБЛЕМНЫХ РЕГИОНОВ ===\n"
            context += "(Примечание 1: 'Длит. проекта' — это среднее количество дней, которое длится проект в этом регионе. Значение может быть дробным)\n"
            context += "(Примечание 2: 'Нагрузка' = Факт визитов / Количество RS. Если Факт падает, нагрузка тоже падает. Это следствие плохого ПФ, а не причина. Не советуй 'повысить нагрузку' — советуй перераспределить RS или изменить план)\n"
            
            for ra in region_success_analysis:
                context += f"Регион {ra['name']}:\n"
                context += f"  - План визитов: {ra['plan_total']} шт., Факт: {ra['fact_total']} шт.\n"
                context += f"  - Динамика: {ra['trend']}\n"
                context += f"  - Успешные месяцы (ПФ 100%, {ra['good_count']} шт): Длит. проекта {ra['avg_good_dur']} дн., Цена {ra['avg_good_tp']} руб., Нагрузка {ra['avg_good_load']} шт/RS\n"
                context += f"  - Провальные месяцы (ПФ < 80%, {ra['bad_count']} шт): Длит. проекта {ra['avg_bad_dur']} дн., Цена {ra['avg_bad_tp']} руб., Нагрузка {ra['avg_bad_load']} шт/RS\n"
                
                if "benchmark" in ra:
                    b = ra["benchmark"]
                    context += f"  - Бенчмарк по региону (медиана других проектов): Длит. проекта {b['dur']} дн., Цена {b['price']} руб., Нагрузка {b['load']} шт/RS\n"
            context += "\n"

        # Добавляем проблемных RS
        bad_rs = [r for r in all_rs if r['pf'] < 80]
        if bad_rs:
            context += "=== ПРОБЛЕМНЫЕ RS (ПФ < 80%) ===\n"
            for r in bad_rs:
                context += f"{r['name']}: ПФ {r['pf']}%\n"
            context += "\n"

        context += "=== ПОМЕСЯЧНАЯ ДИНАМИКА ===\n"
        context += table.to_string()


        # 7. Логика ветвления (гибкий промпт)
        if is_current_project:
            role_task = "Ты — антикризисный менеджер. Твоя ЦЕЛЬ — дожать выполнение ТЕКУЩЕГО проекта до 100%."
            analysis_focus = """
            АЛГОРИТМ (следуй шагам):
            1. Оцени текущий ПФ. Если он < 90%, найди главную причину.
            2. Посмотри на проблемные регионы (ПФ < 80%). Обрати внимание на регионы с ПФ 0% — если план визитов > 0, но факт = 0, это критическая проблема.
            3. Сравни текущие показатели региона (цена, длительность проекта) с БЕНЧМАРКОМ (медиана других проектов). Игнорируй незначительные отклонения (до 10-15%). 
            4. Сравни провальные месяцы с успешными месяцами этого же региона. Если в успешные месяцы цена или длительность проекта были значительно выше, укажи это как причину. 
               ВАЖНО: Если в провальные месяцы нагрузка ниже, чем в успешные — это следствие падения факта, а не причина. Не пиши "нужно повысить нагрузку". Вместо этого предложи перераспределить RS или проверить цену.
            5. Если есть проблемные RS — предложи их заменить или дать в помощь второго сотрудника.
            """
        else:
            role_task = "Ты — стратегический аудитор. Клиент не в текущем проекте. Твоя ЦЕЛЬ — выявить ошибки прошлого для запуска нового проекта."
            analysis_focus = """
            АЛГОРИТМ (следуй шагам):
            1. Оцени общую картину за весь период по этому клиенту.
            2. Найди системные ошибки: какие регионы или RS стабильно показывают ПФ < 80%? Кого стоит не допускать к новому проекту или заменить?
            3. Для проблемных регионов сравни их провальные месяцы с успешными. Найди ключевое отличие (длительность проекта, цена или нагрузка). Сравни с бенчмарком по региону (медиана других проектов).
            4. Проанализируй тренд по месяцам (посмотри на последние 5 месяцев). Если проект проседал в определенные месяцы — учти это при планировании.
            5. Дай рекомендации по бюджету, срокам и составу команды для БУДУЩЕГО проекта.
            """

        prompt = f"""
        {role_task}
        
        {analysis_focus}
        
        ФОРМАТ ОТВЕТА (строго без воды):
        - **Статус:** (Оценка ПФ: ниже/выше нормы)
        - **Проблемные точки:** (Конкретные регионы/RS и их цифры)
        - **Причина:** (На основе сравнения успешных/провальных периодов и бенчмарка)
        - **Действие:** (Что сделать: продлить сроки, повысить цену, заменить сотрудника и т.д.)
        
        ЗАПРЕЩАЕТСЯ: общие фразы про "мотивацию" или "усиление контроля". Сравнивай цифры.
        
        Данные:
        {context}
        """

        # 8. Вызов GigaChat
        try:
            client = openai.OpenAI(
                api_key=access_token,
                base_url="https://api.giga.chat/v1",
                http_client=openai.DefaultHttpxClient(verify=False)
            )
            
            response = client.chat.completions.create(
                model="GigaChat-2-Pro",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка при обращении к GigaChat: {e}"
            
# Глобальный экземпляр
dataviz = DataVisualizer()
