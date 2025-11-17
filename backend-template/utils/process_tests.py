import PIL
import pdf2image
from pypdf import PdfReader
import logging

class DataProcessor:
    def __init__(self, data_root, img_format=".jpg") -> None:
        self.img_format = img_format
        self.data_root = data_root
        self.logger = logging.getLogger(__name__)

    def process_pdf_to_img(self, file_path, save_files:bool = False):
        img_file = pdf2image.convert_from_path(file_path)
        file_name = file_path.split("/")[-1].split(".")[0]
        print(file_name)
        if save_files:
            # May have multiple pages
            for i, img in enumerate(img_file):
                img.save(f"{self.data_root}/image/{file_name}_{i}{self.img_format}")

    def read_pdf(self, file_path):
        pdf_reader = PdfReader(file_path)
        self.logger.info("Complete PDF reading!")
        self.logger.info(f"Uploaded PDF has {len(pdf_reader.pages)} pages.")
        
        for i, page in enumerate(pdf_reader.pages):
            # print(page.extract_text())
            pass

        return pdf_reader
        

if __name__ == "__main__":
    data_root = r"C:/Users/seque/OneDrive - UAM/Escritorio/IPCV MASTER/NOTES/BORDEAUX/SOFTWARE DEVELOPMENT PROJECT/blood-analizer/data"
    file_path = r"C:/Users/seque/OneDrive - UAM/Escritorio/IPCV MASTER/NOTES/BORDEAUX/SOFTWARE DEVELOPMENT PROJECT/blood-analizer/data/pdf/Blood_Test_Sample_JS.pdf"
    processor = DataProcessor(data_root=data_root)
    processor.process_pdf_to_img(file_path=file_path, save_files=True)