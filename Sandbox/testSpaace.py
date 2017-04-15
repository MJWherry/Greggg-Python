stringcheck = 'mc print all fl fr mc'
prefix = stringcheck.split()[0]
type = stringcheck.split()[1]
suffix = stringcheck.replace(prefix+' ','')
split = suffix.replace(type+' ','')
print prefix
print type
print suffix
print split

data = 'sdfsdf,sfdsdf,ssf,'

data = data[:-1]+';'
print data
