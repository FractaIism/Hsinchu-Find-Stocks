import libraries
from globals import *
from utilities import *

# todo: manual search the test cases to find special cases
def main():
    # logging setup
    logging.basicConfig(filename = "main.log", filemode = 'w', level = logging.DEBUG)
    logNprint = functools.partial(logNprint_Template, logging.getLogger())
    # get product list from excel
    ws = xlwings.Book(bookname).sheets[0]
    product_list = getProductList(ws)
    logNprint(len(product_list), product_list)
    # multithreaded search
    t1 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(product_list)) as executor:
        results = executor.map(searchProduct, product_list)
    results = [[res] for res in list(results)]
    print(results)
    t2 = time.time()
    logNprint("Time elapsed: %.3f" % float(t2 - t1))
    # write results back to excel
    ws['f2'].value = results

if __name__ == '__main__':
    main()
