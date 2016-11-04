

def column_chart(title="Column Chart", y_label="y-Axis", data_labels=False, colored_cols=False):
    chart_data = {
        'chart': {'type': 'column'},
        'yAxis': {},
        'plotOptions': {'series': {}},
        'credits': {'enabled': False}
        }

    chart_data['title'] = title
    chart_data['yAxis']['title'] = {'text': y_label}
    if data_labels is True:
        chart_data['plotOptions']['series']['dataLabels'] = {'enabled': True}
    if colored_cols is True: 
        chart_data['plotOptions']['series']['colorByPoint'] = True

    return chart_data

def line_chart(title="Column Chart", y_label="y-Axis", data_labels=False):
    chart_data = {
        'chart': {'type': 'line'},
        'yAxis': {},
        'plotOptions': {'series': {}},
        'credits': {'enabled': False}
        }

    chart_data['title'] = title
    chart_data['yAxis']['title'] = {'text': y_label}
    if data_labels is True:
        chart_data['plotOptions']['series']['dataLabels'] = {'enabled': True}
    
    return chart_data
