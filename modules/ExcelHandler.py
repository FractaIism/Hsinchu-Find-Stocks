from modules.libraries import *
from modules.globals import *

class ExcelHandler:
    # noinspection PyMethodMayBeStatic
    def getProductList(self, ws):
        """Get list of products that we want to search for.
        Input: Excel spreadsheet object (not workbook)
        Output: List of product names to search for"""
        firstCell = ws.range('E2')  # type:xlwings.Range
        lastCell = ws.range('E:E').end("down")  # type:xlwings.Range
        product_list = ws.range(firstCell, lastCell).value
        return product_list if isinstance(product_list, list) else [product_list]

    # noinspection PyMethodMayBeStatic
    def clearResults(self):
        """Clear search results in Excel spreadsheet
        (Only to be called from Excel)"""
        # ws = xlwings.Book(bookname).sheets[0]
        ws = xlwings.sheets.active
        firstCell = ws.range('F2')
        lastCell = ws.range('F1048576').end("up")
        cells = ws.range(firstCell, lastCell)
        cells.clear()

    # noinspection PyMethodMayBeStatic
    def getBrandList(self) -> list[tuple[str, str, list[str]]]:
        """Get brand names (Chinese and English and Alias)
        Input: None
        Output: Dict of brand names as keys and empty lists as values"""

        def csv2list(csv_str: str):
            mylist = csv_str.split(',')
            for index, value in enumerate(mylist):
                mylist[index] = value.strip()
            return mylist

        ws = xlwings.Book(bookname).sheets["廠牌列表"]
        brand_list = []
        row = 2
        while ws[f"A{row}"].value or ws[f"B{row}"].value:
            ch = ws[f"A{row}"].value
            eng = ws[f"B{row}"].value
            aliases_str = ws[f"C{row}"].value
            aliases_list = csv2list(aliases_str) if aliases_str is not None else []
            brand_list.append((ch, eng, aliases_list))
            row += 1

        return brand_list
