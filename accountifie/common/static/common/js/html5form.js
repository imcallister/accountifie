var isDateInputSupported = function(){
	var elem = document.createElement('input');
	elem.setAttribute('type','date');
	elem.value = 'foo';
	return (elem.type == 'date' && elem.value != 'foo');
}
/*
$(document).ready(function() {
	if (isDateInputSupported) {
		$('input[type="date"]').each(function(i){
			if (this.value.length>0) {
				var _d = Date.parse(this.value);
				if (_d)
					this.value = _d.getFullYear() + "-" + (_d.getMonth()+1) + "-" + _d.getDate()
			}
		})
	}
});
*/
