var docengine_load_tester = function(url){
    var errors = [];
    var saved = [];
    var time_out;
    //these should be overriden by the client using the corresponding functions defined at the bottom
    var error_callback = function (){};
    var success_callback = function (){};
    var stop_callback = function (){};
    var response_checker = function (res) {return res};
    var request_data = function () { return {'some_data': 'something'}};
    
    var calc_average = function() {
        var all = errors.concat(saved);
        var times = [];
        var total = 0;
        for(var i = 0; i < all.length; i++) {
            var resp_time = all[i][1]
            times.push(resp_time)
        }
        for(var i = 0; i < times.length; i++) {
            total += times[i]
        }
        return Math.ceil(total/times.length)
    }

    var error_handler =  function (response, load_time, jqXHR){
        errors.push([response, load_time])
        error_callback(response, errors, load_time, jqXHR)
    }
    
    var success_handler =  function (response, load_time, jqXHR){
        if (response_checker(response)){
            saved.push([response, load_time])
            success_callback(response, saved, load_time, jqXHR)
        }
        else {
            error_handler(response)
        }  
    }
    
    var make_request = function (total){
        var count = [];
        var make_post = function () {
            if (!(total == undefined) && (count.length > total || count.length == total)){
                cancel_timeout();
            }
            else {
                count.push('one more request')
                var start = Date.now();
                var check_time = function () {
                    var now = Date.now()
                    return now - start
                }
                var jqxhr = $.ajax({
                    url: url,
                    dataType: "json",
                    type: "POST",
                    data: request_data(),
            	}).error(function(jqXHR, ajax_status, error) {
                    error_handler(error, check_time(), jqXHR)
            	}).success(function(data, status, jqXHR) {
                    check_time()
            	    success_handler(data, check_time(), jqXHR)
            	}) 
            }
        }
        return make_post;
    }

    var set_timeout = function (frequency, count) {
        var freq = frequency * 1000;
        var post_func = make_request(count);
        //call it for the first time immediately
        post_func()
        time_out = setInterval(post_func,  freq || 1000)
    };
                 
    var cancel_timeout = function () { 
        clearInterval(time_out);
        stop_callback();
       
    };
    
    //below are all used by the 'client' to set the right callbacks
    var success = function(callback){
        success_callback = callback;
        return handler;
    }
    
    var error = function(callback){
        error_callback = callback;
        return handler;
    }
    
    var stop = function(callback){
        stop_callback = callback;
        return handler;
    }
    
    var right_answer = function(callback){
        response_checker = callback;
        return handler;
    }
    
    var question = function(func){
        request_data = func;
        return handler;
    }
                
    var handler = {};
    handler.start_test = set_timeout;
    handler.stop_test = cancel_timeout;
    handler.success = success;
    handler.error = error;
    handler.stop = stop
    handler.right_answer = right_answer;
    handler.question = question;
    handler.average = calc_average;
    return handler

};