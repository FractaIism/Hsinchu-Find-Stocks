from modules.libraries import *
from modules.globals import *

def isSameProduct(product1: str, product2: str):
    if product1 == product2:
        return True
    else:
        return False

def makeDictByBrand(ware_list: list[str], brand_list: list[tuple[str, str, list[str]]]):
    """Make a dict to classify wares by brand name
    Input: product list and brand list
    Output: dict with keys=brand name and values=list of products pertaining to the brand"""

    # initialize empty lists for each brand
    ware_dict = {
        'unknown': [],
        'all'    : ware_list,
    }
    for ch, eng, aliases in brand_list:
        # chinese, english, and alias brand names all point to the same list
        ware_dict[ch] = ware_dict[eng] = []
        for alias in aliases:
            ware_dict[alias] = ware_dict[eng]
    # add products to their brand list
    for product in ware_list:
        try:
            for brand in brand_list:
                ch, eng, aliases = brand
                if ch is not None and re.search(ch, product, flags = re.IGNORECASE):
                    ware_dict[ch].append(removeBrand(product, brand))
                    raise ConnectionError
                elif eng is not None and re.search(eng, product, flags = re.IGNORECASE):
                    ware_dict[eng].append(removeBrand(product, brand))
                    raise ConnectionError
                else:
                    for alias in aliases:
                        if alias is not None and re.search(alias, product, flags = re.IGNORECASE):
                            ware_dict[alias].append(removeBrand(product, brand))
                            raise ConnectionError
            # if any of the above succeeds, this line is skipped
            ware_dict['unknown'].append(product)
        except ConnectionError:
            # use a dummy exception
            continue
    return ware_dict

def removeBrand(product_name: str, brand: tuple[str, str, list[str]]):
    """Remove brand info from product name.
    Input: Product name
    Output: Product name without chinese or english brand name"""
    ch, eng, aliases = brand
    if ch is not None:
        product_name = re.sub(ch, "", product_name, flags = re.IGNORECASE)
    if eng is not None:
        product_name = re.sub(eng, "", product_name, flags = re.IGNORECASE)
    for alias in aliases:
        product_name = re.sub(alias, "", product_name, flags = re.IGNORECASE)
    return product_name.strip()

def logNprint(msg, *args):
    for m in [msg, *args]:
        print(m)
        logging.info(m)

# def searchProduct(product_name):
#     """DEPRECATED
#     Search for a product on 新竹倉庫 by 報表查詢
#     Input: product name
#     Output: list of products names found"""
#     logNprint(f"Searching for: {product_name}")
#
#     # send HTTP request to perform search
#     url = "http://lisp-tw.hct.com.tw/AA005.jsp"
#     cookie_jar = browser_cookie3.chrome(domain_name = 'lisp-tw.hct.com.tw')
#     cookie = cookie_jar.__iter__().__next__()
#     headers = {
#         "Host"                     : "lisp-tw.hct.com.tw",
#         "Connection"               : "keep-alive",
#         "Cache-Control"            : "max-age=0",
#         "sec-ch-ua"                : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
#         "sec-ch-ua-mobile"         : "?0",
#         "Upgrade-Insecure-Requests": "1",
#         "Origin"                   : "https://lisp-tw.hct.com.tw",
#         "Content-Type"             : "application/x-www-form-urlencoded",
#         "User-Agent"               : user_agent.random,
#         "Accept"                   : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Sec-Fetch-Site"           : "same-origin",
#         "Sec-Fetch-Mode"           : "navigate",
#         "Sec-Fetch-User"           : "?1",
#         "Sec-Fetch-Dest"           : "frame",
#         "Referer"                  : "https://lisp-tw.hct.com.tw/AA005.jsp",
#         "Accept-Encoding"          : "gzip, deflate, br",
#         "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
#         "Cookie"                   : f"{cookie.name}={cookie.value}",  # this is necessary for some reason...
#     }
#     data = {
#         "P2"         : "",
#         "P3"         : product_name,
#         "RPT_COND"   : "P2,P3,",
#         "RPT_ID"     : "3518",
#         "TITLE_CLASS": "客製查詢",
#         "Query"      : "Y",
#     }
#     response = requests.post(url = url, headers = headers, data = data, cookies = cookie_jar)
#
#     # extract search results from HTTP response
#     soup = BeautifulSoup(response.text, 'html.parser')
#     # print(soup.prettify())
#     try:
#         tables = soup.find_all('table')
#         if len(tables) < 3:
#             # case 1: webpage derped out, returned wrong format (assume no results)
#             return 'X'
#         table = tables[3]  # type:BeautifulSoup
#         trs = table.find_all('tr')
#         if len(trs) < 2:
#             # case 2: no search results #notodo: perform transformations to search again
#             return '-'
#         tr = trs[1]  # type:BeautifulSoup
#         td = tr.find_all('td')[1]  # type:BeautifulSoup
#         # print(td.text)
#         return td.text
#     except Exception:
#         # case 3: unexpected error
#         return "-"
