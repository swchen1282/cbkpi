# Workflow

crawler -> data_reader(get csv, get new column, merge, save to df_all) -> data_processor(read df_all, process) 

`XCom is not set to pass pandas -> so I save file into local folder`

## Out of memory
`egrep -i -r 'Killed' /var/log/syslog`