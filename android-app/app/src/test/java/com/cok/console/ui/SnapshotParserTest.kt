package com.cok.console.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SnapshotParserTest {

    @Test
    fun staleSnapshotAddsRefreshTask() {
        val stale = TriagePolicy.dataFreshness(11 * 60)

        assertEquals(Severity.ATTENTION, stale?.severity)
        assertEquals(QuickAction.REFRESH, stale?.action)
    }

    @Test
    fun expiringShieldIsUrgentAndPrecedesRoutineTasks() {
        val shield = TriagePolicy.shieldTriage(60 * 60 * 1000)
        val sorted = TriagePolicy.sort(
            listOf(
                TriageItem("今日还没签到", "", Severity.ATTENTION),
                shield,
            ),
        )

        assertEquals("保护罩即将到期", shield.title)
        assertEquals(Severity.RISK, shield.severity)
        assertEquals(OperationsFocus.SAFETY, shield.operationsFocus)
        assertEquals("保护罩即将到期", sorted.first().title)
        assertEquals(Severity.RISK, TriagePolicy.shieldSeverity(60 * 60 * 1000))
    }

    @Test
    fun shieldExpiringTodayUsesAttentionSeverity() {
        val shield = TriagePolicy.shieldTriage(4 * 60 * 60 * 1000)

        assertTrue(shield.title == "保护罩将在今天到期" && shield.severity == Severity.ATTENTION)
        assertEquals(Severity.ATTENTION, TriagePolicy.shieldSeverity(4 * 60 * 60 * 1000))
    }

    @Test
    fun riskItemsKeepTheHighestSeverityFirst() {
        val sorted = TriagePolicy.sort(
            listOf(
                TriageItem("签到", "", Severity.ATTENTION),
                TriageItem("连接异常", "", Severity.RISK, destination = TriageDestination.MORE),
            ),
        )

        assertEquals("连接异常", sorted.first().title)
        assertEquals(TriageDestination.MORE, sorted.first().destination)
    }

    @Test
    fun gameChangingQuickActionsRequireConfirmation() {
        assertTrue(QuickAction.ASSIST.requiresConfirm)
        assertTrue(QuickAction.SIGN.requiresConfirm)
        assertTrue(QuickAction.CLAIM.requiresConfirm)
        assertTrue(QuickAction.WELFARE_CLAIM.requiresConfirm)
        assertTrue(QuickAction.DOCK_REWARD.requiresConfirm)
        assertTrue(!QuickAction.REFRESH.requiresConfirm)
    }

}
