<!--

Date.prototype.format = function() 
{
    year = this.getFullYear();
    month = this.getMonth() + 1;
    day = this.getDate();

    if (month < 10)
        month = "0" + month;
    if (day < 10)
        day = "0" + day;

    return (year + "-" + month + "-" + day);
}

//-->
