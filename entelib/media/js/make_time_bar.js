<!--

make_time_bar = function(array, i, item_last_day, item_id)
{
    one_day = 86400000;

    today = new Date();
    today = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    
    temp = item_last_day;//array[i-1][1];
    temp = temp.split("-");
    last_day = new Date(parseInt(temp[0], 10), parseInt(temp[1], 10) - 1, parseInt(temp[2], 10));
    last = last_day.format();
    
    $("#tr_range").html("<td style='text-align: left; border: 0' colspan='6'>Today</td>" + 
                        "<td style='text-align: right; border: 0'>" + 
                        last + "</td>");
                        
    period = (last_day - today) / one_day + 1;
    len = $("table.booklist").width();
    day_len = len / period;
    //len = Math.floor(day_len * period);
    
    to_next_date = today;
    to_next = "Today";
    to_date = today;
    
    str =   "<td colspan='7' style='padding: 0; margin: 0;' class='no_padding_and_margin'>" + 
            "<table style='border: solid 1px; height: 1em' width='" + 
            len + 
            "px'><tr>";
    
    $.each(array, function(index, value)
    {
        temp = value[0];
        temp = temp.split("-");
        from_date = new Date(parseInt(temp[0], 10), parseInt(temp[1], 10) - 1, parseInt(temp[2], 10));
        from = from_date.format();
        from_prev_date = new Date(from_date.getTime() - one_day);
        from_prev = from_prev_date.format();
        
        interval = (from_prev_date - to_next_date) / one_day + 1;
        td_len = Math.floor(interval * day_len);
        if (td_len != 0)
            str +=  "<td class='green' width='" + 
                    td_len + "px'><input type='hidden' name='val', value='Rentable<br>" + 
                    to_next + " : " + 
                    from_prev + 
                    "'></td>";
        
        temp = value[1];
        temp = temp.split("-");
        to_date = new Date(parseInt(temp[0], 10), parseInt(temp[1], 10) - 1, parseInt(temp[2], 10));
        to = to_date.format();
        
        to_next_date = new Date(to_date.getTime() + one_day);
        to_next = to_next_date.format();
        
        interval = (to_date - from_date) / one_day + 1;
        td_len = Math.floor(interval * day_len);
        if (td_len != 0)
            str +=  "<td class='red' width='" + 
                    td_len + "px'><input type='hidden' name='val', value='Not rentable<br>" + 
                    from + " : " + to + 
                    "'></td>";
    });
    
    if (array.length > 0)
    {
        to_next_date = new Date(to_date.getTime() + one_day);
        to_next = to_next_date.format();
    }
    else
    {
        to_next_date = new Date(to_date.getTime());
        to_next = "Today";
    }
    
    interval = (last_day - to_next_date) / one_day + 1;
    td_len = Math.floor(interval * day_len);
    if (td_len != 0)
        str +=  "<td class='green width='" + 
                td_len + "px'><input type='hidden' name='val', value='Rentable<br>" + 
                to_next + " : " + last + 
               "'></td>";
    
    str += "</tr></table></td>";
    $("#" + item_id).html(str);
}

//-->
