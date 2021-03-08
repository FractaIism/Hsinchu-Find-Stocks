from libraries import *
from globals import *

def searchProduct(product_name):
    """Deprecated
    Search for a product on 新竹倉庫 by 報表查詢
    Input: product name
    Output: list of products names found"""
    logNprint(f"Searching for: {product_name}")

    # send HTTP request to perform search
    url = "http://lisp-tw.hct.com.tw/AA005.jsp"
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

    # first log in (or else subsequent code will fail)
    HCTLISP_login()
    # fetch warehouse inventory listing
    url = "https://lisp-tw.hct.com.tw/AA004.jsp"
    # cookie_jar = browser_cookie3.chrome(domain_name = 'lisp-tw.hct.com.tw')
    # cookie = cookie_jar.__iter__().__next__()
    # headers = {
    #     "Host"                     : "lisp-tw.hct.com.tw",
    #     "Connection"               : "keep-alive",
    #     "Cache-Control"            : "max-age=0",
    #     "sec-ch-ua"                : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    #     "sec-ch-ua-mobile"         : "?0",
    #     "Upgrade-Insecure-Requests": "1",
    #     "Origin"                   : "https://lisp-tw.hct.com.tw",
    #     "Content-Type"             : "application/x-www-form-urlencoded",
    #     "User-Agent"               : user_agent.random,
    #     "Accept"                   : "*/*",
    #     "Sec-Fetch-Site"           : "same-origin",
    #     "Sec-Fetch-Mode"           : "navigate",
    #     "Sec-Fetch-User"           : "?1",
    #     "Sec-Fetch-Dest"           : "frame",
    #     "Referer"                  : "https://lisp-tw.hct.com.tw/AA005.jsp",
    #     "Accept-Encoding"          : "gzip, deflate, br",
    #     "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "Cookie"                   : f"{cookie.name}={cookie.value}",  # this is necessary for some reason...
    # }(
    response = session.get(url = url)
    # extract products from HTML table using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # structure: table > (NO TBODY) > tr*N
    try:
        table = soup.find_all('table')[1]  # type:BeautifulSoup
    except IndexError:
        raise Exception("You are not logged in.")
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

class Timer:
    def __init__(self):
        self.initial_time = None
        self.last_time = None

    def checkpoint(self, name: str):
        logNprint("*" * 50)
        logNprint(f"Checkpoint: {name}")
        if self.last_time is None:
            self.initial_time = self.last_time = time.time()
            logNprint(f"Time diff: 0")
            logNprint(f"Total time: 0")
        else:
            cur_time = time.time()
            logNprint(f"Time diff: {cur_time - self.last_time}")
            logNprint(f"Total time: {cur_time - self.initial_time}")
            self.last_time = cur_time
        logNprint("*" * 50)

def HCTLISP_login():
    """Login to HCTLISP to make the cookie "logged-in" so further operations can be performed."""

    def visitLoginPage():
        """Visit the login page to generate a cookie.
        Input: None
        Output: Cookies for lisp-tw.hct.com.tw"""
        url = "https://lisp-tw.hct.com.tw/login.jsp"
        response = requests.get(url = url, headers = headers)
        logging.debug(f"Login page cookie = {response.cookies}")
        return response.cookies

    # send HTTP request to perform search
    url = "http://lisp-tw.hct.com.tw/checklogin.jsp"
    headers = {
        "Host"                     : "lisp-tw.hct.com.tw",
        "Connection"               : "keep-alive",
        "Cache-Control"            : "max-age=0",
        "sec-ch-ua"                : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile"         : "?0",
        "Upgrade-Insecure-Requests": "1",
        "Origin"                   : "https://lisp-tw.hct.com.tw",
        "Content-Type"             : "application/x-www-form-urlencoded",  # "User-Agent"               : user_agent.random,  # maybe not needed?
        "Accept"                   : "*/*",
        "Sec-Fetch-Site"           : "same-origin",
        "Sec-Fetch-Mode"           : "navigate",
        "Sec-Fetch-User"           : "?1",
        "Sec-Fetch-Dest"           : "frame",  # differs
        "Accept-Encoding"          : "gzip, deflate, br",
        "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        # set Cookie when logging in
    }
    cookie_jar = browser_cookie3.chrome(domain_name = 'lisp-tw.hct.com.tw')
    try:
        # Try to get cookie from chrome
        cookie = cookie_jar.__iter__().__next__()
        print(cookie)
    except StopIteration:
        # Cookie not found, create one by visiting login page
        cookie_jar = visitLoginPage()
        cookie = cookie_jar.__iter__().__next__()
    finally:
        logging.debug(f"Chrome cookie = {cookie_jar}")

    # headers = {
    #     "Host"                     : "lisp-tw.hct.com.tw",
    #     "Connection"               : "keep-alive",
    #     "Cache-Control"            : "max-age=0",
    #     "sec-ch-ua"                : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    #     "sec-ch-ua-mobile"         : "?0",
    #     "Upgrade-Insecure-Requests": "1",
    #     "Origin"                   : "https://lisp-tw.hct.com.tw",
    #     "Content-Type"             : "application/x-www-form-urlencoded",
    #     "User-Agent"               : user_agent.random,
    #     "Accept"                   : "*/*",
    #     "Sec-Fetch-Site"           : "same-origin",
    #     "Sec-Fetch-Mode"           : "navigate",
    #     "Sec-Fetch-User"           : "?1",
    #     "Sec-Fetch-Dest"           : "frame",
    #     "Accept-Encoding"          : "gzip, deflate, br",
    #     "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "Cookie"                   : f"{cookie.name}={cookie.value}",  # this is necessary for some reason...
    # }
    headers.update({
        "Cookie": f"{cookie.name}={cookie.value}",  # this header is necessary for some reason...
    })
    data = {
        "USER_ID" : "USER",
        "PASSWORD": "Suntrail",
        "CUST"    : "SI",
    }
    session.cookies.set_cookie(cookie)
    session.headers.update(headers)
    # Inconsistent bug: SSL wrong version...
    # Solution 1: Use HTTP instead of HTTPS in URL
    # Solution 2: Add param verify=False to requests.post()
    # response = requests.post(url = url, headers = headers, data = data, cookies = cookie_jar, verify = False)
    response = session.post(url = url, data = data, verify = False)
    return

def getBrandList() -> list[tuple[str, str, str]]:
    """Get brand names (Chinese and English and Alias)
    Input: None
    Output: Dict of brand names as keys and empty lists as values"""
    ws = xlwings.Book(bookname).sheets["廠牌列表"]
    brand_list = []
    row = 2
    while ws[f"A{row}"].value or ws[f"B{row}"].value:
        brand_list.append((ws[f"A{row}"].value, ws[f"B{row}"].value, ws[f"C{row}"].value))
        row += 1
    return brand_list

def makeDictByBrand(ware_list: list[str], brand_list: list[tuple[str, str, str]]):
    """Make a dict to classify wares by brand name
    Input: product list and brand list
    Output: dict with keys=brand name and values=list of products pertaining to the brand"""

    # initialize empty lists for each brand
    ware_dict = {
        'unknown': [],
        'all'    : ware_list,
    }
    for ch, eng, alias in brand_list:
        # chinese, english, and alias brand names all point to the same list
        ware_dict[ch] = ware_dict[eng] = ware_dict[alias] = []
    # add products to their brand list
    for product in ware_list:
        try:
            for brand in brand_list:
                ch, eng, alias = brand
                if ch is not None and re.match(ch, product, flags = re.IGNORECASE):
                    # ware_dict[ch].append(product)
                    ware_dict[ch].append(removeBrand(product, brand))
                    raise ConnectionError
                elif eng is not None and re.match(eng, product, flags = re.IGNORECASE):
                    # ware_dict[eng].append(product)
                    ware_dict[eng].append(removeBrand(product, brand))
                    raise ConnectionError
                elif alias is not None and re.match(alias, product, flags = re.IGNORECASE):
                    # ware_dict[alias].append(product)
                    ware_dict[alias].append(removeBrand(product, brand))
                    raise ConnectionError
            # if any of the above succeeds, this line is skipped
            ware_dict['unknown'].append(product)
        except ConnectionError:
            # use a dummy exception
            continue
    return ware_dict

def removeBrand(product_name: str, brand: tuple[str, str, str]):
    """Remove brand info from product name.
    Input: Product name
    Output: Product name without chinese or english brand name"""
    for pattern in brand:
        if pattern is not None:
            product_name = re.sub(pattern, "", product_name, flags = re.IGNORECASE)
    return product_name.strip()
