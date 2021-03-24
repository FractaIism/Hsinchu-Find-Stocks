from modules.libraries import *
from modules.utilities import logNprint

def getWaresByBrand(ware_list: list[str], brand_list: list[tuple[str, str, list[str]]]) -> dict[str, list[str]]:
    """Make a dict to classify wares by brand name
    Input: product list and brand list
    Output: dict with keys=brand name and values=list of products pertaining to the brand
    """

    # initialize empty lists for each brand
    ware_dict = {
        'unknown': [],
        'all'    : ware_list,
    }
    for ch, eng, aliases in brand_list:
        # chinese, english, and alias brand names all point to the same list
        ware_dict[ch] = ware_dict[eng] = []
        for alias in aliases:
            ware_dict[alias] = ware_dict[eng]
    # add products to their brand list
    for product in ware_list:
        try:
            for brand in brand_list:
                ch, eng, aliases = brand
                if ch is not None and re.search(ch, product, flags = re.IGNORECASE):
                    ware_dict[ch].append(removeBrand(product, brand))
                    raise ConnectionError
                elif eng is not None and re.search(eng, product, flags = re.IGNORECASE):
                    ware_dict[eng].append(removeBrand(product, brand))
                    raise ConnectionError
                else:
                    for alias in aliases:
                        if alias is not None and re.search(alias, product, flags = re.IGNORECASE):
                            ware_dict[alias].append(removeBrand(product, brand))
                            raise ConnectionError
            # if any of the above succeeds, this line is skipped
            ware_dict['unknown'].append(product)
        except ConnectionError:
            # use a dummy exception
            continue
    return ware_dict

def removeBrand(product: str, brand: tuple[str, str, list[str]]) -> str:
    """Remove brand info from product name.
    Input: Product name and brand name
    Output: Product name without chinese or english brand name
    """
    ch, eng, aliases = brand
    if ch is not None:
        product = re.sub(ch, "", product, flags = re.IGNORECASE)
    if eng is not None:
        product = re.sub(eng, "", product, flags = re.IGNORECASE)
    if aliases is not None:
        for alias in aliases:
            product = re.sub(alias, "", product, flags = re.IGNORECASE)
    return product.strip()

def splitBrandProduct(brand_list: list[tuple[str, str, list[str]]], product: str) -> (tuple[str, str, list[str]], str):
    """Split full product name into brand and pure product name.
    Input: list of brands, product name to split
    Output: (pure-brand, pure-product), or None if brand not found
    """
    for brand in brand_list:
        ch, eng, aliases = brand
        if ch is not None and re.match(ch, product, re.IGNORECASE):
            return (ch, None, None), re.sub(ch, "", product, flags = re.IGNORECASE).strip()
        if eng is not None and re.match(eng, product, re.IGNORECASE):
            return (None, eng, None), re.sub(eng, "", product, flags = re.IGNORECASE).strip()
    # if brand not found, return None
    return (None, None, None), product
