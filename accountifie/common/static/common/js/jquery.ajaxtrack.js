function getURLParams(qs){
	if (typeof qs === 'undefined')
		return [];
	var qparams = {},
		qparts, qpart,
		i=0;
	qparts = qs.split('&');
	for (i; i<qparts.length; i++) {
		qpart = qparts[i].split('=');
		qparams[decodeURIComponent(qpart[0])] = decodeURIComponent(qpart[1] || '');
	}
	return qparams;
};

(function( $ ) {

	var _LOG_ID = 'ajax_log',
		_AJAX_COUNT_ID = 'ajax_count',
		_SAVE_COUNT_ID = 'save_count',
		_ERROR_COUNT_ID = 'error_count',
		_STATUS_ID = 'ajax_status',
		_PROGRESS_HTML = '<div class="progress bg-warning" style="text-align: center; margin-bottom: 1px">\
			<div class="progress-bar progress-bar-info progress-bar-stripped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0;">\
			Saving ...</div></div>',
		_TIMER_STEP_MSEC = 50,
		_TIMER_WARN_STEPS = 7000 / _TIMER_STEP_MSEC, // 7 sec
		_TIMER_MAX_STEPS = 30000 / _TIMER_STEP_MSEC, // 30 sec
		_LOG_CSS_HEIGHT = '1.3em';

	var _defaultSettings = {
		urlPattern: '/api/',
		strict: false,
		log: false,
		responseTime: true
	};

	var update_ajax_status = function(text, kls) {
		var _ajax_status = this.find("#"+_STATUS_ID);
		if (_ajax_status.length) {
			_ajax_status.text(text);
			if (typeof(kls) !== 'undefined') 
				_ajax_status.attr('class', 'label label-'+kls)
			else
				_ajax_status.removeAttr('class');
		}
	};

	var update_ajaxLog = function(id, value) {
		var _ajaxLog = this.find("#"+_LOG_ID);
		if (_ajaxLog.length)
			_ajaxLog.append('<li>' + id + ' -> ' + value + '</li>');
	};

    var bump_span = function(_id, kls) {
		var element = this.find('#'+_id); 
		if (!element.length)
			return;
        var value = parseInt(element.text());
        if (isNaN(value)) {
			value = 0;
			if (typeof(kls)!== 'undefined') {
				var cls = element.attr('class').split(' ')[0];
				kls = cls+'-'+kls;
				var dflt = cls+'-default';
				if (element.hasClass(dflt))
					element.removeClass(dflt);
				if (!element.hasClass(kls))
					element.addClass(kls)
			}
		};
        value++;
        element.text(value);

    };

	$.fn.ajaxtrack = function(settings) {
		if (typeof(settings)==='undefined')
			settings = _defaultSettings;
		else
			$.extend(_defaultSettings, settings);
		var _title = 'Network activity',
			_pnl_grp = this.closest('.panel-group');
		if (_pnl_grp.length)
			_title = '<a data-toggle="collapse" href="#collapseAjaxTrack" data-parent="#' + _pnl_grp.attr('id')+ '">' + _title + '</a>';
		var _inner = '<div class="panel-heading">' + _title + '</div>\
			';
		if (_pnl_grp.length)
			_inner+='<div id="collapseAjaxTrack" class="panel-collapse collapse in">';
		_inner+='<div class="panel-body">\
			<p><span id="' + _AJAX_COUNT_ID + '" class="label bg-info" title="Submits">?</span>\
			= <span id="' + _SAVE_COUNT_ID + '" class="label bg-success" title="Successes">?</span>\
			+ <span id="' + _ERROR_COUNT_ID + '"  class="label bg-danger" title="Errors">?</span></p>\
			<p>Status: <span id="' + _STATUS_ID  + '">Ready</span></p>\
			<div class="log-container" style="height:'+ _LOG_CSS_HEIGHT + '; overflow-y:hidden; cursor: pointer; cursor: hand">\
				<div class="log"></div>\
			</div>\
			';
			if (settings.log)
			_inner+='<p>Call log:</p>\
			<ul id="' + _LOG_ID  + '">\
			</ul>\
			';
			_inner+='</div>';
		if (_pnl_grp.length)
			_inner+='</div>';
		_inner+='</div>';

		this.addClass('panel').addClass('panel-default');
		this.html(_inner);

		var element = this,
			elementSettings = settings;
/*	
		$.ajaxSetup({
			data: function(value, sttngs) {
					update_ajax_status.apply(element, ['Ready']);
					return value
				  }
		});
*/
		var _checkTracking = function(url) {
				var _trackIt = true;
				if (settings.urlPattern.length>0) 
					if (settings.strict)
						_trackIt = (url==settings.urlPattern);
					else
						_trackIt = (url.indexOf(settings.urlPattern)!=-1);
				return _trackIt
			}

		var _timers = {}

		var _startTimer = function(rt) {
			var _cell = element.find('#rt'+rt);
			if (_cell.length) {
				_cell.html(_PROGRESS_HTML);
				_cell.find('.progress-bar').data('step', 0).data('pct',0);
			}
			_timers['rt'+rt] = window.setInterval(function(tm){
					var _pb = element.find('#rt' + tm + ' .progress-bar'),
						_step = 1,
						_pct = _pb.data('pct'); 
					_step += _pb.data('step');
					var _pct = _pct + Math.round((100 - _pct) / 10, 0);// _step / _TIMER_MAX_STEPS * 100;
					_pb.css('width', _pct+'%').attr('aria-valuenow', _pct);
					if (_step == _TIMER_WARN_STEPS)
						_pb.removeClass('progress-bar-info').addClass('progress-bar-warning');
					_pb.data('step', _step).data('pct', _pct);
				}, _TIMER_STEP_MSEC, rt);
		};

		element.find('.log-container').click(function(ev){
				var _expanded = $(this).data('expanded');
				if (typeof(_expanded)==='undefined')
					_expanded = false;
				if (!_expanded) {
					$(this).css('height', '100px').css('overflow-y', 'scroll');
				} else {
					$(this).css('height', _LOG_CSS_HEIGHT).css('overflow-y', 'hidden');
				}
				$(this).data('expanded', (!_expanded));
			});

		$(document).ajaxSend(function(event, xhr, settings) {
				if (_checkTracking(settings.url)) {
					var _params = getURLParams(settings.data);
					//var td = $('#'+_params.id);
					xhr.requestTime = Date.now();
					element.find('.log').prepend('<div id="rt' + xhr.requestTime + '">Saving ...</div>');
					_startTimer(xhr.requestTime);
					bump_span.apply(element,[_AJAX_COUNT_ID, 'info']);
					update_ajax_status.apply(element, ['Saving ...', 'warning']);
					update_ajaxLog.apply(element, [_params.id, _params.value]);
					if (typeof(console)!=='undefined')
						console.log('before_send: ' + _params.id + ' -> ' + _params.value);
				}
		});
		$(document).ajaxComplete(function(event, xhr, settings) {
				if (settings.url.indexOf(elementSettings.urlPattern)!=-1 && xhr.hasOwnProperty('requestTime') && elementSettings.responseTime) {
					window.clearInterval(_timers['rt'+xhr.requestTime]);
					var t2 = Date.now(),
						msec = t2 - xhr.requestTime,
						_pb = element.find('#rt' + xhr.requestTime + ' .progress-bar');
					_pb.removeAttr('progress-bar-striped');
					_pb.text(msec.toString() + "ms");
					if (typeof(console)!=='undefined')
						console.log("msec since call =" + msec)
				}
		});
		$(document).ajaxSuccess(function(event, xhr, settings) {
				if (_checkTracking(settings.url)) {
					var _pb = element.find('#rt' + xhr.requestTime + ' .progress-bar');
					_pb.removeClass('progress-bar-info').addClass('progress-bar-success');
					bump_span.apply(element, [_SAVE_COUNT_ID, 'success']);
					update_ajax_status.apply(element, ["Success", 'success'])
				}
		});
		$(document).ajaxError(function(event, xhr, settings, errorThrown) {
				if (_checkTracking(settings.url)) {
					var _pb = element.find('#rt' + xhr.requestTime + ' .progress-bar');
					_pb.removeClass('progress-bar-info').removeClass('progress-bar-warning').addClass('progress-bar-danger');
					bump_span.apply(element,[_ERROR_COUNT_ID, 'danger']);
					update_ajax_status.apply(element, ["Error", 'danger'])
				}
		});

		return this
	};

	if ($('.ajax_tracking').length) {
		$('.ajax_tracking').ajaxtrack();

	};
}( jQuery ));
