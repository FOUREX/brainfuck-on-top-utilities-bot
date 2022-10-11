from requests import get
from io import BytesIO
from PIL import Image


from utilities.db import conn, cur, new_user
from config import config


STANDARD_ALERTS_MAP_THEME = config["standard_alerts_map_theme"]


masks = {
    "Сумська": 1,
    "Чернігівська": 2,
    "Київська": 3,
    "Житомирська": 4,
    "Рівненська": 5,
    "Волинська": 6,
    "Львівська": 7,
    "Закарпатська": 8,
    "Івано-Франківська": 9,
    "Тернопільська": 10,
    "Чернівецька": 11,
    "Хмельницька": 12,
    "Вінницька": 13,
    "Одеська": 14,
    "Черкаська": 15,
    "Кіровоградська": 16,
    "Миколаївська": 17,
    "Полтавська": 18,
    "Харківська": 19,
    "Луганська": 20,
    "Дніпропетровська": 21,
    "Донецька": 22,
    "Запорізька": 23,
    "Херсонська": 24,
    "Автономна Республіка Крим": 25
}


def get_alerts_map_theme(user_id: int, chat_id: int):
    sql = "SELECT alerts_map_theme FROM users WHERE chat_id = ? AND user_id = ?"
    cur.execute(f"SELECT EXISTS({sql})", (chat_id, user_id))
    user_is_exists = bool(cur.fetchone()[0])

    if not user_is_exists:
        new_user(chat_id, user_id, STANDARD_ALERTS_MAP_THEME)

        conn.commit()
        return STANDARD_ALERTS_MAP_THEME

    cur.execute(sql, (chat_id, user_id))
    theme = cur.fetchone()[0]

    return theme


def set_alerts_map_theme(user_id: int, chat_id: int, theme: str):
    cur.execute("UPDATE users SET alerts_map_theme = ? WHERE chat_id = ? and user_id = ?", (theme, chat_id, user_id))

    conn.commit()


def get_data():
    data = get("https://api.alerts.in.ua/v1/alerts/active.json")
    data = data.json()

    return data


def get_alerts() -> dict:
    data = get_data()
    data_alerts = data["alerts"]
    data_meta = data["meta"]

    alerts = {}
    locates = {}

    for locate in data_alerts:
        if locate["alert_type"] == "air_raid":
            location_title = locate["location_title"]
            location_type = locate["location_type"]
            started_at = locate["started_at"]

            locates.update({
                location_title: {
                    "type": location_type,
                    "started_at": started_at
                }
            })

    alerts.update({
        "locates": locates,
        "last_updated_at": data_meta["last_updated_at"]
    })

    return alerts


def get_alerts_map(chat_id: int, user_id: int, edge_offset: int = 50) -> BytesIO:
    image = BytesIO()
    image.name = "Brainfuck_on_top_utilities_bot alerts_map"

    theme = get_alerts_map_theme(chat_id, user_id)

    map_mask = Image.open(f"src/alerts/themes/{theme}/mask.png")
    ukraine_map = Image.open(f"src/alerts/themes/{theme}/map.png")
    map_mask.convert("RGBA")
    ukraine_map.convert("RGBA")

    alerts_map_size = ukraine_map.size[0] + edge_offset * 2, ukraine_map.size[1] + edge_offset * 2
    alerts_map_color = ukraine_map.getpixel((0, 0))
    alerts_map = Image.new("RGBA", alerts_map_size, alerts_map_color)

    alerts_map.paste(ukraine_map, (edge_offset, edge_offset))

    alerts = get_alerts()
    alerts_locates = alerts["locates"]
    for locate in alerts["locates"]:
        locate_info = alerts_locates[locate]
        if locate_info["type"] == "oblast":
            locate = locate.replace(" область", "")
            image_name = masks[locate]

            mask = Image.open(f"src/alerts/regions masks/{image_name}.png")
            mask.convert("RGBA")

            alerts_map.paste(map_mask, (edge_offset, edge_offset), mask)

    alerts_map.save(image, "PNG")
    image.seek(0)

    return image
