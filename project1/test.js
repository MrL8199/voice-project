function getAllUrls(FEED_URL){
    $.get(FEED_URL, function (data) {
        $(data).find("item").each(function () {
            var el = $(this);
            console.log(el.find("link").text);
        });
    });   
}