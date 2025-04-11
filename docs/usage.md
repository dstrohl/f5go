
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
    keyword: test/*
    target: test.com/l1/{}
    
    go/test/foobar => test.com/l1/goobar
    go/test/foobar/snafu => test.com/l1/foobar/snafu
    go/test/foobar?snafu => test.com/l1/foobar?snafu
    no match:
        go/test
        go/test?snafu=blah

### modified passthrough (querystring)
    notes:
        multiple targets will all get the same extensions
        path modifications can be used with querystring modifications.
    
    keyword: test/*
    target: test.com?l1={}
    
    go/test/foobar => test.com?l1=foobar
    go/test/foobar?snafu=blah => test.com?l1=foobar;snafu=blah
        (any passed querystring will be added to the built one)

    no match:
        go/test =>  test.com
        go/test?snafu=blah   => test.com?snafu=blah



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

### Notes on multi-level requests
    if the parent object does not have a link defined, use of the multi-level request is required.


### Notes on replacement keys:
    
    to use "{" or "}" in the actual querystring, use "{{" or "}}"

    {} will use everything after the keyword.
        {} cannot be used with named or numbered replacement keys

    {1}, {2} ... will use the first, second, etc passed path
        note, when using numbered entries, 
            any entries not specifically called will be lost.
            only 1-9 can be used (max of 9 entries)

    {*p} = remaining path minus querystring
    {*q} = querystring minus path.
    - any {xxx} other than the above will be considered variable names.
    - config var "replacement_error_handling" controls how errors are handled:
        - "ERROR" will return with an error screen to the user indicating an issue with the record.
        - "REPLACE" will replace any missing information with the string defined in "replacement_error_string"
    
    examples:
    go/ogle/a/b/c/d?e=f

    test.com/{} => test.com/a/b/c/d?e=f
    test.com/{p} => test.com/a/b/c/d
    test.com/{q} => test/com?e=f
    test.com/{1} => test.com/a
    test.com/{1}{3}/{p} => test.com/ac/b/d
    test.com/{5} => test.com/
    test.com/{1}/{2}{q} => test.com/a/b?e=f
 

### notes on querystr add
    if there are named/positional replacements:
        any passed querystring will only be added if the {q} is part of the link template.
    if {} is used, the passed querystring will be added to the end of the new URL
    if the link is not a generative link (no replacements)
        the querystring will be added to the end of the new url.
    
    if there is a querystring passed AND a querystring as part of the template (after merging for generative links), 
        they will be merged.  (this is also true for special (regex) templates.)
        as part of the merge, any keys in the passed url will replace the ones from the template.

### url quoting 
    - passed links are converted FROM url quoting before merging.
    - saved / generated links are converted to url quoting before returning

?????



### specials (regex queries)
    Allows for scanning passed path/s through regex and and returning a modified path.
    special listings can be sub listings.
    special listings CAN use variables
        if there is a {var} in the returned string from the regex parser, the variable will be inserted after parsing. 
    special listings do not support passthrough modifications, the entire querystring is passed to the regex and is parsed.
        * Note that you should be able to do almost everything using regex that can be done with the passthrough options.
    Special listing take longer to search so are searched AFTER normal listings.
        * If a match is found in the normal listings, the system will not check the specials.

    Special matching / replace uses the python re module with the re.sub() function (https://docs.python.org/3/howto/regex.html#modifying-strings) 






---
contributed by Saul Pwanson



