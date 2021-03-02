from libraries import *
from globals import *

def searchProduct(product_name):
    """Search for a product on 新竹倉庫
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
        "User-Agent"               : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
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
    resp = requests.post(url = url, headers = headers, data = data, cookies = cookie_jar)

    # extract search results from HTTP response
    soup = BeautifulSoup(resp.text, 'html.parser')
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
        # case 1: search returned no results

        return "-"

def getProductList(ws):
    firstCell = ws.range('E2')  # type:xlwings.Range
    lastCell = ws.range('E:E').end("down")  # type:xlwings.Range
    product_list = ws.range(firstCell, lastCell).value
    return product_list if isinstance(product_list, list) else [product_list]

def clearResults():
    ws = xlwings.Book(bookname).sheets[0]
    firstCell = ws.range('F2')
    lastCell = ws.range('F1048576').end("up")
    cells = ws.range(firstCell, lastCell)
    cells.clear()

def logNprint_Template(logger: logging.Logger, msg: str, *args: list[str]):
    """template to create logNprint functions
    literally 'log and print', two functions in one line
    Seeing multiple lines with the same message is annoying, and harder to maintain"""
    print(msg, *args)
    logger.info(msg)
    for arg in args:
        logger.info(arg)
