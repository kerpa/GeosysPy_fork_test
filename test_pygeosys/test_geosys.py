from datetime import datetime
from geosyspy.geosys import Geosys
from dotenv import load_dotenv
import os
import datetime as dt
import numpy as np

# read .env file
load_dotenv()

API_CLIENT_ID = os.getenv("API_CLIENT_ID")
API_CLIENT_SECRET = os.getenv("API_CLIENT_SECRET")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")


class TestGeosys:

    # polygon with two pixels : mh11v4i225j4612, mh11v4i226j4612
    polygon = "POLYGON((-91.29152885756007 40.39177489815265,-91.28403789132507 40.391776131485386,-91.28386736508233 40.389390758655935,-91.29143832829979 40.38874592864832,-91.29152885756007 40.39177489815265))"
    client = Geosys(
        API_CLIENT_ID, API_CLIENT_SECRET, API_USERNAME, API_PASSWORD, "preprod", "na"
    )

    def test_authenticate(self):
        assert set(
            [
                "access_token",
                "expires_in",
                "token_type",
                "scope",
                "expires_at",
                "refresh_token",
            ]
        ).issubset(set(self.client.token.keys()))

    def test_get_time_series(self):

        start_date = dt.datetime.strptime("2020-01-01", "%Y-%m-%d")
        end_date = dt.datetime.strptime("2020-01-07", "%Y-%m-%d")

        df = self.client.get_time_series(self.polygon, start_date, end_date, "NDVI")

        assert df.index.name == "date"
        assert "value" in df.columns
        assert "index" in df.columns
        assert len(df.index) == 7
        date_range = list(map(lambda x: x.strftime("%Y-%m-%d"), df.index))
        assert set(
            [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-04",
                "2020-01-05",
                "2020-01-06",
                "2020-01-07",
            ]
        ).issubset(set(date_range))

    def test_get_time_series_by_pixel(self):

        start_date = dt.datetime.strptime("2020-01-01", "%Y-%m-%d")
        end_date = dt.datetime.strptime("2020-01-07", "%Y-%m-%d")

        df = self.client.get_time_series_by_pixel(
            self.polygon, start_date, end_date, "NDVI"
        )
        assert df.index.name == "date"
        assert set(["value", "index", "pixel.id"]).issubset(set(df.columns))
        assert np.all((df["index"].values == "NDVI"))
        assert len(df.index) == 14

        assert set(
            [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-04",
                "2020-01-05",
                "2020-01-06",
                "2020-01-07",
            ]
        ).issubset(set(df.index))

        assert set(["mh11v4i225j4612", "mh11v4i226j4612"]).issubset(set(df["pixel.id"]))

    def test_get_coverage_in_season_ndvi(self):
        start_date = dt.datetime.strptime("2021-01-01", "%Y-%m-%d")
        end_date = dt.datetime.strptime("2022-01-01", "%Y-%m-%d")
        df = self.client.get_coverage_in_season_ndvi(self.polygon, start_date, end_date, "SENTINEL_2")

        assert set(
            [
                "coverageType",
                "image.id",
                "image.availableBands",
                "image.sensor",
                "image.soilMaterial",
                "image.spatialResolution",
                "image.weather",
                "image.date",
                "seasonField.id"
            ]
        ).issubset(set(df.columns))

    def test_get_image_as_array(self):
        """
        """

        # The following image has 4 bands, and contains 76*71 pixels.

        img_field_id = "d1bqwqq"
        img_id = "IKc73hpUQ6spGyDC80dOd8SDFIKHF1CezmxsZGmXlzg"
        img_arr = self.client.get_image_as_array(img_field_id, img_id)
        assert img_arr.shape == (4,76,71)
        assert type(img_arr) ==  np.ndarray

    def test_get_weather_temperature(self):

        start_date = dt.datetime.strptime("2021-01-01", "%Y-%m-%d")
        end_date = dt.datetime.strptime("2022-01-01", "%Y-%m-%d")

        df = self.client.get_weather_temperature(self.polygon, start_date, end_date)

        assert set(
            [
                "date",
                "temperature.groundMin",
                "temperature.ground",
                "temperature.agro",
                "temperature.agroMin",
                "temperature.agroMax",
                "temperature.standardMin",
                "temperature.standard",
                "temperature.standardMax",
            ]
        ).issubset(set(df.columns))
