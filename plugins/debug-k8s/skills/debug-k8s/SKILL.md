---
name: debug-k8s
description: Debug Kubernetes issues including pod failures, networking, RBAC, and operator problems. Use when troubleshooting K8s deployments or operators.
argument-hint: "[symptom-or-resource]"
---

# Kubernetes Debugging

Investigate: **$ARGUMENTS**

## Debugging Flowchart

### Step 1: Identify the Problem Layer
```
Pod not running?        → Pod Debugging
Service not reachable?  → Networking Debugging
Permission denied?      → RBAC Debugging
Operator not working?   → Operator Debugging
Node issues?            → Node Debugging
```

## Pod Debugging

```bash
# 1. Check pod status
kubectl get pods -n <ns> -o wide
kubectl describe pod <pod> -n <ns>

# 2. Check events (most useful!)
kubectl get events -n <ns> --sort-by=.lastTimestamp | tail -20

# 3. Check logs
kubectl logs <pod> -n <ns>                    # Current logs
kubectl logs <pod> -n <ns> --previous         # Previous container (if restarted)
kubectl logs <pod> -n <ns> -c <container>     # Specific container (multi-container)
kubectl logs <pod> -n <ns> --since=5m         # Last 5 minutes

# 4. Check container state
kubectl get pod <pod> -n <ns> -o jsonpath='{.status.containerStatuses[*]}'

# 5. Exec into pod (if running)
kubectl exec -it <pod> -n <ns> -- /bin/sh
```

### Common Pod Issues

| Status | Cause | Fix |
|--------|-------|-----|
| `ImagePullBackOff` | Wrong image name, missing auth | Check image tag, imagePullSecrets |
| `CrashLoopBackOff` | App crashes on start | Check logs (`--previous`), check env vars, check health probes |
| `Pending` | No resources, no matching node | Check node resources, affinity rules, PVC binding |
| `OOMKilled` | Memory limit exceeded | Increase memory limit or fix memory leak |
| `CreateContainerConfigError` | Missing ConfigMap/Secret | Check referenced ConfigMaps/Secrets exist |
| `Init:Error` | Init container failing | Check init container logs specifically |

## Networking Debugging

```bash
# 1. Check service endpoints
kubectl get endpoints <service> -n <ns>
kubectl describe service <service> -n <ns>

# 2. DNS resolution (from inside a pod)
kubectl exec -it <pod> -n <ns> -- nslookup <service>.<ns>.svc.cluster.local

# 3. Test connectivity
kubectl exec -it <pod> -n <ns> -- curl http://<service>:<port>/health

# 4. Check network policies
kubectl get networkpolicies -n <ns>

# 5. Check ingress
kubectl describe ingress <ingress> -n <ns>
kubectl get events -n <ns> --field-selector involvedObject.kind=Ingress
```

## RBAC Debugging

```bash
# Check if ServiceAccount has permission
kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<ns>:<sa> -n <ns>
kubectl auth can-i create deployments --as=system:serviceaccount:default:my-operator -n default

# List roles/bindings
kubectl get roles,rolebindings -n <ns>
kubectl get clusterroles,clusterrolebindings | grep <name>

# Describe role to see permissions
kubectl describe clusterrole <role>
```

## Operator Debugging

```bash
# 1. Check operator pod
kubectl get pods -n <operator-ns> -l control-plane=controller-manager
kubectl logs -n <operator-ns> <operator-pod> -c manager

# 2. Check CRD is installed
kubectl get crds | grep <domain>

# 3. Check CR status
kubectl get <kind> -n <ns>
kubectl describe <kind> <name> -n <ns>

# 4. Check RBAC for operator
kubectl auth can-i --list --as=system:serviceaccount:<operator-ns>:<sa>

# 5. Check reconciliation events
kubectl get events -n <ns> --field-selector involvedObject.kind=<Kind>

# 6. Increase operator log verbosity (if using controller-runtime)
# Set --zap-log-level=debug in operator deployment args
```

### Common Operator Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| CR stuck in Pending | Reconciler error | Check operator logs for errors |
| Child resources not created | Missing RBAC | Add RBAC markers, run `make manifests` |
| Status not updating | Missing status subresource | Add `+kubebuilder:subresource:status` |
| Operator crash on CR create | Nil pointer in reconciler | Handle missing optional fields |
| Stale status | Not updating ObservedGeneration | Set `status.observedGeneration = cr.generation` |

## Resource Investigation

```bash
# Compare desired vs actual state
kubectl get <resource> <name> -n <ns> -o yaml | less

# Check resource quotas
kubectl describe resourcequota -n <ns>

# Check limit ranges
kubectl describe limitrange -n <ns>

# Check PVC status
kubectl get pvc -n <ns>
kubectl describe pvc <name> -n <ns>
```

## Rules
- Always check events first — they tell the story
- Check logs with `--previous` for crashed containers
- For networking: verify from inside the cluster, not outside
- For RBAC: use `kubectl auth can-i` to test permissions
- For operators: increase log verbosity before deep debugging
- Document the fix and add monitoring/alerting for the failure mode
