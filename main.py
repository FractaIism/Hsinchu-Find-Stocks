from modules import *

def main():
    # logging setup for use anywhere in the project
    logging.basicConfig(filename = modules.globals.log_file, filemode = 'w', level = logging.DEBUG)
    timer = modules.checkpoint_timer.Timer()
    timer.checkpoint("Initial")
    ws = xlwings.Book.caller().sheets["新竹查庫存"]
    timer.checkpoint("Acquired excel sheet")

    # fetch list of products to search for
    product_list = modules.excel_handler.getProductList()
    timer.checkpoint("Acquired product list")
    logNprint("Product list:", f"{len(product_list)} {product_list}")

    # fetch ware list from hsinchu logistics
    ware_list = modules.web_crawler.listWarehouse()
    timer.checkpoint("Acquired ware list")
    logNprint("Warehouse list:", f"{len(ware_list)} {[(ware.name, ware.quantity) for ware in ware_list]}")

    # organize ware list into a dict (classify by brand name)
    brand_list = modules.excel_handler.getBrandList()
    wares_by_brand = modules.preprocessing.getWaresByBrand(ware_list, brand_list)
    timer.checkpoint("Grouped wares by brand")

    # perform pairwise compare to find matching products
    # this is the bread and butter of the program
    found_count = 0  # number of products that have been matched
    for idx, prod in enumerate(product_list):
        # store matching items in a list, then output the best match at the end
        match_list = list([])  # type:list[modules.utilities.Match]
        brand, brandless_product = modules.preprocessing.splitBrandProduct(brand_list, prod)
        pure_product = modules.preprocessing.purify(brandless_product)

        # compare with items of the same brand (or "unknown" if no brand)
        for ware in wares_by_brand[brand.primary()]:
            brandless_warename = modules.preprocessing.stripBrand(ware.name, brand)
            # first perform some basic checks (heuristics)
            verdict = modules.preprocessing.Filter(brandless_product, brandless_warename).verdict()
            if verdict in (modules.preprocessing.Filter.IDENTICAL, modules.preprocessing.Filter.SUBSTRING_RELATION):
                # direct accept
                match_list.append(modules.utilities.Match(ware, brandless_warename, verdict))
                continue
            elif verdict is not None:
                # direct reject
                continue
            # compare pure products
            pure_warename = modules.preprocessing.purify(brandless_warename)
            similarity = modules.utilities.similarity(pure_product, pure_warename)
            if similarity >= modules.globals.similarity_threshold:
                match_list.append(modules.utilities.Match(ware, pure_warename, similarity))

        if len(match_list) == 0:
            if brand.primary() != "unknown":
                # if no match found in brand, try searching unbranded wares
                for ware in wares_by_brand["unknown"]:
                    pure_warename = modules.preprocessing.purify(ware.name)
                    similarity = modules.utilities.similarity(pure_product, pure_warename)
                    if similarity >= modules.globals.similarity_threshold:
                        match_list.append(modules.utilities.Match(ware, pure_warename, similarity))
            elif modules.globals.search_all:
                # if no brand and no match, search through all wares
                for ware in wares_by_brand["all"]:
                    _, brandless_warename = modules.preprocessing.splitBrandProduct(brand_list, ware.name)
                    # first perform some basic checks (heuristics)
                    verdict = modules.preprocessing.Filter(brandless_product, brandless_warename).verdict()
                    if verdict in (modules.preprocessing.Filter.IDENTICAL, modules.preprocessing.Filter.SUBSTRING_RELATION):
                        # direct accept
                        match_list.append(modules.utilities.Match(ware, brandless_warename, modules.preprocessing.Filter.SUBSTRING_RELATION))
                        continue
                    elif verdict is not None:
                        # direct reject
                        continue
                    # compare pure products
                    pure_warename = modules.preprocessing.purify(brandless_warename)
                    similarity = modules.utilities.similarity(pure_product, pure_warename)
                    if similarity >= modules.globals.similarity_threshold:
                        match_list.append(modules.utilities.Match(ware, pure_warename, similarity))

        # write back to excel
        row = idx + 2  # row number of product in excel
        print(row)
        if len(match_list) > 0:
            # find best match
            best_match = max(match_list, key = lambda match: match.similarity)
            ws[f'F{row}'].value = best_match.original_ware_obj.name
            ws[f'G{row}'].value = best_match.original_ware_obj.quantity
            ws[f'T{row}'].value = pure_product
            ws[f'U{row}'].value = best_match.pure_ware_name
            ws[f'V{row}'].value = best_match.similarity
            if best_match.similarity in (1, modules.preprocessing.Filter.IDENTICAL):
                ws[f'F{row}'].color = (0, 255, 0)  # bright green
            elif best_match.similarity == modules.preprocessing.Filter.SUBSTRING_RELATION:
                ws[f'F{row}'].color = (0, 255, 255)  # dark cyan
            else:
                ws[f'F{row}'].color = (255, 255, 0)  # bright yellow
            found_count += 1
        else:
            ws[f'F{row}'].value = r"¯\_(ツ)_/¯"
            ws[f'G{row}'].value = "-"
            ws[f'T{row}'].value = "-"
            ws[f'U{row}'].value = "-"
            ws[f'V{row}'].value = "-"
            ws[f'F{row}'].color = (200, 200, 200)

    timer.checkpoint("Pairwise compare")
    logNprint(f"Found: {found_count}/{len(product_list)}")

    # output ware_dict to excel for checking
    # first create a hash table to combine chinese/english/alias brand names to prevent duplicate output
    ws2 = xlwings.Book.caller().sheets["新竹庫存字典"]
    hash_table: dict[int, list[str]] = {}
    for _brand, _warelist in wares_by_brand.items():
        if _brand in (None, "all"):
            continue
        elif id(_warelist) in hash_table:
            hash_table[id(_warelist)].append(_brand)
        else:
            hash_table[id(_warelist)] = [_brand]
    # print to excel
    ws2.clear()
    ws2[f"H{1}"].value = "最後更新: " + re.sub(r"\..*$", "", str(datetime.datetime.now()))
    row = 1
    for _, _brand in hash_table.items():
        brand_combined = ",".join(_brand)
        ws2[f"A{row}"].value = brand_combined
        row += 1
        for _ware in wares_by_brand[_brand[0]]:
            ws2[f"B{row}"].value = _ware.name
            row += 1

if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
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
