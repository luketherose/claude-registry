package com.example.shop.payment;

import com.example.shop.model.Address;
import com.example.shop.model.Customer;

public class PaymentClient {

    private final HttpGateway gateway;

    public PaymentClient(HttpGateway gateway) {
        this.gateway = gateway;
    }

    public ChargeResult charge(Customer customer, long amountCents) {   // line 31
        ChargeRequest request = buildRequest(customer, amountCents);
        return gateway.post("/v1/charges", request);
    }

    /**
     * Guest checkout leaves billingAddress null until the payment step completes,
     * so this dereference is only safe for customers created through the
     * registered-user flow.
     */
    private ChargeRequest buildRequest(Customer customer, long amountCents) {
        Address billing = customer.getBillingAddress();
        String country = billing.getCountry();                          // line 47
        return new ChargeRequest(customer.getId(), amountCents, country);
    }
}
