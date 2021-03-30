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
    product_list = modules.excel_handler.getProductList()
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
        # store matching items in a list and similarity score, and output the best match at the end
        match_list = list([])  # type:list[modules.utilities.Match]
        brand, brandless_product = modules.preprocessing.splitBrandProduct(brand_list, prod)
        pure_product = modules.preprocessing.Purifier(brandless_product).purify()

        # compare against items of the same brand
        for ware in wares_by_brand[brand.primary()]:
            brandless_ware = modules.preprocessing.stripBrand(ware, brand)
            # first perform some easy checks for fast results
            verdict = modules.preprocessing.Filter(brandless_product, brandless_ware).verdict()
            if verdict in (modules.preprocessing.Filter.IDENTICAL, modules.preprocessing.Filter.SUBSTRING_RELATION):
                match_list.append(modules.utilities.Match(ware, brandless_ware, verdict))
                continue
            elif verdict is not None:
                continue
            # compare pure products
            pure_ware = modules.preprocessing.Purifier(brandless_ware).purify()
            # if modules.utilities.isSamePureProduct(pure_product, pure_ware):
            similarity = modules.utilities.similarity(pure_product, pure_ware)
            if similarity >= modules.globals.similarity_threshold:
                match_list.append(modules.utilities.Match(ware, pure_ware, similarity))
        # write back to excel
        row = idx + 2  # row number of product in excel
        print(row)
        if len(match_list) > 0:
            # find best match
            best_match = max(match_list, key = lambda match: match.similarity)
            ws[f'F{row}'].value = best_match.original
            ws[f'T{row}'].value = pure_product
            ws[f'U{row}'].value = best_match.pure
            ws[f'V{row}'].value = best_match.similarity
            if best_match.similarity in (1, modules.preprocessing.Filter.IDENTICAL):
                ws[f'f{row}'].color = (0, 255, 0)  # bright green
            elif best_match.similarity == modules.preprocessing.Filter.SUBSTRING_RELATION:
                ws[f'f{row}'].color = (0, 200, 0)  # dark green
            else:
                ws[f'f{row}'].color = (255, 255, 0)  # bright yellow
            found_count += 1
        else:
            ws[f'F{row}'].value = r"¯\_(ツ)_/¯"
            ws[f'T{row}'].value = "-"
            ws[f'U{row}'].value = "-"
            ws[f'V{row}'].value = "-"
            ws[f'F{row}'].color = (200, 200, 200)

    timer.checkpoint("Pairwise compare")
    logNprint(f"Found: {found_count}/{len(product_list)}")

if __name__ == '__main__':
    xlwings.Book(globals.bookname).set_mock_caller()
    main()

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
