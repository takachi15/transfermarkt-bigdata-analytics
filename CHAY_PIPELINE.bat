@echo off
chcp 65001 >nul
title KHOI CHAY TOAN BO BIG DATA PIPELINE TU DONG
cls
echo =========================================================================
echo    DANG CHAY TOAN BO PIPELINE TU DONG (02 -> 07 -> DATABASE)
echo    Giang vien huong dan: ThS. Huynh Thai Hoc
echo    Nhom sinh vien: Dang Duy Loi, Chu Van Quoc Trung, Nguyen The Quang
echo =========================================================================
echo.
python Source_Code\run_pipeline.py
echo.
echo Pipeline da chay xong. Nhan phim bat ky de thoat...
pause >nul
