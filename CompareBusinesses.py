__author__ = 'natelawrence'

# !/usr/bin/python

import sqlite3
import csv
import numpy as np
import matplotlib.pyplot as plt

filename = 'SantaClaraSandwiches.csv'
dbname = 'SCsando'
Nrows = 0 # for testing
MakeDb = 0
dbnameNorm = dbname + 'Norm'


def SanitizeName(string):
    partition = string.split('-')
    exclude = ['san', 'jose', 'sunnyvale', 'cupertino', 'santa', 'clara', 'milpitas', 'campbell']
    outList = []
    for item in partition:
        try:
            int(item)
        except:
            if not item in exclude:
                outList.append(item)
    return '-'.join(outList)


if MakeDb:
    with sqlite3.connect(dbname + '.db') as conn:
        c = conn.cursor()

        # create table
        c.execute('''CREATE TABLE {}
                     (business TEXT, userid TEXT, rating REAL)'''.format(dbname))

        # read data file
        multi_lines = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            if Nrows > 0:
                for nn in range(0, Nrows):
                    row = reader.next()
                    if len(row) == 3:
                        multi_lines.append(reader.next())
            else:
                for row in reader:
                    if len(row) == 3:
                        multi_lines.append(row)
        # sanatize names
        newLines = []
        for item in multi_lines:
            item[0] = SanitizeName(item[0])
            newLines.append(item)

        c.executemany('INSERT INTO {} VALUES (?,?,?)'.format(dbname), newLines)

        # save (commit) the changes
        conn.commit()

    # get name of businesses in db
    BusinessNames = []
    with sqlite3.connect(dbname + '.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
        select DISTINCT(business)
        from {0}
        """.format(dbname))
        temp = cursor.fetchall()
        for tt in range(0, len(temp)):
            BusinessNames.append(temp[tt][0])

    NormList = []
    for nn in range(0, len(BusinessNames)):
        name = BusinessNames[nn]
        with sqlite3.connect(dbname + '.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
            select SUM((rating-3)*(rating-3))
            from {0}
            where business is '{1}'
            """.format(dbname, name))
        NormList.append(np.sqrt(cursor.next()[0]))

    # make database of normalized rating values
    NormDict = dict(zip(BusinessNames, NormList))
    dbnameNorm = dbname + 'Norm'
    with sqlite3.connect(dbnameNorm + '.db') as conn:
        c = conn.cursor()

        # create table
        c.execute('''CREATE TABLE {}
                     (business TEXT, userid TEXT, rating REAL)'''.format(dbname))

        # read data file
        multi_lines = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            if Nrows > 0:
                for nn in range(0, Nrows):
                    row = reader.next()
                    if len(row) == 3:
                        multi_lines.append(reader.next())
            else:
                for row in reader:
                    if len(row) == 3:
                        multi_lines.append(row)

        # sanatize names
        newLines = []
        for item in multi_lines:
            item[0] = SanitizeName(item[0])
            newLines.append(item)

        for mm in range(0, len(newLines)):
            newLines[mm][2] = str((float(newLines[mm][2]) - 3) / NormDict[newLines[mm][0]])

        c.executemany('INSERT INTO {} VALUES (?,?,?)'.format(dbname), newLines)

        # save (commit) the changes
        conn.commit()

# open and query sql file
with sqlite3.connect(dbnameNorm + '.db') as conn:
    cursor = conn.cursor()

    # get business similarities
    cursor.execute('''
    SELECT a.business, b.business, SUM((a.rating)*(b.rating)), COUNT((a.rating)*(b.rating))
    FROM {0} as a, {0} as b
    WHERE a.userid = b.userid
    GROUP BY a.business, b.business
    ORDER BY SUM((a.rating)*(b.rating))
    '''.format(dbname))
    Similarities = cursor.fetchall()
    # get norm of each businesses rating vector

# filter similarities list to remove redundent entries and self similarities
minCount = 10
printed = []
NonRedSims = []
for ss in range(0, len(Similarities)):
    if Similarities[ss][0] == Similarities[ss][1]:
        continue
    if ((Similarities[ss][0], Similarities[ss][1])) in printed or (
    (Similarities[ss][1], Similarities[ss][0])) in printed:
        continue
    if Similarities[ss][3] < minCount:
        continue
    else:
        # print '{}\t{}\t{}'.format(Similarities[ss][0],Similarities[ss][1],Similarities[ss][2])
        printed.append((Similarities[ss][0], Similarities[ss][1]))
        NonRedSims.append((Similarities[ss][0], Similarities[ss][1], Similarities[ss][2], Similarities[ss][3]))

npNonRedSims = np.array(NonRedSims,
                        dtype=[('n1', np.chararray), ('n2', np.chararray), ('sim', float), ('count', float)])
npNonRedSims = np.sort(npNonRedSims, order='sim')

print '\nMost similar businesses:'
for ii in range(len(npNonRedSims) - 10, len(npNonRedSims)):
    item = npNonRedSims[ii]
    print '{}\t{}\t{}\t{}'.format(item[0], item[1], item[2], item[3])

print '\nLeast similar businesses:'
for ii in range(0, 10):
    item = npNonRedSims[ii]
    print '{}\t{}\t{}\t{}'.format(item[0], item[1], item[2], item[3])

# look at similarities for single restaurant
BusinessName = u'ikes-love-and-sandwiches'
with sqlite3.connect(dbnameNorm + '.db') as conn:
    cursor = conn.cursor()

    # get business similarities
    cursor.execute('''
    SELECT a.business, b.business, SUM((a.rating)*(b.rating)), COUNT((a.rating)*(b.rating))
    FROM {0} as a, {0} as b
    WHERE a.userid = b.userid and a.business is '{1}'
    GROUP BY a.business, b.business
    ORDER BY SUM((a.rating)*(b.rating))
    '''.format(dbname, BusinessName))
    SingleBizSims = cursor.fetchall()
    # get norm of each businesses rating vector

# filter similarities list to remove redundent entries and self similarities
minCount = 10
printed = []
SBNonRedSims = []
for ss in range(0, len(SingleBizSims)):
    if SingleBizSims[ss][0] == SingleBizSims[ss][1]:
        continue
    if ((SingleBizSims[ss][0], SingleBizSims[ss][1])) in printed or (
    (SingleBizSims[ss][1], SingleBizSims[ss][0])) in printed:
        continue
    if SingleBizSims[ss][3] < minCount:
        continue
    else:
        # print '{}\t{}\t{}'.format(Similarities[ss][0],Similarities[ss][1],Similarities[ss][2])
        printed.append((SingleBizSims[ss][0], SingleBizSims[ss][1]))
        SBNonRedSims.append((SingleBizSims[ss][0], SingleBizSims[ss][1], SingleBizSims[ss][2], SingleBizSims[ss][3]))

SBnpNonRedSims = np.array(SBNonRedSims,
                          dtype=[('n1', np.chararray), ('n2', np.chararray), ('sim', float), ('count', float)])
SBnpNonRedSims = np.sort(SBnpNonRedSims, order='sim')

print '\nMost similar businesses to {}:'.format(BusinessName)
for ii in range(len(SBnpNonRedSims) - 10, len(SBnpNonRedSims)):
    item = SBnpNonRedSims[ii]
    print '{}\t{}\t{}'.format(item[1], item[2], item[3])

print '\nLeast similar businesses to {}:'.format(BusinessName)
for ii in range(0, 10):
    item = SBnpNonRedSims[ii]
    print '{}\t{}\t{}'.format(item[1], item[2], item[3])

# make plots
# make correlation matrix plot using names of some of the most and least correlated restaurants
names = [u'safeway', u'red-robin-gourmet-burgers', u'honeyberry', u'paris-baguette', u'chiaramontes-deli-and-sausages',
         u'paradiso-delicatessen-and-restaurant', u'piatti', u'togos-sandwiches', u'world-wrapps',
         u'specialtys-cafe-and-bakery']

RatingMatrix = []
for item in names:
    with sqlite3.connect(dbnameNorm + '.db') as conn:
        cursor = conn.cursor()

        # get business similarities
        cursor.execute('''
        SELECT b.business, SUM((a.rating)*(b.rating))
        FROM {0} as a, {0} as b
        WHERE a.userid = b.userid and a.business is '{1}'
        GROUP BY a.business, b.business
        ORDER BY SUM((a.rating)*(b.rating))
        '''.format(dbname, item))
        temp = cursor.fetchall()
        tempDict = dict(zip([t[0] for t in temp], [t[1] for t in temp]))
        RatingVec = []
        for name in names:
            if item == name:
                RatingVec.append(0)
            else:
                RatingVec.append(tempDict[name])
    RatingMatrix.append(RatingVec)

array = np.array(RatingMatrix)

abrNames = [u'safeway', u'red robin', u'honeyberry', u'paris baguette', u'chiaramontes',
            u'paradiso', u'piatti', u'togos', u'world wrapps', u'specialtys']

plt.pcolor(array)
plt.colorbar()
plt.yticks(np.arange(0.5, 10.5), abrNames)
plt.xticks(np.arange(0.5, 10.5), abrNames, rotation='vertical')
plt.gcf().tight_layout()
plt.show()

# look at similarities for single restaurant
BusinessName = u'ikes-love-and-sandwiches'
with sqlite3.connect(dbnameNorm + '.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT b.business, SUM((a.rating)*(b.rating))
    FROM {0} as a, {0} as b
    WHERE a.userid = b.userid and a.business is '{1}'
    GROUP BY a.business, b.business
    ORDER BY SUM((a.rating)*(b.rating))
    '''.format(dbname, BusinessName))
    SingleBizSims = cursor.fetchall()

scores = []
names = []
for s in SingleBizSims[0:10]:
    scores.append(s[1])
    names.append(' '.join(s[0].split('-')))
scores.append(0)
names.append(u'')
for s in SingleBizSims[-11:-1]:
    scores.append(s[1])
    names.append(' '.join(s[0].split('-')))

plt.figure()
ax = plt.subplot(111)
ax.bar(range(0, 21), scores, width=.9, color='b')
plt.xticks(np.arange(0.5, 21.5), names, rotation='vertical')
plt.gcf().tight_layout()
plt.xlim(0, 21)
plt.show()
