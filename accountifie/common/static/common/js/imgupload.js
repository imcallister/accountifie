/*
 * <div class="drop_zone">Drop files here</div>
 * <output id="list"></output>
 */

_ORIGINAL_WIDTH = 400.0;
_ORIGINAL_HEIGHT = 300.0;

$(document).ready(function(){

    $.each('.drop_zone', function(idx, item) {
        item.id = "drop_zone_" + idx;
        var scale = $(item).heigth() / _ORIGINAL_HEIGHT;
        // filter descendants which have a font-size css attribute specified
        $.each($(this).descendents().filter(function(idx){ 
            return $(this).css('font-size')
            }), function(idx, item) {
                var font_size = parseFloat($(item).css('font-size'));
                // last 2 characters hold the font size type
                var font_size_type = $(item).css('font-size').substr($(item).css('font-size').length-2, 2);
                if (!isNaN(parseInt(font_size_type.substr(0,1))))
                    // sorry, I meant 'last character holds the ...'
                    font_size_type = font_size_type.substr(1,1)
                var new_size = (font_size != Math.round(font_size)) ? (font_size * scale) : Math.round(font_size * scale);
                $(item).css('font-size', new_size+font_size_type);
          });
      
  });
    
  $('.drop_zone').on('dragover', function(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
  }
    
  $('.drop_zone').on('drop', function(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    var files = evt.dataTransfer.files; // FileList object.

    // files is a FileList of File objects. List some properties.
    var output = [];
    for (var i = 0, f; f = files[i]; i++) {
      output.push('<li><strong>', escape(f.name), '</strong> (', f.type || 'n/a', ') - ',
                  f.size, ' bytes, last modified: ',
                  f.lastModifiedDate ? f.lastModifiedDate.toLocaleDateString() : 'n/a',
                  '</li>');
    }
    document.getElementById('list').innerHTML = '<ul>' + output.join('') + '</ul>';
  }
});

/*
EXPECTED DIV:
<div style="width:600px;height:300px" class="rptupload" data-csrf="JpBlOI4OgrMxADRu8dgDbHemBVXvrG2W"></div>

with optional attributes:
    data-filter="xlsx"
    data-size-limit="11" (in MB)
    data-url="http://posttestserver.com/post.php"
    validate="true"

test div:
    <div style="width:600px;height:300px" validate="true" class="rptupload" data-filter="xlsx" data-size-limit="11" data-url="http://posttestserver.com/post.php" data-csrf="JpBlOI4OgrMxADRu8dgDbHemBVXvrG2W"></div>

*/

$(document).ready(function() {
  console.log("V0.712");
  rptMessageArray = new Object();
  build();
});

function resizeFont(obj, lines) {
    var fontSize = parseInt(obj.parent().css('font-size'));
    console.log('-==========================');
    console.log(obj.attr('id'));
    console.log(obj.parent().attr('id'));
    if (obj[0].offsetHeight/fontSize<lines) { // can increase size
        while (fontSize*(1+lines)<obj.parent().height()) {
            fontSize = parseInt(obj.parent().css('font-size'))+5;
            obj.parent().css('font-size', fontSize+"px")
        }
    }
    while (fontSize*(1+lines)>obj.parent().height()) {
        fontSize = parseInt(obj.css('font-size'))-5;
        obj.parent().css('font-size', fontSize+"px")
    }
}
function build(){
  
  var _WIDTH=500;
  var _HEIGHT=350;

  $(".rptupload").each(function( index ) {
    
      function popup(string){
          $("#rptmessageboxbody"+index).html('<div class="alert alert-error">'+string+'</div>');
          $("#rptmessageboxbackground"+index).fadeIn("100");
      }
      
      var extFilter = "";
      var uploadsize;
      
      var _height = $(this).height();
      var _width = $(this).width();
      
      var isFullWidget = _height>150?true:false;
      
      if (rptMessageArray[index])
          console.log("");
      else
          rptMessageArray[index]=$(this).html();
      $(this).html("");
      var mimeArray = $(this).attr("data-filter").split(",");
      var mimeArrayComplete = new Array();

      if ($(this).attr("data-filter")){
          for (item in mimeArray){
              console.log(mimeArray[item]);
              switch(mimeArray[item]){
                  case "xlsx":
                    mimeArrayComplete[mimeArrayComplete.length] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
                    break;
                  case "xls":
                    mimeArrayComplete[mimeArrayComplete.length] = "application/vnd.ms-excel";
                    break;
                  case "jpg": case "png": case "gif":
                    mimeArrayComplete[mimeArrayComplete.length] = "image/*";
                    break;
                  case "pdf":
                    mimeArrayComplete[mimeArrayComplete.length] = "application/pdf";
                    break;
                  case "csv":
                    mimeArrayComplete[mimeArrayComplete.length] = "text/csv";
                    break;
                  default:
                    mimeArrayComplete[mimeArrayComplete.length] = "";
              }
          }
          uniqueArray = mimeArrayComplete.filter(function(elem, pos) {
            return mimeArrayComplete.indexOf(elem) == pos;
          })
          extFilter = uniqueArray.join("|");
      }
      console.log("* ** * * ** " + extFilter);
      $(this).append('<input accept="'+extFilter+'" type="file" id="fileToUpload'+index+'" />');
      $(this).append('<div id="undermask'+index+'">&nbsp;</div>');
      $(this).append('<div id="mask'+index+'">&nbsp;</div>');
      $(this).append('<div id="rptmessageboxbackground'+index+'"><div id="rptmessagebox'+index+'"><div id="rptmessageboxheader'+index+'">Message<div id="rptmessageboxclose'+index+'"><b>X</b>&nbsp;&nbsp;</div></div><div id="rptmessageboxbody'+index+'"></div></div></div>');

      var scaleX = $(this).width()/_WIDTH;
      var scaleY = $(this).height()/_HEIGHT;
            
      console.log("scaleX:" + scaleX);
      console.log("scaleY:" + scaleY);

      $("#rptmessageboxbackground"+index).css({
                "background-color":"rgba(0,0,0,0.5)",
                "position":"absolute",
                "height":$(document).height(),
                "width":"100%",
                "top":"0px",
                "left":"0px",
                "display":"none"
              });
      $("#rptmessagebox"+index).css({"background-color":"white",
                "position":"relative",
                "width":"500px",
                "top": "30%",
                "left": "50%",
                "margin-left":"-250px",
                "box-shadow":"0px 0px 70px #333333",
                "top":"200px",
                "border-radius":"8px",
                "position": "fixed"
              });
      $("#rptmessageboxheader"+index).css({
                "background-image": "linear-gradient(to bottom, #ccc, #aaa)",
                "background": "-webkit-linear-gradient(#ccc, #aaa)",
                "height":"20px",
                "color":"white",
                "border-radius":"8px 8px 0px 0px",
                "text-align":"center",
                "text-shadow": "0px 0px 3px black"
              });
      $("#rptmessageboxclose"+index).css({"float":"right",
                "color":"white",
                "position":"relative",
                "cursor" : "default"
              });
      $("#rptmessageboxbody"+index).css({"margin-top":"50px",
                "margin-left": "30px",
                "margin-right": "30px",
                "padding-bottom":"50px",
                "text-align":"center"
              });
      $("#fileToUpload"+index).css({"background-color":"#aabbcc",
                "color":"red",
                "height":$(this).css("height"),
                "width":$(this).css("width"),
                "border-radius": "30px"//,
                //"transform": "scale("+scaleX+","+scaleY+")"
              });
      $("#undermask"+index).css({"background-color":"white",
                "pointer-events":"none",
                "position":"relative",
                "top": ($("#fileToUpload"+index).height()*-1)+"px",
                "width":"100%",
                "height":"100%"//,
                //"transform": "scale("+scaleX+","+scaleY+")"
            });
      $("#mask"+index).css({"background-color":"white",
                "pointer-events":"none",
                "position":"relative",
                "top": ($("#undermask"+index).height()*-2)+"px",
                "width":"100%",
                "height":"100%",
                "border-radius": "30px",
                "border": "5px dashed #cccccc"//,
                //"transform": "scale("+scaleX+","+scaleY+")"
            });

      $("#mask"+index).append("<div id='rptdropmessage"+index+"'style='line-height:80%'></div>");
      
      if (isFullWidget) {
          $("#mask"+index).append("<div class='rptdropclass"+index+"' id='rptfilename"+index+"'></div>");
          $("#mask"+index).append("<div class='rptdropclass"+index+"' style='font-family:arial;font-size:20px;color:#bbbbbb' id='rptimage"
          + index + "'><div style='float:left;height:100%;width:30%;'><img id='docext"+index+"'height='"
          + Math.round(_height/3)+"px' src='' alt='"+ $(this).attr("data-filter") 
          + "'/></div><div style='float:left;height:100%;margin: 5%'>size: <span id='rptFileSize" + index
          + "'></span><br/>type: <span id='rptuploadfiletype"+index+"'></span></div></div>");
          $("#rptdropclass"+index).css("margin","1em");
          $("#rptimage"+index).css({"width":"100%",
                "height": Math.round(_height/3)+"px",
                "border":"0px solid black",
                "display":"none"
            });
          $("#rptfilename"+index).css({"width":"100%",
                //"height":"40px",
                "pointer-events":"none",
                "margin-left":"auto",
                "margin-right":"auto",
                "border":"0",
                "position":"relative",
                "color":"#aaaaaa",
                "text-align":"center",
                "font-size":"22px",
                "font-family":"arial",
                "margin-top":"10px",
                "overlow":"auto",
                "display":"none"
            });
      }
      $("#rptdropmessage"+index).css({"width":"100%",
                "height":"90%",
                //"border":"0px solid black",
                "position":"relative",
                "top":"50px",
                "color":"#eeeeee",
                "text-align":"center",
                "font-size":"80px",
                "pointer-events":"none",
                "font-family":"arial"
            });   
      
      $("#mask"+index).append('<div class="rptdropclass'+index+'" id="rptuploadbar'+index+'"></div>');
      $("#rptuploadbar"+index).append('<div id="rptuploadbarvalue'+index+'"></div><div id="rptuploadbarmask'+index+'"></div>');

      $("#rptdropmessage"+index).html(rptMessageArray[index]);
      // restore font aspect
      //$("#rptdropmessage"+index).height($(this).height()*scaleY);
      //$("#rptdropmessage"+index).width($(this).width()*scaleX);
      //$("#rptdropmessage"+index).css('transform', "scale("+(1/scaleX)+", "+(1/scaleY)+")");
      //var fontSize;
      var lines=2;
      resizeFont($("#rptdropmessage"+index+" div"), lines);
      /*while ($("#rptdropmessage"+index+" div")[0].offsetHeight > $("#rptdropmessage"+index).height()) {
          fontSize = parseInt($("#rptdropmessage"+index+" div").css('font-size'))-5;
          $("#rptdropmessage"+index+" div").css('font-size', fontSize+"px")
      }*/
      var topMargin = 1;//Math.round((_height/-$("#rptdropmessage"+index).height())/4);
      if (topMargin>0)
          $("#rptdropmessage"+index).css('top', topMargin+"px");
      
      $("#rptuploadbar"+index).css({"width":"70%",
                "min-height":"30px",
                "height":"5%",
                "pointer-events":"all",
                "padding-top":"4%",
                "margin":".1em auto",
                "border":"1px solid #bbbbbb",
                "background-repeat": "repeat-x",
                "background-image": "linear-gradient(to bottom, #ccc, #aaa)",
                "background": "-webkit-linear-gradient(#ccc, #aaa)",
                "border-radius": "6px 6px 6px 6px",
                "box-shadow": "0px 1px 0px rgba(255, 255, 255, 0.1) inset, 0px 1px 5px rgba(0, 0, 0, 0.25)",
                "position":"absolute",
                "left": "15%",
                "bottom": '3%',
                "display":"none",
                "font-size": "30px"
            });
      $("#rptuploadbarvalue"+index).css({"width":"0%",
                "height":"100%",
                "background-image": "linear-gradient(to bottom, rgb(0, 136, 204), rgb(0, 68, 204))",
                "background": "-webkit-linear-gradient(rgb(0, 136, 204), rgb(0, 68, 204))",
                "border":"0px",
                "background-repeat": "repeat-x",
                "position":"absolute",
                "left":"0px",
                "top":"0px",
                "box-shadow": "0px 0px 15px rgb(0, 136, 204)"                       
            });
      $("#rptuploadbarmask"+index).css({"width":"100%",
                "height":"100%",
                "padding-top":"3%",
                "text-shadow": "0px -1px 0px rgba(0, 0, 0, 0.25)",
                "color":"white",
                "position":"absolute",
                "left":"0px",
                "top":"0px",
                "text-align":"center",
                "pointer-events":"none",
                "font-family":"arial"
            });
      // TODO: resize the button, at least for too small widgets
      upload_button = $('[id^="rptuploadbar"][id$="'+index+'"]')
      // event handlers
      
      $("#rptmessageboxbackground"+index).on("click",function(){
          $(this).fadeOut("100");
      });
      $("#rptmessageboxclose"+index).on("click",function(){
          $("#rptmessageboxbackground"+index).fadeOut("100");
      });
      $("#rptmessagebox"+index).on("click",function(){
          event.stopPropagation();
      });
      $("#rptuploadbar"+index).on("click",function(){
          var par = $(this).parent();
          par = $(par).parent();
         
          //console.log($(par).attr("data-url"));
          if($("#rptuploadbarmask"+index).html()=="start"){
              $("#rptuploadbarmask"+index).html("uploading");
              var fd = new FormData();
              fd.append("fileToUpload"+index, $('#fileToUpload'+index)[0].files[0]);
              var csrf_token = $(par).attr('data-csrf');
              fd.append('csrfmiddlewaretoken', csrf_token);
              
              var xhr = new XMLHttpRequest();
              xhr.upload.addEventListener("progress", function(evt){
                  percentComplete = parseInt(evt.loaded/evt.total*100);
                  $("#rptuploadbarvalue"+index).css({"width":percentComplete + "%"});
                  $("#rptuploadbar"+index).css("pointer-events","none");
                  $("#fileToUpload"+index).css("pointer-events","none");
                  console.log("uploaded: " + evt.loaded + "bytes");
                  }, false);

              xhr.addEventListener("load", function(evt){
                  console.log(evt);
                  var valid = true;
                  var error = new Array();
                  responseObj = JSON.parse(evt.target.responseText);
                  if ($(par).attr("data-validate")=="true") {
                      try {
                          console.log("message: "+ responseObj.message);
                          console.log("bytes_sent: " + uploadsize);
                          console.log("bytes_received: "+ responseObj.bytes_received);
                          console.log("id: "+ responseObj.id);
                          console.log("success: "+ responseObj.success);
                          
                          if (typeof responseObj.bytes_received === "undefined")
                              console.log("Enforced validation but file handler did not return a 'bytes_received' instance");
                          else
                              if (uploadsize!=responseObj.bytes_received){
                                  popup("<h4>Error</h4><br/>The server did not receive a full payload, please try again");  
                                  valid = false;                 
                              }
                          if (responseObj.message && responseObj.message!=""){
                            $("#rptmessageboxbody"+index).html(responseObj.message);
                            $("#rptmessageboxbackground"+index).fadeIn("100");
                          }
                      }
                      catch(e) {
                          popup("<h4>Error</h4><br/>The server reported an unknown error:<br/>"+e.message);
                          valid = false;
                      }
                  }
                  if (valid==true){
                      if (responseObj.redirect_to && responseObj.redirect_to.trim()!="")
                          window.location = responseObj.redirect_to;
                      $("#rptuploadbarmask"+index).html("<span style='position:relative; top:-8px;'>upload complete</span><br/><span style='position:relative; top:-8px;font-size:16px'>(click to upload again)</span>");
                      if ($(par).attr("data-success"))
                          eval($(par).attr("data-success")+"(responseObj)")
                  }
                  else
                      $("#rptuploadbarmask"+index).html("<span style='position:relative; top:-8px'>Error Uploading</span><br/><span style='position:relative; top:-8px;font-size:16px'>(click to try again)</span>");
                  //-- post back to div ---
                  /*var attribute = $(par).attr("onSubmit");
                
                  attribute = attribute.replace(/\^/g,evt.target.responseText[0]); // change response to whatever you want the user too sea
                  $(par).attr("onSubmit",attribute);
                  $(par).trigger('submit');*/
                  //------------------------
                  $("#rptuploadbar"+index).css("pointer-events","auto");
                  $("#fileToUpload"+index).css("pointer-events","auto");
                  }, false);

              xhr.addEventListener("error", function(){
                  popup("<h4>Error</h4><br/> the upload encountered an unknown error");
                  $("#rptuploadbarmask"+index).html("<span style='position:relative; top:-8px;font-size:30px'>Error Uploading</span><br/><span style='position:relative; top:-8px;font-size:16px'>(click to try again)</span>");
                  }, false);
                
              xhr.addEventListener("abort", function(){
                  popup("<h4>Error</h4><br/> the upload encountered an unknown error");
                  $("#rptuploadbarmask"+index).html("<span style='position:relative; top:-8px;'>Error Uploading</span><br/><span style='position:relative; top:-8px;font-size:16px'>(click to try again)</span>");
                  }, false);
                
              var postUrl = "http://docengine-test.reportlab.com/sandbox/html5-upload/";

              if ($(par).attr("data-url"))
                  postUrl = $(par).attr("data-url");
              xhr.open("POST", postUrl);
              xhr.send(fd);
          }
          else {
              build();
                /*$('.rptdropclass'+index).fadeOut('fast', function() {
                  $("#rptuploadbarmask"+index).html("start");
                  $("#rptuploadbarvalue"+index).css("width","0%");
                  $("#rptdropmessage"+index).fadeIn('fast');
                });*/
          }
      });
      $("#fileToUpload"+index).on("drop",function(){
          $('#mask'+index).css('border-color', '#cccccc');
      });
      
      $("#fileToUpload"+index).on("dragleave",function(){
          $('#mask'+index).css('border-color', '#cccccc');
      });
      
      $("#fileToUpload"+index).on("dragenter",function(){
          $('#mask'+index).css('border-color', '#BADA55');
      });
      
      $("#fileToUpload"+index).on("change",function(){
          var par = $(this).parent();
          var file = document.getElementById('fileToUpload'+index).files[0];
              if (file) {
                  var fullname = file.name;
                  var extentionArray = file.name.split(".")
                  var extention = extentionArray[extentionArray.length-1];
                  var filesizeReadable;
                  var filesizecheck = 50*1000*1000;
                  if ($(par).attr("data-size-limit")){
                    //console.log($(par).attr("data-size-limit"));
                    filesizecheck = $(par).attr("data-size-limit")*1000*1000;
                  }
                  if (file.size>1000*1000)
                      filesizeReadable = Math.round(file.size/(1000*1000) * 100) / 100 + (" MB");
                  else
                      filesizeReadable = Math.round(file.size/(1000) * 100) / 100 + (" KB");
                  //console.log(filesizeReadable); 
                  console.log($.inArray(extention, mimeArray));

                  if (($.inArray(extention, mimeArray)!=-1 || $(par).attr("data-filter")==undefined)&&(file.size <= filesizecheck)){
                      if (isFullWidget) {
                          var img;
                          if (file.type.match('image.*')) {
                              if (window.File && window.FileReader && window.FileList && window.Blob) {
                                  var reader = new FileReader();

                                  // Closure to capture the file information.
                                  reader.onload = (function(theFile) {
                                      return function(e) {
                                          img = e.target.result
                                      };
                                  })(file);

                                  // Read in the image file as a data URL.
                                  reader.readAsDataURL(file);
                                };
                          } else
                              switch(extention){
                                  case "pdf":
                                      img = "http://thecustomizewindows.com/wp-content/uploads/2011/03/Adobe-PDF-Logo.jpg";
                                      break;
                                  case "xlsx":
                                      img = "http://www.progressivetraining.ie/wp-content/uploads/2009/06/excel-logo.png"
                                      break;
                                  default:
                                      img = "http://www.psdgraphics.com/file/blank-document.jpg";
                              }
                          $("#docext"+index).attr("src",img);
                          $('#rptdropmessage'+index).fadeOut('500', function() {
                              $("#rptfilename"+index).text(file.name);
                              $("#rptFileSize"+index).html(filesizeReadable);
                              $("#rptuploadfiletype"+index).html(extention);
                              $("#rptuploadbarmask"+index).html("start");
                              $(".rptdropclass"+index).fadeIn('500');
                          })
                      }
                      else 
                          $('#rptdropmessage'+index).fadeOut('500', function() {
                              $("#rptuploadbarmask"+index).html("start");
                              $(".rptdropclass"+index).fadeIn('500');
                          });
                      resizeFont($("#rptfilename"+index),1);
                      console.log('Name: ' + file.name);
                      console.log('Size: ' + file.size);
                      console.log('Type: ' + file.type);
                      uploadsize=file.size;
                  }
                  else {
                      if (file.size > filesizecheck)
                          popup("<h4>file too large</h4><br/> please select a file less than "+filesizecheck/(1000*1000) + "MB");
                      else
                        if ($.inArray(extention, mimeArray)!=-1)
                            popup("<h4>wrong file type</h4> <br/>You selected a <b>"+extention+"</b> file,<br/> please select a <b>" + $(par).attr("data-filter") +"</b> file type.");
                  }
            }
        })
    });
}

