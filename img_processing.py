import os
os.environ.pop("PROJ_LIB", None)
os.environ.pop("PROJ_DATA", None)
import rasterio
from rasterio.warp import transform_bounds
from rasterio.mask import mask
from pathlib import Path

def merge_bands(band_files, output_path):
    with rasterio.open(band_files[0]) as src0:
        meta = src0.meta.copy()

    meta.update({
        "driver": "GTiff",
        "count": len(band_files),
    })
    id
    with rasterio.open(output_path, 'w', **meta) as dest:
        for id_band, file in enumerate(band_files, start=1):
            with rasterio.open(file) as src:
                data = src.read(1)
                dest.write(data, id_band)
                name = Path(file).stem[-3:]
                dest.set_band_description(id_band, name)


def clip(img_path, output_path, col_start, row_start, col_end, row_end):
    with rasterio.open(img_path) as src:
        min_x, min_y, max_x, max_y = transform_bounds(
            "EPSG:4326", 
            src.crs, 
            col_start, row_start, col_end, row_end
        )
        boundary = [
            {
                "type": "Polygon",
                "coordinates": [[
                    [min_x, min_y],
                    [min_x, max_y],
                    [max_x, max_y],
                    [max_x, min_y],
                    [min_x, min_y]
                ]]
            }
        ]
        clipped, transform = mask(src, boundary, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": clipped.shape[1],
            "width": clipped.shape[2],
            "transform": transform
        })
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(clipped)


if __name__ == "__main__":

    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

    for year in years:
        bands = list(Path(f"./images/{year}").glob("*.jp2"))
        output_path = f"images/{year}/img_{year}.tiff"
        merge_bands(bands, output_path)


    images = [file for year in years for file in Path(f"./images").glob(f"*{year}/*.tiff")]

    for img in images:
        output_path = img.parent / f"clipped_{img.stem}.tiff"
        clip(img, output_path, -0.215, 38.676, -0.187, 38.695)
