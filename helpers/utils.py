from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent    # folder PROJEK (induk dari helpers/)
SVG_DIR = ROOT / "assets" / "SVG"
 
PATH_POHON    = str(SVG_DIR / "pohon.svg")
PATH_API      = str(SVG_DIR / "api.svg")
PATH_PETA     = str(SVG_DIR / "peta.svg")
PATH_AWAN     = str(SVG_DIR / "awan.svg")
PATH_MATAHARI = str(SVG_DIR / "matahari.svg")
PATH_TERMOMETER = str(SVG_DIR / "thermometer.svg")
