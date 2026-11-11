package com.cok.console.ui

/** Pure presentation rules for time-sensitive home-screen decisions. */
internal object TriagePolicy {
    private const val STALE_AFTER_SECONDS = 10 * 60L
    private const val SHIELD_URGENT_AFTER_MS = 2 * 60 * 60 * 1000L
    private const val SHIELD_ATTENTION_AFTER_MS = 6 * 60 * 60 * 1000L

    fun dataFreshness(ageSeconds: Long?): TriageItem? = when {
        ageSeconds == null -> TriageItem(
            "尚未获取游戏数据", "连接后点击刷新以读取最新状态", Severity.ATTENTION,
            QuickAction.REFRESH.actionLabel, QuickAction.REFRESH,
        )
        ageSeconds > STALE_AFTER_SECONDS -> TriageItem(
            "游戏数据已过期", "上次读取于 ${ageSeconds / 60} 分钟前", Severity.ATTENTION,
            QuickAction.REFRESH.actionLabel, QuickAction.REFRESH,
        )
        else -> null
    }

    fun shieldTriage(leftMillis: Long): TriageItem = when {
        leftMillis <= 0L -> TriageItem(
            "当前没有保护罩", "被攻击会掉兵，建议尽快开罩", Severity.RISK,
            operationsFocus = OperationsFocus.SAFETY,
        )
        leftMillis <= SHIELD_URGENT_AFTER_MS -> TriageItem(
            "保护罩即将到期", "剩余 ${humanDuration(leftMillis)}，请检查自动保护", Severity.RISK,
            operationsFocus = OperationsFocus.SAFETY,
        )
        leftMillis <= SHIELD_ATTENTION_AFTER_MS -> TriageItem(
            "保护罩将在今天到期", "剩余 ${humanDuration(leftMillis)}，建议提前安排", Severity.ATTENTION,
            operationsFocus = OperationsFocus.SAFETY,
        )
        else -> TriageItem("保护罩生效中", "剩余 ${humanDuration(leftMillis)}", Severity.OK)
    }

    fun shieldSeverity(leftMillis: Long): Severity = shieldTriage(leftMillis).severity

    fun isStale(ageSeconds: Long?): Boolean = ageSeconds == null || ageSeconds > STALE_AFTER_SECONDS

    fun sort(items: List<TriageItem>): List<TriageItem> = items.sortedByDescending { it.severity.ordinal }

    fun humanDuration(ms: Long): String {
        val totalSec = ms / 1000
        val d = totalSec / 86400
        val h = (totalSec % 86400) / 3600
        val m = (totalSec % 3600) / 60
        return when {
            d > 0 -> "${d}天${h}小时"
            h > 0 -> "${h}小时${m}分"
            else -> "${m}分"
        }
    }
}
