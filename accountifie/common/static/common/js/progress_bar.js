/*GLOBALS = TASK_MONITOR(task_monitoring.js), MONITOR_CONTROLLER(monitor_controller.js), PROGRESS_BAR(progress_bar.js)
*/

var PROGRESS_BAR = (function () {

    var PROGRESS_BAR = {}
    
    var create = function (data) {
        var progress = $('<div class="progress">');
        var bar = $('<div class="progress-bar progress-bar-info ">');
        bar.css('width', data.percent_complete + '%');
        if (data.task_state == 'failed') {
            bar.removeClass('progress-bar-info');
            bar.addClass('progress-bar-danger');
        }
        if (data.task_state == 'succeeded') {
            bar.removeClass('progress-bar-info');
            bar.addClass('progress-bar-success');
        }   
        progress.append(bar);
        return progress;
    };
    
    var create_task_sent_message = function (task_name) {
        var progress = $('<div class="progress progress-striped active">');
        var bar = $('<div class="progress-bar ">');
        bar.css('width', '2%');
        return progress;
    }
    
    PROGRESS_BAR.create = create;
    PROGRESS_BAR.create_task_sent_message = create_task_sent_message;
    return PROGRESS_BAR;

}());
