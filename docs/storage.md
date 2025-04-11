# Storage Format

RecordList:
    dict of <Records>


Common Record Fields:
    active: true
    start_date:
    end_date:
    created_date: x/x/x
    edits: 
        list:
            user:
            date:
    recent_uses:
        list:
            date: x/x/x
            count: 3


Record:
    keyword:  ogle
    select: [priority/choose/random]
    children:
        <RecordList>
    links:
        <LinksList>


LinksList:
    list of <links>

Link:
    url: https://google.com
    modify_path:
    modify_query:
    priority:

    
SpecialRecord:
    regex_match:
    regex_replace_template:
