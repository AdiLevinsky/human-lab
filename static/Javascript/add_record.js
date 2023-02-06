
$(document).ready(function (){
    $('#tags').css('display','none')
    $('#tags').children().css({"display":"none"})
    $('#tags').parent().find("label")[0].style.display = "none"
    for (let i=0;i < $('#record_category').find('input').length;i++)
    {
        input_id = $('#record_category').find('input')[i].id
        input_value = $('#record_category').find('input')[i].value
        $('#'+input_id).attr('onclick','add_tags("'+input_id+'","'+input_value+'")')
    }

});


function add_tags(id,value){
    var uncheck = $("input[type='checkbox'][id^=record_category]").filter(':checked')

    if (uncheck.length == 0){
            $('#tags').css('display','none')
            $('#tags').children().css({"display":"none"})
            $('#tags').parent().find("label")[0].style.display = "none"
    }
    if($('#'+id).is(':checked')){
        $('#tags').css('display','block')
        $('#tags').parent().find("label")[0].style.display = "block"
        $("input[type='checkbox'][value^="+value+"]").parent().css({"display":"block"})
    }
    else{
       $("input[type='checkbox'][value^="+value+"_]").parent().css({"display":"none"})
        $("input[type='checkbox'][value^="+value+"_]").prop('checked',false)
    }

}