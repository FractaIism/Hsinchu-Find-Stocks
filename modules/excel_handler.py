from modules.libraries import *
from modules.globals import *
import modules.utilities

def getProductList() -> list[str]:
    """Get list of products that we want to search for.
    Input: Excel spreadsheet object (not workbook)
    Output: List of product names to search for
    """
    ws = xlwings.Book.caller().sheets["新竹查庫存"]
    firstCell = ws.range('E2')  # type:xlwings.Range
    lastCell = ws.range('E:E').end("down")  # type:xlwings.Range
    product_list = ws.range(firstCell, lastCell).value
    return product_list if isinstance(product_list, list) else [product_list]

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

    ws = xlwings.Book.caller().sheets["廠牌列表"]
    brand_list = []
    row = 2
    while ws[f"A{row}"].value or ws[f"B{row}"].value:
        # get brand names from preconfigured table data
        ch = ws[f"A{row}"].value
        eng = ws[f"B{row}"].value
        aliases_str = ws[f"C{row}"].value
        # convert csv to list, default to empty list if no alias exists
        aliases_list = csv2list(aliases_str) if aliases_str is not None else None
        brand = modules.utilities.Brand(ch, eng, aliases_list)
        brand_list.append(brand)
        row += 1

    return brand_list

def generateVerificationData(ws: xlwings.Sheet) -> None:
    """Fill in exact matches to 應有品名 column."""
    ware_list = modules.web_crawler.listWarehouse()
    new_ware_list = list(map(lambda x: x.replace(" ", ""), ware_list))
    for row in range(2, 250):
        product = ws[f"E{row}"].value
        if product.replace(" ", "") in new_ware_list:
            ws[f"L{row}"].value = product
            ws[f"L{row}"].color = (0, 200, 0)

"""DEPRECATED (clearing can be done faster with VBA)"""

# def clearResults() -> None:
#     """Clear search results in Excel spreadsheet."""
#     ws = xlwings.Book(bookname).sheets[0]
#     # ws = xlwings.sheets.active
#     firstCell = ws.range('F2')
#     lastCell = None
#     for row in range(3, 1048576):
#         if ws[f"F{row}"].value is None:
#             lastCell = ws[f"F{row - 1}"]
#             break
#     cells = ws.range(firstCell, lastCell)
#     cells.clear()
#
# def clearSimilarityData() -> None:
#     """Clear prod1, prod2, similarity fields in Excel."""
#     ws = xlwings.Book(bookname).sheets[0]
#     firstCell = ws.range('T2')
#     lastCell = None
#     for row in range(3, 1048576):
#         if ws[f"V{row}"].value is None:
#             lastCell = ws[f"V{row - 1}"]
#             break
#     cells = ws.range(firstCell, lastCell)
#     cells.clear()
