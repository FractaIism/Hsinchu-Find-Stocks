from modules import *

def main():
    # use this as a hack to set CWD to project dir in all modules (does it work?)
    os.chdir(os.path.dirname(__file__))
    # logging setup for use anywhere in the project
    logging.basicConfig(filename = globals.log_file, filemode = 'w', level = logging.DEBUG)
    timer = checkpoint_timer.Timer()
    timer.checkpoint("Initial")
    ws = xlwings.Book.caller().sheets[0]
    timer.checkpoint("Acquired excel sheet")

    # fetch product list to search for
    product_list = excel_handler.getProductList(ws)
    timer.checkpoint("Acquired product list")
    logNprint("Product list:", f"{len(product_list)} {product_list}")

    # fetch ware list from hsinchu logistics
    ware_list = web_crawler.listWarehouse()
    timer.checkpoint("Acquired ware list")
    logNprint("Warehouse list:", f"{len(ware_list)} {ware_list}")

    # perform pairwise compare to find matching products
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

# def main_old():
#     """DEPRECATED
#      Uses multithreaded search for each item."""
#     # get product list from excel
#     # NOTE: if run from IDE, make sure to select the correct sheet
#     ws = xlwings.Book(bookname).sheets[0]
#     product_list = getProductList(ws)
#     logNprint(len(product_list), product_list)
#     # multithreaded search
#     t1 = time.time()
#     with concurrent.futures.ThreadPoolExecutor(max_workers = len(product_list)) as executor:
#         results = executor.map(searchProduct, product_list)
#     results = [[res] for res in list(results)]
#     print(results)
#     t2 = time.time()
#     logNprint("Time elapsed: %.3f" % float(t2 - t1))
#     # write results back to excel
#     ws['f2'].value = results

if __name__ == '__main__':
    xlwings.Book(globals.bookname).set_mock_caller()
    main()
