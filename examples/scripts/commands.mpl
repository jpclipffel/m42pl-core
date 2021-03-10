| commands
| stats
    values(command.syntax) as command.syntax, 
    values(command.about) as command.about 
    by command.aliases
| eval 
    command.name = at(command.aliases, 0),
    command.about = at(command.about, 0),
    command.syntax = at(command.syntax, 0)
| fields command.name, command.about, command.syntax, command.aliases
| output
