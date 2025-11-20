import os

com = {"steam":{
    "open": '"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Steam\Steam.lnk"',
    "close": 'taskkill /F /IM scype.exe',
    "open_bigpicture": 'start "Steam" "steam://open/bigpicture"',
    "close_bigpicture": 'start "Steam" "steam://close/bigpicture"',
}
       }

def open_steam():
    os.system(com['steam']['open'])

def close_steam():
    os.system(com['steam']['close'])

def open_steam_bigpicture():
    os.system(com['steam']['open_bigpicture'])

def close_steam_bigpicture():
    os.system(com['steam']['close_bigpicture'])