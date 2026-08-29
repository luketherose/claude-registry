package com.example.shop

import jakarta.persistence.Entity
import jakarta.persistence.Id
import java.util.Optional
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

// data class used as a JPA entity: equals/hashCode and copy() break identity semantics
@Entity
data class OrderEntity(
    @Id var id: Long? = null,
    var total: Double = 0.0,
    var status: String = "NEW"
)

@Service
class OrderService {

    @Autowired
    lateinit var repository: OrderRepository

    @Autowired
    lateinit var gateway: PaymentGateway

    private var lastOrder: OrderEntity? = null

    // Java-style accessors carried into Kotlin
    fun getLastOrder(): OrderEntity? = lastOrder
    fun setLastOrder(o: OrderEntity?) { lastOrder = o }

    @Throws(PaymentException::class)
    fun place(customerId: Long?, total: Double?): Optional<OrderEntity> {
        val id = customerId!!
        val amount = total!!

        val customer = repository.findCustomer(id)!!
        if (customer.email!!.isEmpty()) {
            throw PaymentException("missing email")
        }

        val order = OrderEntity(null, amount, "CONFIRMED")
        repository.save(order)
        setLastOrder(order)
        return Optional.of(order)
    }
}
