/*GLOBALS = TASK_MONITOR (task_monitoring.js), MONITOR_CONTROLLER(monitor_controller.js), PROGRESS_BAR(progress_bar.js)
 *Controller for the front end task monitoring client.
 *Model is found in task_monitoring.js, which handles the communication with the server and returns cleaned data to the controller
 *progress_bar.js provides some generic view code to create a bootstrap based progress bar.
 *the glue between this all is found in here.
 *Please note the containing <li> element is created here too. 
 */

var MONITOR_CONTROLLER = (function () {
    
    var MONITOR_CONTROLLER = {};
    
    
    var check_all_done = function (data, task_name) {
        var done = 0
        for (var i = 0; i < data.length; i++) {
            if (data[i].task_state == 'succeeded') {
                done ++;
            }
        }
        if (done == data.length) {
            return true;
        }
        else {
            return false;
        }
    }
         
    var render_tasks = function(d) {
        //callback that will receive data from server and defines how it should be displayed
        var that = this;
        var task_names = Object.keys(d);
        $.each(task_names, function (index, element) {
            var data = d[element];
            for (var i = 0; i < data.length; i++) {
                var el = $('<li id=' + data[i].task_id + ' >')
                var progress = PROGRESS_BAR.create(data[i])
                el.text(data[i].task_name + '(' + data[i].task_state + ') ' + data[i].percent_complete + '% complete' )
                var id_name = '#' + element;
                $(id_name).prepend(el, progress);
            } 
        })      
    };
    
    var render_single_task_type = function(data) {
        //callback that will receive data from server and defines how it should be displayed
        var task_name = data[0].task_name;
        var id_name = '#' + task_name;
        $(id_name).empty();
        for (var i = 0; i < data.length; i++) {
            var el = $('<li id=' + data[i].task_id + ' >')
            var progress = PROGRESS_BAR.create(data[i])
            el.text(data[i].task_name + '(' + data[i].task_state + ') ' + data[i].percent_complete + '% complete' )
            $(id_name).prepend(el, progress);
        }
    };
    
    var render_task_sent_message = function (task_name) {
        //used to render the initial message when button is clicked
        var id_name = '#' + task_name;
        var el = $('<li>')
        var progress = PROGRESS_BAR.create_task_sent_message(task_name);
        el.text(task_name + '(sent) ' +  ' 0% complete' )
        $(id_name).prepend(el, progress);
    }
        
    var log_to_console = function (data) {
        //to use as callback to just log data to the console.
        console.log(data);    
    }
    
    var launch_task = function (monitor) {
        render_task_sent_message(monitor.task_name);
        monitor.ongoing_tasks = true;
        monitor.launch_task()
        if (monitor.polling != true) {
            setInterval(function(){
            monitor.polling = true;
            monitor.check_progress();
                    }, 3000);
        }
        
    }
    
    var setup = function (task_button_class) {
        
        //for every button that creates a type of tasks, setup a task monitor with the correct urls and callbacks
        $(task_button_class).each(function () { 
            //setup a task monitor with the correct urls to launch a task and check progress
            var options = {};//object to hold option to be passed along to the task setup function
            options['create_url'] = $(this).attr('data_create_url');
            options['info_url'] = $(this).attr('data_info_url');
            options['task_name'] = $(this).attr('data_name');
            options['object_id'] = $(this).attr('data_object_id');
            options['view'] = render_single_task_type//optionally provide a default  callback
            var monitor = TASK_MONITOR.setup_monitor(options);
            //proceed without first showing a confirm modal
            $(this).click(function(evt){
                var btn = $(this);
                btn.button('loading')
                setTimeout(function () {
                    btn.button('reset')
                }, 5000)
                evt.preventDefault();
                launch_task(monitor);
            })     
        })
        //this function is useful if you want to display running or completed tasks to users who did not initiate them
        //check all running tasks or recently ran ones, polling the server and order the data by task type
        //pass the function a callback function that will render the data on the page
        TASK_MONITOR.check_running_tasks(render_tasks);    
    }
    
    MONITOR_CONTROLLER.setup = setup;
    return MONITOR_CONTROLLER;
    
    
}());