import csv
import requests
import logging
import os
from dotenv import load_dotenv
# load env
load_dotenv()
# get api key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# logging
logging.basicConfig(
    filename='etl_log.log',
    level=logging.INFO,
    format='%(asctime)s = %(levelname)s = %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)
# extract
def extract():
    if not WEATHER_API_KEY:
        logger.error("not found api_key")
        return
    logger.info("Get data from api")
    url =f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q=Hanoi&aqi=no"
    reponse = requests.get(url, timeout = 10)
    reponse.raise_for_status()
    logger.info("success")
    return reponse.json()

def transform(raw_data):
    if not raw_data:
        logger.warning("no data to transform")
        return []
    logger.info("start transform data")
    location = raw_data.get('location',{})
    current = raw_data.get('current',{})
    cleaned_data = [
        {
        "city" : location.get('name', ''),
        "country" : location.get('country', ''),
        "time_recorded" : current.get('last_updated',''),
        "feels_like_c": current.get("feelslike_c"),
        "humidity_percent": current.get("humidity"),
        "wind_kmh": current.get("wind_kph"),
        "condition": current.get("condition", {}).get("text"),
    }
    ]
    logger.info("transform data success")
    return cleaned_data
def load_csv(data, filename='weather_data.csv'):
    if not data:
        logger.warning("no data to load")
        return 
    logger.info("load to csv")
    fieldnames = data[0].keys()

    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(data)

    logger.info("load to csv success")

if __name__ == "__main__":
    logger.info("=== RUN PIPELINE WEATHERAPI ===")
    raw = extract()
    clean = transform(raw)
    load_csv(clean)
    logger.info("=== FINISH PIPELINE ===")
