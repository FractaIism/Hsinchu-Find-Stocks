from modules.libraries import *
import modules.utilities

" ========== CLASSES ========== "

class Filter:
    """Perform preliminary simple checks to directly accept/reject certain wares."""
    IDENTICAL: int = 999
    SUBSTRING_RELATION: int = 111
    MISSING_REQUIRED_KEYWORD: int = 222
    NUMBER_MISMATCH: int = 333
    MODEL_MISMATCH: int = 444

    def __init__(self, product: str, ware: str):
        self.product: str = product
        self.ware: str = ware

    def verdict(self):
        """Return True if ware if to be accepted as equal, False if ware is to be rejected, None if no conclusion can be drawn.
        If no conclusion can be drawn, carry on with string similarity comparison.
        """
        if self.checkIdentical() is True:
            return Filter.IDENTICAL
        if self.checkSubstringRelation() is True:
            return Filter.SUBSTRING_RELATION
        if self.checkModel() is False:
            return Filter.MODEL_MISMATCH
        if self.checkRequiredKeywords() is False:
            return Filter.MISSING_REQUIRED_KEYWORD
        if self.checkNumbers() is False:
            return Filter.NUMBER_MISMATCH

    def checkIdentical(self):
        """Check if product and ware are identical without brand and spaces."""
        if self.product.replace(" ", "") == self.ware.replace(" ", ""):
            return True

    def checkSubstringRelation(self):
        """Check if product or ware contain each other as a substring.
        If yes, consider them equal.
        """
        product_compact = self.product.replace(" ", "")
        ware_compact = self.ware.replace(" ", "")
        if (product_compact in ware_compact) or (ware_compact in product_compact):
            return True

    def checkRequiredKeywords(self):
        """Check if the ware contains all *necessary keywords* in product.
        If not, consider them unequal.
        """
        color_keywords = ["黑", "紅", "藍", "綠", "橙", "黃", "紫", "黑", "白", "金", "銀", "玫瑰金"]
        for color in color_keywords:
            if (color in self.product) and (color not in self.ware):
                return False

    def checkNumbers(self):
        """Check if the numbers (weight, size, quantity, etc...) match.
        If not, consider them unequal.
        """
        # use noncapturing group to obtain the full float (or int)
        regex = r"[0-9]+(?:\.[0-9]+)?"
        prod_nums: list[str] = re.findall(regex, self.product)
        ware_nums: list[str] = re.findall(regex, self.product)
        for num in range(min(len(prod_nums), len(ware_nums))):
            if prod_nums[num] != ware_nums[num]:
                return False

    def checkModel(self):
        regex = r"[A-Z]+(-[0-9A-Z]+)+"  # model should be in uppercase letters and numbers
        product_model = re.search(regex, self.product)
        ware_model = re.search(regex, self.ware)
        if not product_model:  # product has no model
            return True
        elif product_model and not ware_model:  # product has model but ware doesn't
            return False
        elif product_model.group() != ware_model.group():  # both have models but are different
            return False

" ========== FUNCTIONS ========== "

def getWaresByBrand(ware_list: list[modules.utilities.Ware], brand_list: list[modules.utilities.Brand]) -> dict[str, list[modules.utilities.Ware]]:
    """Make a dict to classify wares by brand name
    Input: product list and brand list
    Output: dict with keys=brand name and values=list of products pertaining to the brand
    """
    # initialize empty lists for each brand
    ware_dict = {
        'unknown': [],
        'all'    : ware_list,
    }  # type:dict[str,list[modules.utilities.Ware]]
    # chinese, english, and alias brand names all point to the same list object
    for brand in brand_list:  # type:modules.utilities.Brand
        ware_dict[brand.ch] = ware_dict[brand.eng] = []
        if brand.aliases is not None:
            for alias in brand.aliases:  # type:str
                ware_dict[alias] = ware_dict[brand.eng]

    # add products to their brand list
    for ware in ware_list:  # type:modules.utilities.Ware
        try:
            for brand in brand_list:  # type:modules.utilities.Brand
                if brand.ch is not None and re.search(brand.ch, ware.name, flags = re.IGNORECASE):
                    ware_dict[brand.ch].append(ware)
                    raise modules.utilities.Success
                elif brand.eng is not None and re.search(brand.eng, ware.name, flags = re.IGNORECASE):
                    ware_dict[brand.eng].append(ware)
                    raise modules.utilities.Success
                elif brand.aliases is not None:
                    for alias in brand.aliases:  # type:str
                        if alias is not None and re.search(alias, ware.name, flags = re.IGNORECASE):
                            ware_dict[alias].append(ware)
                            raise modules.utilities.Success
            # if any of the above succeeds, this line is skipped
            ware_dict['unknown'].append(ware)
        except modules.utilities.Success:
            # use a dummy exception to signify success
            continue
    return ware_dict

def stripBrand(product: str, brand: modules.utilities.Brand) -> str:
    """Remove brand info from product name (need to know the brand beforehand).
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
    """Split full product name into brand and pure product name (searches for a matching brand).
    Input: list of brands, product name to split
    Output: (brand, brandless-product), with brand=UNKNOWN_BRAND if not found
    """

    def findMatchingBrand(brand_list: list[modules.utilities.Brand], product: str):
        for cur_brand in brand_list:  # type:modules.utilities.Brand
            if cur_brand.ch is not None and re.search(cur_brand.ch, product, flags = re.IGNORECASE) is not None:
                return cur_brand
            if cur_brand.eng is not None and re.search(cur_brand.eng, product, flags = re.IGNORECASE) is not None:
                return cur_brand
            if cur_brand.aliases is not None:
                for alias in cur_brand.aliases:
                    if re.search(alias, product, flags = re.IGNORECASE):
                        return cur_brand

    # only need one of brand.ch/brand.eng to find its place in wares dict
    brandless_product = product  # type:str
    # identify and strip brand from product
    matching_brand = findMatchingBrand(brand_list, product)  # type:modules.utilities.Brand
    # if brand has been found
    if matching_brand is not None:
        if matching_brand.ch is not None:
            brandless_product = re.sub(matching_brand.ch, "", brandless_product, flags = re.IGNORECASE)
        if matching_brand.eng is not None:
            brandless_product = re.sub(matching_brand.eng, "", brandless_product, flags = re.IGNORECASE)
        if matching_brand.aliases is not None:
            for alias in matching_brand.aliases:
                brandless_product = re.sub(alias, "", brandless_product, flags = re.IGNORECASE)
        return matching_brand, brandless_product.strip()
    else:
        return modules.utilities.UNKNOWN_BRAND, product

@functools.cache
def purify(product: str):
    """Call various methods to clean up product name."""

    def replaceKeywords(product: str):
        # dict to map certain keywords to their standardized equivalents
        # make sure to put longer keywords in front so they get replaced first
        repl_dict = {
            "公升": "L",
            "毫升": "mL",
            "毫米": "mm",
            "公斤": "kg",
            "公克": "g",
            "毫克": "mg",
            "微克": "ug",
            "米" : "M",
            "克" : "g",
        }
        new_product = product
        for old, new in repl_dict.items():
            new_product = new_product.replace(old, new)
        return new_product

    def stripQuantity():
        # self.purified = re.sub(r"[xX*][0-9]*入?組?$", "", self.purified)
        # do nothing until certain what to do with quantities
        pass

    def stripParentheses(product: str):
        return re.sub(r"[()]", "", product)

    def stripUnits(product: str):
        # todo:make a list of units and remove them from product
        units = []
        pass

    # perform preprocessing here
    purified: str = product
    purified = purified.replace(" ", "")
    purified = stripParentheses(purified)
    purified = replaceKeywords(purified)
    purified = purified.lower()
    return purified
