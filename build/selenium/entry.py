import os
from selenium import webdriver
from selenium.webdriver.common.by import By

link = "https://nerdcave.com/tailwind-cheat-sheet"
driver = webdriver.Chrome()
driver.get(link)


doc_path = os.path.join("../../lua/tailiscope", "docs/")
category_file = open(doc_path + "categories.lua", "w")


btns = driver.find_elements(By.CSS_SELECTOR, "button")
containers = driver.find_elements(By.CSS_SELECTOR, 'div:has( > header)')


for b in btns:
    if b.text == "EXPAND ALL":
        expander = b
        expander.click()
        break


items = []
for c in containers:
    category = c.find_element(By.CSS_SELECTOR, 'header > h2').text
    items.append({'name': category, 'items': []})

    lis = c.find_elements(By.CSS_SELECTOR, 'li')
    for li in lis:
        type = li.find_element(By.CSS_SELECTOR, 'span').text
        link = li.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        items[-1]['items'].append({'name': type, 'items': [], 'doc': link})
        table = li.find_element(By.CSS_SELECTOR, 'table')
        trs = table.find_elements(By.CSS_SELECTOR, 'tr')
        print('table: ', type)
        for t in trs:
            tds = t.find_elements(By.CSS_SELECTOR, 'td')
            value = tds[1].text
            if tds[2] and tds[2].text != '':
                value += '\t' + tds[2].text
            items[-1]['items'][-1]['items'].append({
                'name': tds[0].text,
                'value': value,
            })
# write files


def replace_char(str):
    chars = [" ", "-", ":", ",", "/"]
    temp = ""
    for s in str:
        c = s
        if s in chars:
            c = "_"
        temp += c
    # todo choose appropriate char to replace with and split accordingly in lua
    return temp.lower().replace("\n", " ")


def recursive_write(name, items):
    path = os.path.join(doc_path, replace_char(name)+".lua")
    with open(path, "w") as f:
        f.write('return {\n')
        for item in items:
            value = ""
            if item.get('items') is not None:
                recursive_write(item['name'], item['items'])
                value = "'%s'" % replace_char(item['name'])
            else:
                value = "'%s', base=true" % replace_char(item['value'])
            if item.get('doc') is not None:
                value += ", doc='%s'" % item['doc']
                write = "\t{'%s', %s},\n" % (item['name'], value)
                category_file.write(write)
            write = "\t{'%s', %s},\n" % (item['name'], value)
            f.write(write)
        f.write('}')


if not os.path.exists(doc_path):
    os.makedirs(doc_path)

recursive_write('base', items)

print("done")
