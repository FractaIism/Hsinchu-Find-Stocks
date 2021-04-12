from modules.libraries import *
from modules.utilities import logNprint
import modules.globals

# start session to preserve cookies
session = requests.Session()

def listWarehouse() -> list[modules.utilities.Ware]:
    """Get a list of wares from 庫存總表
    Input: None
    Output: List of product names in the warehouse"""

    if modules.globals.mock_web is True:
        url = "http://hsinchu"  # using WAMP
    else:
        # first log in (or else subsequent code will fail)
        HCTLISP_login(use_existing_cookie = True)  # first try grabbing cookies from browser to save network requests
        # fetch warehouse inventory listing
        url = "https://lisp-tw.hct.com.tw/AA004.jsp"

    response = session.get(url = url)
    # explicitly set encoding to prevent garbage data
    response.encoding = "UTF-8"
    # extract products from HTML table using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    def getTable():
        tables = soup.find_all('table')
        for tbl in tables:
            if len(tbl.find_all('tr')) > 100:  # the "big" table is what we want (prevent website changes from breaking this program)
                return tbl
        # if table not found, return None
        return None

    table = getTable()
    if table is None:
        # login failed, try again without using existing cookies
        HCTLISP_login(use_existing_cookie = False)
        table = getTable()
        if table is None:
            # if login still fails, crash the program
            raise Exception("Login to Hsinchu Logistics failed. Login manually, then try again.")
    trs = table.find_all('tr')[1:]  # type:list[BeautifulSoup]
    # preallocate list for infinitesimal performance gains
    ware_list = [modules.utilities.Ware(r"¯\_(ツ)_/¯", 1) for x in range(len(trs))]  # type:list[modules.utilities.Ware]
    for index, tr in enumerate(trs):
        ware_name = tr.find_all('td')[2].contents[0]
        ware_quantity = tr.find_all('td')[3].contents[0]
        ware_list[index] = modules.utilities.Ware(ware_name, ware_quantity)
    return ware_list

def HCTLISP_login(use_existing_cookie: bool = True) -> None:
    """Login to HCTLISP to make the cookie "logged-in" so further operations can be performed."""

    def visitLoginPage():
        """Visit the login page to generate a cookie.
        Input: None
        Output: Cookies for lisp-tw.hct.com.tw"""
        url = "https://lisp-tw.hct.com.tw/login.jsp"
        response = session.get(url = url, headers = headers)
        return response.cookies

    # send HTTP request to perform search
    headers = {
        "Host"                     : "lisp-tw.hct.com.tw",
        "Connection"               : "keep-alive",
        "Cache-Control"            : "max-age=0",
        "sec-ch-ua"                : '"Chromium";v="89", "Google Chrome";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile"         : "?0",
        "Upgrade-Insecure-Requests": "1",
        "Origin"                   : "https://lisp-tw.hct.com.tw",
        "Content-Type"             : "application/x-www-form-urlencoded",  # "User-Agent"               : fake_useragent.UserAgent().random,  # maybe not needed?
        # "User-Agent"               : '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "Referer"                  : "",
        "Accept"                   : "*/*",
        "Sec-Fetch-Site"           : "none",
        "Sec-Fetch-Mode"           : "navigate",
        "Sec-Fetch-User"           : "?1",
        "Sec-Fetch-Dest"           : "document",
        "Accept-Encoding"          : "gzip, deflate, br",
        "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:  # try getting cookies from multiple browsers
        if not use_existing_cookie:
            raise StopIteration
        cookie_jar = browser_cookie3.load(domain_name = 'lisp-tw.hct.com.tw')
    except KeyError:  # KeyError: 'os_crypt'
        cookie_jar = browser_cookie3.chrome(domain_name = 'lisp-tw.hct.com.tw')
    try:
        # Try to get cookie from chrome
        cookie = next(iter(cookie_jar))
    except StopIteration:
        # Cookie not found, create one by visiting login page
        cookie_jar = visitLoginPage()
        cookie = next(iter(cookie_jar))
    finally:
        logging.debug(f"Chrome cookie = {cookie_jar}")

    headers["Cookie"] = f"{cookie.name}={cookie.value}"  # this header is necessary for some reason...
    credentials = modules.globals.hsinchu_credentials
    session.cookies.set_cookie(cookie)
    session.headers.update(headers)
    # Inconsistent bug: SSL wrong version...
    # Solution 1: Use HTTP instead of HTTPS in URL (NVM STILL NEED HTTPS TO GET COOKIE)
    # Solution 2: Add param verify=False to requests.post()
    # response = requests.post(url = url, headers = headers, data = data, cookies = cookie_jar, verify = False)
    http_url = "http://lisp-tw.hct.com.tw/checklogin.jsp"
    https_url = "https://lisp-tw.hct.com.tw/checklogin.jsp"
    try:
        # first try using HTTPS
        https_response = session.post(url = https_url, data = credentials, verify = False)
        # session expired message (?)
        if https_response.text.find("alert(") > 0:
            raise Exception(https_response.text)
    except Exception as exc:
        # if it fails, fallback to HTTP
        print(exc)
        print("Trying HTTP ...")
        http_response = session.post(url = http_url, data = credentials, verify = False)
        print(http_response)
