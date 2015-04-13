#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Externals
import cgi
import cgitb
import codecs
import sys
import io
import json
from xml.sax.saxutils import escape

# Internals
import html
import generator
import exceptions
import language


# We need to overwrite stdout due to stupidity of the cgi module
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)


# Extend field storage
class FieldStorage(cgi.FieldStorage):
    # Return a field value as a boolean
    def getbool(self, key):
        # Convert to integer (if possible)
        try:
            value = int(self.getvalue(key))
        except (ValueError, TypeError):
            value = self.getvalue(key)

        # Return as boolean
        return bool(value)

# Get settings
with io.open('settings.json', mode='r', encoding='utf-8') as fd:
    settings = json.load(fd)

# Debugging
debug = settings['DEBUG']

# Debug: Show exceptions as HTML code
if debug:
    cgitb.enable()

# Remote debugging
if settings['REMOTE_DEBUG']:
    sys.path.append('/home/vbox/pycharm/pycharm-debug-py3k.egg')
    import pydevd

    pydevd.settrace('192.168.56.1', port=22222, stdoutToServer=True, stderrToServer=True)

# Get version
version = settings['VERSION']

# Get fields
post = FieldStorage()
default = 'generate' not in post

# Get translation table
L = language.Language(post.getvalue('lang'))

# Required fields
required = ['operators', 'pointers', 'functions']

# Form dict
form = {'debug': '', 'error': '', 'code': ''}

# Check if all required fields exist
if all(field in post for field in required):
    # Wrap error message
    def error(msg, raw=False):
        form['error'] = msg.format(L) if raw else '<article class="error"><div>{:oops}</div>{}</article>'.format(L, msg)

    # Generate code from gathered data
    def generate():
        # Set generator settings
        try:
            # Create random code generator
            gen = generator.RandomCodeGenerator()

            # Levels
            gen.operator_level = post.getvalue('operators')
            gen.pointer_level = post.getvalue('pointers')
            gen.function_level = post.getvalue('functions')

            # Booleans
            gen.void = post.getvalue('void')
            gen.float_ = post.getvalue('float')
            gen.conditionals = post.getvalue('conditionals')

        # Catch error on settings
        except exceptions.RandomGeneratorSettingError as exc:
            # Catch error
            error('<article class="error"><div>{:please_fix_problem}</div>{}</article>'.format(L, exc), raw=True)

        # Settings made, now generate code
        else:
            # Now try to generate code
            try:
                form['code'] = '<h2>{:output}</h2><pre class="lang:c">{}</pre>'.format(L, escape(gen.code()))

            # Catch errors
            # Note: We are catching IndexError exceptions as well until this will be improved in operations and functions
            except (exceptions.GeneratorVerifyError, exceptions.GeneratorCompileError, IndexError):
                if debug and post.getvalue('debug'):
                    raise
                else:
                    # Verifying and compiling errors happen so often... just try again
                    generate()

            # Catch exceptions where we ran out of identifiers (this is so rare we don't have to track it above)
            except exceptions.GeneratorGenerationNotPossibleError as exc:
                error('{0:could_not_generate_code}<br /><b>{0:message}:</b> {1}'.format(L, exc))
                if debug and post.getvalue('debug'):
                    raise

            # Catch other exceptions that might indicate major bugs
            except Exception as exc:
                error('{0:horrific_exception}<br /><b>{0:message}:</b> {1}'.format(L, exc))
                if debug and post.getvalue('debug'):
                    raise

    # Call generator
    generate()

# Select options
operatorLevels = [str_.format(L) for str_ in (
    '1. {:basic} (+, -, *, /)', '2. {:advanced} (i++, ++i, +=, *=, ...)',
    '3. {:bitwise_operators} (&, |, ^, %, ...)', '4. {:bit_shifts} (<<, >>, ...)')]
pointerLevels = [str_.format(L) for str_ in ('{:none}', '{:single_references}', '{:multiple_references}')]
functionLevels = [str_.format(L) for str_ in ('{:none}', '{:by_value}', '{:by_reference}')]

# Build selects
form['operators'] = html.select('operators', operatorLevels, selected=post.getvalue('operators'))
form['pointers'] = html.select('pointers', pointerLevels, selected=post.getvalue('pointers'))
form['functions'] = html.select('functions', functionLevels, selected=post.getvalue('functions'))

# Build Checkboxes
form['identifiers'] = '<br />'.join([
    html.checkbox('void', '{:void_functions}'.format(L), checked=(default or post.getbool('void'))),
    html.checkbox('float', '{:floating_point}'.format(L), checked=post.getbool('float')),
    html.checkbox('arrays', '{:arrays}'.format(L), disabled=True),
    html.checkbox('strings', '{:strings}'.format(L), disabled=True)
])
form['additionals'] = '<br />'.join([
    html.checkbox('conditionals', '{:conditional_statements}'.format(L), checked=post.getbool('conditionals')),
    html.checkbox('loops', '{:loops}'.format(L), disabled=True)
])
form['toggleDebug'] = '''
            <tr>
                <td>{:debug}</td>
                <td>
                    {}
                </td>
            </tr>
'''.format(L, html.checkbox('debug', '{:on}'.format(L), checked=(default or post.getbool('debug')))) if debug else ''

# Build submit button
form['submit'] = html.submit('{:generate_code}'.format(L))

# Build hidden inputs
form['hidden'] = '\n'.join([
    html.hidden('lang', post.getvalue('lang', L.default)),
    html.hidden('generate', '1')
])

# Debug POST data
#if debug:
#	form['debug'] = '<pre>{}</pre><hr />'.format(post)

# HTML content
content = '''
<div id="container">
    {1[debug]}

    <h1>{0:klausuromat}</h1>
    <h3>{0:version} {2}</h3>

    {1[error]}

    <form method="get">
        {1[hidden]}
        <table>
            <tr>
                <td>{0:operator_level}</td>
                <td>
                    {1[operators]}
                </td>
            </tr>
            <tr>
                <td>{0:pointer_level}</td>
                <td>
                    {1[pointers]}
                </td>
            </tr>
            <tr>
                <td>{0:function_level}</td>
                <td>
                    {1[functions]}
                </td>
            </tr>
            <tr>
                <td>{0:identifier_options}</td>
                <td>
                    {1[identifiers]}
                </td>
            </tr>
            <tr>
                <td>{0:additional_options}</td>
                <td>
                    {1[additionals]}
                </td>
            </tr>
            {1[toggleDebug]}
            <tr>
                <td colspan="2">{1[submit]}</td>
            </tr>
        </table>

        {1[code]}
    </form>
</div>
'''

# Build includes
path = settings['INCLUDE_DIRECTORY']
includes = [
    html.css.format(path + '/generator.css'),
    html.css.format(path + '/jquery.snippet.css'),
    html.javascript.format(path + '/jquery-2.0.3.min.js'),
    html.javascript.format(path + '/jquery.snippet.js'),
    html.javascript.format(path + '/generator.js')
]

# Print HTTP Header and HTML Content
print('Content-Type: text/html;charset=utf-8\n\n', html.html.format({
    'title':    '{:klausuromat}'.format(L),
    'includes': '\n'.join(includes),
    'content':  content.format(L, form, version)
}))
