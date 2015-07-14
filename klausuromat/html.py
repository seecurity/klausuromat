# Basic HTML skeleton
html = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{0[title]}</title>
    {0[includes]}
</head>
<body>
    {0[content]}
</body>
</html>
'''

# Favicon skeleton
favicon = '<link type="image/x-icon" rel="shortcut icon" href="{}" />'

# CSS include skeleton
css = '<link type="text/css" rel="stylesheet" href="{}" />'

# JavaScript include skeleton
javascript = '<script src="{}" type="text/javascript" charset="utf-8"></script>'


# Generate a hidden input
def hidden(name, value):
    # Set formatters
    code = '<input type="hidden" name="{}" value="{}" />'

    # Return formatted html
    return code.format(name, value)


# Generate a submit button
def submit(description, name=None):
    # Set formatters
    code = {
        'input':    '<input type="submit"{} value="{}" />',
        'name':     ' name="{}"'
    }

    # Return formatted html
    return code['input'].format(code['name'].format(name) if name else '', description)


# Generate a checkbox
def checkbox(name, description, space=True, checked=False, disabled=False):
    # Set space, checked, disabled if None
    check = [space, checked, disabled]
    if None in check:
        space, checked, disabled = [False if item is None else item for item in check]

    # Set formatters
    code = {
        'input':    '<input type="checkbox" name="{}"{}{} />{}{}',
        'checked':  ' checked="checked"',
        'disabled': ' disabled="disabled"'
    }

    # Return formatted html
    return code['input'].format(
        name,
        code['checked'] if checked else '',
        code['disabled'] if disabled else '',
        ' ' if space else '',
        description
    )


# Generate a select
def select(name, options, size=1, selected=False):
    # Set selected if None and convert if necessary
    selected = False if selected is None else int(selected)

    # Set formatters
    code = {
        'select': '''
            <select name="{}" size="{}">
                {}
            </select>
        ''',
        'option':   '<option value="{}"{}>{}</option>',
        'selected': ' selected="selected"'
    }

    # Return formatted html
    return code['select'].format(
        name, size,
        '\n'.join([
            code['option'].format(index, code['selected'] if index == selected and selected is not False else '', value)
            for index, value in enumerate(options)
        ])
    )
