from collections import Counter
from yolov5 import YOLOv5
from PIL import Image
import pymupdf as fitz
import base64
from PIL import Image
import pytesseract

class SardineZone:
    _id: str
    _type: str
    _coordinates: list[float]
    _content: list[list[str]]

    def __init__(self, id: str, type: str, coordinates: list[float], content: str = ""):
        self._id = id
        self._type = type
        self._coordinates = coordinates
        self._content = content
    
    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "type": self._type,
            "coordinates": self._coordinates,
            "content": self._content
        }

class SardinePage:
    _page: any
    _page_number: int
    _content: str
    _image: Image
    _zones: list[SardineZone]
    _type: int
    _read: bool = False

    def __init__(self, page: any, page_number: int, content: str = None):
        self._page = page
        self._page_number = page_number
        self._content = content if content else page.get_text()
        self._zones = []
        self._type = None

        self.load_image()

    def load_image(self):
        pix = self._page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        self._image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    def load_zones(self, model: YOLOv5):

        for zone in model.predict(self._image).xywh[0]:
            x1 = zone[0].item() - zone[2].item() / 2
            y1 = zone[1].item() - zone[3].item() / 2
            x2 = zone[2].item() + x1
            y2 = zone[3].item() + y1
            self._zones.append(SardineZone(
                id=zone[4].item(),
                type=zone[5].item(),
                coordinates=[x1, y1, x2, y2],
            ))
        
    def read_zone(self):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Utilisateur\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

        for zone in self._zones:
            if not zone._content == "": continue
            
            x1, y1, x2, y2 = zone._coordinates
            cropped_image = self._image.crop((x1, y1, x2, y2)).convert("RGB")
            zone._content = pytesseract.image_to_string(cropped_image, lang="fra+eng").strip()
            zone._content = zone._content.replace("\n\n", "\n").split("\n")
            zone._content = [line.split("\t") if "\t" in line else [line] for line in zone._content]
        
        self._read = True

    def load_type(self):
        if len(self._zones) == 0: 
            self._type = 10
            return
        
        temp_types = [zone._type // 20 for zone in self._zones]
        most_common_type, occ_common_type = Counter(temp_types).most_common(1)[0]
        self._type = 10 if occ_common_type <= 2 and (most_common_type == 0 or most_common_type == 5) else most_common_type

    def to_dict(self) -> dict:
        return {
            "number": self._page_number,
            "zones": [zone.to_dict() for zone in self._zones],
            "type": self._type
        }

class SardineDocument:
    _bytes: bytes
    _pages: list[SardinePage]

    def __init__(self, document64: str):
        self._bytes = base64.b64decode(document64)
        self._pages = []

    def load_pages(self, model, version) -> list[SardinePage]:
        document = fitz.open(stream=self._bytes, filetype="pdf")
        self._pages = [SardinePage(document.load_page(i), i) for i in range(len(document))]

        model = YOLOv5(f"src/static/agents/{model}/{version}.pt", device="cpu")
        for page in self._pages:
            page.load_zones(model)
            page.load_type()
    
    def read_zones(self):
        for page in self._pages:
            page._read = True
            page.read_zone()
            print(f"Page {page._page_number} read with {len(page._zones)} zones.")
            

    def to_dict(self) -> dict:
        return {
            "types": Counter([page._type for page in self._pages]),
            "pages": [page.to_dict() for page in self._pages]
        }

class Sardine:
    _document: SardineDocument

    def __init__(self, model: str = "sadr", version: str = "latest"):
        self.model = model
        self.version = version

    def load_document(self, base64: str):
        self._document = SardineDocument(base64)
        self._document.load_pages(self.model, self.version)

    def read_document(self):
        self._document.read_zones()