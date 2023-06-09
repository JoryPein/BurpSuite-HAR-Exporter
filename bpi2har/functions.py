from .harlog import HarLog
import pathlib


def bpi2har_run(xml_path:pathlib.Path, result_path:pathlib.Path):
    HarLog().generate_har(xml_path, result_path)
