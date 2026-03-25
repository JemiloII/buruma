import os
import shutil
import sqlite3
import sys

DB_PATH = os.path.join(
    os.path.expanduser("~"),
    "AppData", "LocalLow", "Cygames", "Umamusume", "master", "master.mdb"
)
BACKUP_PATH = os.path.join(os.path.dirname(DB_PATH), "master.mdb.bak")
TABLES = ["chara_data", "mob_data"]

CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
INVERT = "\033[7m"

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False

CHARACTER_NAMES = {
    1001: "Special Week", 1002: "Silence Suzuka", 1003: "Tokai Teio",
    1004: "Maruzensky", 1005: "Fuji Kiseki", 1006: "Oguri Cap",
    1007: "Gold Ship", 1008: "Vodka", 1009: "Daiwa Scarlet",
    1010: "Taiki Shuttle", 1011: "Grass Wonder", 1012: "Hishi Amazon",
    1013: "Mejiro McQueen", 1014: "El Condor Pasa", 1015: "T.M. Opera O",
    1016: "Narita Brian", 1017: "Symboli Rudolf", 1018: "Air Groove",
    1019: "Agnes Digital", 1020: "Seiun Sky", 1021: "Tamamo Cross",
    1022: "Fine Motion", 1023: "Biwa Hayahide", 1024: "Mayano Top Gun",
    1025: "Manhattan Cafe", 1026: "Mihono Bourbon", 1027: "Mejiro Ryan",
    1028: "Hishi Akebono", 1029: "Yukino Bijin", 1030: "Rice Shower",
    1031: "Ines Fujin", 1032: "Agnes Tachyon", 1033: "Admire Vega",
    1034: "Inari One", 1035: "Winning Ticket", 1036: "Air Shakur",
    1037: "Eishin Flash", 1038: "Curren Chan", 1039: "Kawakami Princess",
    1040: "Gold City", 1041: "Sakura Bakushin O", 1042: "Seeking the Pearl",
    1043: "Shinko Windy", 1044: "Sweep Tosho", 1045: "Super Creek",
    1046: "Smart Falcon", 1047: "Zenno Rob Roy", 1048: "Tosen Jordan",
    1049: "Nakayama Festa", 1050: "Narita Taishin", 1051: "Nishino Flower",
    1052: "Haru Urara", 1053: "Bamboo Memory", 1054: "Biko Pegasus",
    1055: "Marvelous Sunday", 1056: "Matikanetukukitare", 1057: "Mr. C.B.",
    1058: "Meisho Doto", 1059: "Mejiro Dober", 1060: "Nice Nature",
    1061: "King Halo", 1062: "Matikanetannhauser", 1063: "Ikuno Dictus",
    1064: "Mejiro Palmer", 1065: "Daitaku Helios", 1066: "Twin Turbo",
    1067: "Satono Diamond", 1068: "Kitasan Black", 1069: "Sakura Chiyono O",
    1070: "Sirius Symboli", 1071: "Mejiro Ardan", 1072: "Yaeno Muteki",
    1074: "Mejiro Bright", 1077: "Narita Top Road", 2001: "Happy Meek",
    2002: "Bitter Glasse", 2003: "Little Cocon", 9001: "Hayakawa Tazuna",
    9002: "Director Akikawa", 9003: "Otonashi Etsuko", 9004: "Trainer Kiryuin",
    9005: "Anshinzawa Sasami", 9006: "Kashimoto Riko",
}

HEIGHT_OPTIONS = {0: "Short", 1: "Normal", 2: "Tall"}
BUST_OPTIONS = {0: "A Cup", 1: "B Cup", 2: "C Cup", 3: "D Cup", 4: "F Cup"}
SKIN_OPTIONS = {0: "Pale", 1: "Normal", 2: "Tan", 3: "Dark"}
SOCKS_OPTIONS = {
    0: "None", 1: "White Long Socks", 2: "Black Long Socks",
    3: "White Thighhighs", 4: "Black Thighhighs",
    5: "White Tights", 6: "Black Tights", 7: "Brown Tights"
}
TAIL_OPTIONS = {-1: "No Tail", 1: "Pointed Tail", 2: "Flat Tail"}
RACE_OPTIONS = {1: "1", 2: "2", 3: "3"}

FIELDS = [
    ("height", "Height", HEIGHT_OPTIONS),
    ("bust", "Bust", BUST_OPTIONS),
    ("skin", "Skin", SKIN_OPTIONS),
    ("socks", "Socks", SOCKS_OPTIONS),
    ("tail_model_id", "Tail", TAIL_OPTIONS),
    ("race_running_type", "Race Running Type", RACE_OPTIONS),
    ("scale", "Scale", None),
]


def clear():
    os.system("cls")


def get_patch_status() -> str:
    if not os.path.exists(DB_PATH):
        return "Status: DB not found"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        unpatched = 0
        for table in TABLES:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE sex = 1")
            unpatched += cursor.fetchone()[0]
        conn.close()
        if unpatched == 0:
            return "Status: Patched"
        return f"Status: Not Patched ({unpatched} unpatched rows)"
    except Exception as e:
        return f"Status: Error ({e})"


def patch() -> str:
    if not os.path.exists(DB_PATH):
        return "DB not found."
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        total = 0

        for table in TABLES:
            cursor.execute(f"UPDATE {table} SET sex = 2 WHERE sex = 1")
            total += cursor.rowcount

        conn.commit()
        conn.close()
        return f"Patched {total} rows. Backup saved."
    except Exception as e:
        return str(e)


def reset() -> str:
    if not os.path.exists(BACKUP_PATH):
        return "No backup found."
    shutil.copy2(BACKUP_PATH, DB_PATH)
    return "Reset complete."


def open_db_dir():
    os.startfile(os.path.dirname(DB_PATH))


def get_char_row(char_id: int) -> dict | None:
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT height, bust, scale, skin, shape, socks, personal_dress, tail_model_id, race_running_type "
            "FROM chara_data WHERE id = ?",
            (char_id,)
        )
        row = cursor.fetchone()
    except sqlite3.OperationalError as e:
        conn.close()
        return {"error": str(e)}
    conn.close()
    if row is None:
        return None
    return {
        "height": row[0], "bust": row[1], "scale": row[2],
        "skin": row[3], "shape": row[4], "socks": row[5],
        "personal_dress": row[6], "tail_model_id": row[7],
        "race_running_type": row[8],
    }


def get_scale_range() -> tuple[int, int]:
    if not os.path.exists(DB_PATH):
        return (100, 200)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(scale), MAX(scale) FROM chara_data")
    row = cursor.fetchone()
    conn.close()
    return (row[0] - 20, row[1] + 20)


def save_char_row(char_id: int, data: dict) -> str:
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chara_data SET height=?, bust=?, scale=?, skin=?, socks=?, tail_model_id=?, race_running_type=? WHERE id=?",
            (
                data["height"], data["bust"], data["scale"],
                data["skin"], data["socks"],
                data["tail_model_id"], data["race_running_type"],
                char_id,
            )
        )
        conn.commit()
        conn.close()
        return "Saved."
    except Exception as e:
        return str(e)


def read_key() -> str:
    key = msvcrt.getch()
    if key == b"\xe0":
        key = msvcrt.getch()
        if key == b"H":
            return "UP"
        if key == b"P":
            return "DOWN"
        if key == b"K":
            return "LEFT"
        if key == b"M":
            return "RIGHT"
    if key in (b"\r", b"\n"):
        return "ENTER"
    if key == b"\x08":
        return "BACKSPACE"
    if key == b"\x1b":
        return "ESC"
    return key.decode("utf-8", errors="ignore")


def draw_menu(selected: int, options: list[str], message: str = ""):
    clear()
    print(f"{CYAN}{BOLD}Buruma Patcher by Shibiko{RESET}")
    print(f"{CYAN}{'─' * 30}{RESET}")
    print(f" {get_patch_status()}")
    print(f"{CYAN}{'─' * 30}{RESET}")
    print()
    for i, option in enumerate(options):
        if i == selected:
            print(f"  {INVERT}> {option}{RESET}")
        else:
            print(f"    {option}")
    print()
    print(f"{CYAN}{'─' * 30}{RESET}")
    print(f"{CYAN}↑↓ Navigate   Enter Select{RESET}")
    if message:
        print(f"\n{message}")
        print(f"\n{CYAN}Press any key to continue...{RESET}", end="", flush=True)


def wait_for_key():
    msvcrt.getch()


def draw_character_picker(query: str, filtered: list[tuple], selected: int, visible_start: int, visible_count: int = 15):
    clear()
    print(f"{CYAN}{BOLD}Buruma Patcher by Shibiko — Character Editor{RESET}")
    print(f"{CYAN}{'─' * 40}{RESET}")
    print(f" Search: {query}_")
    print(f"{CYAN}{'─' * 40}{RESET}")

    visible = filtered[visible_start:visible_start + visible_count]
    for i, (char_id, name) in enumerate(visible):
        actual = visible_start + i
        if actual == selected:
            print(f"  {INVERT}> {char_id} {name}{RESET}")
        else:
            print(f"    {char_id} {name}")

    print()
    print(f"{CYAN}{'─' * 40}{RESET}")
    print(f"{CYAN}↑↓ Navigate   Enter Select   ESC Back{RESET}")


def character_picker() -> int | None:
    all_chars = sorted(CHARACTER_NAMES.items())
    query = ""
    selected = 0
    visible_start = 0
    visible_count = 15

    while True:
        filtered = [(cid, name) for cid, name in all_chars if query.lower() in name.lower() or query in str(cid)]
        if selected >= len(filtered):
            selected = max(0, len(filtered) - 1)

        draw_character_picker(query, filtered, selected, visible_start, visible_count)
        key = read_key()

        if key == "ESC":
            return None
        elif key == "BACKSPACE":
            query = query[:-1]
            selected = 0
            visible_start = 0
        elif key == "UP":
            if selected > 0:
                selected -= 1
                if selected < visible_start:
                    visible_start = selected
        elif key == "DOWN":
            if selected < len(filtered) - 1:
                selected += 1
                if selected >= visible_start + visible_count:
                    visible_start = selected - visible_count + 1
        elif key == "ENTER":
            if filtered:
                return filtered[selected][0]
        elif len(key) == 1:
            query += key
            selected = 0
            visible_start = 0


def draw_field_editor(char_id: int, name: str, data: dict, selected: int, scale_range: tuple, message: str = ""):
    clear()
    print(f"{CYAN}{BOLD}Buruma Patcher by Shibiko — Editing: {char_id} {name}{RESET}")
    print(f"{CYAN}{'─' * 40}{RESET}")
    print()

    for i, (field, label, options) in enumerate(FIELDS):
        value = data[field]
        if options is not None:
            display = options.get(value, str(value))
        else:
            display = str(value)

        if i == selected:
            print(f"  {INVERT}> {label:<20} {display}{RESET}")
        else:
            print(f"    {label:<20} {display}")

    print()
    print(f"{CYAN}{'─' * 40}{RESET}")
    print(f"{CYAN}↑↓ Navigate   ←→ Change Value   Enter Save   ESC Back{RESET}")
    if message:
        print(f"\n{message}")
        print(f"\n{CYAN}Press any key to continue...{RESET}", end="", flush=True)


def cycle_option(options: dict, current: int, direction: int) -> int:
    keys = sorted(options.keys())
    if current not in keys:
        return keys[0]
    index = keys.index(current)
    return keys[(index + direction) % len(keys)]


def field_editor(char_id: int) -> str | None:
    name = CHARACTER_NAMES.get(char_id, str(char_id))
    data = get_char_row(char_id)
    if data is None:
        return "Character not found in DB."
    if "error" in data:
        return data["error"]

    scale_range = get_scale_range()
    selected = 0
    message = ""

    while True:
        draw_field_editor(char_id, name, data, selected, scale_range, message)
        if message:
            wait_for_key()
            message = ""
            continue

        key = read_key()

        if key == "ESC":
            return None
        elif key == "UP":
            if selected > 0:
                selected -= 1
        elif key == "DOWN":
            if selected < len(FIELDS) - 1:
                selected += 1
        elif key in ("LEFT", "RIGHT"):
            direction = 1 if key == "RIGHT" else -1
            field, label, options = FIELDS[selected]
            if options is not None:
                data[field] = cycle_option(options, data[field], direction)
            else:
                data[field] = max(scale_range[0], min(scale_range[1], data[field] + direction))
        elif key == "ENTER":
            message = save_char_row(char_id, data)


def menu():
    options = ["Patch", "Reset", "Edit Character", "Open DB Folder", "Exit"]
    selected = 0
    message = ""

    while True:
        draw_menu(selected, options, message)
        if message:
            wait_for_key()
            message = ""
            continue

        key = read_key()

        if key == "UP" and selected > 0:
            selected -= 1
        elif key == "DOWN" and selected < len(options) - 1:
            selected += 1
        elif key == "ENTER":
            if selected == 0:
                message = patch()
            elif selected == 1:
                message = reset()
            elif selected == 2:
                char_id = character_picker()
                if char_id is not None:
                    result = field_editor(char_id)
                    if result:
                        message = result
            elif selected == 3:
                open_db_dir()
            elif selected == 4:
                clear()
                sys.exit(0)


def main():
    if os.path.exists(DB_PATH) and not os.path.exists(BACKUP_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
    menu()


if __name__ == "__main__":
    main()