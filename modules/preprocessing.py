from modules.libraries import *
import modules.utilities

def getWaresByBrand(ware_list: list[str], brand_list: list[modules.utilities.Brand]) -> dict[str, list[str]]:
    """Make a dict to classify wares by brand name
    Input: product list and brand list
    Output: dict with keys=brand name and values=list of products pertaining to the brand
    """
    # initialize empty lists for each brand
    ware_dict = {
        'unknown': [],
        'all'    : ware_list,
    }
    # chinese, english, and alias brand names all point to the same list object
    for brand in brand_list:  # type:modules.utilities.Brand
        ware_dict[brand.ch] = ware_dict[brand.eng] = []
        for alias in brand.aliases:  # type:str
            ware_dict[alias] = ware_dict[brand.eng]

    # add products to their brand list
    for product in ware_list:  # type:str
        try:
            for brand in brand_list:  # type:modules.utilities.Brand
                if brand.ch is not None and re.search(brand.ch, product, flags = re.IGNORECASE):
                    ware_dict[brand.ch].append(stripBrand(product, brand))
                    raise modules.utilities.Success
                elif brand.eng is not None and re.search(brand.eng, product, flags = re.IGNORECASE):
                    ware_dict[brand.eng].append(stripBrand(product, brand))
                    raise modules.utilities.Success
                else:
                    for alias in brand.aliases:  # type:str
                        if alias is not None and re.search(alias, product, flags = re.IGNORECASE):
                            ware_dict[alias].append(stripBrand(product, brand))
                            raise modules.utilities.Success
            # if any of the above succeeds, this line is skipped
            ware_dict['unknown'].append(product)
        except modules.utilities.Success:
            # use a dummy exception to signify success
            continue
    return ware_dict

def stripBrand(product: str, brand: modules.utilities.Brand) -> str:
    """Remove brand info from product name.
    Input: Product name and brand name
    Output: Product name without chinese or english brand name
    """
    if brand.ch is not None:
        product = re.sub(brand.ch, "", product, flags = re.IGNORECASE)
    if brand.eng is not None:
        product = re.sub(brand.eng, "", product, flags = re.IGNORECASE)
    if brand.aliases is not None:
        for alias in brand.aliases:
            product = re.sub(alias, "", product, flags = re.IGNORECASE)
    return product.strip()

def splitBrandProduct(brand_list: list[modules.utilities.Brand], product: str) -> (modules.utilities.Brand, str):
    """Split full product name into brand and pure product name.
    Input: list of brands, product name to split
    Output: (brand-obj, pure-product), or None if brand not found
    """
    # only need to one of brand.ch/brand.eng to find its place in wares dict
    for brand in brand_list:  # type:modules.utilities.Brand
        if brand.ch is not None and re.search(brand.ch, product, re.IGNORECASE):
            return modules.utilities.Brand(brand.ch, None, None), re.sub(brand.ch, "", product, flags = re.IGNORECASE).strip()
        if brand.eng is not None and re.search(brand.eng, product, re.IGNORECASE):
            return modules.utilities.Brand(None, brand.eng, None), re.sub(brand.eng, "", product, flags = re.IGNORECASE).strip()
    # brand not found
    return modules.utilities.Brand(None, None, None), product
