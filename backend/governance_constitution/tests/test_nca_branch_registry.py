from governance_constitution.nca.branch_registry import ECC_ORIGIN, NCA_BRANCH_LICENSES


def test_no_branch_license_alias_mismatch() -> None:
    for branch_id, branch_license in NCA_BRANCH_LICENSES.items():
        assert branch_license.branch_id == branch_id
        assert branch_license.branch == branch_id


def test_all_nca_branches_licensed_from_ecc_origin() -> None:
    for branch_license in NCA_BRANCH_LICENSES.values():
        assert branch_license.origin.origin_id == ECC_ORIGIN.origin_id == "ECC"
        assert branch_license.effective_attribute is not None
        assert branch_license.sabab is not None
        assert branch_license.conditions
        assert branch_license.mani
        assert branch_license.qadih_differences
