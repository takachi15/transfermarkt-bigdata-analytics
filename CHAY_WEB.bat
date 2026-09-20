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
echo Dang mo trinh duyet tai dia chi: http://localhost:8501
start http://localhost:8501
echo.
echo Dang khoi dong may chu Streamlit... (Nhan Ctrl+C de dung)
python -m streamlit run Source_Code\08_dashboard_streamlit.py --server.port 8501
pause
