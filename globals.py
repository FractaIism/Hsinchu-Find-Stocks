# define variables to use throughout the project and rc scripts
from libraries import *

bookname = "測試單.xlsm"  # excel workbook to work with
os.chdir(os.path.dirname(__file__))  # use this as a hack to set CWD to project dir in all modules
user_agent = fake_useragent.UserAgent()
