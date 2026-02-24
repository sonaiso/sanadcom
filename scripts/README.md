# Utility Scripts

## SICO GRC Platform Utility Scripts

This directory contains automation scripts for various platform operations.

## Directory Structure

```
scripts/
├── debug/                          # Debugging & diagnostic scripts (dev only)
│   ├── test_api.py                 # Quick API connectivity test
│   ├── test_serialization.py       # Control serialization debug
│   ├── test_async_db.py            # Async database connectivity test
│   ├── test_control_6.py           # Control serialization debug
│   ├── check_missing.py            # Check for missing controls
│   ├── check_schema.py             # Check schema fields
│   ├── fix_async_execute.py        # Async execute migration helper
│   └── crud_endpoints_fix.py       # CRUD endpoint code snippets
├── load_sample_data.py             # Load sample data (baseline)
├── load_nca_controls.py            # Load NCA ECC/CCC/PDPL controls
├── load_official_nca_controls.py   # Load official NCA control sets
├── load_complete_controls.py       # Load complete control libraries
├── load_comprehensive_data.py      # Load comprehensive demo data
├── load_enterprise_demo.py         # Load enterprise demo data
├── load_more_data.py               # Load additional data
├── load_sample_evidence.py         # Load sample evidence
├── load_data_direct.py             # Direct database data loader
├── load_enterprise_sample_data.py  # Load enterprise sample data
├── load_evidence_data.py           # Load evidence data
├── load_missing_controls.py        # Load missing controls
├── load_saudi_frameworks.py        # Load Saudi framework controls
├── add_arabic_translations.py      # Add Arabic translations
├── build_rag_index.py              # Build AI/RAG knowledge base index
├── export_portable.py              # Export portable data package
├── generate-attestation.py         # Generate security attestation
├── generate_security_keys.ps1      # Generate security keys (Windows)
├── production_readiness_validation.py  # Validate production readiness
├── production_setup.py             # Production environment setup
├── setup_security.py               # Security configuration setup
├── validate_deployment.py          # Validate deployment
├── validate_system.sh              # System validation (Linux/macOS)
├── validate_system.ps1             # System validation (Windows)
├── demo_platform.py                # Platform demonstration script
├── start-demo.sh                   # Start demo environment
├── start-dev.ps1                   # Start dev environment (Windows)
├── deploy-launch.sh                # Deploy and launch script
├── load_demo_data.ps1              # Load demo data (Windows)
├── verify-complete-platform.sh     # Verify complete platform
├── verify-launch.sh                # Verify launch readiness
├── dev_setup.sh                    # Development setup
├── setup.sh                        # General setup
├── setup_git_config.sh             # Git configuration setup
├── setup_git_config_auto.sh        # Automatic Git configuration
├── check_conflicts.sh              # Check for Git conflicts
├── quick-start.sh                  # Quick start script
├── test-evidence-approval-setup.js # Evidence approval test setup
└── test_phase_2.1.sh               # Phase 2.1 test script
```

## Common Operations

### Load Initial Data
```bash
# Load NCA controls (ECC, CCC, PDPL)
python scripts/load_nca_controls.py

# Load sample data for development
python scripts/load_sample_data.py

# Load enterprise demo data
python scripts/load_enterprise_demo.py
```

### Build AI Index
```bash
python scripts/build_rag_index.py
```

### System Validation
```bash
# Linux/macOS
make validate
# or
./scripts/validate_system.sh

# Windows
.\scripts\validate_system.ps1
```

### Demo Environment
```bash
./scripts/start-demo.sh
```

## Script Categories

### Data Loading Scripts
Scripts for populating the database with control and compliance data.
- `load_sample_data.py` - Baseline sample data
- `load_nca_controls.py` - NCA ECC/CCC/PDPL controls
- `load_enterprise_demo.py` - Full enterprise demo dataset

### Setup Scripts
Scripts for configuring the development and production environment.
- `dev_setup.sh` - Development environment setup
- `production_setup.py` - Production environment configuration
- `setup_security.py` - Security configuration

### Validation Scripts
Scripts for verifying system health and readiness.
- `validate_system.sh` / `validate_system.ps1` - System prerequisites check
- `validate_deployment.py` - Deployment validation
- `production_readiness_validation.py` - Production readiness check

### Debug Scripts (`debug/`)
Diagnostic scripts for development troubleshooting. **Not for production use.**
See [debug/README.md](debug/README.md) for details.

## Usage Guidelines

1. **Check Environment**: Ensure you're in the correct environment before running
2. **Backup First**: Create backups before running data-modifying scripts
3. **Development Only**: Scripts in `debug/` are for development use only
4. **Windows Scripts**: Use `.ps1` variants on Windows, `.sh` on Linux/macOS

---

**Last Updated**: February 2026
