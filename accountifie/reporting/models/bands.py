

class Band(object):
    "Specifies what to fetch and create"
    def __init__(self, id=None, indent=0, group=None):
        self.id = id
        self.indent = indent
        self.group = group

    def get_rows(self, report):
        "Generate one or more rows. Base class does one row"

        row = dict(id=self.id, indent=self.indent)
        row['text'] = "Dummy report band"
        values = []
        for colspec in report.columns:
            values.append(Decimal('0.00'))
            row['values'] = values
        rows = [row]
        return rows


class TextBand(Band):
    """"Just inserts a slice of text.

    Suggested classes:
        h1 = bigger bolder heading
        h2 = slightly less prominent heading
        None, plain = ordinary text suitable for a paragraph
        small = smaller text for notes

        major = matches text of major band row
        minor = matches minor band row

    Any indent level will increase the default indent
    """
    def __init__(self, text, css_class=None, indent = 0, group=None):
        self.text = text
        self.id = None
        self.css_class = css_class
        self.indent = indent
        self.group = group

    def get_rows(self, report):
        #just one row
        return [dict(
            id=self.id,
            group=self.group,
            text=self.text, 
            css_class=self.css_class, 
            indent=self.indent, 
            type='text', 
            values=[''] * len(report.columns)
            )]
        #don't bother with the cells, the format layer can handle missing ones.

class BasicBand(object):

    def __init__(self, text, id=None, css_class=None, indent = 0, line_above=0, line_below=0, group=None, values=None, num_cols=1, type='basic'):
        self.text = text
        self.id = id
        self.group = group
        self.css_class = css_class
        self.indent = indent
        self.line_above=line_above
        self.line_below = line_below
        self.type = type
        if values:
            self.values = values
        else:
            self.values = [{'text': '', 'link':''} for x in range(num_cols)]

    def get_rows(self, num_cols=1):
        #just one row
        return [dict(
            id=self.id,
            text=self.text,
            css_class=self.css_class,
            indent=self.indent,
            type=self.type,
            values=self.values
            )]
