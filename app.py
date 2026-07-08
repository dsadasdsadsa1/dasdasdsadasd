import streamlit as st
import subprocess
import os
import sys

st.set_page_config(page_title="Maigret Web UI", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ Maigret Web UI")
st.write("Maigret — мощный инструмент OSINT. Поиск ведется строго по введенному никнейму.")

username = st.text_input("Введите имя пользователя (username):")

if st.button("Начать расследование"):
    if username:
        # Безопасная очистка ввода
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).strip()
        
        if not safe_username:
            st.error("Неверный формат имени пользователя.")
        else:
            with st.spinner("Идет сканирование... Это может занять около 1-2 минут."):
                # Отключаем рекурсию (--no-recursion и --no-extracting)
                # Ограничиваем поиск до топ-250 популярных сайтов для скорости
                result = subprocess.run(
                    ["maigret", "--html", "--no-recursion", "--no-extracting", "--top", "250", safe_username],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Умный поиск файла отчета во всех папках проекта (results, reports или корень)
                report_path = None
                expected_filename = f"report_{safe_username}.html"
                
                for root, dirs, files in os.walk("."):
                    # Пропускаем скрытые и служебные папки для ускорения поиска
                    if any(p in root for p in [".git", ".streamlit", "venv", "__pycache__"]):
                        continue
                    if expected_filename in files:
                        report_path = os.path.join(root, expected_filename)
                        break
                
                st.subheader("Результаты сканирования:")
                
                # Выводим логи работы Maigret
                if result.stdout:
                    lines = result.stdout.split('\n')
                    found_lines = [line for line in lines if "[+]" in line or "Found" in line or "http" in line]
                    
                    if found_lines:
                        st.success("Сканирование завершено!")
                        for line in found_lines:
                            st.write(line)
                    else:
                        st.info("По данному запросу совпадений не найдено.")
                
                # Если файл отчета был успешно найден на сервере
                if report_path and os.path.exists(report_path):
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="📥 Скачать полное HTML-досье",
                            data=file,
                            file_name=f"maigret_{safe_username}.html",
                            mime="text/html"
                        )
                    try:
                        os.remove(report_path) # Удаляем файл после скачивания
                    except:
                        pass
                else:
                    st.warning("Файл HTML-отчета не был обнаружен. Возможно, утилите не удалось его сгенерировать.")
                    if result.stderr:
                        st.error("Технические логи ошибок:")
                        st.code(result.stderr)
    else:
        st.warning("Пожалуйста, введите никнейм.")
