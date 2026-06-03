---
name: dev-k8s-operator
description: Develop Kubernetes operator features with proper reconciliation patterns, CRD design, and testing. Use when writing K8s controller/operator code.
argument-hint: "[feature-description]"
---

# Kubernetes Operator Development

Implement the following operator feature: **$ARGUMENTS**

## Development Workflow

1. **Define CRD types** — Spec, Status, validation markers
2. **Write controller test** — using envtest
3. **Implement reconciler** — idempotent reconciliation loop
4. **Generate manifests** — `make manifests` to update CRDs, RBAC
5. **Test with kind** — deploy and verify end-to-end

## CRD Design Patterns

### Spec Design
```go
type MyAppSpec struct {
    // +kubebuilder:validation:MinLength=1
    // +kubebuilder:validation:Required
    Name string `json:"name"`

    // +kubebuilder:validation:Minimum=1
    // +kubebuilder:validation:Maximum=10
    // +kubebuilder:default=1
    Replicas *int32 `json:"replicas,omitempty"`

    // +kubebuilder:validation:Enum=ClusterIP;NodePort;LoadBalancer
    // +kubebuilder:default=ClusterIP
    ServiceType corev1.ServiceType `json:"serviceType,omitempty"`

    // +kubebuilder:validation:Optional
    Resources corev1.ResourceRequirements `json:"resources,omitempty"`
}
```

### Status with Conditions
```go
type MyAppStatus struct {
    // Standard Kubernetes conditions
    Conditions []metav1.Condition `json:"conditions,omitempty"`

    // +kubebuilder:validation:Enum=Pending;Running;Failed;Degraded
    Phase string `json:"phase,omitempty"`

    // Track what was last applied for drift detection
    ObservedGeneration int64  `json:"observedGeneration,omitempty"`
    ReadyReplicas      int32  `json:"readyReplicas,omitempty"`
}
```

### Print Columns
```go
// +kubebuilder:printcolumn:name="Status",type=string,JSONPath=`.status.phase`
// +kubebuilder:printcolumn:name="Ready",type=integer,JSONPath=`.status.readyReplicas`
// +kubebuilder:printcolumn:name="Age",type=date,JSONPath=`.metadata.creationTimestamp`
// +kubebuilder:subresource:status
type MyApp struct { ... }
```

## Reconciler Pattern

```go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // 1. Fetch the CR
    var app myappv1.MyApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. Handle deletion with finalizer
    if !app.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, &app)
    }
    if err := r.ensureFinalizer(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    // 3. Reconcile child resources (idempotent)
    if err := r.reconcileDeployment(ctx, &app); err != nil {
        return r.updateStatusFailed(ctx, &app, "DeploymentFailed", err)
    }
    if err := r.reconcileService(ctx, &app); err != nil {
        return r.updateStatusFailed(ctx, &app, "ServiceFailed", err)
    }

    // 4. Update status
    return r.updateStatusReady(ctx, &app)
}
```

### Resource Builder Pattern
```go
func (r *MyAppReconciler) reconcileDeployment(ctx context.Context, app *myappv1.MyApp) error {
    desired := r.buildDeployment(app)

    // Set owner reference for garbage collection
    if err := ctrl.SetControllerReference(app, desired, r.Scheme); err != nil {
        return err
    }

    // CreateOrUpdate — idempotent
    existing := &appsv1.Deployment{}
    err := r.Get(ctx, client.ObjectKeyFromObject(desired), existing)
    if apierrors.IsNotFound(err) {
        return r.Create(ctx, desired)
    }
    if err != nil {
        return err
    }

    // Update only if spec changed
    existing.Spec = desired.Spec
    return r.Update(ctx, existing)
}
```

## Testing with envtest

```go
var _ = Describe("MyApp Controller", func() {
    ctx := context.Background()

    It("should create deployment when CR is created", func() {
        app := &myappv1.MyApp{
            ObjectMeta: metav1.ObjectMeta{Name: "test", Namespace: "default"},
            Spec: myappv1.MyAppSpec{Name: "test", Replicas: ptr.To(int32(2))},
        }
        Expect(k8sClient.Create(ctx, app)).To(Succeed())

        // Wait for reconciliation
        deployment := &appsv1.Deployment{}
        Eventually(func() error {
            return k8sClient.Get(ctx, client.ObjectKey{Name: "test", Namespace: "default"}, deployment)
        }, timeout, interval).Should(Succeed())

        Expect(*deployment.Spec.Replicas).To(Equal(int32(2)))
    })

    It("should update status conditions", func() {
        // ...verify status is set correctly after reconciliation
    })
})
```

## Rules
- Reconciliation MUST be idempotent
- Always use status conditions (`metav1.Condition`)
- Set owner references for all child resources
- Use finalizers for cleanup on deletion
- Never block reconcile loop — requeue with backoff
- Handle `IsNotFound` gracefully (resource may be deleted mid-reconcile)
- Use `ObservedGeneration` for drift detection
- Log with structured `logr` logger
- RBAC: request minimum permissions, annotate with `// +kubebuilder:rbac:...`
- Run `make manifests` after changing types or RBAC markers
