"""
simulation.py

Inventory simulation engine for supply chain policy evaluation.
Simulates daily inventory dynamics using a reorder point policy.
"""

import numpy as np


def simulate_inventory(demand_series, forecast_series, safety_stock_multiplier,
                       lead_time, order_quantity, reorder_point, hc_rate, p99_demand):
    """
    Simulate inventory dynamics for one product-store combination.

    Parameters
    ----------
    demand_series : array — actual daily demand
    forecast_series : array — model forecast
    safety_stock_multiplier : float — 1.0 = baseline, 1.5 = treatment
    lead_time : int — days between order and receipt
    order_quantity : int — units per replenishment order
    reorder_point : float — inventory level that triggers reorder
    hc_rate : float — holding cost per unit per day
    p99_demand : float — 99th percentile demand cap

    Returns
    -------
    dict of simulation outcome metrics
    """
    n_days = len(demand_series)

    # Adjust reorder point by safety stock multiplier
    adjusted_reorder = reorder_point * safety_stock_multiplier

    # Initialize inventory
    inventory = adjusted_reorder + order_quantity

    # Track pending orders: {arrival_day: quantity}
    pending_orders = {}

    # Outcome tracking
    stockout_days = 0
    units_lost    = 0
    total_holding = 0.0
    units_sold    = 0

    for day in range(n_days):
        # Receive pending orders
        if day in pending_orders:
            inventory += pending_orders.pop(day)

        # Cap demand at 99th percentile
        demand = min(float(demand_series[day]), p99_demand)
        demand = max(0, demand)

        # Fulfill demand
        if demand <= inventory:
            inventory -= demand
            units_sold += demand
        else:
            units_sold  += inventory
            units_lost  += demand - inventory
            inventory    = 0
            stockout_days += 1

        # Holding cost
        total_holding += inventory * hc_rate

        # Reorder check
        if inventory <= adjusted_reorder and day not in [
            v for v in range(day, day + lead_time) if v in pending_orders
        ]:
            arrival_day = day + lead_time
            pending_orders[arrival_day] = order_quantity

    total_demand = units_sold + units_lost

    return {
        'stockout_days':      stockout_days,
        'stockout_rate':      stockout_days / n_days if n_days > 0 else 0,
        'units_lost':         units_lost,
        'units_sold':         units_sold,
        'fill_rate':          units_sold / total_demand if total_demand > 0 else 1.0,
        'total_holding_cost': total_holding,
        'avg_holding_cost':   total_holding / n_days if n_days > 0 else 0,
        'n_days':             n_days
    }