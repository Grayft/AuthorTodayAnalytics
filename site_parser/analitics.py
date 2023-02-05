import json


def get_dict_from_json_lines(file_name: str) -> dict:
    """Возвращает словарь из файла *.jl, в который спарсились книги с сайта.
    В файле *.jl каждая строка я вляется json-объектом
    dict = {'item_1' : {словарь с книгами 1-го json-объекта},
                ...
            'item_n' : {...},
    """
    cnt = 0
    all_books = {}
    with open(file_name, 'r') as file:
        for row in file.readlines():
            cnt += 1
            books_from_json = json.loads(row)
            all_books['item_' + str(cnt)] = books_from_json
    return all_books


if __name__ == '__main__':
    items = get_dict_from_json_lines('all_books.jl')
    print(items)

