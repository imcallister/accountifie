"""Mini-framework for generating banded reports


A Report is initialised with a list of time identifiers for the columns,
and a list of bands running vertically.   A Band can be a piece of text,
or a row for an account, or a group of rows involving some kind of
drill-down.

When executed, a report returns a list of rows.  Each row is a dictionary
containing information to be formatted.   The possible entries are...

    id:  optional. logical identifier to be used in calculations or as
        a target for links
    type: required. 'text' or 'account'

    values:  required for non-text rows.
        the numbers to be drawn in each numeric cell.  Reports do a last minute
        pass over all the values formatting them as strings (accounting format)

    css_class:  the main typographic class we will use for its text

    indent:  default 0, 1 or 2 indent it further across to allow nesting

    line_above:  False or True or 0 or 1 or 2 (for double)
    line_below:  False or True or 0 or 1 or 2 (for double)




"""
from dateutil.parser import parse
import datetime


from .bands import TextBand, BasicBand
from .reportdef import ReportDef

import accountifie.query.query_manager
from accountifie.common.api import api_func
import accountifie.toolkit.utils as utils
import accountifie.reporting.rptutils as rptutils




ITEM = {'css_class': 'minor', 'indent': 1, 'type': 'group_item'}
MINOR_TOTAL = {'css_class': 'minor', 'indent': 0, 'type': 'group_total'}
MAJOR_TOTAL = {'css_class': 'major', 'indent': 0, 'type': 'group_total2'}
WARNING = {'css_class': 'warning', 'indent': 0, 'type': 'normal'}
ROW_FORMATS = {'item': ITEM, 'minor_total': MINOR_TOTAL, 'major_total': MAJOR_TOTAL, 'warning': WARNING}



class Report(object):
    def __init__(self, company_id, description='', date=None, title='', subtitle='', footer='', bands=[], columns=None, calc_type='as_of'):
        self.description = description
        self.title = title
        self.subtitle = subtitle
        self.footer = footer
        self.dflt_title = title
        self.company_id = company_id
        self.bands = bands
        self.columns = columns
        self.calc_type = calc_type
        self.column_order = None
        self.date = None
        self.path = None
        self.set_company()
        self.by_id = {}
        self.format = 'html'
        self.from_file = None
        


    def set_company(self):
        self.company_name = api_func('gl', 'company', self.company_id)['name']


    def set_columns(self, columns, column_order=None):
        self.columns = columns
        self.column_order = column_order

    def set_gl_strategy(self, gl_strategy):
        self.query_manager = accountifie.query.query_manager.QueryManager(gl_strategy=gl_strategy)

    
    def configure(self, config):
        qs_matches = rptutils.qs_parse(config)

        if len(qs_matches) == 0:
            raise ValueError('Unexpected query string: %s' % repr(config))
        elif len(qs_matches) > 1:
            raise ValueError('Unexpected query string: %s' % repr(config))
        else:
            config['config_type'] = qs_matches[0]


        if config['config_type'] == 'shortcut':
            config.pop('config_type')
            config.update(rptutils.parse_shortcut(config['col_tag']))


        if config['config_type'] == 'date':
            dt = rptutils.date_from_shortcut(config['date'])
            config.update(rptutils.config_fromdate(self.calc_type, self.description, dt))
        elif config['config_type'] == 'period':
            config.update(rptutils.config_fromperiod(self.calc_type, self.description, config))
        elif config['config_type'] == 'date_range':
            config.update(rptutils.config_fromdaterange(self.calc_type, self.description, config))
        
        self.title = config.get('title')
        self.set_columns(config['columns'], column_order=config.get('column_order'))
        self.date = config.get('date')
        self.path = config.get('path')
        return


    def get_row(self, df_row):
        if 'fmt_tag' in df_row:
            if df_row['fmt_tag'] == 'header':
                return TextBand(df_row['label'], css_class='normal').get_rows(self)
            else:
                values = [utils.entry(df_row[col_label]['text'] , link=df_row[col_label]['link']) for col_label in self.column_order]
                fmt_tag = df_row['fmt_tag']
                _css_class = ROW_FORMATS[fmt_tag]['css_class']
                _indent = ROW_FORMATS[fmt_tag]['indent']
                _type = ROW_FORMATS[fmt_tag]['type']
                return BasicBand(df_row['label'], css_class=_css_class, values=values, indent=_indent, type=_type).get_rows(self)
        else:
            values = [utils.entry(df_row[col_label]['text'] , link=df_row[col_label]['link']) for col_label in self.column_order]
            return BasicBand(df_row['label'], css_class=df_row['css_class'], values=values, \
                                indent=df_row['indent'], type=df_row['type']).get_rows(self)


    def _context(self):
        if self.column_order:
            column_titles = self.column_order
        else:
            column_titles = list(self.columns.keys())

        columns = [self.columns[x] for x in column_titles]
        context = dict(
                report=self,
                columns=columns,
                column_titles=column_titles,
                title=self.title,
                colcount=2+len(self.columns),
                italic_styles=['group_header', 'group_total'],
                no_space_before_styles=['group_item', 'group_total'],
                numeric_column_indices=list(range(2, len(self.columns) + 2)),
                )

        return context


    def html_report_context(self):
        return self._context()

    def pdf_report_context(self):
        return self._context()

    def get_content(self):
        "Returns list of dictionaries with info to format"
        self.by_id = {}
        content = []

        for band in self.bands:
            this_content = band.get_rows(self)
            content.extend(this_content)

            #allow next few rows to have access to wwhat we worked out
            if band.id and this_content:
                last_row = this_content[-1]
                #last row has values for maths
                if 'values' in last_row:
                    self.by_id[band.id] = last_row['values']
        #at the end, walk through formatting
        for row in content:
            if 'values' in row:
                if row['values'] != '':
                    row['values'] = [{'text': utils.fmt(c['text']), 'link': c['link']} if c != '' else '' for c in row['values']]
                    
        return content
