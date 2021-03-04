# define variables to use throughout the project and rc scripts
from libraries import *

# excel workbook to work with
bookname = "測試單.xlsm"
# use this as a hack to set CWD to project dir in all modules (does it work?)
os.chdir(os.path.dirname(__file__))
# to generate random user agents on each request
user_agent = fake_useragent.UserAgent()
# logging setup for use anywhere in the project
logging.basicConfig(filename = "main.log", filemode = 'w', level = logging.DEBUG)

def logNprint(msg, *args):
    for m in [msg, *args]:
        print(m)
        logging.info(m)
