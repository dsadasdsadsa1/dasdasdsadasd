import streamlit as st
import subprocess
import os
import sys

st.set_page_config(page_title="Sherlock Web UI", page_icon="🔍")
st.title("🔍 Sherlock Web UI")
st.write("Поиск профилей по имени пользователя на сотнях сайтов без использования консоли.")

username = st.text_input("Введите имя пользователя (username):")

if st.button("Начать поиск"):
    if username:
        # Очищаем ввод от нежелательных символов для безопасности
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).strip()
        
        if not safe_username:
            st.error("Неверный формат имени пользователя.")
        else:
            with st.spinner("Идет сканирование... Это может занять около 1-2 минут."):
                # Запускаем без "--txt", так как .txt файл создается по умолчанию
                result = subprocess.run(
                    [sys.executable, "-m", "sherlock_project", "--timeout", "5", safe_username],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                txt_filename = f"{safe_username}.txt"
                
                # Если файл с результатами создался, читаем его
                if os.path.exists(txt_filename):
                    with open(txt_filename, "r", encoding="utf-8") as f:
                        links = [line.strip() for line in f if line.strip()]
                    os.remove(txt_filename) # Удаляем временный файл
                    
                    if links:
                        st.success(f"Найдено профилей: {len(links)}")
                        for link in links:
                            st.write(f"- [{link}]({link})")
                    else:
                        st.info("Профилей не найдено.")
                else:
                    st.error("Результаты не найдены или произошла ошибка во время сканирования.")
                    if result.stderr:
                        st.code(result.stderr)
    else:
        st.warning("Пожалуйста, введите никнейм.")
