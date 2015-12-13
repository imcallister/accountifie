(function ($) {
    $.fn.extend({
        //pass the options variable to the function
        confirmModal: function (opt) {
            var html = '<div class="modal" id="confirmContainer"><div class="modal-header"><a class="close" data-dismiss="modal">x</a>' +
            '<h3>#Heading#</h3></div><div class="modal-body">' +
            '#Body#</div><div class="modal-footer">' +
            '<a href="#" class="btn btn-primary" id="confirmYesBtn">Confirm</a>' +
            '<a href="#" class="btn" data-dismiss="modal">Close</a></div></div>';

            var defaults = {
                heading: 'Please confirm',
                body:'Body contents',
                callback : null,
                arg: null
            };
            
            var options = $.extend(defaults, opt);
            html = html.replace('#Heading#',options.heading).replace('#Body#',options.body);
            $(this).html(html);
            $(this).modal('show');
            var context = $(this); 
            $('#confirmYesBtn',this).click(function(){
                if(options.callback!=null)
                    options.callback(options.arg);
                $(context).modal('hide');
            });
        }
    });

})(jQuery);