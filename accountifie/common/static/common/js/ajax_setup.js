function showalert(message,alerttype) {
	if (typeof alerttype !== 'undefined')
	alerttype=' alert-'+alerttype;
	else
		alerttype='alert-warning';
	$('#alert_placeholder').append('<div id="alertdiv" class="alert' +  alerttype + '"><a class="close" aria-hidden="true" type="button"  data-dismiss="alert">×</a><span>'+message.replace("'","\'")+'</span></div>');
	setTimeout(function() { 
	  if ($("#alertdiv").length)
	$("#alertdiv").remove();
	}, 5000);
  };

/*
 * convert any `src_elm` input element to an element of type `new_tag`
 * `src_elm` is most likely an <input> or <textarea> element
 * 'new_tag' is most-likely 'div' or 'a'
 * This is used both by editable.js and gridfield
 */ 

var convert_to = function(src_elm, new_tag) {
	if (src_elm instanceof jQuery)
		src_elm = src_elm[0];
	var _html = src_elm.outerHTML;
	var _tag = src_elm.tagName.toLowerCase();
	_html = _html.replace('<'+src_elm.tagName, '<'+new_tag);
	_html = _html.replace('<'+_tag, '<'+new_tag);
	// closing tag
	if (_tag === 'textarea' || _tag === 'select') {
		_html = _html.replace('</'+src_elm.tagName+'>', '</'+new_tag+'>');
		_html = _html.replace('</'+_tag+'>', '</'+new_tag+'>');
	} else
		if (_html.indexOf('</'+new_tag+'>')<0)
			_html+='</'+new_tag+'>';
	//ie8 related
	if (_html.indexOf('<')>0) 
		_html = _html.substr(_html.indexOf('<'));
	var _new_el = $(_html);
	if (_new_el.find('option').length)
		_new_el.find('option').remove();
	if (new_tag == 'a')
		_new_el.attr('href','#');
	if (_tag=='select')
		_new_el.attr('value', $(src_elm).find('option:selected').text());
	if (_new_el.attr('value')) {
		_new_el.text(_new_el.attr('value'));
		_new_el.removeAttr('value');
	}
	// discard possible options
	if (_new_el.children('option')) {
		// and set text to selected option
		var _selected = _new_el.children('option:selected');
		var _selected_text = null;
		if (_selected.length)
			_selected_text = _selected.text();
		_new_el.children('option').remove();
		if (_selected_text !== null)
			_new_el.text(_selected_text);
	}
	// bootstrap?
	if (_new_el.hasClass('form-control')) {
		_new_el.addClass('form-control-static');
		_new_el.removeClass('form-control');
	}
	$(src_elm).before(_new_el);
	$(src_elm).remove();
	return _new_el[0];
};


$(document).ajaxError(function(event, xhr, settings, errorThrown) {
	if (settings.url.indexOf('/api/')<0)
		return;
	var _errs = '',
		_out = '',
		_i=0;
	//Problem.  if a network error, we can't parse the json.
	if (xhr.status)
		try {
			_errs = JSON.parse(xhr.responseText); 
		}
		catch(err) {
            console.log('erroring in ajax_setup');
			_errs = "Bad Request";
		}

	if (typeof _errs == "string") {
		_errs = _errs.replace('script', '');
		showalert(_errs, 'danger');
	} else {
		for (_i; _i<_errs.length; _i++) {
			// get the label
			var _la = _errs[_i][0],
				_label = $('label[for$=":'+ _la +'"]');
			// if there is no <label> there should be s <span> before the actual field
			if (!_label.length)
				_label = $('[data-field_name="'+ _la +'"]').prev();
			if (!_label.length)
				_label = _la;
			else
				_label = _label.text();
			_out += "<p>"+_label.replace('script', '')+": <b>"+_errs[_i][1]+"</b></p>"
		};
		showalert(_out, 'danger');
	};
});

$.ajaxSetup({ 
        beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});
