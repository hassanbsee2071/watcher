#!/bin/bash

namespace="activity"
configmaps=("activity-booking-configmap" "activity-cache-indexer-configmap" "activity-cart-service-configmap" "activity-content-api-configmap" "activity-gateway-configmap" "activity-klook-adapter-configmap" "activity-marketing-service-configmap" "activity-order-service-configmap" "activity-post-order-configmap" "activity-price-availability-configmap" "activity-repository-configmap" "activity-scheduler-configmap" "activity-sync-configmap" "activity-utility-configmap" "activity-webhook-configmap")

for configmap in "${configmaps[@]}"; do
    kubectl edit configmap -n $namespace "$configmap"
    
done
