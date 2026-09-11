"""Unit test untuk Operational Guard (klasifikasi risiko aksi & persetujuan per-aksi)."""

import unittest

from self_learning.operational_guard import (
    ActionAssessment,
    ActionGuard,
    ApprovalRegistry,
    ConfirmationRequiredError,
    RiskLevel,
)


class TestActionGuardClassification(unittest.TestCase):
    def assertRisk(self, command: str, expected: RiskLevel) -> ActionAssessment:
        assessment = ActionGuard.assess(command)
        self.assertEqual(assessment.risk, expected, f"{command!r} -> {assessment.reasons}")
        return assessment

    def test_safe_commands(self):
        for cmd in [
            "ls -la", "git status", "git log --oneline -5", "grep -rn foo src/",
            "python -m unittest discover", "cat README.md", "Get-ChildItem", "echo hello",
            "git diff --cached", "docker ps", "pm2 ls", "curl https://example.com/health",
            "python script.py > /dev/null", "npm test", "",
        ]:
            assessment = self.assertRisk(cmd, RiskLevel.SAFE)
            self.assertFalse(assessment.requires_confirmation)
            self.assertEqual(assessment.reasons, ())

    def test_reversible_commands(self):
        for cmd in [
            "git commit -m 'x'", "git add -A", "git checkout -b feature", "mkdir build",
            "pip install requests", "npm install", "sed -i 's/a/b/' file.txt",
            "echo data > out.txt", "cp a.txt b.txt", "pm2 restart api", "docker compose up -d",
            "git rm old.py", "git stash",
        ]:
            assessment = self.assertRisk(cmd, RiskLevel.REVERSIBLE)
            self.assertFalse(assessment.requires_confirmation)

    def test_outward_commands_require_confirmation(self):
        for cmd in [
            "git push origin main", "git push", "gh pr create --fill", "npm publish",
            "curl -X POST https://api.example.com/deploy", "curl -d '{}' https://hooks.example.com",
            "Invoke-RestMethod -Uri https://x -Method Post", "docker push repo/img:1",
            "ssh vps 'sudo systemctl restart nginx'", "scp build.zip ubuntu@host:/srv/",
            "kubectl apply -f deploy.yaml",
        ]:
            assessment = self.assertRisk(cmd, RiskLevel.OUTWARD)
            self.assertTrue(assessment.requires_confirmation)
            self.assertTrue(assessment.reasons)

    def test_irreversible_commands_require_confirmation(self):
        for cmd in [
            "rm -rf build/", "rm -fr node_modules", "rm -r tmp", "Remove-Item .\\dist -Recurse -Force",
            "git reset --hard HEAD~1", "git checkout -- src/app.py", "git restore .", "git clean -fd",
            "git push --force origin main", "git push -f", "git branch -D feature", "git stash drop",
            "DROP TABLE users;", "TRUNCATE TABLE logs", "DELETE FROM users;", "UPDATE users SET active=0;",
            "pm2 delete api", "docker system prune -af", "terraform destroy", "dd if=/dev/zero of=/dev/sda",
        ]:
            assessment = self.assertRisk(cmd, RiskLevel.IRREVERSIBLE)
            self.assertTrue(assessment.requires_confirmation)

    def test_sql_with_where_and_staged_restore_are_not_irreversible(self):
        self.assertRisk("DELETE FROM users WHERE id = 1;", RiskLevel.SAFE)
        self.assertRisk("UPDATE users SET active = 0 WHERE id = 1;", RiskLevel.SAFE)
        self.assertRisk("git restore --staged file.py", RiskLevel.SAFE)
        self.assertRisk("git push --dry-run", RiskLevel.OUTWARD)  # tetap outward, bukan irreversible

    def test_compound_command_takes_highest_risk(self):
        assessment = self.assertRisk("git status && rm -rf build && git push", RiskLevel.IRREVERSIBLE)
        self.assertIn("hapus berkas rekursif/paksa (rm -r/-f)", assessment.reasons)
        self.assertRisk("pytest; git commit -am fix; git push origin main", RiskLevel.OUTWARD)
        self.assertRisk("cat a.txt | tee b.txt", RiskLevel.REVERSIBLE)

    def test_force_push_is_irreversible_with_single_reason_set(self):
        assessment = self.assertRisk("git push --force-with-lease origin main", RiskLevel.IRREVERSIBLE)
        self.assertEqual(assessment.reasons, ("force push menimpa riwayat remote",))

    def test_assess_many_preserves_order(self):
        results = ActionGuard.assess_many(["ls", "git push", "rm -rf x"])
        self.assertEqual([r.risk for r in results], [RiskLevel.SAFE, RiskLevel.OUTWARD, RiskLevel.IRREVERSIBLE])


class TestApprovalAndEnforcement(unittest.TestCase):
    def test_enforce_passes_safe_and_reversible_without_approval(self):
        self.assertEqual(ActionGuard.enforce("git status").risk, RiskLevel.SAFE)
        self.assertEqual(ActionGuard.enforce("git commit -m x").risk, RiskLevel.REVERSIBLE)

    def test_enforce_blocks_unapproved_outward_and_irreversible(self):
        with self.assertRaises(ConfirmationRequiredError) as ctx:
            ActionGuard.enforce("git push origin main")
        self.assertIn("OUTWARD", str(ctx.exception))
        self.assertIn("push ke remote", str(ctx.exception))
        self.assertTrue(issubclass(ConfirmationRequiredError, PermissionError))

        with self.assertRaises(ConfirmationRequiredError):
            ActionGuard.enforce("rm -rf /tmp/x", ApprovalRegistry())  # registry kosong

    def test_approval_is_exact_and_single_use(self):
        approvals = ApprovalRegistry()
        approvals.grant("git  push   origin main")  # spasi dinormalisasi
        self.assertTrue(approvals.is_approved("git push origin main"))
        # Persetujuan tidak berlaku untuk perintah lain (OP-5.1)
        self.assertFalse(approvals.is_approved("git push origin develop"))
        with self.assertRaises(ConfirmationRequiredError):
            ActionGuard.enforce("git push origin develop", approvals)

        # Dipakai sekali -> hangus
        self.assertEqual(ActionGuard.enforce("git push origin main", approvals).risk, RiskLevel.OUTWARD)
        self.assertFalse(approvals.is_approved("git push origin main"))
        with self.assertRaises(ConfirmationRequiredError):
            ActionGuard.enforce("git push origin main", approvals)

    def test_revoke_all(self):
        approvals = ApprovalRegistry()
        approvals.grant("rm -rf build")
        approvals.revoke_all()
        self.assertFalse(approvals.consume("rm -rf build"))


if __name__ == "__main__":
    unittest.main()
