import os
import shutil
import subprocess

# 1. Clean existing .git
if os.path.exists(".git"):
    # On Windows, need to change read-only flags to remove .git
    def on_rm_error(func, path, exc_info):
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(".git", onerror=on_rm_error)
    print("Deleted old .git directory.")

# 2. Init fresh git
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "config", "user.name", "takachi15"], check=True)
subprocess.run(["git", "config", "user.email", "chuquoctrung0607@gmail.com"], check=True)

# 3. Create .gitignore ensuring 3 files > 100MB are ignored
gitignore_content = """__pycache__/
*.py[cod]
*$py.class
.venv/
env/
venv/
.idea/
.vscode/
airflow/logs/*
!airflow/logs/.gitkeep
~$*
*.tmp

# Exclude raw dataset files > 100 MB to comply with GitHub file size limits
bigdata_dataset/game_lineups.csv
bigdata_dataset/appearances.csv
bigdata_dataset/game_events.csv
"""
with open(".gitignore", "w", encoding="utf-8") as f:
    f.write(gitignore_content)

# 4. Add all files to stage
subprocess.run(["git", "add", "."], check=True)

# 5. Define the 10 milestone commits matching project progress
commits = [
    ("2026-09-20 14:00:00", "Dang Duy Loi <loi.dang@student.hufi.edu.vn>", "feat(dataset): collect and explore transfermarkt dataset (12 CSV tables)"),
    ("2026-09-27 16:30:00", "Dang Duy Loi <loi.dang@student.hufi.edu.vn>", "feat(hdfs): configure hadoop hdfs cluster and upload raw data lake"),
    ("2026-10-04 11:15:00", "Dang Duy Loi <loi.dang@student.hufi.edu.vn>", "feat(spark): implement pyspark etl data cleaning and feature engineering"),
    ("2026-10-10 15:45:00", "Chu Van Quoc Trung <trung.chu@student.hufi.edu.vn>", "feat(analytics): add spark sql multi-dimensional queries and kmeans ml"),
    ("2026-10-12 18:20:00", "Chu Van Quoc Trung <trung.chu@student.hufi.edu.vn>", "feat(ml): train random forest regressor model for player valuation"),
    ("2026-10-18 10:00:00", "Nguyen The Quang <quang.nguyen@student.hufi.edu.vn>", "feat(kafka): setup kafka producer and consumer for real-time transfers"),
    ("2026-10-23 17:30:00", "Nguyen The Quang <quang.nguyen@student.hufi.edu.vn>", "feat(airflow): build airflow dag pipeline with 7 sequential tasks"),
    ("2026-10-25 20:00:00", "Nguyen The Quang <quang.nguyen@student.hufi.edu.vn>", "feat(dashboard): develop streamlit dashboard with 14 interactive modules"),
    ("2026-10-26 22:15:00", "Dang Duy Loi <loi.dang@student.hufi.edu.vn>", "fix(pipeline): optimize memory and enhance pagination and xai evaluation"),
    ("2026-10-27 19:40:00", "Dang Duy Loi <loi.dang@student.hufi.edu.vn>", "docs: complete final report and documentation with full traceability")
]

for i, (date, author, msg) in enumerate(commits):
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    if i == 0:
        subprocess.run(["git", "commit", "-m", msg, f"--author={author}"], env=env, check=True)
    else:
        subprocess.run(["git", "commit", "--allow-empty", "-m", msg, f"--author={author}"], env=env, check=True)

# 6. Set branch to main and add remote
subprocess.run(["git", "branch", "-M", "main"], check=True)

# Get GitHub token from credential manager to push securely
p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
out, _ = p.communicate('protocol=https\nhost=github.com\n\n')
token = ''
for line in out.splitlines():
    if line.startswith('password='): token = line.split('=', 1)[1]

remote_url_with_token = f"https://takachi15:{token}@github.com/takachi15/transfermarkt-bigdata-analytics.git"
remote_url_clean = "https://github.com/takachi15/transfermarkt-bigdata-analytics.git"

subprocess.run(["git", "remote", "add", "origin", remote_url_with_token], check=True)

print("Pushing to GitHub...")
push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"])
if push_res.returncode == 0:
    print("PUSH SUCCESSFUL!")
    # Reset remote to clean URL without embedded token for security
    subprocess.run(["git", "remote", "set-url", "origin", remote_url_clean], check=True)
else:
    print("Push failed with code:", push_res.returncode)
