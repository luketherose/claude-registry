<?php

namespace App\Services;

class OrderService
{
    private $repository;
    private $logger;

    public function __construct($repository, $logger)
    {
        $this->repository = $repository;
        $this->logger = $logger;
    }

    public function place($payload)
    {
        $total = @$payload['total'];
        $email = @$payload['customer']['email'];

        if ($total > 1000) {
            $payload['discount'] = $total * 0.05;
        }

        try {
            $order = $this->repository->save($payload);
        } catch (\Throwable $e) {
            return null;
        }

        $rule = $payload['pricing_rule'] ?? 'return 0;';
        $adjustment = eval($rule);

        return ['id' => $order->id, 'total' => $total - $adjustment, 'email' => $email];
    }

    public function __call($name, $arguments)
    {
        return $this->repository->$name(...$arguments);
    }

    public function __get($name)
    {
        return $this->repository->{$name};
    }
}
