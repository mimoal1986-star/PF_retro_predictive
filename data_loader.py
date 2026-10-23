# utils/data_loader.py
import pandas as pd
import streamlit as st

class DataProcessor:
    """
    Обработчик загруженных данных
    """
    
    @staticmethod
    def validate_data(uploaded_files):
        """Проверяет корректность загруженных данных"""
        required_files = ['портал', 'автокодификация', 'сервизория', 'иерархия']
        
        for file in required_files:
            if file not in uploaded_files:
                return False, f"Отсутствует файл: {file}"
            
            df = uploaded_files[file]
            if df is None or df.empty:
                return False, f"Файл {file} пустой"
        
        return True, "Все файлы корректны"
    
    @staticmethod
    def merge_data(uploaded_files):
        """Объединяет все данные"""
        try:
            # Здесь будет логика объединения (Power Query эмуляция)
            st.info("🔗 Объединяю данные...")
            
            # Пока просто возвращаем исходные данные
            return uploaded_files
            
        except Exception as e:
            st.error(f"❌ Ошибка объединения: {e}")
            return None

# Глобальный экземпляр
processor = DataProcessor()