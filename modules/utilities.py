from modules.libraries import *
import modules.globals

" ========== CLASSES ========== "

@dataclass
class Brand:
    """A brand with chinese and/or english name, and with optional aliases"""
    ch: str = None
    eng: str = None
    aliases: list[str] = None

    def __init__(self, ch: str = None, eng: str = None, aliases: list[str] = None):
        self.ch = ch
        self.eng = eng
        self.aliases = aliases

    def __eq__(self, other):
        if self.ch != other.ch:
            return False
        if self.eng != other.eng:
            return False
        return True

    def primary(self):
        """Return the first nonempty name, or None if not found."""
        if self.ch is not None:
            return self.ch
        if self.eng is not None:
            return self.eng
        return "unknown"

@dataclass
class Ware:
    """An item in the warehouse inventory"""
    name: str
    quantity: int

    def __init__(self, name: str, quantity: int):
        self.name = name
        self.quantity = quantity

@dataclass
class Match:
    """A ware that matches a certain product"""
    original_ware_obj: Ware
    pure_ware_name: str
    similarity: float

    def __init__(self, original: Ware, pure: str, similarity: float):
        self.original_ware_obj = original
        self.pure_ware_name = pure
        self.similarity = similarity

class Success(Exception):
    pass

" ========== CONSTANTS ========== "

UNKNOWN_BRAND = Brand("unknown", None, None)

" ========== FUNCTIONS ========== "

def calcSimilarity(product1: str, product2: str):
    # product1 = product1.lower()
    # product2 = product2.lower()
    sim = difflib.SequenceMatcher(None, product1, product2).quick_ratio()
    return sim

def isSameProduct(prodname: str, warename: str, brand: Brand) -> (bool, str, int):
    """Compare product with ware and determine if they are the same.
    Input: Original product name, original ware name, brand
    Output: is_same, processed_warename, verdict/similarity
    """
    brandless_product = modules.preprocessing.stripBrand(prodname, brand)
    brandless_warename = modules.preprocessing.stripBrand(warename, brand)
    # first perform some basic checks (heuristics)
    verdict = modules.preprocessing.Filter(brandless_product, brandless_warename).verdict()
    if verdict in (modules.preprocessing.Filter.IDENTICAL, modules.preprocessing.Filter.SUBSTRING_RELATION):
        return True, brandless_warename, verdict  # direct accept
    elif verdict is not None:
        return False, brandless_warename, verdict  # direct reject
    # compare pure products
    pure_product = modules.preprocessing.purify(brandless_product)
    pure_warename = modules.preprocessing.purify(brandless_warename)
    similarity = calcSimilarity(pure_product, pure_warename)
    if similarity >= modules.globals.similarity_threshold:
        return True, pure_warename, similarity
    else:
        return False, pure_warename, similarity

def logNprint(msg, *args) -> None:
    """Output message to both console and log file. (tee!)"""
    for m in [msg, *args]:
        print(m)
        logging.info(m)

" ========== DEPRECATED ========== "

# def searchProduct(product_name):
#     """Search for a product on 新竹倉庫 by 報表查詢
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
