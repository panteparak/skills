---
name: init-k8s-operator
description: Scaffold a new Kubernetes operator using kubebuilder or operator-sdk. Use when creating a K8s custom controller or operator.
argument-hint: "[project-name] [domain] [api-version] [kind]"
disable-model-invocation: true
---

# Initialize Kubernetes Operator

Scaffold a production-grade Kubernetes operator for: **$ARGUMENTS**

## Step 1: Project Generation

Use Kubebuilder (official CNCF tool):

```bash
mkdir $0 && cd $0
kubebuilder init --domain $1 --repo github.com/<org>/$0 --owner "<org>"
kubebuilder create api --group $0 --version $2 --kind $3 --resource --controller
```

Defaults if not provided:
- domain: `example.com`
- api-version: `v1alpha1`
- kind: derive from project name (PascalCase)

If `kubebuilder` is not installed, provide installation instructions:
```bash
# macOS
brew install kubebuilder
# Linux
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)
chmod +x kubebuilder && sudo mv kubebuilder /usr/local/bin/
```

## Step 2: Project Structure

Kubebuilder generates this — enhance it:

```
$0/
├── api/
│   └── $2/
│       ├── types.go             # CRD spec and status types
│       ├── webhook.go           # Admission webhooks
│       ├── zz_generated.deepcopy.go
│       └── groupversion_info.go
├── internal/
│   ├── controller/
│   │   ├── reconciler.go        # Main reconciliation loop
│   │   ├── reconciler_test.go   # Controller tests with envtest
│   │   ├── conditions.go        # Status condition helpers
│   │   └── finalizers.go        # Finalizer logic
│   ├── domain/                  # Business logic (pure Go)
│   │   ├── service.go
│   │   └── service_test.go
│   └── resources/               # Kubernetes resource builders
│       ├── deployment.go        # Build Deployment specs
│       ├── service.go           # Build Service specs
│       └── configmap.go
├── config/
│   ├── crd/                     # Generated CRD manifests
│   ├── rbac/                    # RBAC rules
│   ├── manager/                 # Controller manager deployment
│   ├── samples/                 # Example CR YAML
│   └── default/                 # Kustomize default overlay
├── test/
│   ├── e2e/                     # End-to-end tests
│   │   └── e2e_test.go
│   └── utils/                   # Test helpers
├── hack/                        # Scripts and tools
├── Dockerfile
├── Makefile
└── PROJECT                      # Kubebuilder project metadata
```

## Step 3: CRD Design

Design the Custom Resource with:
- Clear `.spec` with validation markers (`// +kubebuilder:validation:...`)
- `.status` with conditions (use `meta/v1.Condition`)
- `// +kubebuilder:printcolumn:...` for `kubectl get` output
- `// +kubebuilder:subresource:status` for status subresource
- Default values via `// +kubebuilder:default:...`

Example pattern:
```go
type MyAppSpec struct {
    // +kubebuilder:validation:MinLength=1
    // +kubebuilder:validation:Required
    Name string `json:"name"`

    // +kubebuilder:validation:Minimum=1
    // +kubebuilder:default=1
    Replicas *int32 `json:"replicas,omitempty"`
}

type MyAppStatus struct {
    Conditions []metav1.Condition `json:"conditions,omitempty"`
    Ready      bool               `json:"ready"`
}
```

## Step 4: Reconciler Pattern

Implement the reconciler with:
- Idempotent reconciliation (same input = same output)
- Status condition updates after each reconciliation
- Finalizer for cleanup on deletion
- Proper error handling with requeue strategies
- Owner references for garbage collection
- Event recording for observability

## Step 5: Test Infrastructure

Set up:
- `envtest` for controller integration tests (spins up API server + etcd)
- Unit tests for domain logic (no K8s dependencies)
- E2E test skeleton using `kind` or `envtest`
- `Makefile` targets: `test`, `test-e2e`, `lint`

## Step 6: Documentation

- `README.md` with: purpose, prerequisites, install, usage, development
- Example CR YAML in `config/samples/`
- RBAC documentation

## Rules
- Reconciliation must be idempotent
- Always use status conditions (not custom boolean fields)
- Always set owner references for child resources
- Use finalizers for cleanup logic
- Never block the reconcile loop — requeue instead
- Handle "not found" errors gracefully (resource may be deleted)
- Use structured logging with `logr`
