def greedy_group_by_reviews(items: list[dict], threshold: int = 500):
    items = sorted(items, key=lambda x: x['Отзывов'], reverse=True)
    groups = []

    for item in items:
        placed = False

        # Попробуем вставить элемент в уже существующие группы
        for group in groups:
            group_sum = sum(x['Отзывов'] for x in group)

            # Если элемент можно добавить в текущую группу
            if group_sum + item['Отзывов'] <= threshold:
                group.append(item)
                placed = True
                break

        # Если элемент не удалось вставить в существующую группу — создаем новую
        if not placed:
            groups.append([item])
    return groups


import pandas as pd
items = list(pd.read_excel('gpt.xlsx').to_dict('records'))[::-1]

nm_id = 'Артикул'
cat = 'Категория'
feedbacks = 'Отзывов'


lol_dict = dict()
for item in items:
    name = item[cat]

    if lol_dict.get(name):
        lol_dict[name].append(item)
    else:
        lol_dict[name] = [item]


output = []
indexes = list(range(1, 1000000))[::-1]
for index, _ in enumerate(lol_dict.items(), start=1):
    cat, lil_items = _

    res = greedy_group_by_reviews(lil_items)
    for i in res:
        loool = indexes.pop()
        for j in i:
            j.update({'index': loool})
            output.append(j)

pd.DataFrame(output).to_excel('res.xlsx', index=False)






