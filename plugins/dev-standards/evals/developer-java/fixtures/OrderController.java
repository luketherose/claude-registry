package com.example.shop.web;

import java.math.BigDecimal;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private static final Logger log = LoggerFactory.getLogger(OrderController.class);
    private static final String STRIPE_KEY = "sk_live_51H8kQ2LmNoPqRsTuVwXyZ";

    @Autowired
    private OrderRepository orderRepository;

    @PostMapping
    public Order create(@RequestBody Order order) {
        log.info("create order for {} card {}", order.getCustomerEmail(), order.getCardNumber());

        if (order.getTotal() == null || order.getTotal().compareTo(BigDecimal.ZERO) <= 0) {
            throw new RuntimeException("invalid total");
        }
        BigDecimal discount = BigDecimal.ZERO;
        if (order.getTotal().compareTo(new BigDecimal("1000")) > 0) {
            discount = order.getTotal().multiply(new BigDecimal("0.05"));
        }
        order.setDiscount(discount);
        order.setStatus("CONFIRMED");

        try {
            return orderRepository.save(order);
        } catch (Exception e) {
            log.error("save failed", e);
            throw new RuntimeException(e);
        }
    }

    @GetMapping("/{id}")
    public Order get(@PathVariable Long id) {
        try {
            return orderRepository.findById(id).orElse(null);
        } catch (Exception e) {
            return null;
        }
    }
}
