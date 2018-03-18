// Here You can type your custom JavaScript..
   

var field_email = document.getElementById('field_email');
var field_password = document.getElementById('field_password');
var login_button = $x("//*[contains(@data-l,'loginButton')]")[0];

var XHR = ("onload" in new XMLHttpRequest()) ? XMLHttpRequest : XDomainRequest;
var xhr = new XHR();

xhr.onload = function() {
  alert( this.responseText );
}


xhr.onerror = function() {
  console.log( 'Ошибка ' + this.status );
}

// field_email.addEventListener('mousemove', getStat, false);
// field_password.addEventListener('mousemove', getStat, false);
// login_button.addEventListener('mousemove', getStat, false);

document.addEventListener('mousemove', getStat, false);

function getOffset( el ) {
    var _x = 0;
    var _y = 0;
    while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
        _x += el.offsetLeft - el.scrollLeft;
        _y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return { top: _y, left: _x };
}
var x = getOffset( document.getElementById('yourElId') ).left; 

function getStat(event) {  
    
    event.stopPropagation();
    
    var x = event.pageX;
    var y = event.pageY;
  
    var pos = getOffset(event.target);
    var elem_y1 = pos.top;
    var elem_y2 = elem_y1 + event.target.offsetHeight;
    var elem_x1 = pos.left;
    var elem_x2 = elem_x1 + event.target.offsetWidth;
    
    var response = {};
    
    response.target_id = event.target.id;    
    response.target_type = event.target.type;  
    response.target_value = event.target.value;      
    response.element_position_top_left = elem_x1 + ", " + elem_y1;
    response.element_position_bottom_right = elem_x2 + ", " + elem_y2;
    response.mouse_position = x + ", " + y;
    
    var r_tl_x = x-elem_x1;
    var r_tl_y = y-elem_y1;
    var r_br_x = elem_x2-x;
    var r_br_y = elem_y2-y;
    
    response.relative_to_tl = r_tl_x + ", " + r_tl_y;
    response.relative_to_br = r_br_x + ", " + r_br_y;
    
    if(r_tl_x == 0 || r_tl_y == 0 || r_br_x == 0 || r_br_y == 0)
    {
        response.warning = "HIT THE BORDER!";
    }
    
    console.log(response);
    
    xhr.open("POST", "http://127.0.0.1:8080/", true);
    xhr.send(JSON.stringify(response));
}