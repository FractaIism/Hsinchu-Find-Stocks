from libraries import *
from globals import *

def searchProduct(product_name):
    """Deprecated
    Search for a product on 新竹倉庫 by 報表查詢
    Input: product name
    Output: list of products names found"""
    print(f"Searching for: {product_name}")
    logging.info(f"Searching for: {product_name}")

    # send HTTP request to perform search
    url = "https://lisp-tw.hct.com.tw/AA005.jsp"
    cookie_jar = browser_cookie3.chrome(domain_name = 'lisp-tw.hct.com.tw')
    cookie = cookie_jar.__iter__().__next__()
    headers = {
        "Host"                     : "lisp-tw.hct.com.tw",
        "Connection"               : "keep-alive",
        "Cache-Control"            : "max-age=0",
        "sec-ch-ua"                : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile"         : "?0",
        "Upgrade-Insecure-Requests": "1",
        "Origin"                   : "https://lisp-tw.hct.com.tw",
        "Content-Type"             : "application/x-www-form-urlencoded",
        "User-Agent"               : user_agent.random,
        "Accept"                   : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site"           : "same-origin",
        "Sec-Fetch-Mode"           : "navigate",
        "Sec-Fetch-User"           : "?1",
        "Sec-Fetch-Dest"           : "frame",
        "Referer"                  : "https://lisp-tw.hct.com.tw/AA005.jsp",
        "Accept-Encoding"          : "gzip, deflate, br",
        "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie"                   : f"{cookie.name}={cookie.value}",  # this is necessary for some reason...
    }
    data = {
        "P2"         : "",
        "P3"         : product_name,
        "RPT_COND"   : "P2,P3,",
        "RPT_ID"     : "3518",
        "TITLE_CLASS": "客製查詢",
        "Query"      : "Y",
    }
    response = requests.post(url = url, headers = headers, data = data, cookies = cookie_jar)

    # extract search results from HTTP response
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify())
    try:
        tables = soup.find_all('table')
        if len(tables) < 3:
            # case 1: webpage derped out, returned wrong format (assume no results)
            return 'X'
        table = tables[3]  # type:BeautifulSoup
        trs = table.find_all('tr')
        if len(trs) < 2:
            # case 2: no search results #todo: perform transformations to search again
            return '-'
        tr = trs[1]  # type:BeautifulSoup
        td = tr.find_all('td')[1]  # type:BeautifulSoup
        # print(td.text)
        return td.text
    except Exception:
        # case 3: unexpected error
        return "-"

def getProductList(ws):
    """Get list of products that we want to search for.
    Input: Excel spreadsheet object (not workbook)
    Output: List of product names to search for"""

    firstCell = ws.range('E2')  # type:xlwings.Range
    lastCell = ws.range('E:E').end("down")  # type:xlwings.Range
    product_list = ws.range(firstCell, lastCell).value
    return product_list if isinstance(product_list, list) else [product_list]

def listWarehouse():
    """Get a list of wares from 庫存總表
    Input: None
    Output: List of product names in the warehouse"""

    # fetch warehouse inventory listing
    url = "https://lisp-tw.hct.com.tw/AA004.jsp"
    cookie_jar = browser_cookie3.chrome(domain_name = 'lisp-tw.hct.com.tw')
    cookie = cookie_jar.__iter__().__next__()
    headers = {
        "Host"                     : "lisp-tw.hct.com.tw",
        "Connection"               : "keep-alive",
        "Cache-Control"            : "max-age=0",
        "sec-ch-ua"                : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile"         : "?0",
        "Upgrade-Insecure-Requests": "1",
        "Origin"                   : "https://lisp-tw.hct.com.tw",
        "Content-Type"             : "application/x-www-form-urlencoded",
        "User-Agent"               : user_agent.random,
        "Accept"                   : "*/*",
        "Sec-Fetch-Site"           : "same-origin",
        "Sec-Fetch-Mode"           : "navigate",
        "Sec-Fetch-User"           : "?1",
        "Sec-Fetch-Dest"           : "frame",
        "Referer"                  : "https://lisp-tw.hct.com.tw/AA005.jsp",
        "Accept-Encoding"          : "gzip, deflate, br",
        "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie"                   : f"{cookie.name}={cookie.value}",  # this is necessary for some reason...
    }
    response = requests.get(url = url, headers = headers, cookies = cookie_jar)
    # extract products from HTML table using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    # structure: table > (NO TBODY) > tr*N
    table = soup.find_all('table')[1]  # type:BeautifulSoup
    trs = table.find_all('tr')  # type:list[BeautifulSoup]
    # preallocate list for slight performance gains
    ware_list = [r"¯\_(ツ)_/¯" for x in range(len(trs))]  # type:list[str]
    for index, tr in enumerate(trs):
        ware_list[index] = tr.find_all('td')[2].contents[0]
    # remove 0th element '產品名稱'
    ware_list.pop(0)
    return ware_list

def clearResults():
    """Clear search results in Excel spreadsheet
    (Only to be called from Excel)"""
    # ws = xlwings.Book(bookname).sheets[0]
    ws = xlwings.sheets.active
    firstCell = ws.range('F2')
    lastCell = ws.range('F1048576').end("up")
    cells = ws.range(firstCell, lastCell)
    cells.clear()

def isSameProduct(product1: str, product2: str):
    if product1 == product2:
        return True
    else:
        return False
