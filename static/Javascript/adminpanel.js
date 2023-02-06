function select_type(){
    document.getElementById("types").style.display = "inline"
    document.getElementById("btn_types").onclick = hide_btns


}
function  hide_btns(){
    document.getElementById("types").style.display = "none"
    document.getElementById("btn_types").onclick  = select_type
}
