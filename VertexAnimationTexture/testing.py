import os

image_path = r"C:\Users\charl\Downloads\dumper\T_pPlane1_position_VAT.png"

if not os.path.exists(image_path):
    raise FileNotFoundError(f"File does not exist: {image_path}")