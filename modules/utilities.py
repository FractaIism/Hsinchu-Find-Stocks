from modules.libraries import *
import modules.globals

# ========== EXTERNALS ========== #
# (to be accessed from other modules)

def isSamePureProduct(product1: str, product2: str) -> bool:
    """Compare pure product names and determine if they are the same."""
    if product1 == product2:
        return True
    else:
        return False

def logNprint(msg, *args) -> None:
    """Output message to both console and log file. (tee!)"""
    for m in [msg, *args]:
        print(m)
        logging.info(m)

class Brand:
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
        return None

class Success(Exception):
    pass

# ========== INTERNALS ========== #
# (only used within this module as subroutines)


# ========== DEPRECATED ========== #
""" Deprecated code """

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
