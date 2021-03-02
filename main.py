import libraries
from utilities import *

bookname = "測試單.xlsm"

def main():
    os.chdir(os.path.dirname(__file__))
    ws = xlwings.Book(bookname).sheets[0]
    firstCell = ws.range('E2')  # type:xlwings.Range
    lastCell = ws.range('E:E').end("down")  # type:xlwings.Range
    product_list = ws.range(firstCell, lastCell).value
    print(len(product_list), product_list)
    result_list = []
    for index, product in enumerate(product_list):
        print(f"Search product: {product}")
        result = searchProduct(product)
        ws[f'F{2 + index}'].value = result
    exit()

    htmlfile = open("搜尋結果.html", "w")
    htmlfile.write(resp.text)
    htmlfile.flush()
    htmlfile.close()

def clearResults():
    ws = xlwings.Book(bookname).sheets[0]
    firstCell = ws.range('F2')
    lastCell = ws.range('F1048576').end("up")
    cells = ws.range(firstCell, lastCell)
    cells.clear()

if __name__ == '__main__':
    main()
