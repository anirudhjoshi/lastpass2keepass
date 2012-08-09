#!/usr/bin/python
# url,username,password,1extra,name,grouping(\ delimited),last_touch,launch_count,fav
import random, datetime, unicodedata, string

now = datetime.datetime.now()
formattedNow = now.strftime("%Y-%m-%dT%H:%M")

appendToFile = open("test_passwords.txt", "w" ).close()
appendToFile = open("test_passwords.txt", "a" )

unicode_glyphs = ''.join(
    unichr(char)
    for char in xrange(65533) # 0x10ffff + 1
    if unicodedata.category(unichr(char))[0] in ('LMNPSZ')
    )

# Generator

for i in range(1, 250):

    url = "http://www." + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)]) + ".com"
    username = "username_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
    password = "password_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(15)] )
    extra = "extra_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
    name = "WEBSITE_NAME_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
    grouping = "All\Main"
    last_touch = formattedNow
    launch_count = str(i)
    fav = "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(1)] )

    entry = [url, username, password, extra, name, grouping, last_touch, launch_count, fav]

    appendToFile.write(",".join(entry)+'\n')

appendToFile.close()