@echo off
chcp 65001 >nul
title KHOI CHAY FOOTBALL BIG DATA WEB DASHBOARD
cls
echo =========================================================================
echo    DANG KHOI CHAY FOOTBALL BIG DATA DASHBOARD (STREAMLIT)
echo    Giang vien huong dan: ThS. Huynh Thai Hoc
echo    Nhom sinh vien: Dang Duy Loi, Chu Van Quoc Trung, Nguyen The Quang
echo =========================================================================
echo.
echo [1/2] Dang khoi dong may chu Hadoop HDFS Web UI (Cong 9870)...
start "Hadoop HDFS Web UI (Port 9870)" /min python Source_Code\hdfs_web_ui_server.py
echo [2/2] Dang mo trinh duyet Dashboard: http://localhost:8501
start http://localhost:8501
echo.
echo Dang khoi dong may chu Streamlit... (Nhan Ctrl+C de dung)
python -m streamlit run Source_Code\08_dashboard_streamlit.py --server.port 8501
pause
