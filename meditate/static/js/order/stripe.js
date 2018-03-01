function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var handler = StripeCheckout.configure({
  key: 'pk_test_AnHLc2bnR0joVD20uza73MI5',
  image: 'https://stripe.com/img/documentation/checkout/marketplace.png',
  locale: 'auto',
  token: function(token) {
    // You can access the token ID with `token.id`.
    // Get the token ID to your server-side code for use.
    var orderTotal = getOrderTotal() * 100; // Total in USD cents.
    
    var url = '{% url "stripe_charge" %}';
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        type: 'POST',
        url: url,
        data: {'csrfmiddlewaretoken': csrftoken, 'stripeToken': token.id, 'amount': orderTotal},
        success: function(responseData){
            window.location = '{% url "order_complete" %}';
        },
        failure: function(responseData){
            window.alert("Something went wrong: " + responseData);
        }
    });
  }
});

document.getElementById('customButton').addEventListener('click', function(e) {
  // Open Checkout with further options:
  handler.open({
    name: 'JivanAmara.net',
    description: 'Your Order',
    zipCode: true,
    amount: getOrderTotal() * 100
  });
  e.preventDefault();
});

// Close Checkout on page navigation:
window.addEventListener('popstate', function() {
  handler.close();
});