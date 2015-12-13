/* 
 * This module should precede editable.js
 */

// tentative handsontable rendered for unsaved cells
var grid_dirtyRenderer = function(instance, td, row, col, prop, value, cellProperties) {
    // TODO: apply formatting to cells which have changed and are not yet saved
    // and clear upon saving
    Handsontable.renderers.TextRenderer.apply(this, arguments);
    $(td).css({background: '#f99'});
};


var grid_greyRenderer = function(instance, td, row, col, prop, value, cellProperties) {
    // TODO: apply formatting to cells which have changed and are not yet saved
    // and clear upon saving
    Handsontable.renderers.TextRenderer.apply(this, arguments);
    $(td).css({background: '#ccc'});
};

//there is a validateCells method, but it's not clear
//what signature the callback takes.  This is simple, counts the red cells.
function hot_is_valid(container) {
	return container.find(".htInvalid").length === 0;
}

Array.prototype.clean = function(deleteValue) {
    for (var i = 0; i < this.length; i++) 
        if (this[i] == deleteValue)        
            this.splice(i--, 1) ;
    return this;
};

function array_accum(prevVal, currVal) {
    return currVal+prevVal;
}

function grid_calc_totals(src, _totals){
    // expects a handsontable container and an aggregates defintion array
    if (typeof _totals === 'undefined' || typeof src === 'undefined')
        return [];
    var _HOT_totals = $('#' + src.attr('id') + '_totals').handsontable('getInstance'),
        _HOT = src.handsontable('getInstance'),
        _results = [], i=0;
    for (i; i<_totals.length; i++) {
        var _func = _totals[i],
            _func_result = '--';
        var _column_data = _HOT.getDataAtCol(i).clean('').clean(null).clean(undefined);
        if (_column_data.length)
            switch (_func) {
                case 'count': _func_result = _column_data.length; break;
                case 'sum': _func_result = _column_data.map(parseFloat).reduce(array_accum); break;
                case 'avg': _func_result = _column_data.map(parseFloat).reduce(array_accum)/_column_data.length;
            }
        _results.push(_func_result);
    }
    return [_results];
}

function get_widths(hot) {
	var _widths = [], j=0;
	for (j; j < hot.countCols(); j++)
		_widths.push(hot.getColWidth(j));
	return _widths;
}

$(document).ready(function() {

	$('textarea.gridfield').add('textarea.resultsfield').each(function(idx){
		var _name = this.name,
			_initial_data = window[_name + '_jeditable'],
			_container = $("<div id='" + _name + "_ht'></div>");
		if ($(this).hasClass('resultsfield'))
			_container = $("<div id='" + _name + "_ht' style='height: 300px; overflow: auto'></div>");
		if ($(this).data('choices'))
			_container.data('choices',$(this).data('choices'));
		_container.insertBefore(this);
		_container.handsontable(_initial_data.settings);

		var _HOT = _container.handsontable('getInstance');
		var _updated_columns = _HOT.getSettings().columns,
			_is_columns_updated = false;

		if (_initial_data.hasOwnProperty('autofields') && _initial_data.autofields!== null) { 
			for (var h=0; h<_updated_columns.length; h++)
				if (_updated_columns[h].hasOwnProperty('auto') && [null, false].indexOf(_updated_columns.auto)<0)
					if (!_updated_columns.hasOwnProperty('renderer')) {
						_updated_columns.renderer = grid_greyRenderer;
						_is_columns_updated=true;
					}
		}



		var _obj_model = $(this).data('instance_name'),
			_obj_id = $(this).data('instance_id');

		var _settings_to_update = {
			afterChange: function(change, source) {
					if (!change || source=="dont_care")
						return;
					var updated_data = $.extend([],this.getData()),
						_sets = this.getSettings(),
						_spare_rows=0;
					if (!this.hasOwnProperty('fieldname'))
						this.fieldname = this.container.parent()[0].id.substr(0, this.container.parent()[0].id.length-3)
					if (_sets.hasOwnProperty('minSpareRows'))
						_spare_rows = _sets.minSpareRows;
					else
						_spare_rows = this.countEmptyRows();
					for (var k=0; k< _spare_rows; k++)
						 updated_data.pop(_spare_rows);
					$('[name="'+this.fieldname+'"]').val(JSON.stringify(updated_data))

					if (_initial_data.totals && typeof _totals_container !== 'undefined') {
						var _HOT_totals = _totals_container.handsontable('getInstance');
						_HOT_totals.updateSettings({
							data: grid_calc_totals(_container, _initial_data.totals),
							colWidths: get_widths(_HOT)
						});
					}
				},
			beforeValidate: function(value, row, prop, source) {
					// unformat first
					var idx;
					console.log('validate');
					if (source != 'dont_care') {
						var cols = this.getSettings().columns,
							col = this.propToCol(prop),
							column_spec = cols[col];
						if (column_spec.hasOwnProperty('type') && column_spec.type=='numeric') {
							if (!String(value).length)
								value=null;
							else if (null !== value) {
								var _numbers = String(value).replace(/[^0-9]*/g,'');
								_numbers = parseFloat(_numbers);
								if (!isNaN(_numbers)) {
									var unformatted = numeral().unformat(String(value));
									if (unformatted === 0) {
										if (_numbers === 0)
											value=0;
									} else
										value = parseFloat(unformatted);
								}
							}
						}
					}
					return value;
				},
			beforeChange: function(changed, source) {
					// unformat first
					if (source != 'dont_care')
					{
					console.log(changed[0][1]);
					var idx, col, value, column_spec;

					var cols = this.getSettings().columns;
					for (idx=0; idx < changed.length; idx++) {
						col = changed[idx][1]; 
						// this can be either an index or a name
						if (typeof(col)==="string") 
							col = this.propToCol(col);
						if ("undefined" !== typeof cols) { // ready for boneless grids 
							column_spec = cols[col];
							if (column_spec.hasOwnProperty('type') && column_spec.type=='numeric') {
								value = changed[idx][3];
								if (!String(value).length)
									value=null;
								else if (null !== value) {
									var _numbers = String(value).replace(/[^0-9]*/g,'');
									_numbers = parseFloat(_numbers);
									if (!isNaN(_numbers)) {
										var unformatted = numeral().unformat(String(value));
										if (unformatted === 0) {
											if (_numbers === 0)
												value=0;
										} else
											value = parseFloat(unformatted);
										}
									}
								changed[idx][3]=value
							}
						}
					}
					// unformat date/time
					var chg=changed[0];
					console.log("[beforeChange] " + changed + " " + source);
					var _choices = this.rootElement.data('choices');
					if (_choices)
						var _cols = this.getSettings().columns;
					if (_initial_data.hasOwnProperty('time_columns') && _initial_data.time_columns.length>0 && [false, null, ''].indexOf(_initial_data.time_columns)<0)
						var _has_time = true;
					else
						var _has_time = false;
					var _changes = [];
					for (var i=0, len = changed.length; i<len; i++, chg=i<len?changed[i]:null) {
						if (_has_time && _initial_data.time_columns.indexOf(chg[1])>-1)
						   chg[3] = numeral().unformat(chg[3], '00:00:00.000');
						if (_choices) {
							var _referrer = false;
							for (var jj=0; jj<_cols.length; jj++)
								if (_cols[jj].hasOwnProperty('source')) {
									_referrer = _cols[jj].data.toLowerCase();
									break;
								}
							if (chg[1]==_referrer) {
								var _row = _choices[chg[3]];
								for (_r in _row)
									_changes.push([parseInt(chg[0]), _r, _row[_r]]);
							}
						}
					}
					if (_changes.length>0)
						this.setDataAtRowProp(_changes, 'dont_care')    
				}
				},
			beforeRemoveRow : function (row_idx, amount) {
					if ('undefined'=== typeof(amount))
						  amount = 0;
					if (!_initial_data.hasOwnProperty('removeEmptyRows') || _initial_data.removeEmptyRows===false) {
						var _nCols = this.countCols(),
							_last_row = row_idx+amount,
							_empties = [];
						for (var _i=row_idx; _i<(row_idx+amount);_i++)
								for (var _j=0; _j<_nCols; _j++) 
									_empties.push([_i,_j,'']);
						this.setDataAtCell(_empties, 'empty');
						// don't delete the row(s)
						return false;
					}
				}
			};
		if (_is_columns_updated) {
			_settings_to_update.columns = _updated_columns;
			_settings_to_update.afterCreateRow = function(index, amount) {
					for (var j=0; j<_initial_data.autofields.length; j++) {
						var _current_value = this.getDataAtRowProp(index-1, _initial_data.autofields[j]);
						if (_current_value === '' || _current_value === null)
							this.setDataAtRowProp(index-1, _initial_data.autofields[j], index);
					}
			 }
		 }

		if ($(this).hasClass('resultsfield')) {
			function cells(row, col, prop) {
				var _table = this.instance,
					_val = _table.getDataAtRowProp(row,prop),
					_rowIsEmpty = _table.getDataAtRow(row).reduce(function(n,val){
							return n && (val == null)
						}, true);
				if (_rowIsEmpty)
					if (row < (_table.countRows()-1))
						return {renderer: grid_dirtyRenderer};
				if (prop == "number") {
					if (_val === null)  // check if row is not empty
						return {renderer: grid_dirtyRenderer};
					var _colData = _table.getDataAtProp(prop).map(function(x){
							return parseInt(x)
						}),
						_count = _colData.reduce(function(n, val) {
							return n + (val === _val);
						}, 0);
					if (_count>1) 
						return {renderer: grid_dirtyRenderer};
					else
						return {}
				} else
					if (prop == "name" && (_val === null || _val == "")
							&& _table.getDataAtRowProp(row, "number") !== null)
						return {renderer: grid_dirtyRenderer};
					else
						return {}
			}
			_settings_to_update.cells = cells;
		}
		
		_HOT.updateSettings(_settings_to_update);

		if (_initial_data.totals) {
			var _totals_container = $("<div id='" + _name + "_ht_totals'></div>");
			_totals_container.insertBefore(this);

			// requires settings.columns: will aggregate on text type columns
			var _totals_columns = $.extend(true, [], _initial_data.settings.columns),
				_tmp_totals = $.extend(true, [], _initial_data.totals),
				_row_header = _initial_data.settings.rowHeaders ? ['totals']: false;
			for (var j=0; j<_totals_columns.length; j++) {
				if (typeof _tmp_totals[j] == "undefined")
					_tmp_totals.push(null);
				if (_tmp_totals[j] == null)
					_totals_columns[j] = {'type': 'text'}; 
				else
				   	if (_tmp_totals[j] == 'count')
						_totals_columns[j] = {'type': 'numeric', format: '0'}; 
					else if (_totals_columns[j].hasOwnProperty('data'))
						delete _totals_columns[j].data;
			}
				
			_totals_container.handsontable({
				data: grid_calc_totals(_container, _initial_data.totals),
				rowHeaders: _row_header,
				readOnly: true,
				minCols: _HOT.countCols(),
				colWidths: get_widths(_HOT),
				columns: _totals_columns
			});
		}
	var _hidden = $('<input type="hidden" name="'+ this.name + '" class="'+ this.className +'" id="'+ this.id +'">');
	_hidden.val($(this).text())
	if (typeof $(this).data('can_edit') !== "undefined") {
		_hidden.data('can_edit', $(this).data('can_edit'));
		_hidden.data('field_name', $(this).data('field_name'));
		_hidden.data('instance_id', $(this).data('instance_id'));
		_hidden.data('instance_name', $(this).data('instance_name'));
	}
	_hidden.insertBefore(this);
	$(this).remove();
	});

	if ($('.htContextMenu').length)
		$('.htContextMenu').css('font-size', '.8em');
});
