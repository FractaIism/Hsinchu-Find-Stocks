from modules import *

def main():
    # logging.basicConfig(filename = modules.globals.log_file, filemode = 'w', level = logging.DEBUG)

    # get excel worksheet
    timer = modules.checkpoint_timer.Timer()
    timer.checkpoint("Initial")
    ws = xlwings.Book.caller().sheets["新竹查庫存"]
    timer.checkpoint("Acquire excel sheet")

    # fetch list of products to search for
    product_list = modules.excel_handler.getProductList()
    timer.checkpoint("Acquire product list")
    # logNprint("Product list:", f"{len(product_list)} {product_list}")

    # fetch ware list from hsinchu logistics
    ware_list = modules.web_crawler.listWarehouse()
    timer.checkpoint("Acquire ware list")
    # logNprint("Warehouse list:", f"{len(ware_list)} {[(ware.name, ware.quantity) for ware in ware_list]}")

    # organize ware list into a dict (classify by brand name)
    brand_list = modules.excel_handler.getBrandList()
    wares_by_brand = modules.preprocessing.getWaresByBrand(ware_list, brand_list)
    timer.checkpoint("Group wares by brand")

    # perform pairwise compare to find matching products (the bread and butter of the program!)
    found_count = 0  # number of products that have been matched
    for idx, prod in enumerate(product_list):
        # store matching items in a list, then output the best match at the end
        match_list = list([])  # type:list[modules.utilities.Match]
        brand, brandless_product = modules.preprocessing.splitBrandProduct(brand_list, prod)
        pure_product = modules.preprocessing.purify(brandless_product)

        # compare with items of the same brand (or "unknown" if no brand)
        for ware in wares_by_brand[brand.primary()]:
            is_same, processed_warename, similarity = modules.utilities.isSameProduct(prod, ware.name, brand)
            if is_same:
                match_list.append(modules.utilities.Match(ware, processed_warename, similarity))
        if len(match_list) == 0:
            if brand.primary() != "unknown":
                # if no match found in brand, try searching unbranded wares
                for ware in wares_by_brand["unknown"]:
                    is_same, processed_warename, similarity = modules.utilities.isSameProduct(prod, ware.name, modules.utilities.UNKNOWN_BRAND)
                    if is_same:
                        match_list.append(modules.utilities.Match(ware, processed_warename, similarity))
            elif modules.globals.search_all:
                # if no brand and no match, search through all wares
                for ware in wares_by_brand["all"]:
                    is_same, processed_warename, similarity = modules.utilities.isSameProduct(prod, ware.name, modules.utilities.Brand("all", None, None))
                    if is_same:
                        match_list.append(modules.utilities.Match(ware, processed_warename, similarity))

        # write back to excel
        if len(match_list) > 0:
            # find match with highest similarity score (or filter code if found by Filter)
            best_match = max(match_list, key = lambda match: match.similarity)
            modules.excel_handler.writeSearchResult(idx, best_match, pure_product)
            found_count += 1
        else:
            modules.excel_handler.writeSearchResult(idx, None, pure_product)

        print(idx)  # to show that the program is actually running

    ws[f"F{len(product_list) + 3}"].value = f"找到{found_count}/{len(product_list)}"

    timer.checkpoint("Pairwise compare")
    logNprint(f"Found: {found_count}/{len(product_list)}")

    # write wares categorized by brand for manual checking
    modules.excel_handler.writeWaresByBrand(wares_by_brand)
    timer.checkpoint("Write wares_by_brand to Excel")

if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    xlwings.Book(globals.bookname).set_mock_caller()
    main()
