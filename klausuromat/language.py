# Internals
import enumerator


# Language class
# To do: Maybe we should use gettext instead but for now this will be fine
class Language:
    # Possible languages
    languages = enumerator.Enum(EN=0, DE=1, l337=2, KLI=3)

    # Translations
    translation = {
        'klausuromat': (
            'Klausuromat',
            'Klausuromat',
            'kl4u5ur0m47',
            'waH HablI\''
        ),
        'version': (
            'Version',
            'Version',
            'v3r510n',
            'nuH',
        ),
        'debug': (
            'Debug',
            'Debug',
            'd3bu6',
            'Qagh vItu\''
        ),
        'on': (
            'On',
            'An',
            '0n',
            'pov'
        ),
        'off': (
            'Off',
            'Aus',
            '0ff',
            'DoH'
        ),
        'oops': (
            'Ooops...',
            'Ups...',
            '000p5...',
            'va...'
        ),
        'please_fix_problem': (
            'Please fix the following problem:',
            'Folgendes Problem ist aufgetreten:',
            'pl3453 f1x 7h3 f0ll0w1n6 pr0bl3m:',
            'Qagh tI\''
        ),
        'output': (
            'Output',
            'Ausgabe',
            '0u7pu7',
            'nobHa\''
        ),
        'could_not_generate_code': (
            'Could not generate code. Please change your settings if this doesn\'t stop happening.',
            'Ein Fehler beim Generieren des Codes ist aufgetreten. Bitte ändere die Einstellungen, wenn dieser Fehler'
            ' kontinuierlich auftritt.',
            'c0uld n07 63n3r473 c0d3. pl3453 ch4n63 y0ur 53771n65 1f 7h15 d035n\\\'7 570p h4pp3n1n6.',
            'laH wej chenmoH. lo\'laHghach choH'
        ),
        'message': (
            'Message',
            'Fehlermeldung',
            'm355463',
            'QIn'
        ),
        'horrific_exception': (
            'Something wen\'t really wrong! If this doesn\'t stop happening, please contact the administrator.',
            'Das sollte eigentlich nicht passieren! Wenn dieser Fehler weiterhin auftritt, kontaktiere bitte den'
            'Administrator.',
            '50m37h1n6 w3n\\\'7 r34lly wr0n6! 1f 7h15 d035n\\\'7 570p h4pp3n1n6, pl3453 c0n74c7 7h3 4dm1n157r470r.',
            'qab Qagh. pagh qaStaH. \'oH pong HoD'
        ),
        'operator_level': (
            'Operator level',
            'Operatoren-Level',
            '0p3r470r l3v3l',
            'patlh \'orwI\''
        ),
        'basic': (
            'Basic',
            'Grundlegend',
            'b451c',
            'ngeD'
        ),
        'advanced': (
            'Advanced',
            'Erweitert',
            '4dv4nc3d',
            'choghIjtaHghach'
        ),
        'bitwise_operators': (
            'Bitwise operators',
            'Bitweise Operatoren',
            'b17w153 0p3r470r5',
            'waw\' \'orwI\' 2'
        ),
        'bit_shifts': (
            'Bit shifts',
            'Bitweise Verschiebungen',
            'b17 5h1f75',
            'waw\' 2 vIH'
        ),
        'pointer_level': (
            'Pointer level',
            'Zeiger-Level',
            'p01n73r l3v3l',
            'DoS patlh'
        ),
        'none': (
            'None',
            'Kein',
            'n0n3',
            'Qo\''
        ),
        'single_references': (
            'Single references',
            'Einfache Referenzen',
            '51n6l3 r3f3r3nc35',
            'Dov\'agh DoS'
        ),
        'multiple_references': (
            'Multiple references',
            'Mehrfache Referenzen',
            'mul71pl3 r3f3r3nc35',
            'Qay\'qu\' cha\''
        ),
        'function_level': (
            'Function level',
            'Funktions-Level',
            'func710n l3v3l',
            'Qap patlh'
        ),
        'by_value': (
            'By value',
            'Wertparameter',
            'by v4lu3',
            'pong lo\'laHghach'
        ),
        'by_reference': (
            'By reference',
            'Referenzparameter',
            'by r3f3r3nc3',
            'pong cha\''
        ),
        'identifier_options': (
            'Identifier options',
            'Bezeichner Optionen',
            '1d3n71f13r 0p710n5',
            'pong choH'
        ),
        'void_functions': (
            'Void functions',
            'Void-Funktionen',
            'v01d func710n5',
            'chIm Qap'
        ),
        'floating_point': (
            'Floating point',
            'Fließkommazahlen',
            'fl0471n6 p01n7',
            'lang \'ej Dunbogh jom'
        ),
        'arrays': (
            'Arrays',
            'Felder',
            '4rr4y5',
            'yotlh'
        ),
        'strings': (
            'Strings',
            'Zeichenketten',
            '57r1n65',
            'SIrgh'
        ),
        'additional_options': (
            'Additional options',
            'Sonstige Optionen',
            '4dd1710n4l 0p710n5',
            'Saturjaj DuH'
        ),
        'conditional_statements': (
            'Conditional statements',
            'Konditionale Sprünge',
            'c0nd1710n4l 57473m3n75',
            'motlh Sup'
        ),
        'loops': (
            'Loops',
            'Schleifen',
            'l00p5',
            're Sup'
        ),
        'generate_code': (
            'Generate Code',
            'Code generieren',
            '63n3r473 c0d3',
            'ngoq chenmoH'
        )
    }

    # Constructor: Define language
    def __init__(self, language):
        # Default language
        self.default = 'de'

        # Language codes
        self._codes = {
            'en':   Language.languages.EN,
            'de':   Language.languages.DE,
            'l337': Language.languages.l337,
            'kli':  Language.languages.KLI
        }

        # Default value of code
        self._default = self._codes[self.default]

        # Check if language is a language code
        if language in self._codes:
            self._language = self._codes[language]
        # Or if language is a direct reference to an enumerator item
        elif language in Language.languages:
            self._language = language
        # Otherwise set default
        else:
            self._language = self._default

    # Will be called if format applies to this class
    def __format__(self, key):
        return Language.translation[key][self._language]
