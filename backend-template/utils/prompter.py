import pandas as pd

class MedPrompter:

    def __init__(self, data_df, language:str) -> None:
        self.data = data_df
        self.lang = language.lower()

    def extract_info(self):
        report_prompt = ""
        for idx, row in self.data.iterrows():
            if self.lang == "es":
                if row['Ref Low'] == 0.0:
                    line = f"El test de {row['Test']} tiene un valor de {row['Value']} {row['Unit']} y el rango aceptado de valores es menor (<) que {row['Ref High']} {row['Unit']}.\n"
                
                elif row['Ref High'] == "inf":
                    line = f"El test de {row['Test']} tiene un valor de {row['Value']} {row['Unit']} y el valor tiene que ser mayor (>) que {row['Ref Low']} {row['Unit']}.\n"
                else:
                    line = f"El test de {row['Test']} tiene un valor de {row['Value']} {row['Unit']} y el rango aceptado de valores es [{row['Ref Low']}, {row['Ref High']}] {row['Unit']}.\n"
            else:
                if row['Ref Low'] == 0.0:
                    line = f"{row['Test']} has a value of {row['Value']} {row['Unit']} and the accepted range of values is [{row['Ref Low']}, {row['Ref High']}] {row['Unit']}.\n"
                elif row['Ref High'] == "inf":
                    line = f"{row['Test']} has a value of {row['Value']} {row['Unit']} and the accepted range of values is [{row['Ref Low']}, {row['Ref High']}] {row['Unit']}.\n"
                else:
                    line = f"{row['Test']} has a value of {row['Value']} {row['Unit']} and the accepted range of values is [{row['Ref Low']}, {row['Ref High']}] {row['Unit']}.\n"

            report_prompt += line

        return report_prompt