import streamlit as st
import subprocess
import os
import sys

st.set_page_config(page_title="Maigret Web UI", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ Maigret Web UI")
st.write("Maigret — мощный инструмент OSINT. Он собирает подробное досье по никнейму на тысячах сайтов.")

username = st.text_input("Введите имя пользователя (username):")

if st.button("Начать расследование"):
    if username:
        # Безопасная очистка ввода
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).strip()
        
        if not safe_username:
            st.error("Неверный формат имени пользователя.")
        else:
            with st.spinner("Идет глубокое сканирование... Это может занять около 2-3 минут."):
                # Запуск maigret через subprocess с флагом --html для генерации красивого отчета
                result = subprocess.run(
                    ["maigret", "--html", safe_username],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # По умолчанию Maigret сохраняет отчеты в папку reports/ в текущей директории
                report_dir = "reports"
                html_filename = f"report_{safe_username}.html"
                report_path = os.path.join(report_dir, html_filename)
                
                # Если папки "reports" нет, проверяем текущую директорию
                if not os.path.exists(report_path) and os.path.exists(html_filename):
                    report_path = html_filename
                
                st.subheader("Результаты сканирования:")
                
                # Выводим логи работы Maigret
                if result.stdout:
                    # Показываем пользователю строки, содержащие найденные профили
                    lines = result.stdout.split('\n')
                    found_lines = [line for line in lines if "[+]" in line or "Found" in line or "http" in line]
                    
                    if found_lines:
                        st.success("Сканирование завершено!")
                        for line in found_lines:
                            st.write(line)
                    else:
                        st.info("В логах не найдено прямых совпадений. Полный лог работы:")
                        st.text(result.stdout)
                
                # Кнопка для скачивания интерактивного HTML-отчета
                if os.path.exists(report_path):
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="📥 Скачать полное HTML-досье",
                            data=file,
                            file_name=f"maigret_{safe_username}.html",
                            mime="text/html"
                        )
                    # Удаляем временный файл, чтобы не забивать диск сервера
                    try:
                        os.remove(report_path)
                    except:
                        pass
                else:
                    if result.stderr:
                        st.error("Произошла ошибка при выполнении Maigret:")
                        st.code(result.stderr)
    else:
        st.warning("Пожалуйста, введите никнейм.")
