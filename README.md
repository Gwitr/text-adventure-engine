# text-adventure-engine
A text adventure engine (badly) written in python.

## Special text format
My engine uses a special text formatting system to add text that only shows up if certain flags are set.
Examples:
```
%!secret diamond:collected{There's something shiny on the floor... }
```
The percent sign starts an if block.
The exclamation mark is optional, and inverts the result.
After that you need to give the object's name.
After the object's name you put a double colon and the field name.
Following the field name, there is an optional field value (ex. `:foo`), and after that the text block, encased inside curly brackets.

### List of fields
1. collected