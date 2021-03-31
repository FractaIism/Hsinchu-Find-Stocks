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
        HCTLISP_login()
        # fetch warehouse inventory listing
        url = "https://lisp-tw.hct.com.tw/AA004.jsp"

    response = session.get(url = url)
    # explicitly set encoding to prevent garbage data
    response.encoding = "UTF-8"
    # extract products from HTML table using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # structure: table > (NO TBODY) > tr*N
    try:
        table = soup.find_all('table')[1]  # type:BeautifulSoup
    except IndexError:
        logging.error(soup.prettify())
        raise Exception("You are not logged in.")
    trs = table.find_all('tr')  # type:list[BeautifulSoup]
    # preallocate list for infinitesimal performance gains
    ware_list = [modules.utilities.Ware(r"¯\_(ツ)_/¯", 1) for x in range(len(trs))]  # type:list[modules.utilities.Ware]
    for index, tr in enumerate(trs):
        # ware_list[index] = tr.find_all('td')[2].contents[0]
        ware_name = tr.find_all('td')[2].contents[0]
        ware_quantity = tr.find_all('td')[3].contents[0]
        ware_list[index] = modules.utilities.Ware(ware_name, ware_quantity)
    # remove 0th element '產品名稱'
    ware_list.pop(0)
    return ware_list

def HCTLISP_login() -> None:
    """Login to HCTLISP to make the cookie "logged-in" so further operations can be performed."""

    def visitLoginPage():
        """Visit the login page to generate a cookie.
        Input: None
        Output: Cookies for lisp-tw.hct.com.tw"""
        url = "https://lisp-tw.hct.com.tw/login.jsp"
        response = session.get(url = url, headers = headers)
        # logNprint(f"Login page headers = {response.headers}")
        # logNprint(f"Login page cookie = {response.cookies}")
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
        "Sec-Fetch-Dest"           : "document",  # differs
        "Accept-Encoding"          : "gzip, deflate, br",
        "Accept-Language"          : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
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
    data = {
        "USER_ID" : "USER",
        "PASSWORD": "Clark2021",
        "CUST"    : "SI",
    }
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
        https_response = session.post(url = https_url, data = data, verify = False)
        if re.search("alert\(", https_response.text):
            raise Exception(https_response.text)
    except Exception as exc:
        # if it fails, fallback to HTTP
        print(exc)
        print("Trying HTTP ...")
        http_response = session.post(url = http_url, data = data, verify = False)
        print(http_response)
