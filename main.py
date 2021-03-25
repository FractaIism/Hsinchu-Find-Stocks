from modules import *

def main():
    # use this as a hack to set CWD to project dir in all modules (does it work?)
    os.chdir(os.path.dirname(sys.argv[0]))
    # logging setup for use anywhere in the project
    logging.basicConfig(filename = globals.log_file, filemode = 'w', level = logging.DEBUG)
    timer = modules.checkpoint_timer.Timer()
    timer.checkpoint("Initial")
    ws = xlwings.Book.caller().sheets[0]
    timer.checkpoint("Acquired excel sheet")

    # fetch product list to search for
    product_list = modules.excel_handler.getProductList(ws)
    timer.checkpoint("Acquire product list")
    logNprint("Product list:", f"{len(product_list)} {product_list}")

    # fetch ware list from hsinchu logistics
    ware_list = modules.web_crawler.listWarehouse()
    timer.checkpoint("Acquire ware list")
    logNprint("Warehouse list:", f"{len(ware_list)} {ware_list}")

    # organize ware list into a dict (classify by brand name)
    brand_list = modules.excel_handler.getBrandList()
    wares_by_brand = modules.preprocessing.getWaresByBrand(ware_list, brand_list)
    timer.checkpoint("Group wares by brand")

    # perform pairwise compare to find matching products
    found_count = 0
    for idx, prod in enumerate(product_list):
        # by "pure_brand" we mean the brand name alone without any specific product information
        # by "pure_product" we mean the product name alone without any brand information
        brand, pure_product = modules.preprocessing.splitBrandProduct(brand_list, prod)
        found_ware = ""  # type:str

        if brand != modules.utilities.Brand(None, None, None):
            # if product brand is found, compare within the same brand
            for ware in wares_by_brand[brand.primary()]:
                pure_ware = modules.preprocessing.stripBrand(ware, brand)
                # if modules.utilities.isSamePureProduct(pure_product, pure_ware):
                if modules.utilities.similarity(pure_product, pure_ware, ws, idx + 2):
                    found_ware = ware  # output original ware name to excel (including brand)
                    found_count += 1
                    break
        else:
            # if product has no brand, compare with unbranded products
            for ware in wares_by_brand["unknown"]:
                if modules.utilities.isSamePureProduct(pure_product, ware):
                    found_ware = ware
                    found_count += 1
                    break
        # write back to excel
        ws[f'f{2 + idx}'].value = found_ware if found_ware != "" else r"¯\_(ツ)_/¯"
    timer.checkpoint("Pairwise compare")
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
