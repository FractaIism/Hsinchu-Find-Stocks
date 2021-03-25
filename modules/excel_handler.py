from modules.libraries import *
from modules.globals import *
import modules.utilities

def getProductList(ws) -> list[str]:
    """Get list of products that we want to search for.
    Input: Excel spreadsheet object (not workbook)
    Output: List of product names to search for
    """
    firstCell = ws.range('E2')  # type:xlwings.Range
    lastCell = ws.range('E:E').end("down")  # type:xlwings.Range
    product_list = ws.range(firstCell, lastCell).value
    return product_list if isinstance(product_list, list) else [product_list]

def clearResults() -> None:
    """Clear search results in Excel spreadsheet
    (Only to be called from Excel)
    """
    ws = xlwings.Book(bookname).sheets[0]
    # ws = xlwings.sheets.active
    firstCell = ws.range('F2')
    lastCell = ws.range('F1048576').end("up")
    cells = ws.range(firstCell, lastCell)
    cells.clear()

def getBrandList() -> list[modules.utilities.Brand]:
    """Get brand names (Chinese and English and Aliases)
    Input: None
    Output: Dict of brand names as keys and empty lists as values
    """

    def csv2list(csv_str: str) -> list[str]:
        mylist = csv_str.split(',')
        for index, value in enumerate(mylist):
            mylist[index] = value.strip()
        return mylist

    ws = xlwings.Book(bookname).sheets["廠牌列表"]
    brand_list = []
    row = 2
    while ws[f"A{row}"].value or ws[f"B{row}"].value:
        # get brand names from preconfigured table data
        ch = ws[f"A{row}"].value
        eng = ws[f"B{row}"].value
        aliases_str = ws[f"C{row}"].value
        # convert csv to list, default to empty list if no alias exists
        aliases_list = csv2list(aliases_str) if aliases_str is not None else []
        brand=modules.utilities.Brand(ch,eng,aliases_list)
        brand_list.append(brand)
        row += 1

    return brand_list
