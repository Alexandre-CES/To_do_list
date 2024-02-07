
var sideMenu = document.querySelector('#side_menu')
var ul = document.querySelector('#side_menu_ul')

var ul_visible = true

function hide_span(){
    if (ul_visible == true){
        ul.style.visibility = 'hidden'
        sideMenu.style.width = '0%'
        ul_visible = false
    }else{
        ul.style.visibility = 'visible'
        sideMenu.style.width = '60px'
        ul_visible = true
    }
}
