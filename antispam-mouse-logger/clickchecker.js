'allow pasting'

var mainContent = document.getElementById('mainContent');
mainContent.addEventListener("click", determineElement);
mainContent.addEventListener("mousemove", mouseMoveEvent);
OK.hookModel.addActivityAidToNextRequest(function() {console.log("hello");})

OK.onload.addCallback(function() {
    console.log("Onload");
});

function determineElement(e) {
    var el = e.target;
    if (        
        !!el.closest('[data-module = "LikeComponent"]') || 
        !!el.closest('input') ||
        !!el.closest('a') ||
        !!el.closest('img')
        )
    {
        getStat(e);   
    }
}

function getOffset( el ) {
    var x = 0;
    var y = 0;
    while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
        x += el.offsetLeft - el.scrollLeft;
        y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return { top: y, left: x };
}

function getStat(event) {      
    var mouse_x = event.pageX;
    var mouse_y = event.pageY;
  
    var pos = getOffset(event.target);
    var elem_y1 = pos.top;
    var elem_y2 = elem_y1 + event.target.offsetHeight;
    var elem_x1 = pos.left;
    var elem_x2 = elem_x1 + event.target.offsetWidth;
    
    var info = {};
    
    info.stat_type = "click";
    info.element_id = event.target.id;
    info.element_class_name = event.target.className; 
    info.element_tag_name = event.target.tagName; 
    info.element_oktarget = event.okTarget;
    info.element_position_top_left_x = elem_x1;
    info.element_position_top_left_y = elem_y1;
    info.element_position_bottom_right_x = elem_x2;
    info.element_position_bottom_right_y = elem_y2;
    info.mouse_position_x = mouse_x;
    info.mouse_position_y = mouse_y;
    info.window_width = window.innerWidth;
    info.window_height = window.innerHeight;
    info.client_timestamp = event.timeStamp;   
    
    console.log(info);
    
    //xhr.open("POST", "http://127.0.0.1:8080/", true);
    //xhr.send(info);
}

(function() {
    var cssLoadDurations = Object.values(OK.perf.cssEntries).map(v => v.duration);
    var info = {};
    info.stat_type = "css_load";
    info.max_css_load_duration = Math.max(...cssLoadDurations);
    info.min_css_load_duration = Math.min(...cssLoadDurations);
    
    console.log(info);
    
    //xhr.open("POST", "http://127.0.0.1:8080/", true);
    //xhr.send(info);
})();

function mouseMoveEvent(e) {
    mainContent.removeEventListener(e.type, arguments.callee);
    
    var info = {};
    info.stat_type = "mouse_move";
    info.window_width = window.innerWidth;
    info.window_height = window.innerHeight;
    info.mouse_position_x = e.pageX;
    info.mouse_position_y = e.pageY;
    info.client_timestamp = event.timeStamp;   
    
    console.log(info);
    
    //xhr.open("POST", "http://127.0.0.1:8080/", true);
    //xhr.send(info);
};


/*
Exception: SyntaxError: missing ) after argument list
@Scratchpad/1:11
*/