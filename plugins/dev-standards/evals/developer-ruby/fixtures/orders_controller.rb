class String
  def to_money
    "%.2f" % to_f
  end
end

class OrdersController < ApplicationController
  before_action :load_order, only: [:show, :update]
  before_action :apply_discount, only: [:update]
  before_action :recalculate_totals, only: [:update]
  before_action :notify_warehouse, only: [:update]

  def index
    @orders = Order.where("status = 'NEW'").where("total > 1000").order("created_at DESC")
    render json: @orders
  end

  def update
    @order.status = params[:status]
    @order.save
    render json: @order
  rescue Exception => e
    Rails.logger.error e
    render json: { error: e.message }, status: 500
  end

  private

  def load_order
    @order = Order.where(id: params[:id]).first
  end

  def apply_discount
    @order.discount = @order.total > 1000 ? @order.total * 0.05 : 0
    @order.save!
  end

  def recalculate_totals
    @order.total = @order.line_items.map { |i| i.price * i.qty }.sum - @order.discount
    @order.save!
  end

  def notify_warehouse
    WarehouseClient.new.notify(@order)
  end
end
