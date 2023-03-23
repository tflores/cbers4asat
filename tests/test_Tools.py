from cbers4asat.tools import rgbn_composite, grid_download
from rasterio import open as rasterio_open
from fixtures import rgb_assert_metadata
from os import remove
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent.resolve() / 'data'


class MockResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    @staticmethod
    def iter_content(chunk_size):
        yield b"dummydata"


class TestTools:

    @pytest.mark.datafiles(
        FIXTURE_DIR / 'BAND1.tif',
        FIXTURE_DIR / 'BAND2.tif',
        FIXTURE_DIR / 'BAND3.tif'
    )
    def test_rgbn_composite(self, rgb_assert_metadata, tmp_path, datafiles):
        rgbn_composite(
            red=datafiles / 'BAND3.tif',
            green=datafiles / 'BAND2.tif',
            blue=datafiles / 'BAND1.tif',
            outdir=tmp_path.as_posix(),
            filename='RGBN_COMPOSITE_TEST.tif'
        )

        print(tmp_path.as_posix())

        with rasterio_open(f"{tmp_path.as_posix()}/RGBN_COMPOSITE_TEST.tif") as raster:
            assert rgb_assert_metadata == raster.meta

        remove(f"{tmp_path.as_posix()}/RGBN_COMPOSITE_TEST.tif")

    def test_grid_download(self, monkeypatch, tmp_path):
        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr("requests.Session.get", mock_get)

        grid_download(satellite='amazonia1', sensor='wfi', outdir=tmp_path.as_posix())

        with open(f"{tmp_path.as_posix()}/grid_amazonia1_wfi_sa.zip", 'rb') as f:
            assert f.read() == b"dummydata"

        remove(f"{tmp_path.as_posix()}/grid_amazonia1_wfi_sa.zip")