import csv


def getCsvFiles(filename):
    all_item = []
    with open(filename, 'r') as f:
        data = csv.reader(f, delimiter=' ', quotechar='|')
        for item in data:
            a = ' '.join(item)
            all_item.append(a)
    return all_item


def main():
    store = {'arxiv': 0, 'IEEE': 0, 'ACM': 0, 'ScienceDirect': 0, 'Other': 0}
    filename = './records/scholar.csv'
    data = getCsvFiles(filename)
    for item in data:
        item.replace('[', '')
        item.replace(']', '')
        if 'arxiv.org' in item:
            store['arxiv'] += 1
        elif 'ieeexplore.ieee.org' in item:
            store['IEEE'] += 1
        elif 'dl.acm.org' in item:
            store['ACM'] += 1
        elif 'Elsevier' in item:
            store['ScienceDirect'] += 1
        else:
            store['Other'] += 1
            print(item)
    print('a')


if __name__ == '__main__':
    main()