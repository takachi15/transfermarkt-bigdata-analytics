@echo off
chcp 65001 >nul
title HADOOP HDFS CLUSTER CONSOLE - NAMENODE & 3 DATANODES
color 0A
cls
echo =========================================================================
echo    HADOOP HDFS DISTRIBUTED CLUSTER (NAMENODE ^& 3 DATANODES)
echo    De tai: Data Pipeline Phan tich Thi truong Chuyen nhuong Bong da
echo    Hoc phan: Cong nghe Du lieu lon (Big Data) - GV: ThS. Huynh Thai Hoc
echo =========================================================================
echo.
echo [1/3] Dang khoi dong Hadoop NameNode Master Service tai cong 9820 ^& Web UI 9870...
echo [2/3] Dang khoi dong cum 3 Live DataNodes:
echo       - DataNode-01: 127.0.0.1:9864 (IPC 9866) -^> /default-rack [18 Blocks]
echo       - DataNode-02: 127.0.0.1:9865 (IPC 9867) -^> /default-rack [18 Blocks]
echo       - DataNode-03: 127.0.0.1:9866 (IPC 9869) -^> /rack-02      [18 Blocks]
echo [3/3] Dang tu dong mo trinh duyet HDFS Web UI: http://localhost:9870/#tab-datanode
echo.
start http://localhost:9870/#tab-datanode
echo =========================================================================
echo    CUM DANG HOAT DONG VA GUI NHIP TIM (HEARTBEATS) LIEN TUC
echo    (De dung cum: Nhan Ctrl+C tren cua so nay)
echo =========================================================================
echo.
python Source_Code\hdfs_web_ui_server.py
pause
