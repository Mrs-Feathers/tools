import pwd
import os
import datetime
from securedata import securedata, mail

userDir = pwd.getpwuid(os.getuid())[0]

securedata.log("Started Daily Tasks")

status_email_warnings = []
status_email = "Dear Tyler,<br><br>This is your daily status report.<br><br>"

# Run Backups
backendPath = securedata.getItem("path_log_backup")
logPath = f"{backendPath}/log"
cron = f"/var/spool/cron/crontabs/{userDir}"
bash = f"/home/{userDir}/.bashrc"
today = datetime.date.today()
filePath = f"{securedata.getItem('path_log')}/{today}/"

# copy settings.json to root
os.system(f"cp {securedata.getConfigItem('path_securedata')}/settings.json {securedata.getItem('path_securedata_all_users')}/settings.json")

os.system(f"mkdir -p {logPath}/tasks")
os.system(f"mkdir -p {logPath}/cron")
os.system(f"mkdir -p {logPath}/bash")

os.system(
    f"cp -r {securedata.getItem('path_tasks_notes') + '/Tasks.md'} '{logPath}/tasks/Tasks {today}.md'")
os.system(f"cp -r {cron} '{logPath}/cron/Cron {today}.md'")
os.system(f"cp -r {bash} '{logPath}/bash/Bash {today}.md'")

securedata.log(f"Tasks, Cron, and Bash copied to {logPath}.")

# Push today's Log files to Github
os.system(
    f"cd {backendPath}; git pull; git add -A; git commit -m 'Updated Logs'; git push")
securedata.log("Updated Git")

# Spotify Stats
spotify_count = securedata.getItem("spotipy", "total_tracks")
spotify_avg_year = securedata.getItem("spotipy", "average_year")
spotify_log = "<font face='monospace'>" + \
    '<br>'.join(securedata.getFileAsArray(
        f"LOG_SPOTIFY.log", filePath=filePath)) + "</font><br><br>"
spotify_stats = "<b>Spotify Stats:</b><br>"

if "ERROR —" in spotify_log:
    status_email_warnings.append('Spotify')
    spotify_stats += "Please review your songs! We found some errors.<br><br>"

spotify_stats += f"You have {spotify_count} songs; the mean song is from {spotify_avg_year}.<br><br>"

if 'Spotify' in status_email_warnings:
    spotify_stats += spotify_log

# Daily Log
daily_log_file = '<br>'.join(securedata.getFileAsArray(
    f"LOG_DAILY {today}.log", filePath=filePath))

if "ERROR —" in daily_log_file or "CRITICAL —" in daily_log_file:
    status_email_warnings.append("Errors")
if "WARNING —" in daily_log_file:
    status_email_warnings.append("Warnings")

daily_log = f"<b>Daily Log:</b><br><font face='monospace'>{daily_log_file}</font><br><br>"

if 'Errors' in status_email_warnings or 'Warnings' in status_email_warnings:
    status_email += daily_log

status_email += spotify_stats

# Weather
weather_data = securedata.getItem("weather", "data")
weather_data_text = "Unavailable"
if weather_data:
    weather_data_text = f""" <b>Weather Tomorrow:</b><br>{weather_data['tomorrow_high']}° and {weather_data['tomorrow_conditions']}.<br> Sunrise:
                        {weather_data['tomorrow_sunrise']}<br>Sunset: {weather_data['tomorrow_sunset']}<br><br>"""

status_email += weather_data_text

# Git Status
git_status = os.popen(
    f"cd {backendPath}; git log -1").read().replace("\n", "<br>")

try:
    lastCommitTime = int(
        os.popen(f'cd {backendPath}; git log -1 --format="%at"').read())
except Exception as e:
    lastCommitTime = 0

now = int(os.popen("date +%s").read())

if now - lastCommitTime > 7200:
    status_email_warnings.append("Git")
    status_email = f"<b>❌ Check Git:</b><br>Your last Git commit to your website was before today:<br><br>{git_status}<br><hr><br><br>{status_email}"
else:
    status_email += f"<br><br><br><b>✔ Git Up to Date:</b><br>{git_status}"

status_email.replace("<br><br><br><br>", "<br><br>")

status_email_warnings_text = "- Check " + \
    ', '.join(status_email_warnings) + \
    " " if len(status_email_warnings) else ""

mail.send(f"Daily Status {status_email_warnings_text}- {today}", status_email)
