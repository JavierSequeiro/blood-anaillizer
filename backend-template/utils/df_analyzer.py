import pandas as pd
import os
import os.path as osp


class DFAnalyzer:

    def __init__(self, data_df) -> None:
        self.df = data_df


    def get_colored_csv(self, save_csv:bool, **kwargs):

        def highlight_value(val, low, high):
            try:
                if low <= val <= high:
                    return "background-color: lightgreen"
                
                else:
                    return "background-color: lightred"
                
            except:
                return ""
            
        df_colored = self.df.style.apply(lambda row: [
        highlight_value(row["Value"], row["Ref Low"], row["Ref High"]) if col == "Value" else ""
        for col in self.df.columns], axis=1)

        if save_csv:
            df_colored.to_csv(kwargs["csv_path"])

        return df_colored
    
    def get_colored_xlsx(self, save_xlsx:bool, **kwargs):

        def highlight_value(val, low, high):
            try:
                if low <= val <= high:
                    return "background-color: lightgreen"
                
                else:
                    # return "background-color: #red"
                    return "background-color: #FF4500"
                
            except:
                return ""
            
        df_colored = self.df.style.apply(lambda row: [
        highlight_value(row["Value"], row["Ref Low"], row["Ref High"]) if col == "Value" else ""
        for col in self.df.columns], axis=1)

        if save_xlsx:
            excel_path = kwargs["excel_path"]
            if osp.exists(excel_path):
                os.remove(excel_path)
            df_colored.to_excel(excel_path)

        return df_colored