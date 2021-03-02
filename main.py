import libraries
from globals import *
from utilities import *

def main():
    ws = xlwings.Book(bookname).sheets[0]
    product_list = getProductList(ws)
    print(len(product_list), product_list)
    # for index, product in enumerate(product_list):
    #     print(f"Search product: {product}")
    #     result = searchProduct(product)
    #     ws[f'F{2 + index}'].value = result
    t1 = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(searchProduct, product) for product in product_list]
        results = [[future.result()] for future in futures]
    t2 = time.time()
    print("Time elapsed: %.3f" % float(t2 - t1))
    ws['f2'].value = results

if __name__ == '__main__':
    main()
