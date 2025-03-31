
# Usage Information

*A simple service for redirecting mnemonic terms to destination urls.*

Features include:

  - anyone can add terms easily
  - regex parsing for "special cases" (using regular expressions)
  - automatically appends everything after the second slash to the destination url
  - tracks and displays term usage frequency on frontpage with fontsize
  - variables allow destination URLs to change en masse (e.g. project name)

## Required Packages

python-cherrypy3
python-jinja2

## Tips

To run, execute go.py and go to localhost:8080 in a browser.

backup go database regularly

        $ ./go.py export
        $ backup newterms.txt

## General Usage:


### normal single option
    keyword: test
    target: test.com

    go/test => test.com
        

        
### more than one link per keyword
    keyword: test
    target: test.com <marked primary>
    target2: foo.com
    option: choose primary

    go/test => test.com

    option: select
    
    go/test => <returns page with list of options>

### variables
    variables:
    - project = "coolstuff" 
    keyword: test
    target: test.com/{project}
    
    go/test => test.com/coolstuff

### standard passthrough (ext url + querystring)
    keyword: test
    target: test.com

    go/test/foobar => test.com/foobar
    go/test?foobar=snafu = test.com?foobar=snafu

### modified passthrough (ext url)
    notes:
        multiple targets will all get the same extensions
        path modifications can be used with querystring modifications.
    keyword: test
    target: test.com
    extension: l1/{}
    
    go/test =>  test.com
    go/test/foobar => test.com/l1/goobar
    go/test/foobar/snafu => test.com/l1/foobar/snafu
    go/test/foobar?snafu => test.com/l1/foobar?snafu
    go/test?snafu=blah   => test.com?snafu=blah

### modified passthrough (querystring)
    notes:
        multiple targets will all get the same extensions
        path modifications can be used with querystring modifications.
    
    keyword: test
    target: test.com
    querystring: ?l1={}
    
    go/test =>  test.com
    go/test/foobar => test.com?l1=foobar
    go/test?snafu=blah   => test.com?snafu=blah
    go/test/foobar?snafu=blah => test.com?l1=foobar;snafu=blah
        (any passed querystring will be added to the built one)
       

### 2 level request
    parent key: ogle
    child key: m
    target: google.com/maps

    go/ogle/m => google.com/maps

### 3 level request
    parent key: ogle/m
    child key: home
    target: google.com/maps/search="1234 any street, anytown usa."

    go/ogle/m/home => google.com/maps/search="1234 any street, anytown usa."

### Notes on replacement keys:
    
    to use "{" or "}" in the actual querystring, use "{{" or "}}"

    {1}, {2} ... will use the first, second, etc passed path
        note, when using numbered entries, any entries not specifically called will be lost. 
    {p} = full path minus querystring
    {q} = querystring minus path.
    {} will use everything after the keyword.
    
    examples:
    go/ogle/a/b/c/d?e=f

    test.com/{} => test.com/a/b/c/d?e=f
    test.com/{p} => test.com/a/b/c/d
    test.com/{q} => test/com?e=f
    test.com/{1} => test.com/a
    test.com/{1}{3} => test.com/ac
    test.com/{5} => test.com/
    test.com/{1}/{2}{q} => test.com/a/b?e=f
 

### specials (regex queries)
    Allows for scanning passed path/s through regex and and returning a modified path.
    special listings can be sub listings.
    special listings CAN use variables
        if there is a {var} in the returned string from the regex parser, the variable will be inserted after parsing. 
    special listings do not support passthrough modifications, the entire querystring is passed to the regex and is parsed.
        * Note that you should be able to do almost everything using regex that can be done with the passthrough options.
    Special listing take longer to search so are searched AFTER normal listings.
        * If a match is found in the normal listings, the system will not check the specials.

    Special matching / replace uses the python regex module with the re.sub() function (https://docs.python.org/3/howto/regex.html#modifying-strings) 





---
contributed by Saul Pwanson

