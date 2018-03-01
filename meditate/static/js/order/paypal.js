function recordPayPalPayment(paymentId, amount) {
            var url = '{% url "paypal_charge" %}';
            var csrftoken = getCookie('csrftoken');
            $.ajax({
                type: 'POST',
                url: url,
                data: {'csrfmiddlewaretoken': csrftoken, 'paymentId': paymentId, 'amount': amount},
                success: function(responseData){
                    console.log('ajax success');
                    window.location = '{% url "order_complete" %}';
                },
                failure: function(responseData){
                    console.log('ajax failure');
                    window.alert("Something went wrong: " + responseData);
                }
            });
        }

        paypal.Button.render({
            env: 'sandbox', // sandbox | production

            // PayPal Client IDs
            // Create a PayPal app: https://developer.paypal.com/developer/applications/create
            client: {
                sandbox: 'AUMc2uxkRjLdFPlZGRkOIKI_D3TINTeQF6sncwR-tXZKF2gyUHsEFsjdJ74iWvkLO0ia4FOu4REEj1ky',
                production: 'ARyE8lRZLRbg0XHFMw1EmZwV1b1GtxLzhZYM_H-Q5mXaMuoi-iQn-Cah2iSBwhVBiO6v46g6puH0VVc9'
            },

            // Show the buyer a 'Pay Now' button in the checkout flow
            commit: true,

            // payment() is called when the button is clicked
            payment: function(data, actions) {
                // Create a payment object with the current order total.
                var p = {
                    payment: {
                        transactions: [
                            { amount: { total: getOrderTotal(), currency: 'USD' } }
                        ]
                    }
                };

                // Make a call to the REST api to create the payment
                return actions.payment.create(p)
            },

            // onAuthorize() is called when the buyer approves the payment
            onAuthorize: function(data, actions) {
                // Make a call to the REST api to execute the payment
                return actions.payment.execute().then(function() {
                    var amount = getOrderTotal();
                    var paymentId = data.paymentID;
                    recordPayPalPayment(paymentId, amount);
                });
            }

        }, '#paypal-button-container');