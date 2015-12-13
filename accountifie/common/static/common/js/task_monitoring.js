/*GLOBALS = TASK_MONITOR(task_monitoring.js), MONITOR_CONTROLLER(monitor_controller.js), PROGRESS_BAR(progress_bar.js)
 *front-end client to poll the server and fetch info about ongoing celery tasks
 *This client expects JSON data from the server in the following format:
 *A list [] of dictionaries each representing and instance of a docengine.common.TaskMonitor
 * where m is the TaskMonitor instance:
 * {'task_id'=m.task_id,
    'task_name'=m.task_name,
    'traceback'=m.traceback,
    'task_state'=m.task_state,
    'percent_complete'=m.percent_complete,
    }
 */

var TASK_MONITOR = (function () {
    //everything in here is hidden unless explicitely added to the TASK_MONITOR object
    //the TASK_MONITOR object is visibile because it is returned and available as the TASK_MONITOR var globally
    //functions declared in here have access to everything else declared in here, as do the callbacks
    var TASK_MONITOR = {};
    //every time you create a monitor, it is pushed onto task_types
    var task_types = [];
    //every new monitor is also added to this map, with the task_name as key
    task_map = {};
    
    
    var filter_for_taskname = function (iterable, task_name) {
        //utility module level function to clean data obtained by server by type task
        clean_list = [];
        $.each(iterable, function (index, element) {
            if (element.task_name == task_name) {
                clean_list.push(element);
            }
        });
        return clean_list;
    };
    
    var check_for_ongoing = function (data) {
        //utility module level function, data is coming from the server
        //check the data coming from the server to determine if any tasks have already started
        var started = false;
        $.each(data, function (index, element) {
            if (element.task_state == 'started') {
               started = true;
               //stop the iteration
               return false;
            }
            //continue to iterate
            return true;
        });
        //return true or false
        return started;
    }
    
    var start_polling_ongoing = function (ongoing) {
        //ongoing is an object whose keys are the name of the various task types initialized on this page
        //utility module level function 
        //launches a polling loop for tasks that have been started in a previous process and are still ongoing
        var task_names = Object.keys(ongoing);
        for (var i = 0; i < task_names.length; i++) {
            var name = task_names[i]
            if (ongoing[name]) {
                //start polling, using an immediate function to capture name variable from the loop
                (function (name){
                    task_map[name].ongoing_tasks = true;
                    task_map[name].check_progress();
                    setInterval(function(){
                        task_map[name].check_progress();
                    }, 5000);
                })(name);
            }      
        };
    }
    
    var launch_task = function (render_callback){
        //this function should always be used as a method of a monitor as returned by TASK_MONITOR.setup_monitor
        //callback should be a function to render the view related to the succesfully created task
        var that = this;//retain access to the monitor object within the JQuery function
        $.post(this.create_url, {'object_id': that.object_id}, function(d){
            that.ongoing_tasks = true;
            if (render_callback) {
                render_callback(that.task_name);
            }
            
        });  
    };
    
    var check_progress = function(render_callback) {
       //checking progress of tasks for a particular type by way of a monitor
       //this function should always be used as a method of a monitor as returned by TASK_MONITOR.setup_monitor
        var that = this;//retain access to the monitor object within the JQuery function
        if (that.ongoing_tasks == true) {
            //poll the server
            $.get(this.info_url, this.task_name, function (d){
                var data = JSON.parse(d);
                var cleaned_data = filter_for_taskname(data, that.task_name);
                //handle rendering of data by way of a callback or a saved view function
                if (render_callback) {
                    render_callback(cleaned_data);
                }
                else {
                  that.view(cleaned_data);
                }
                //check if all tasks are finished, if so stop polling the server
                that.ongoing_tasks = check_for_ongoing(cleaned_data);
            });
        }
    };
    
    var check_running_tasks = function (callback){
        /*Function to be launched directly on page load, to check the server for any tasks it might want to return
         *These tasks can be finished but still relevant, or these can be still ongoing and appropriate to be displayed
         *to the current user
         *Essentially this function handles getting 'up to speed' for the client if the page was just loaded and
         *the JS code cannot be aware of any tasks that was previously launched
         */
        var all_tasks = {};
        var counter = 0;
        var ongoing = {}
        
        $.each(task_types, function (index, element) {
            $.get(element.info_url, element.task_name, function (d){
                var data = JSON.parse(d);
                //in case the data returned was not specific to this one task type, we filter it here to avoid duplicates
                var cleaned_data = filter_for_taskname(data, element.task_name);
                //if any task is ongoing, the interval polling should start to track progress
                ongoing[element.task_name] = check_for_ongoing(cleaned_data);
                all_tasks[element.task_name] = cleaned_data;
                counter ++;
                if (counter == task_types.length) {
                    //we have finished iterating over all types of tasks defined for this page
                    //the callback is used to display all tasks that the server returned, without starting a polling loop
                    callback(all_tasks);
                    //if there are any ongoing tasks, a polling loop is started for them
                    start_polling_ongoing(ongoing);
                };
            });
        });
    };
    
    var setup_monitor = function (options) {
        /*create a monitor for a specific type of task (please note a monitor is used for a type of task,
         *not for every task that is launched)
         *expects to be passed an object with the following keys:
         *task_name => the name of the task, a string
         *create_url => the url to post for new task creation
         *info_url => the url to poll for info about currently running or completed task
         *please note the the info url does not have to be task specific, one url for all tasks will do fine
         *the data will be filtered by task automatically
        */
        var monitor = {};
        monitor.task_name = options['task_name'];//what's the name of the task?
        monitor.create_url = options['create_url'];//where do you poll the server to create new tasks?
        monitor.info_url = options['info_url'];//where do you poll the server to fetch info about created tasks?
        monitor.view = options['view']//how do you want this type of task rendered on the page?
        monitor.object_id = options['object_id']//does this monitor relate to some sort of back end object we need to be aware of?
        monitor.launch_task = launch_task;
        monitor.ongoing_tasks = false;//set it to true when launching a task, back to false when all tasks of this type are done
        monitor.polling = false;
        monitor.check_progress = check_progress;
        task_types.push(monitor);
        task_map[monitor.task_name] = monitor
        return monitor;
    };
    
    //These two functions are set directly on TASK_MONITOR and are not related to any specific type of tasks
    //these are used to create specific monitors for a type of task and to poll the server for all tasks
    TASK_MONITOR.setup_monitor = setup_monitor;
    TASK_MONITOR.check_running_tasks = check_running_tasks;
    return TASK_MONITOR;

}())




