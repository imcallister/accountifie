/*invoke jeditable on our classes
Since this is a static javascript module and we need a CSRF token from somewhere, we
code it in the enclosing page and yank it out.
*/

'use sctrict';

function arrayOfArrays2arrayOfObjects(data, columns) {
    var _out = [];
    if (!Array.isArray(data[0]))
        return data;
	for (var i=0; i<data.length; i++) {
		var _tmpObj = {};
		for (var j=0; j<data[i].length; j++)
			_tmpObj[columns[j]]=data[i][j];
		_out.push(_tmpObj)
		}
	return _out
}


_EDITABLE_CANCEL_BTN =  '<button class="btn btn-sm btn-default" type="button">Cancel</button>';
_EDITABLE_SUBMIT_BTN = '<button class="btn btn-sm btn-primary" type="button">Save</button>';
_TEXT_PLACEHOLDER = '<a href="#">Click to edit</a>';
_CHOICES_PLACEHOLDER = 'Click to choose';
_PLAIN_PLACEHOLDER = _TEXT_PLACEHOLDER.replace(/(<([^>]+)>)/ig,""); 

function htmlDecode(value){ 
  return $('<div/>').html(value).text(); 
}
    
var reload_function = function(result){
	if ("undefined" !== typeof console)
		console.log("obsolete (?) reload_function :" + result);
};

//callback pattern for direct use with jeditable.
//This receives the value, which is json, and 'this' is
//the widget.
var editable_on_success = function(value, settings) {
	if (typeof value === 'string')
		value = JSON.parse(value);
	if (typeof this.loadData !== "undefined") 
		this.loadData(value);
	else
		$(this).text(value);
};

var show_cleaned_html = function(el, data) {
	var value = JSON.parse(el);
	$(this).html(value);
	
};

var show_cleaned_data = function(response, settings) {
	if (typeof response === "string")
		response = JSON.parse(response);
	if (typeof this.loadData !== "undefined") {
	   if (Array.isArray(response[0])) {
		   var _cols_array = [],
			   _cols = this.getSettings().columns;
		   if (_cols[0].hasOwnProperty('data')) {
			   for (var k=0; k<_cols.length; k++)
				   _cols_array.push(_cols[k].data);
			   response = arrayOfArrays2arrayOfObjects(response, _cols_array)
		   }
	   }
	   this.loadData(response)
	} else
		$(this).text(response);
	//support for RGF saving_feedback call.  
	if (window.hasOwnProperty('saving_feedback')) 
		saving_feedback.success(response);
};

function can_edit(jqElement) {
    return (jqElement.hasClass('can_edit') || jqElement.attr('can_edit') == 'True' || typeof jqElement.data('can_edit') !== "undefined" && jqElement.data('can_edit') == "True") 
}

$(document).ready(function() {

    $("[class*='edit_']").each(function(idx, elm){
		if (elm.type=="radio")
			return;
        var _this = $(elm);
        var _label = $('label[for="'+elm.id+'"]');
        var instance_name = _this.data('instance_name');
        if (typeof  instance_name !== 'undefined' && instance_name !== false) {
            var _new_id = _this.data('instance_name')+":"+_this.data('instance_id')+":"+_this.data('field_name');
            _this.attr('id', _new_id);
            _label.attr('for', _new_id);
            if (_this.hasClass('edit_htmlfield'))
                _this.html(_this.text());
        }
    });

    // Will be true if bootstrap is loaded, false otherwise
    var bootstrap_enabled = (typeof $().modal == 'function');




//grab the token
var csrf_token = $('#csrfmiddlewaretoken').text();
    
//jeditable custom input methods.
    //extend with a custom input type.  If we end up with 3-4 of these, we could
    //put them in our own jeditable module.
/* 
    $.editable.addInputType("datepicker", {
        element: function(settings, original) {
            var nd = new Date(original.revert);
            var input = $('<input type="date" value="'+nd.getFullYear()+'-'+(nd.getMonth()+1)+'-'+nd.getDate()+'"/' + ">");  //avoid inline JS eyesore in editor
            $(this).append(input);
            return (input);
        },
        plugin: function(settings, original) {
            settings.onblur = 'ignore';
			var datepicker = $.fn.datepicker.noConflict();
			$.fn.bootstrapDP = datepicker;  
            $(this).find('input').bootstrapDP({
                'autoclose': false,
                format: 'yyyy-mm-dd'// iso, comparable
            });
        }
    });    
*/
	
    $.editable.addInputType('bootstrap-generic', {
        element : function(settings, original) {
			var _type = "text";
			if ($(original).hasClass('edit_datefield'))
				_type="date";
			else if (original.className.indexOf('integer')>-1 || original.className.indexOf('float')>-1 )
				_type="number";
			else if ($(original).hasClass('edit_emailfield'))
				_type="email";
			else if ($(original).hasClass('edit_urlfield'))
				_type="url";
            var div = $('<input type="'+_type+'">');
			if ($(original).hasClass('form-control-static'))
				if (!$(original).hasClass('edit_choice'))
					div.attr('class','form-control');
            if (settings.width) 
                div.css('span', settings.span);
            $(this).append(div);
            return(div);
        }
    });

    
    // http://stackoverflow.com/questions/1597756/is-there-a-jquery-jeditable-multi-select-plugin
    $.editable.addInputType("multiselect", {
        element: function (settings, original) {
            var select = $('<select multiple="multiple" />');
			if ($(original).hasClass('form-control-static'))
				select.attr('class','form-control');
            if (settings.width != 'none') { select.width(settings.width); }
            if (settings.size) { select.attr('size', settings.size); }

            $(this).append(select);
            return (select);
        },
        content: function (data, settings, original) {
            /* If it is string assume it is json. */
            var json = data;
            if (String == data.constructor) {
                eval('var json = ' + data);
            } 
            for (var key in json) {
                if (!json.hasOwnProperty(key)) {
                    continue;
                }
                if ('selected' == key) {
                    continue;
                }
                var option = $('<option />').val(key).append(json[key]);
                $('select', this).append(option);
            }

            if ($(this).val() == json.selected ||
                                $(this).html() == $.trim(original.revert)) {
                $(this).attr('selected', 'selected');
            }

            /* Loop option again to set selected. IE needed this... */
            $('select', this).children().each(function () {
                if (json.selected) {
                    var option = $(this);
                    $.each(json.selected, function (index, value) {
                        if (option.val() == value) {
                            option.attr('selected', 'selected');
                        }
                    });
                } else
                    if (original.revert.indexOf($(this).html()) != -1)
                        $(this).attr('selected', 'selected');
            });
        }
    });


    $.editable.addInputType('tinymce-textarea', {
        element : function(settings, original) {
            var div = $('<input class="tiny-editable">');
            div.text(settings.content);
            if (settings.span) {
                div.attr('span', settings.span);
            }
            $(this).append(div);
            return(div);
        },
        plugin : function(settings, original) {
            //initialize tinymce
            var defaults = {
                menubar: false,
                statusbar: false,
                width: '100%',
                //inline: true,
                selector: ".tiny-editable",
                plugins: "code",         
                toolbar: "undo redo | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | code"
            };
            // override/update default config options
            if ($(original).data('mce-config'))
                for (var key in $(original).data('mce-config')) 
                    defaults[key] = $(original).data('mce-config')[key];
            tinymce.init(defaults);
        }
    });

    $.editable.addInputType('color-input', {
        element : function(settings, original) {
            var div = $('<input type="text">');
            $(this).append(div);
            return(div);
        },
        plugin : function(settings, original) {
            if (settings.colors) {
                $('input', this).colorPicker(settings.colors);
            }
            else {
                $('input', this).colorPicker();
            }
        }
    });
/*
    $.editable.addInputType('typeahead-select', {
        element : function(settings, original) {
            var div = $('<input class="typeahead form-control" type="text" placeholder="Start typing">');
            $(this).append(div);
            return(div);
        },
        plugin : function(settings, original) {
              hint: true,
              highlight: true,
              minLength: 1
            },
            {
              name: $(this).attr('name'),
              displayKey: 'value',
              source: substringMatcher(fundnames)
            });
        }
    });
  */   
// jeditablilise elements
    var _JEDITABLE_SETTINGS = { 
        call_count: 0,
        save_count: 0,
        error_count: 0,
        submitdata : { csrfmiddlewaretoken : csrf_token},
        callback: editable_on_success,
        /*onsubmit: function(settings, td) {

            //default is no validation, log what we're about to do,
            //then allow save to go ahead.
            var input = $(td).find('input');
            var value = input.val();
            var id = $(td).attr('id');
            editable_before_send(id, value);
            return td;
        },*/
        onerror: function(settings, original, xhr) {

            var _errs = '',
                _out = '',
                _i=0;
            //Problem.  if a network error, we can't parse the json.
            if (xhr.status)
                try {
                    _errs = JSON.parse(xhr.responseText);
                }
                catch(err) {
                    console.log('erroring in editable.js');
                    _errs = "Bad Request";
                }


            if (typeof _errs == "string")
                showalert(_errs, 'danger');
            else {
                for (_i; _i<_errs.length; _i++) {
                    // get the label
                    var _la = _errs[_i][0];
                    var _label = $('label[for$=":'+ _la +'"]');
                    // if there is no <label> there should be s <span> before the actual field
                    if (!_label.length)
                        _label = $('[data-field_name="'+ _la +'"]').prev();
                    if (!_label.length)
                        _label = _la;
                    else
                        _label = _label.text();
                    _out += "<p>"+_label+": <b>"+_errs[_i][1]+"</b></p>";
                }
                showalert(_out, 'danger');
            }
            
            /* may not be right at all */
            
            //editable_on_failure.apply(original, [settings,  xhr]);
            original.reset();
        },
        cancel: _EDITABLE_CANCEL_BTN,
        submit: _EDITABLE_SUBMIT_BTN,
        onblur: 'cancel',
        type: 'text'
    };
    //the 'bog standard' jeditable invocation
    $('.edit').editable('/api/jeditable_save/', _JEDITABLE_SETTINGS);
    
    $('.edit_booleanfield').each(function(index, element) {
        //custom ajax, not through jeditable
        var jqelement = $(element);
		if (element.tagName.toUpperCase() == 'INPUT' || typeof jqelement.iCheck !== "undefined") {
			jqelement.iCheck({
				checkboxClass: 'icheckbox_flat-blue',
				}).iCheck('disable');
			if (can_edit(jqelement)) {
				jqelement.iCheck('enable');
				jqelement.on('ifToggled', function(event){
					//within betterforms, $(this) seems to be the input.
					//with ordinary tags, it seems to be a child.
					//handle both.
					if ($(this).prop("tagName") == 'INPUT')
						var inputbox = $(this);
					else
						var inputbox = $(this).find("input");

					var bool_value = inputbox.is(':checked');
					var data = {id: jqelement.context.id, value: bool_value};
					//editable_before_send(data.id, data.value);
					$.post('/api/jeditable_save/', data);
				});   
			}
		} else 
			jqelement.on('change','input[type="checkbox"]', function(ev){
				var data = {id: jqelement.attr('id'), 
					value: $(this).is(':checked')
				};
				$.post('/api/jeditable_save/', data);
			})
    });
    
    $('.edit_manytomanyfield').each(function(index, element) {
        //custom ajax, not through jeditable
        element = $(element);
        var related_class_name = element.context.id.split(':')[2],
            _data = {};
        element.on('chosen:ready', function(evt, obj) {
            var _container = $(obj.chosen.container),
            _values = [];
            $(this).find(':selected').each(function(idx, elm){
                _values.push($(elm).text());
				});
			if (can_edit(element)) {
				if (!_values.length)
					_values = ['Click to choose ...'];
				_container.after('<a id="'+_container.attr('id')+'_span"><span>' + _values.join('</span> <span>')+'</span></a>');
				var _span = _container.next();
				$(_span).click(function(evt) {
					$(this).hide();
					_container.show();
				});
			} else { 
				if (!_values.length)
					_values = ['[ ]'];
				_container.after('<span>' + _values.join('</span> <span>')+'</span>');
			};
			_container.hide();
        });
        element.chosen({
            allow_single_deselect: true,
            inherit_select_classes: true,
            placeholder_text_multiple: 'Click to select ' + related_class_name,
            width: "90%",
            }).on('change', function(evt, params) {
               if(params.selected) {
                    _data = {id: element.context.id, value: params.selected + ':1'};
                    $.post('/api/jeditable_save_manytomany/',
                            _data,
                            reload_function
                        );
               }
               if (params.deselected) {
                    _data = {id: element.context.id, value: params.deselected + ':0'};
                    $.post('/api/jeditable_save_manytomany/',
                            _data,
                            reload_function
                        );
                }
            }).on('chosen:hiding_dropdown', function(evt, obj) {
                    var _container = $(obj.chosen.container),
                        _span = _container.next(),
                        _values = [];
                    $(this).find(':selected').each(function(idx, elm){
                        _values.push($(elm).text());
                    });
                    if (!_values.length)
                        _values = ['Click to choose ...'];
                    _container.hide();
                    _span.show();
                    _span.html('<span>'+_values.join('</span> <span>')+'</span>');
           });
   }); 


$('.edit_foreignkey, .edit_choice:not([type="radio"])').each(function(idx, elm) {
    var _data = {};
	if (!elm.hasOwnProperty('options'))
		return;
	$.each(elm.options, function(ix, op) {
		_data[op.value]=op.text;
	});
    // convert to plain <span> and then 'editibilise'
    elm = convert_to(elm, 'span');
    var post_url = '/api/jeditable_save/';
    if ($(elm).hasClass('edit_foreignkey'))
        post_url = '/api/jeditable_save_relational/';
	if (can_edit($(elm))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            data: _data, 
            type: 'select',
			placeholder : '<span class="placeholder">'+_CHOICES_PLACEHOLDER+'</span>',
            tooltip: 'choose ...',
            cssclass: 'form-inline',
            onblur : 'ignore',
            });
        $(elm).editable(post_url, _jsettings);
    }   
    if ($(elm).hasClass('edit_foreignkey'))
        $(elm).text(_data[$(elm).text()]);
});
    
$('.edit_htmlfield').each(function(idx, elm){
    elm = convert_to(elm, 'div');
    var value = $(elm).text();
    var max_length = $(this).attr('max_length');
	if (can_edit($(elm))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            menubar: false,
            type : 'tinymce-textarea',
            onblur : 'ignore',
            content: value,
            max_length: max_length,
            //indicator : '<img src="img/indicator.gif">',
            tooltip   : 'Click to edit...',
            callback: show_cleaned_html,
            onsubmit: function(settings, td) {
                    //get the content of the tinymce editor and pass it back to the hidden form input from Jeditable
                    var edited = tinymce.activeEditor.getContent();
                    var hidden_input = $(elm).find("input");
                    hidden_input.val(edited);
                    //editable_before_send($(td).attr("id"), edited);
                    return true;
                }
        });
        $(elm).editable('/api/jeditable_save/', _jsettings);
    }
});
    
$('.edit_textfield').each(function(index, item){
    item = convert_to(item, 'div');
    var value = $(item).text();
    var max_length = $(this).attr('max_length');
	if (can_edit($(item))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            data: function(value, settings) {
                    return htmlDecode(value);
                  },
            type: 'textarea',
            width: 400,
            height: 160,
            onblur : 'ignore',
            placeholder : '<span class="placeholder">'+_TEXT_PLACEHOLDER+'</span>',
            tooltip   : _PLAIN_PLACEHOLDER,
            onsubmit: function(settings, td) {
                    var max_length = parseInt($(td).attr('max_length'));
                    var input = $(td).find('textarea');
                    var original = input.val();
                    if (original.length < max_length || !max_length) {
                       return true;
                    } else {
                       input.css('background-color','#c00').css('color','#fff');
                      return false;
                    }
                }
            });
        $(item).editable('/api/jeditable_save/', _jsettings);
    }
});

$('.edit_charfield, .edit_urlfield, .edit_emailfield').each(function(idx, item){
    var value = $(this).text(),
		max_length = $(this).attr('max_length');
    item = convert_to(item, 'div');
    $(item).data('original', value);
	if (can_edit($(item))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            onblur: 'ignore',
            placeholder : '<span class="placeholder">'+_TEXT_PLACEHOLDER+'</span>',
            tooltip: _PLAIN_PLACEHOLDER,
            data: function (value, settings) {
                //update_ajax_status('Ready');
                return htmlDecode(value);
            },
			type: 'bootstrap-generic',
            onsubmit: function(settings, td) {
                var max_length = parseInt($(td).attr('maxlength'));
                var input = $(td).find('input');
                var original = input.val();
                var id = $(td).attr('id');
                if (original.length <= max_length || !max_length) {
                    //editable_before_send(id, original);
                    return true;
                } else {
                    input.css('background-color','#c00').css('color','#fff');
                    return false;
                }
                }
            });
        $(item).editable('/api/jeditable_save/', _jsettings);
    }
});

$('.edit_floatfield, .edit_integerfield, .edit_positiveintegerfield').each(function(idx, elm){
    elm = convert_to(elm, 'div');
	if (can_edit($(elm))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            type: 'bootstrap-generic',
            //indicator : '<img src="img/indicator.gif">',
            placeholder : '<span class="placeholder">'+_TEXT_PLACEHOLDER+'</span>',
            tooltip   : _PLAIN_PLACEHOLDER, 
            onsubmit: function(settings, td) {
                        var input = $(td).find('input');
                        var original = parseFloat(input.val());
                if ($(elm).hasClass('edit_integerfield')) {
                            if (!isNaN(parseInt(original)) && original % 1 === 0)
                    return true;
                } else  
                    if (!isNaN(original)) {
                        //parseFloat ignore trailing characters that are not numbers
                        //but we need to filter them out before submitting
                        input.val(original.toString());
                        return true;
                    }
                    input.css('background-color','#c00').css('color','#fff');
                    return false;
            }
        });
        $(elm).editable('/api/jeditable_save/', _jsettings);
    }
});
    
    
$('.edit_choice.rgbcolorfield').each( function(idx, elm) {
    //this one has been provided with a 'choices' option in the model and is therefore limited in the colorchoices
    var choices = $(elm).attr('choices');
	if (can_edit($(elm))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            type : 'color-input',
            colors: choices,
            onblur : 'ignore',
        });
        $(elm).editable('/api/jeditable_save/', _jsettings);
    }
});
    

$('.edit_rgbcolorfield').each( function(idx, elm) {
    //this one is not limited in the color choices
	if (can_edit($(elm))) {
        $(elm).css('width', '40px');
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            type : 'color-input',
            onblur : 'ignore',
        });
        $(elm).editable('/api/jeditable_save/', _jsettings);
    }
});
    
    // date picker 
    // http://anotherjsl.blogspot.co.uk/2012/10/jeditable-custom-type-using-bootstrap.html
$('.edit_datefield').each(function(idx, elm){
    elm = convert_to(elm, 'div');
	if (can_edit($(elm))) {
        var _jsettings = {};
        $.extend(true, _jsettings, _JEDITABLE_SETTINGS, {
            data: function (value, settings) {
                //update_ajax_status('Ready');
                if (Date.parse(value))
                    return value;
                else 
                    return '';
            },
            type: 'bootstrap-generic',
            indicator: 'Saving...',
            placeholder: _TEXT_PLACEHOLDER,
            //style: 'display: inline;',
            //width: 'none',
            onblur : 'ignore',
        });
        $(elm).editable('/api/jeditable_save/', _jsettings);
    }
});


//put back on 8 September because Quilter are still using it a lot! 
//Took from revision 956, last working one for them

$('.edit_jsonfield').each(function(){
    var id = $(this).attr('id'),
        name = $(this).attr('field_name'),
        elm = $('<div id="'+ name + '_ht"></div>'),
        headers;
    if (typeof name == 'undefined')
        name = $(this).attr('name');
    elm.insertBefore(this);
    var _initial_data = window['jeditable_' + name];
    if (typeof _initial_data == 'undefined') {
        _initial_data = JSON.parse($(this).val());
        _headers = true;
    } else
        _headers = window['jeditable_' + $(this).attr('field_name') + '_headers'];
    var has_changed = false,
        _that = $(this),
        _widths = [],
        _charWidth = Math.round(2*parseInt($(this).css('font-size'))/3),
        _strWidth = 0;
    // set column widths by looking at data
    for (var i=0; i<_initial_data.length; i++)
        for (var j=0;j<_initial_data.length; j++) {
            if (typeof _initial_data[i][j] == 'string') {
                _strWidth = _initial_data[i][j].length*_charWidth;
                if (i==0)
                   _widths.push(_strWidth);
                else {
                    if (_strWidth>_widths[j])
                        _widths[j]=_strWidth;
                }
            } else {
                if (i==0)
                   _widths.push(50);
                else
                   _widths[j]=50;
            }
        };
    // get column width by looking at headers
    if (_widths.length==0 && _headers.length>0)
        for (var k=0;k<_headers.length; k++)
            _widths[k]=_headers[k].length*_charWidth;
    else
        if (_headers.length>0) {
            for (var k=0;k<_headers.length; k++) {
                _strWidth = _headers[k].length*_charWidth;
                if (_strWidth > _widths[k])
                    _widths[k]=_strWidth;
            }
        };
    if (_widths.length==0)
        _widths = null;

    elm.handsontable({
        colHeaders: _headers,
        colWidths: _widths,
        rowHeaders: true,
        removeRowPlugin: true,
        data: _initial_data,
        onChange: function (change, source) { 
            if (!change) {
                return;
            }
            _initial_data[change[0][0]][change[1]] = change[3];
            if (!has_changed){
                has_changed = true;
                var save_id = _that.attr('field_name') + 'save_changes',
                    cancel_id =  _that.attr('field_name') + 'cancel_changes',
                    __that = this;
                this.rootElement.after('<button class="btn btn-primary btn-xs" id=' + save_id + '>save changes</button>');
                this.rootElement.after('<button class="btn btn-default btn-xs" id=' + cancel_id + '>cancel changes</button>');
                $('#' + save_id).click(function(){
                    var new_data = {};
                    new_data.value = JSON.stringify(_initial_data);
                    new_data.id = id;
                    $.ajax({
                        url: "/api/jeditable_save/",
                        dataType: "json",
                        type: "POST",
                        data: new_data//, //contains changed cells' data
                    }).done(function(){
                       __that.clearUndo();
                    });
                   $('#' + save_id).add($('#' + cancel_id)).remove();
                   has_changed = false;
                });

                $('#' + cancel_id).click(function(evt){
                    evt.stopPropagation();
                    while (__that.isUndoAvailable())
                        __that.undo();
                    window.setTimeout(function(sid, cid){
                        $('#' + sid).add($('#' + cid)).remove();
                    }, 250, save_id, cancel_id);
                    return false;
                });
            }
        }
    });
    var add_id = name + 'add_row';
    var remove_id = name + 'remove_row';
    elm.after('<button class="btn btn-default btn-xs" id=' + add_id + '>Append row</button>');
    elm.after('<br /><button class="btn btn-default btn-xs" id=' + remove_id + '>Remove last row</button>');
    var _hot = elm.handsontable('getInstance');
    $('#' + add_id).click(function(){
        _hot.alter('insert_row');
    });
    $('#' + remove_id).click(function(){
        _hot.alter('remove_row');
    });
    $(this).remove();
});


/* gridfield.js should have run by now */
$('div[id$="_ht"]').each(function(idx){
    var _name = this.id.substr(0, this.id.length-3),
		_HOT = $(this).handsontable('getInstance'),
        cancel_btn = $(_EDITABLE_CANCEL_BTN), 
        save_btn = $(_EDITABLE_SUBMIT_BTN),
		_initial_data = window[_name + '_jeditable'];
    cancel_btn.attr('id', _name + '_cancel_changes');
    save_btn.attr('id', _name +'_save_changes');

    var _buttons = cancel_btn.add(save_btn);
    _buttons.css({
        margin:'.3em .3em 0 0',
        visibility: 'hidden'
    });
    var _id = $('input[name="'+ _name +'"]').attr('id');
    // events
    save_btn.click(function(evt){
        var _data = $.extend(true, [], _HOT.getData());
        // discard empty trailing rows
        //for (var p=0; p<_initial_data.settings.minSpareRows; p++)
        //    _data.pop()
        
        $.ajax({
            url: "/api/jeditable_save_json/",
            dataType: "json",
            type: "POST",
            data: {id: _id, //_obj_model+':'+_obj_id+':'+ _name, 
                value: JSON.stringify(_data)
                }
        }).done(function(data, textStatus, jqXHR) {
            show_cleaned_data.apply(_HOT, [JSON.stringify(data), jqXHR]);
        }).fail(function(jqXHR, status, errorThrown){
            showalert("<b>"+status+"</b><p>"+errorThrown+"</p>", 'danger');
        });
        _HOT.clearUndo();
    });

    cancel_btn.click(function(evt){
        evt.stopPropagation();
        while (_HOT.isUndoAvailable())
            _HOT.undo();
        // "undo" will apparently trigger the same events the previous steps have triggered
        // namely, a row removal (which in turn triggers the visibility of these buttons)
        window.setTimeout(function(){_buttons.css('visibility','hidden');}, 250);
        return false;
    });

    _buttons.click(function(evt){
        _buttons.css('visibility','hidden');
    });

    var _settings_to_update = {
        afterChange: function(change, source) {
                if (!change || source=="dont_care")
                    return;
				if ("undefined" !== typeof(console))
					console.log("[afterChange] " + change + " source=" + source);
                if (cancel_btn.css('visibility')=='hidden')
                    cancel_btn.css('visibility','visible');
                
                if (hot_is_valid(this.container))
                    save_btn.css('visibility', 'visible');
                else
                    save_btn.css('visibility', 'hidden');

                if (_initial_data.totals && typeof _totals_container !== 'undefined') {
                    var _HOT_totals = _totals_container.handsontable('getInstance');
                    _HOT_totals.updateSettings({
                        data: grid_calc_totals(_container, _initial_data.totals),
                        colWidths: get_widths(_HOT)
                    });
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
				} else                                
					for (var i=0; i<amount; i++) 
						if (!this.isEmptyRow(row_idx+i)) {
							if (cancel_btn.css('visibility')=='hidden')
								cancel_btn.css('visibility','visible');
							if (hot_is_valid(this.container))
								save_btn.css('visibility', 'visible');
							else
								save_btn.css('visibility', 'hidden');
							break;
						}
			}
        };
    
    _HOT.updateSettings(_settings_to_update);
    $(this).after(_buttons)

});


var form = $("input[class*='edit_']").closest('form');
form.find('input[type="submit"]').add(form.find('button[type="submit"]')).remove();
});

