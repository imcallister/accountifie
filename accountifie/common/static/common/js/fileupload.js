$(document).ready(function() {
        
        $("#rptupload").append('<input ondrop="rptdragleave()" ondragleave="rptdragleave()" ondragenter="rptdragover()" type="file" id="fileToUpload" onchange="fileSelected();"/>');
        $("#rptupload").append('<div id="mask">&nbsp;</div>');
        $("#fileToUpload").css({"background-color":"#aabbcc",
                                "color":"red",
                                "height":$("#rptupload").css("height"),
                                "width":$("#rptupload").css("width")
                                
                              });

        $("#mask").css({"background-color":"white",

                        "pointer-events":"none",
                        "position":"relative",
                        "top":parseInt($("#fileToUpload").css("height"))*-1,
                        "width":"100%",
                        "height":"100%",
                      
                        "border": "5px dashed #cccccc",
                      });
        $("#mask").append("<div id='rptdropmessage'>drop files here");

        $("#mask").append("<div class='rptdropclass' id='rptfilename'></div>");
        $("#mask").append("<div class='rptdropclass' style='font-family:arial;font-size:20px;color:#bbbbbb' id='rptimage'><div style='float:left;height:100%;width:50%;'><img style='float:right;margin-right:30px' height='150px' width='120px' src='http://www.progressivetraining.ie/wp-content/uploads/2009/06/excel-logo.png' alt='XLSX'/></div><div style='float:left;height:100%;width:200px;'><br/><br/>size: <span id='rptFileSize'></span><br/>type: <span id='rptuploadfiletype'></span></div></div>");
        

        $("#rptdropmessage").css({"width":"100%",
                            "height":"150px",
                            "border":"0px solid black",
                            "position":"relative",
                            "top":"50px",
                            "color":"#eeeeee",
                        "text-align":"center",
                        "font-size":"80px",
                        "font-family":"arial"
        });   


        $("#rptimage").css({"width":"100%",
                            "height":"150px",
                            "border":"0px solid black",
                            "display":"none"
        });
            
        $("#mask").append('<div class="rptdropclass" id="rptuploadbar"><span id="rptstart">start</span></div>');
        $("#rptuploadbar").append('<div id="rptuploadbarvalue"></div>');

        $("#rptfilename").css({"width":"90%",
                                  "height":"40px",
                                  "pointer-events":"all",
                                  "margin-left":"auto",
                                  "margin-right":"auto",
                                  "border":"0px",
                                  
                                  "position":"relative",
                                  "color":"#bbbbbb",
                                  "text-align":"center",
                                  "font-size":"20px",
                                  "font-family":"arial",
                                  "padding-top":"10px",
                                  "display":"none"
        });

        $("#rptuploadbar").css({"width":"70%",
                                  "height":"40px",
                                  "pointer-events":"all",
                                  "margin-left":"auto",
                                  "margin-right":"auto",
                                  "border":"4px solid #cccccc",
                                  
                                  "position":"relative",
                                  "color":"#bbbbbb",
                                  "text-align":"center",
                                  "font-size":"30px",
                                  "font-family":"arial",
                                  "display":"none",
                                  "box-shadow": "0px 10px 20px -15px #888888"
        });
            

        $("#rptuploadbarvalue").css({"width":"0%",
                                  "height":"100%",
                                  "background-color":"#cacaca",
                                  "border":"0px",
                                  "color":"white",
                                  "position":"absolute",
                                  "left":"0px",
                                  "top":"0px",
                                  "text-align":"center",
                                  "font-size":"30px",
                                  "font-family":"arial"
        });
        $("#rptuploadbar").on("click",function(){
              $("#rptstart").html("uploading");
              uploadFile();
        });
});

function rptdragover(){
    $('#mask').css('border-color', '#BADA55');
}
function rptdragleave(){
    $('#mask').css('border-color', '#cccccc');
}

function fileSelected() {
    $(".rptdropclass").show();
    $("#rptdropmessage").hide();
    
    var file = document.getElementById('fileToUpload').files[0];
    if (file) {
            var fullname = file.name;
            var extentionArray = file.name.split(".")
            var extention = extentionArray[extentionArray.length-1];

            $("#rptfilename").html(file.name);
            var filesizeReadable;
            if (file.size>1000*1000){
              filesizeReadable = Math.round(file.size/(1000*1000) * 100) / 100 + (" MB");
              console.log(filesizeReadable);
            }
            else{
              filesizeReadable = Math.round(file.size/(1000) * 100) / 100 + (" KB");
              console.log(filesizeReadable);
            
            }
            $("#rptFileSize").html(filesizeReadable);
            $("#rptuploadfiletype").html(extention);

            console.log('Name: ' + file.name);
            console.log('Size: ' + file.size);
            console.log('Type: ' + file.type);
    }
}

function uploadFile() {
          var fd = new FormData();
          fd.append("fileToUpload", document.getElementById('fileToUpload').files[0]);
          
          var csrf_token = document.getElementById('rptupload').getAttribute('data-csrf');
          
          fd.append('csrfmiddlewaretoken', csrf_token);
          
          var xhr = new XMLHttpRequest();
          xhr.upload.addEventListener("progress", function(evt){
            percentComplete = parseInt(evt.loaded/evt.total*100);
            $("#rptuploadbarvalue").css({"width":percentComplete + "%"});
            console.log("uploaded: " + evt.loaded + "bytes");


          }, false);
          xhr.addEventListener("load", function(evt){
            console.log(evt.target.responseText);
            $("#rptuploadbarvalue").html("complete");
          }, false);


          xhr.addEventListener("error", function(){
            console.log("failed");
          }, false);
          
          xhr.addEventListener("abort", function(){
            console.log("cancelled");
          }, false);
          
          xhr.open("POST", "/sandbox/html5-upload/");
          xhr.send(fd);
}
