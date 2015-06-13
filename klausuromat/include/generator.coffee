# Úτƒ-8 encoded

# Get substring of string between two strings
String::between = (start, stop, escape) ->
  # Get positions of start delimiter
  pBefore = @.indexOf(start)

  # Get position of stop delimiter
  pos = 0
  loop
  # Get position
    pAfter = @.indexOf(stop, pos)

    # Check if stop position is not the escape string
    break if pAfter is -1 or @.substring(pAfter, pAfter + escape.length) != escape
    pos = pAfter + escape.length

  # Not found
  if pBefore is -1 or pAfter is -1
    return [null, null, @.toString()]

  # Found: Get substrings & replace escape character
  return [
    @.substring(0, pBefore),
    @.substring(pBefore + start.length, pAfter).replace(escape, stop),
    @.substring(pAfter + stop.length),
  ]

($ document).ready ->
  # Loop through code elements
  for element in $('pre[class*=lang]')
    element = $(element)

    # Initializers
    [start, stop, escape, splitter] = ['#{', '}', '}}', '\n']
    [search, replace] = [';;', '<br />']
    lines = element.html().split(splitter)
    strings = []
    remove = []

    # Strip unformatted strings from code so snippet can't fuck it up
    for line, i in element.html().split(splitter)
      # Get strings before, between and after needles
      [before, text, after, raw] = line.between(start, stop, escape)

      # String found
      if text
        # Add string to list
        strings.push([i - remove.length - 1, text.split(search).join(replace)])

        # Mark line for deletion
        remove.push(i)

    # Replace html
    element.html((line for line, i in lines when i not in remove).join('\n'))

    # Get language
    [_, lang] = element.attr('class').split(':')

    # Apply snippet on code
    element.snippet(lang, style: 'ide-eclipse')

    # Get element content
    content = element.html()

    # Haha, tricked you snippet! Now put strings back in place, njarharhar!
    lines = $('ol', element).children()
    for str in strings
      # Unpack string
      [pos, str] = str

      # Append string to list item
      $(lines[pos]).append("<div class=\"hint\">#{str}</div>")
		
