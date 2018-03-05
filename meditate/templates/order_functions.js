<!--    This is a javascript library which makes use of django template tags to set the URLs
        for API endpoints instead of hard-coding them.
-->
<script type='text/javascript'>
    function updateOrderCount() {
        // Collects the current item total and updates the 'OrderCount' element with that value.
        $.ajax({
            type: "GET",
            url: "{% url 'all_item_count' %}",
            success: function(data) {
                document.getElementById('OrderCount').innerHTML = data.count;
                 if(data.count === 0){
                    $('#emptyCart').addClass('active');
                    $('#orderContent').removeClass('active');
                }
                else{
                    $('#orderContent').addClass('active');
                    $('#emptyCart').removeClass('active');
                }
            },
        });
    }

    function AddToCart(saleItemName, callback=null) {
        // Increases the count of saleItemName by one.
        addItemUrl = "{% url 'add_order_item' 'saleItemName' %}"
        addItemUrl = addItemUrl.replace('saleItemName', saleItemName)

        $.ajax({
           type: 'GET',
           url: addItemUrl,
           success: function(responsedata) {
               updateOrderCount();
               if (callback != null) {
                 callback();
               }
           },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                    var msg = `Unable to add "${saleItemName}" to cart` 
                    alert(msg); // TODO: Remove this.
                    var logUrl = '{% url "log_javascript" "msgPlaceholder" %}'
                    logUrl = logUrl.replace('msgPlaceholder', msg)

                    $.ajax({
                        type: 'GET',
                        url: logUrl,
                    });
                    if (callback != null) {
                        callback();
                    }
            }
        })
    }

    function RemoveFromCart(saleItemName, callback=null) {
        // Decreases the count of saleItemName by one.
        removeItemUrl = "{% url 'remove_order_item' 'saleItemName' %}"
        removeItemUrl = removeItemUrl.replace('saleItemName', saleItemName)

        $.ajax({
           type: 'GET',
           url: removeItemUrl,
           success: function(responsedata) {
               updateOrderCount();
               if (callback != null) {
                 callback();
               }
           },
       error: function(XMLHttpRequest, textStatus, errorThrown) {
               var msg = `Unable to remove "${saleItemName}" to cart` 
               alert(msg); // TODO: Remove this.
               var logUrl = '{% url "log_javascript" "msgPlaceholder" %}'
               logUrl = logUrl.replace('msgPlaceholder', msg)

               $.ajax({
                   type: 'GET',
                   url: logUrl,
               });
               if (callback != null) {
                 callback();
               }
           }
        })
    }
</script>
