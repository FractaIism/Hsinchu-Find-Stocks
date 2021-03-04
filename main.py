import libraries
from globals import *
from utilities import *

def main():
    timer = Timer()
    timer.checkpoint("Initial")
    ws = xlwings.Book(bookname).sheets[0]
    timer.checkpoint("Got sheet")

    product_list = getProductList(ws)
    timer.checkpoint("Got product list")
    logNprint("Product list:", len(product_list), product_list)

    ware_list = listWarehouse()
    logNprint("Warehouse list:", len(ware_list), ware_list)
    timer.checkpoint("Got ware list")

    found_count = 0
    for idx, prod in enumerate(product_list):
        found = None
        for ware in ware_list:
            if isSameProduct(prod, ware):
                found = ware
                found_count += 1
                break
        if found is not None:
            ws[f'f{2 + idx}'].value = found
        else:
            ws[f'f{2 + idx}'].value = r"¯\_(ツ)_/¯"
    timer.checkpoint("Finished pairwise compare")
    logNprint(f"Found: {found_count}/{len(product_list)}")

def main_old():
    """Deprecated
     Uses multithreaded search for each item."""
    # get product list from excel
    # NOTE: if run from IDE, make sure to select the correct sheet
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
