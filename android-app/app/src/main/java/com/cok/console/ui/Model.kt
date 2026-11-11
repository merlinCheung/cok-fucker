package com.cok.console.ui

import com.cok.console.net.ConsoleRepository
import org.json.JSONObject

/** Lifecycle of the embedded Python control server. */
sealed interface ServerState {
    data object Booting : ServerState
    data class Failed(val message: String) : ServerState
    data class Ready(val baseUrl: String, val token: String, val fullUrl: String) : ServerState
}

typealias RepositoryFactory = (baseUrl: String, token: String) -> ConsoleRepository

/** Severity for a triage item. Order matters: higher ordinal shows first. */
enum class Severity { OK, INFO, ATTENTION, RISK }

/** The native destination most likely to resolve a non-inline triage item. */
enum class TriageDestination { OPERATIONS, MORE }

/** A focused section within the operations tab for a home-screen handoff. */
enum class OperationsFocus { SAFETY, HUNT }

/** A single "what should I do now" row derived from the raw snapshot. */
data class TriageItem(
    val title: String,
    val detail: String,
    val severity: Severity,
    val actionLabel: String? = null,
    val action: QuickAction? = null,
    val destination: TriageDestination = TriageDestination.OPERATIONS,
    val operationsFocus: OperationsFocus? = null,
)

/** A compact status metric shown on the home screen. */
data class StatusMetric(
    val label: String,
    val value: String,
    val severity: Severity,
)

/** Read-only operational detail migrated from the web dashboard. */
data class DashboardCard(
    val title: String,
    val summary: String = "",
    val fields: List<DashboardField> = emptyList(),
    val emptyMessage: String? = null,
)

data class DashboardField(
    val label: String,
    val value: String,
    val severity: Severity = Severity.INFO,
)

/** A completed task/action, grouped by the server's day, ISO week, and month. */
data class TaskStatDetail(
    val label: String,
    val count: Int,
)

data class TaskStatEntry(
    val label: String,
    val count: Int,
    val details: List<TaskStatDetail>,
)

data class TaskStatPeriod(
    val label: String,
    val total: Int,
    val entries: List<TaskStatEntry>,
)

data class TaskStats(
    val day: TaskStatPeriod,
    val week: TaskStatPeriod,
    val month: TaskStatPeriod,
)

/** A recent local console event suitable for a compact diagnostics timeline. */
data class ConsoleEvent(
    val time: String,
    val kind: String,
    val message: String,
    val severity: Severity = Severity.INFO,
)

/** A registered game account and its engine state from the local manager. */
data class AccountProfile(
    val key: String,
    val label: String,
    val roleName: String,
    val gameUid: String,
    val server: String,
    val isActive: Boolean,
    val isRunning: Boolean,
    val isParallel: Boolean,
    val priority: Int = 2,
    val automationEnabled: Int = 0,
    val automationPaused: Boolean = false,
    val lastAutomationStatus: String = "waiting",
    val lastAutomationSummary: String = "尚未执行",
    val summary: AccountSummary? = null,
)

/** Compact per-account state for the multi-account fleet overview. */
data class AccountSummary(
    val hasShield: Boolean,
    val shieldMs: Long,
    val dockRewardable: Int,
    val welfareClaimable: Boolean,
    val hunting: Boolean,
    val huntKills: Int,
    val error: String,
    val disconnected: Boolean,
    val appYield: Boolean,
    val stale: Boolean,
)

/** A game identity returned after a successful Guopan channel-account login. */
data class ChannelGameAccount(
    val perGameId: String,
    val name: String,
    val roleName: String,
    val gameUid: String,
    val zone: String,
    val level: String,
    val hasCharacter: Boolean,
    val inLibrary: Boolean,
    val note: String,
)

/** A short-lived channel-login result; credentials remain only in the local server session. */
data class ChannelLoginResult(
    val sessionId: String,
    val account: String,
    val guopanUid: String,
    val note: String,
    val smallAccounts: List<ChannelGameAccount>,
)

/** One rule as evaluated by the local automation engine. */
data class AutomationRule(
    val key: String,
    val label: String,
    val enabled: Boolean,
    val status: String,
    val reason: String,
    val lastAt: Long,
    val nextCheckAt: Long,
    val failures: Int,
)

/** A durable result for a manual, automatic, or background execution. */
data class AutomationHistoryItem(
    val id: String,
    val timestamp: Long,
    val rule: String,
    val source: String,
    val status: String,
    val summary: String,
    val reason: String,
)

/** A failed rule that needs a person rather than another silent retry. */
data class AutomationAlert(
    val key: String,
    val label: String,
    val reason: String,
    val failures: Int,
    val lastAt: Long,
    val inBackoff: Boolean,
)

data class AutomationPolicy(
    val paused: Boolean,
    val mode: String,
    val maxFailures: Int,
    val backoffMinutes: Int,
    val alertLevel: String,
    val huntMinStamina: Int,
    val skyMinPower: Int,
    val dockMinResourceReserve: Int,
)

/** Action-oriented subset of a raw game snapshot for the native operations tab. */
data class OperationsSnapshot(
    val shieldActive: Boolean,
    val shieldStatus: String,
    val automation: AutomationSettings,
    val shieldSlots: List<ShieldSlot>,
    val runningQueues: List<QueueStatus>,
    val speedupItems: List<SpeedupItem>,
    val huntDataAvailable: Boolean,
    val huntUnavailableReason: String,
    val hunt: HuntStatus,
    val sky: SkyStatus,
    val dock: DockStatus,
    val automationRuntime: AutomationRuntime,
    val automationRules: List<AutomationRule>,
    val automationHistory: List<AutomationHistoryItem>,
    val automationAlerts: List<AutomationAlert>,
    val automationPolicy: AutomationPolicy,
    val alliance: AllianceStatus?,
    val assist: QuickAssistStatus?,
)

/**
 * Alliance panel state (alliance tree / task board / donation tiers).
 *
 * Mirrors the web console's `alliance` snapshot section. Donating and accepting
 * tasks are real side effects, so the UI only exposes them as explicit actions.
 */
data class AllianceStatus(
    val loaded: Boolean,
    val researchingScienceId: String,
    val researchingLevel: Int,
    val researchingStar: Int,
    val researchingProgress: String,
    val researchingPercent: Int,
    val researchingFull: Boolean,
    val donateReady: Boolean,
    val donateReason: String,
    val donateTiers: List<AllianceDonateTier>,
    val taskAcceptLeft: Int,
    val taskPublishLeft: Int,
    val publishedTasks: Int,
    val pendingTaskCount: Int,
    val signInDays: Int,
    val signInDone: Boolean,
    val signInReward: String,
    val alliancePoint: Int,
    val autoSignIn: Boolean,
    val assistAuto: Boolean,
)

/** 游戏内「一键完成」(CityAssist) 面板的清单与状态。 */
data class QuickAssistStatus(
    val items: List<QuickAssistItem>,
    val autoEnabled: Boolean,
    val costly: Boolean,
    val lastDay: String,
)

/** 面板里的一个项目(共 13 项)。 */
data class QuickAssistItem(
    val name: String,
    val groupName: String,
    val cost: String,
    val autoKind: String,
    val state: String,
)

/** One donation tier offered by the server for the researching alliance tech. */
data class AllianceDonateTier(
    val key: String,
    val name: String,
    val resource: String,
    val amount: String,
    val contribute: String,
    val progress: String,
    val available: Boolean?,
)

/** Observable evidence that saved automation is connected and being evaluated. */
data class AutomationRuntime(
    val lastPoll: String,
    val autoShieldPersistent: Boolean,
    val shieldWatchTicks: Int,
    val shieldWatchIntervalSeconds: Int,
    val latestAutomaticEvent: ConsoleEvent?,
)

/** Compact native representation of the harbour workflow. */
data class DockStatus(
    val available: Boolean,
    val disabled: Boolean,
    val family: String,
    val rewardable: Int,
    val trading: Int,
    val idle: Int,
    val shipLimit: Int,
    val cargoClaimable: Boolean,
    val note: String,
    val lastReward: String,
    val lastAutomaticRun: String,
)

/** Persisted console rules which act on a later eligible refresh. */
data class AutomationSettings(
    val autoSign: Boolean,
    val autoShield: Boolean,
    val autoWelfare: Boolean,
    val scoreAutoClaim: Boolean,
    val dockAutoReward: Boolean,
    val dockAutoSend: Boolean,
    val skyAutoReward: Boolean,
    val skyAutoExplore: Boolean,
    val allianceDonate: Boolean,
    val allianceSignIn: Boolean,
    val assistAuto: Boolean,
    val assistAutoCostly: Boolean,
) {
    val enabledCount: Int
        get() = listOf(
            autoSign, autoShield, autoWelfare, scoreAutoClaim,
            dockAutoReward, dockAutoSend, skyAutoReward, skyAutoExplore,
            allianceDonate, allianceSignIn, assistAuto,
        ).count { it }
}

/** A configured one-key shield slot returned by the game. */
data class ShieldSlot(
    val index: Int,
    val name: String,
    val items: List<ShieldItem>,
)

data class ShieldItem(
    val id: String,
    val name: String,
    val duration: String,
    val count: Int,
)

data class QueueStatus(
    val uuid: String,
    val queueId: String,
    val type: Int,
    val name: String,
    val detail: String,
    val remainingMillis: Long,
)

/** One owned acceleration-item instance returned by the local console. */
data class SpeedupItem(
    val itemId: String,
    val uuid: String,
    val name: String,
    val label: String,
    val count: Int,
    val seconds: Long,
    val type: Int,
)

data class HuntStatus(
    val isAvailable: Boolean,
    val stamina: Int,
    val staminaMax: Int,
    val isRunning: Boolean,
    val kills: Int,
    val level: Int,
    val soldiersPerSquad: Int,
    val squadCount: Int,
    /** 每队最多用几种兵: 1 = 每队一种兵; 2+ = 一次出征混编多种兵(只同类)。 */
    val mix: Int,
    val maxKills: Int,
    val failures: Int,
    val note: String,
    val waitFor: String,
    val squads: List<HuntSquadStatus>,
    /** 体力不足时自动喝背包里的体力药水。 */
    val autoStamina: Boolean = false,
    /** 本次运行已经喝掉多少瓶体力药水。 */
    val staminaPotions: Int = 0,
)

/** Live progress of one native auto-hunt squad. */
data class HuntSquadStatus(
    val slot: Int,
    val name: String,
    val soldiers: Int,
    val state: String,
    val kills: Int,
    val failures: Int,
    val target: String,
    val elapsedSeconds: Int,
    val note: String,
    /** 混编明细: 每个兵种的名字 + 人数(单兵种时为空)。 */
    val troops: List<HuntSquadTroop> = emptyList(),
)

/** One troop type inside a (possibly mixed) auto-hunt squad. */
data class HuntSquadTroop(
    val name: String,
    val num: Int,
)

/** One rally duration tier, as configured by the server's world_rally table. */
data class RallySlot(
    val slot: Int,
    val minutes: Int,
)

/** One known giant-griffin target on the world map. */
data class RallyTarget(
    val index: Int,
    val monsterId: String,
    val level: Int,
    val hp: Int,
    val maxHp: Int,
    val busy: Boolean,
)

/** One rally this account has already created. */
data class RallyMine(
    val targetId: Int,
    val monsterId: String,
    val waitMinutes: Double,
    val members: Int,
)

/**
 * Giant-griffin rally (activity boss) state.
 *
 * A rally spends real stamina and soldiers and creates a team in the alliance,
 * so the native UI only exposes it as an explicit, confirmed action.
 */
data class RallyStatus(
    val loaded: Boolean,
    val levels: List<Int>,
    val bosses: List<RallyTarget>,
    val slots: List<RallySlot>,
    val myRallies: List<RallyMine>,
    val rallyCount: Int,
    val known: Int,
    val stamina: Int,
    val staminaCost: Int,
)

data class SkyStatus(
    val stateText: String,
    val canExplore: Boolean,
    val canClaim: Boolean,
    val reason: String,
    val remaining: Long,
    val level: Int,
    val currentPower: Long,
    val requiredPower: Long,
    val lastAutomaticRun: String,
)

/** Visible result of a native action, retained long enough to validate the outcome. */
data class ActionOutcome(
    val title: String,
    val detail: String,
    val succeeded: Boolean,
    val snapshotVerified: Boolean,
    val pendingCount: Int? = null,
)

/** Read-only map index health, updated separately while an independent scan runs. */
data class MapIndexStatus(
    val playerCount: Int,
    val isScanning: Boolean,
    val requestsDone: Int,
    val requestsTotal: Int,
    val percent: Float,
    val isPartial: Boolean,
    val errors: Int,
    val mismatched: Int,
    val dropped: Int,
)

data class LocatedPlayer(
    val name: String,
    val uid: String,
    val x: String,
    val y: String,
    val level: String,
)

data class LocateResult(
    val source: String,
    val players: List<LocatedPlayer>,
    val message: String = "",
    val scanRequests: Int = 0,
    val stale: Boolean = false,
)

/** One past full/partial scan run, shown in the Android map-index history list. */
data class ScanHistoryRun(
    val startedAt: Long,
    val finishedAt: Long,
    val status: String,
    val step: Int,
    val radius: Int,
    val players: Int,
    val realPlayers: Int,
    val requestsDone: Int,
    val requestsTotal: Int,
    val errors: Int,
)

data class ExportPayload(
    val filename: String,
    val bytes: ByteArray,
)

/** Actions the native home screen can trigger directly against the local API. */
enum class QuickAction(
    val actionLabel: String,
    val requiresConfirm: Boolean = false,
    val confirmTitle: String = "",
    val confirmBody: String = "",
) {
    REFRESH("立即刷新"),
    ASSIST(
        "一键完成", true, "确认一键完成",
        "等同游戏里「领地辅助 → 一键完成」：按面板顺序逐项执行。" +
            "默认只跑无损项(收取资源/科研工坊/文明结晶)；" +
            "若开启「连消耗项一起」，英雄试炼/龙塔试炼/研习/招募/献祭会消耗金币、道具或体力。",
    ),
    SIGN("立即签到", true, "确认签到", "将提交今日签到并领取对应奖励。"),
    CLAIM("领取任务奖励", true, "确认领取任务奖励", "将领取当前可用的任务奖励。"),
    WELFARE_CLAIM("领取福利", true, "确认领取福利", "将领取当前可用的福利奖励。"),
    DOCK_REWARD("领取港口奖励", true, "确认领取港口奖励", "将领取当前可用的港口奖励。"),
    ALLIANCE_ACCEPT(
        "接取联盟任务", true, "确认接取联盟任务",
        "将占用联盟任务位接取队友发布的任务（上限 10 个）。",
    ),
    ALLIANCE_DONATE(
        "捐献联盟科技", true, "确认捐献联盟科技",
        "将消耗资源捐献给正在研究的联盟科技，换取联盟贡献与科技进度。",
    ),
    ALLIANCE_HELP_ALL(
        "帮助联盟全体", true, "确认帮助联盟全体",
        "将帮助联盟全体正在进行的队列（等于游戏里点「帮助全体」）。",
    ),
    ALLIANCE_SIGN_IN(
        "领取联盟签到", true, "确认领取联盟签到",
        "将领取今天的联盟签到奖励（每天一次）。",
    ),
    ;
}

/** Everything the native UI needs, parsed once from the raw snapshot JSON. */
data class ConsoleSnapshot(
    val connectionLabel: String,
    val connectionSeverity: Severity,
    val gameDataAvailable: Boolean,
    val account: String,
    val accounts: List<AccountProfile>,
    val accountSource: String,
    val lastPoll: String,
    val dataIsStale: Boolean,
    val triage: List<TriageItem>,
    val taskStats: TaskStats,
    val metrics: List<StatusMetric>,
    val dashboardCards: List<DashboardCard>,
    val recentEvents: List<ConsoleEvent>,
    val operations: OperationsSnapshot,
    val mapIndex: MapIndexStatus,
    val bannerText: String?,
    val bannerIsError: Boolean,
) {
    val pendingCount: Int get() = triage.count { it.severity == Severity.ATTENTION || it.severity == Severity.RISK }

    companion object {
        fun from(json: JSONObject): ConsoleSnapshot = SnapshotParser.parse(json)
    }
}
