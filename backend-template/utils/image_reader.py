import easyocr
import logging

class ImageReader:

    def __init__(self, lang:list = ["es", "en"]) -> None:
        self.reader = easyocr.Reader(lang)
        self.logger = logging.getLogger(__name__)

    def read_img2text(self, img_path:str):
        self.logger.info("Starting text extraction from given image...")
        text_n_info = self.reader.readtext(img_path)
        self.logger.info("Finished text extraction from given image...")
        text = [output[1] for output in text_n_info]
        return text, text_n_info