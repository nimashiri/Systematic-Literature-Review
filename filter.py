import csv
import re

def getCsvFiles(filename):
    all_item = []
    with open(filename, 'r') as f:
        data = csv.reader(f, delimiter=' ', quotechar='|')
        for item in data:
            a = ' '.join(item)
            all_item.append(a)
    return all_item

def write_to_csv(paper_list, filename):
  paper_list = set(paper_list)
  with open(filename, "w", newline="") as f:
      for item in paper_list:
          item = item.split(',')
          f.write("%s\n" % item[0])

def filter1(data):
    newdata = []
    #regex = re.compile(rule)
    for item in data:
        item = ' '.join(item.split())
        item = item.replace('[', '')
        item = item.replace(']', '')
        item = item.replace('++','')
        if 'vulnerability' in item or 'vulnerabilities' in item or 'faults' in item \
             or 'faults' in item or 'defect' in item or 'defects' in item or 'bug' in item or 'bugs' in item \
                  or 'failure' in item or 'failures' in item:
            newdata.append(item)
        # if 'vulnerability detector' in item:
        #     newdata.append(item)
        # if 'detection of vulnerability' in item:
        #     newdata.append(item)
        # if 'detection of vulnerabilities' in item:
        #     newdata.append(item)
        # if 'software vulnerability detection' in item:
        #     newdata.append(item)
        # if 'software vulnerability' in item:
        #     newdata.append(item)
        # if 'automatic vulnerability detection' in item:
        #     newdata.append(item)
    return newdata

def filter2(data):
    pass

def main():
    list_of_files = [
        './records/ACMPaperList.csv',
        './records/IEEEpaperslist.csv',
        './records/scholar.csv',
        './records/scienceDirectPaperList.csv'
    ]
    for d in list_of_files:
        data = getCsvFiles(d)
        data = set(data)
        
        f1 = filter1(data)
        s = d.split('/')
        s[2] = s[2].replace('.csv', '.txt')
        s = './phase1/' + s[2]
        write_to_csv(f1, s)


if __name__ == '__main__':
    main()