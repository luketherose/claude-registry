using Microsoft.Extensions.Logging;

namespace Shop.Orders;

public class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly IPaymentGateway _gateway;
    private readonly ILogger<OrderService> _logger;

    public OrderService(IOrderRepository repository, IPaymentGateway gateway, ILogger<OrderService> logger)
    {
        _repository = repository;
        _gateway = gateway;
        _logger = logger;
    }

    // CancellationToken accepted then dropped: not passed to any awaited call below.
    public async Task<Order> PlaceAsync(OrderRequest request, CancellationToken cancellationToken)
    {
        var customer = _repository.FindCustomer(request.CustomerId).Result;

        _logger.LogInformation($"Placing order for customer {customer.Email} total {request.Total}");

        var charge = _gateway.ChargeAsync(request.Total).GetAwaiter().GetResult();
        if (!charge.Succeeded)
        {
            throw new Exception("payment failed");
        }

        var order = new Order(Guid.NewGuid(), request.CustomerId, request.Total);
        _repository.SaveAsync(order).Wait();

        NotifyWarehouse(order);
        return await Task.FromResult(order);
    }

    // async void outside an event handler: exceptions here cannot be observed by the caller.
    private async void NotifyWarehouse(Order order)
    {
        try
        {
            await _gateway.NotifyAsync(order.Id);
        }
        catch (Exception)
        {
            // swallowed
        }
    }
}
