from modules.libraries import *
from modules.globals import *
import modules.utilities

def getProductList() -> list[str]:
    """Get list of products that we want to search for.
    Input: Excel spreadsheet object (not workbook)
    Output: List of product names to search for
    """
    ws = xlwings.Book.caller().sheets["新竹查庫存"]
    firstCell = ws.range('B2')  # type:xlwings.Range
    lastCell = ws.range('B:B').end("down")  # type:xlwings.Range
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

def writeSearchResult(index: int, best_match: typing.Optional[modules.utilities.Match] = None, processed_prodname: str = None):
    """Write matching ware to Excel (or defaults if no match)
    Input: index (product number starting from 0), best matching ware, pure product name (temp for debugging)
    Output: None
    """
    ws = xlwings.Book.caller().sheets("新竹查庫存")
    row = index + 2  # row number of product in excel
    if best_match is not None:
        ws[f'C{row}'].value = best_match.original_ware_obj.name
        ws[f'D{row}'].value = best_match.original_ware_obj.quantity
        ws[f'F{row}'].value = processed_prodname
        ws[f'G{row}'].value = best_match.processed_warename
        ws[f'H{row}'].value = best_match.similarity
        if best_match.similarity in (1, modules.preprocessing.Filter.IDENTICAL):
            ws[f'C{row}'].color = (0, 255, 0)  # bright green
        elif best_match.similarity == modules.preprocessing.Filter.SUBSTRING_RELATION:
            ws[f'C{row}'].color = (0, 255, 255)  # dark cyan
        else:
            ws[f'C{row}'].color = (255, 255, 0)  # bright yellow
    else:
        ws[f'C{row}'].value = r"¯\_(ツ)_/¯"
        ws[f'D{row}'].value = "-"
        ws[f'F{row}'].value = "-"
        ws[f'G{row}'].value = "-"
        ws[f'H{row}'].value = "-"
        ws[f'C{row}'].color = (200, 200, 200)  # gray

def writeWaresByBrand(wares_by_brand: dict[str, list[modules.utilities.Ware]]):
    # output ware_dict to excel for checking
    # first create a hash table to combine chinese/english/alias brand names to prevent duplicate output
    ws2: xlwings.Sheet = xlwings.Book.caller().sheets["新竹庫存字典"]
    hash_table: dict[int, list[str]] = {}
    for _brand, _warelist in wares_by_brand.items():
        if _brand in (None, "all"):
            continue
        elif id(_warelist) in hash_table:
            hash_table[id(_warelist)].append(_brand)
        else:
            hash_table[id(_warelist)] = [_brand]
    # print to excel
    ws2.clear()
    ws2.range("A1:C1").value = ["廠牌", "數量", "商品"]
    ws2.range("A1:C1").color = (255, 192, 0)  # orange
    ws2["E1"].value = "最後更新: " + re.sub(r"\..*$", "", str(datetime.datetime.now()))
    row = 2
    for _, _brand in hash_table.items():
        brand_combined = ", ".join(_brand)
        ws2[f"A{row}"].value = brand_combined
        row += 1
        for _ware in wares_by_brand[_brand[0]]:
            ws2[f"B{row}"].value = _ware.quantity
            ws2[f"C{row}"].value = _ware.name
            row += 1

" ========== DEPRECATED ========== "

# def generateVerificationData(ws: xlwings.Sheet) -> None:
#     """Fill in exact matches to 應有品名 column. Not terribly useful."""
#     ware_list = modules.web_crawler.listWarehouse()
#     new_ware_list = list(map(lambda x: x.replace(" ", ""), ware_list))
#     for row in range(2, 250):
#         product = ws[f"E{row}"].value
#         if product.replace(" ", "") in new_ware_list:
#             ws[f"L{row}"].value = product
#             ws[f"L{row}"].color = (0, 200, 0)
#
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
