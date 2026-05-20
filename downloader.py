import os
from cdsetool.query import query_features, get_product_attribute
from cdsetool.query import describe_collection
from cdsetool.download import download_feature
from cdsetool.credentials import Credentials
from cdsetool.credentials import validate_credentials
from datetime import datetime
import shutil
from pathlib import Path
import zipfile
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("CDSE_USERNAME")
password = os.getenv("CDSE_PASSWORD")

if not validate_credentials(username=username, password=password):
    print("Nieprawidłowe dane logowania")
    exit(1)


boundary = "POLYGON((-0.21 38.69,-0.21 38.67,-0.18 38.67,-0.18 38.69,-0.21 38.69))"


bands = ["B01", "B02", "B03", "B08"]
images_path = Path("./images")
SAFE_PATH = "./download_scenes"

years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

for year in years:
    date_start = datetime(year, 1, 1, 0, 0, 0)
    date_end = datetime(year, 1, 31, 23, 59, 59)

    scenes = query_features(
        "SENTINEL-2",
        {
            "contentDateStartGe": date_start,
            "contentDateStartLe": date_end,
            "productType": "S2MSI1C",
            "geometry": boundary,
        },
        options={"expand_attributes": True}

    )

    scene_list = [scene for scene in scenes if (cc := get_product_attribute(scene, "cloudCover")) is not None and cc < 20]

    if  scene_list:
        download_feature(scene_list[0], SAFE_PATH, {"credentials": Credentials(username, password)})
    
        zip_files = list(Path(SAFE_PATH).glob("*.zip"))
        zip_files  = zip_files[0]
        if zip_files:
            with zipfile.ZipFile(zip_files, 'r') as zip_ref:

                for zip_file in zip_ref.namelist():
                    if "IMG_DATA" in zip_file and zip_file.endswith(".jp2") and any(band in zip_file for band in bands):
                        with zip_ref.open(zip_file) as source, open(images_path/str(year)/zip_file.split("/")[-1], 'wb') as target:
                            shutil.copyfileobj(source, target)

            zip_files.unlink()